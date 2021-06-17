"""
Various utilities for recording and embedding state in a rendered app.
"""
import datetime as dt
import json
import threading

from collections import OrderedDict
from weakref import WeakKeyDictionary, WeakSet
from urllib.parse import urljoin

import param

from bokeh.document import Document
from bokeh.io import curdoc as _curdoc
from pyviz_comms import CommManager as _CommManager
from tornado.web import decode_signed_value

from ..util import base64url_decode


class _state(param.Parameterized):
    """
    Holds global state associated with running apps, allowing running
    apps to indicate their state to a user.
    """

    base_url = param.String(default='/', readonly=True, doc="""
       Base URL for all server paths.""")

    busy = param.Boolean(default=False, readonly=True, doc="""
       Whether the application is currently busy processing a user
       callback.""")

    cache = param.Dict(default={}, doc="""
       Global location you can use to cache large datasets or expensive computation results
       across multiple client sessions for a given server.""")

    encryption = param.Parameter(default=None, doc="""
       Object with encrypt and decrypt methods to support encryption
       of secret variables including OAuth information.""")

    rel_path = param.String(default='', readonly=True, doc="""
       Relative path from the current app being served to the root URL.""")

    session_info = param.Dict(default={'total': 0, 'live': 0,
                                       'sessions': OrderedDict()}, doc="""
       Tracks information and statistics about user sessions.""")

    webdriver = param.Parameter(default=None, doc="""
      Selenium webdriver used to export bokeh models to pngs.""")

    _curdoc = param.ClassSelector(class_=Document, doc="""
        The bokeh Document for which a server event is currently being
        processed.""")

    # Whether to hold comm events
    _hold = False

    # Used to ensure that events are not scheduled from the wrong thread
    _thread_id = None

    _comm_manager = _CommManager

    # Locations
    _location = None # Global location, e.g. for notebook context
    _locations = WeakKeyDictionary() # Server locations indexed by document

    # Templates
    _templates = WeakKeyDictionary() # Server templates indexed by document
    _template = None

    # An index of all currently active views
    _views = {}

    # For templates to keep reference to their main root
    _fake_roots = []

    # An index of all currently active servers
    _servers = {}

    # Jupyter display handles
    _handles = {}

    # Dictionary of callbacks to be triggered on app load
    _onload = WeakKeyDictionary()
    _on_session_created = []

    # Stores a set of locked Websockets, reset after every change event
    _locks = WeakSet()

    # Indicators listening to the busy state
    _indicators = []

    # Endpoints
    _rest_endpoints = {}

    def __repr__(self):
        server_info = []
        for server, panel, docs in self._servers.values():
            server_info.append(
                "{}:{:d} - {!r}".format(server.address or "localhost", server.port, panel)
            )
        if not server_info:
            return "state(servers=[])"
        return "state(servers=[\n  {}\n])".format(",\n  ".join(server_info))

    def _unblocked(self, doc):
        thread = threading.current_thread()
        thread_id = thread.ident if thread else None
        return doc is self.curdoc and self._thread_id == thread_id

    @param.depends('busy', watch=True)
    def _update_busy(self):
        for indicator in self._indicators:
            indicator.value = self.busy

    def _init_session(self, event):
        if not self.curdoc.session_context:
            return
        session_id = self.curdoc.session_context.id
        session_info = self.session_info['sessions'].get(session_id, {})
        if session_info.get('rendered') is not None:
            return
        self.session_info['live'] += 1
        session_info.update({
            'rendered': dt.datetime.now().timestamp()
        })

    def _get_callback(self, endpoint):
        _updating = {}
        def link(*events):
            event = events[0]
            obj = event.cls if event.obj is None else event.obj
            parameterizeds = self._rest_endpoints[endpoint][0]
            if obj not in parameterizeds:
                return
            updating = _updating.get(id(obj), [])
            values = {event.name: event.new for event in events
                      if event.name not in updating}
            if not values:
                return
            _updating[id(obj)] = list(values)
            for parameterized in parameterizeds:
                if parameterized in _updating:
                    continue
                try:
                    parameterized.param.set_param(**values)
                except Exception:
                    raise
                finally:
                    if id(obj) in _updating:
                        not_updated = [p for p in _updating[id(obj)] if p not in values]
                        _updating[id(obj)] = not_updated
        return link

    def _on_load(self, event):
        for cb in self._onload.pop(self.curdoc, []):
            cb()

    #----------------------------------------------------------------
    # Public Methods
    #----------------------------------------------------------------

    def as_cached(self, key, fn, **kwargs):
        """
        Caches the return value of a function, memoizing on the given
        key and supplied keyword arguments.

        Note: Keyword arguments must be hashable.

        Arguments
        ---------
        key: (str)
          The key to cache the return value under.
        fn: (callable)
          The function or callable whose return value will be cached.
        **kwargs: dict
          Additional keyword arguments to supply to the function,
          which will be memoized over as well.

        Returns
        -------
        Returns the value returned by the cache or the value in
        the cache.
        """
        key = (key,)+tuple((k, v) for k, v in sorted(kwargs.items()))
        if key in self.cache:
            ret = self.cache.get(key)
        else:
            ret = self.cache[key] = fn(**kwargs)
        return ret

    def add_periodic_callback(self, callback, period=500, count=None,
                              timeout=None, start=True):
        """
        Schedules a periodic callback to be run at an interval set by
        the period. Returns a PeriodicCallback object with the option
        to stop and start the callback.

        Arguments
        ---------
        callback: callable
          Callable function to be executed at periodic interval.
        period: int
          Interval in milliseconds at which callback will be executed.
        count: int
          Maximum number of times callback will be invoked.
        timeout: int
          Timeout in seconds when the callback should be stopped.
        start: boolean (default=True)
          Whether to start callback immediately.

        Returns
        -------
        Return a PeriodicCallback object with start and stop methods.
        """
        from .callbacks import PeriodicCallback

        cb = PeriodicCallback(callback=callback, period=period,
                              count=count, timeout=timeout)
        if start:
            cb.start()
        return cb

    def kill_all_servers(self):
        """Stop all servers and clear them from the current state."""
        for server_id in self._servers:
            try:
                self._servers[server_id][0].stop()
            except AssertionError:  # can't stop a server twice
                pass
        self._servers = {}

    def onload(self, callback):
        """
        Callback that is triggered when a session has been served.
        """
        if self.curdoc is None:
            callback()
            return
        if self.curdoc not in self._onload:
            self._onload[self.curdoc] = []
            self.curdoc.on_event('document_ready', self._on_load)
        self._onload[self.curdoc].append(callback)

    def on_session_created(self, callback):
        """
        Callback that is triggered when a session is created.
        """
        self._on_session_created.append(callback)

    def publish(self, endpoint, parameterized, parameters=None):
        """
        Publish parameters on a Parameterized object as a REST API.

        Arguments
        ---------
        endpoint: str
          The endpoint at which to serve the REST API.
        parameterized: param.Parameterized
          The Parameterized object to publish parameters from.
        parameters: list(str) or None
          A subset of parameters on the Parameterized to publish.
        """
        if parameters is None:
            parameters = list(parameterized.param)
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        if endpoint in self._rest_endpoints:
            parameterizeds, old_parameters, cb = self._rest_endpoints[endpoint]
            if set(parameters) != set(old_parameters):
                raise ValueError("Param REST API output parameters must match across sessions.")
            values = {k: v for k, v in parameterizeds[0].param.get_param_values() if k in parameters}
            parameterized.param.set_param(**values)
            parameterizeds.append(parameterized)
        else:
            cb = self._get_callback(endpoint)
            self._rest_endpoints[endpoint] = ([parameterized], parameters, cb)
        parameterized.param.watch(cb, parameters)

    def sync_busy(self, indicator):
        """
        Syncs the busy state with an indicator with a boolean value
        parameter.

        Arguments
        ---------
        indicator: An BooleanIndicator to sync with the busy property
        """
        if not isinstance(indicator.param.value, param.Boolean):
            raise ValueError("Busy indicator must have a value parameter"
                             "of Boolean type.")
        self._indicators.append(indicator)

    #----------------------------------------------------------------
    # Public Properties
    #----------------------------------------------------------------

    @property
    def access_token(self):
        from ..config import config
        access_token = self.cookies.get('access_token')
        if access_token is None:
            return None
        access_token = decode_signed_value(config.cookie_secret, 'access_token', access_token)
        if self.encryption is None:
            return access_token.decode('utf-8')
        return self.encryption.decrypt(access_token).decode('utf-8')

    @property
    def app_url(self):
        if not self.curdoc:
            return
        app_url = self.curdoc.session_context.server_context.application_context.url
        app_url = app_url[1:] if app_url.startswith('/') else app_url
        return urljoin(self.base_url, app_url)

    @property
    def curdoc(self):
        if self._curdoc:
            return self._curdoc
        elif _curdoc().session_context:
            return _curdoc()

    @curdoc.setter
    def curdoc(self, doc):
        self._curdoc = doc

    @property
    def cookies(self):
        return self.curdoc.session_context.request.cookies if self.curdoc else {}

    @property
    def headers(self):
        return self.curdoc.session_context.request.headers if self.curdoc else {}

    @property
    def location(self):
        if self.curdoc and self.curdoc not in self._locations:
            from .location import Location
            self._locations[self.curdoc] = loc = Location()
            return loc
        elif self.curdoc is None:
            return self._location
        else:
            return self._locations.get(self.curdoc) if self.curdoc else None

    @property
    def session_args(self):
        return self.curdoc.session_context.request.arguments if self.curdoc else {}

    @property
    def template(self):
        from ..config import config
        if self.curdoc in self._templates:
            return self._templates[self.curdoc]
        elif self.curdoc is None and self._template:
            return self._template
        template = config.template(theme=config.theme)
        if self.curdoc is None:
            self._template = template
        else:
            self._templates[self.curdoc] = template
        return template

    @property
    def user(self):
        from ..config import config
        user = self.cookies.get('user')
        if user is None or config.cookie_secret is None:
            return None
        return decode_signed_value(config.cookie_secret, 'user', user).decode('utf-8')

    @property
    def user_info(self):
        from ..config import config
        id_token = self.cookies.get('id_token')
        if id_token is None or config.cookie_secret is None:
            return None
        id_token = decode_signed_value(config.cookie_secret, 'id_token', id_token)
        if self.encryption is None:
            id_token = id_token
        else:
            id_token = self.encryption.decrypt(id_token)
        if b"." in id_token:
            signing_input, _ = id_token.rsplit(b".", 1)
            _, payload_segment = signing_input.split(b".", 1)
        else:
            payload_segment = id_token
        return json.loads(base64url_decode(payload_segment).decode('utf-8'))


state = _state()
