"""
Various utilities for recording and embedding state in a rendered app.
"""
from __future__ import annotations

import asyncio
import datetime as dt
import functools
import inspect
import json
import logging
import shutil
import sys
import threading
import time

from collections import OrderedDict, defaultdict
from collections.abc import Iterator
from contextlib import contextmanager
from functools import partial
from typing import (
    TYPE_CHECKING, Any, Callable, ClassVar, Coroutine, Dict,
    Iterator as TIterator, List, Optional, Tuple, TypeVar, Union,
)
from urllib.parse import urljoin
from weakref import WeakKeyDictionary

import param

from bokeh.document import Document
from bokeh.document.locking import UnlockedDocumentProxy
from bokeh.io import curdoc as _curdoc
from pyviz_comms import CommManager as _CommManager
from typing_extensions import Literal

from ..util import base64url_decode, parse_timedelta
from .logging import LOG_SESSION_RENDERED, LOG_USER_MSG

_state_logger = logging.getLogger('panel.state')

if TYPE_CHECKING:
    from bokeh.model import Model
    from bokeh.server.contexts import BokehSessionContext
    from bokeh.server.server import Server
    from IPython.display import DisplayHandle
    from pyviz_comms import Comm
    from tornado.ioloop import IOLoop

    from ..template.base import BaseTemplate
    from ..viewable import Viewable
    from ..widgets.indicators import BooleanIndicator
    from .callbacks import PeriodicCallback
    from .location import Location
    from .notifications import NotificationArea
    from .server import StoppableThread

    T = TypeVar("T")


@contextmanager
def set_curdoc(doc: Document):
    orig_doc = state._curdoc
    state._curdoc = doc
    yield
    state._curdoc = orig_doc

def curdoc_locked() -> Document:
    doc = _curdoc()
    if isinstance(doc, UnlockedDocumentProxy):
        doc = doc._doc
    return doc

class _Undefined: pass

Tat = Union[dt.datetime, Callable[[dt.datetime], dt.datetime], TIterator[dt.datetime]]

class _state(param.Parameterized):
    """
    Holds global state associated with running apps, allowing running
    apps to indicate their state to a user.
    """

    admin_context = param.Parameter()

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
       Relative path from the current app being served to the root URL.
       If application is embedded in a different server via autoload.js
       this will instead reflect an absolute path.""")

    session_info = param.Dict(default={'total': 0, 'live': 0,
                                       'sessions': OrderedDict()}, doc="""
       Tracks information and statistics about user sessions.""")

    webdriver = param.Parameter(default=None, doc="""
      Selenium webdriver used to export bokeh models to pngs.""")

    _memoize_cache = param.Dict(default={}, doc="""
       A dictionary used by the cache decorator.""")

    # Holds temporary curdoc overrides per thread
    _curdoc_ = defaultdict(WeakKeyDictionary)

    # Whether to hold comm events
    _hold: ClassVar[bool] = False

    # Used to ensure that events are not scheduled from the wrong thread
    _thread_id_: ClassVar[WeakKeyDictionary[Document, int]] = WeakKeyDictionary()
    _thread_pool = None

    # Admin application (remove in Panel 1.0 / Bokeh 3.0)
    _admin_context = None

    # Jupyter communication
    _comm_manager = _CommManager
    _kernels = {}

    # Locations
    _location: ClassVar[Location | None] = None # Global location, e.g. for notebook context
    _locations: ClassVar[WeakKeyDictionary[Document, Location]] = WeakKeyDictionary() # Server locations indexed by document

    # Locations
    _notification: ClassVar[NotificationArea | None] = None # Global location, e.g. for notebook context
    _notifications: ClassVar[WeakKeyDictionary[Document, NotificationArea]] = WeakKeyDictionary() # Server locations indexed by document

    # Templates
    _template: ClassVar[BaseTemplate | None] = None
    _templates: ClassVar[WeakKeyDictionary[Document, BaseTemplate]] = WeakKeyDictionary() # Server templates indexed by document

    # An index of all currently active views
    _views: ClassVar[Dict[str, Tuple[Viewable, Model, Document, Comm | None]]] = {}

    # For templates to keep reference to their main root
    _fake_roots: ClassVar[List[str]] = []

    # An index of all currently active servers
    _servers: ClassVar[Dict[str, Tuple[Server, Viewable | BaseTemplate, List[Document]]]] = {}
    _threads: ClassVar[Dict[str, StoppableThread]] = {}

    # Jupyter display handles
    _handles: ClassVar[Dict[str, [DisplayHandle, List[str]]]] = {}

    # Stacks for hashing
    _stacks = WeakKeyDictionary()

    # Dictionary of callbacks to be triggered on app load
    _onload: ClassVar[Dict[Document, Callable[[], None]]] = WeakKeyDictionary()
    _on_session_created: ClassVar[List[Callable[[BokehSessionContext], []]]] = []

    # Module that was run during setup
    _setup_module = None

    # Scheduled callbacks
    _scheduled: ClassVar[Dict[str, Tuple[Iterator[int], Callable[[], None]]]] = {}
    _periodic: ClassVar[WeakKeyDictionary[Document, List[PeriodicCallback]]] = WeakKeyDictionary()

    # Indicators listening to the busy state
    _indicators: ClassVar[List[BooleanIndicator]] = []

    # Profilers
    _launching = []
    _profiles = param.Dict(defaultdict(list))

    # Endpoints
    _rest_endpoints = {}

    # Locks
    _cache_locks: ClassVar[Dict[str, threading.Lock]] = {'main': threading.Lock()}

    def __repr__(self) -> str:
        server_info = []
        for server, panel, docs in self._servers.values():
            server_info.append(
                "{}:{:d} - {!r}".format(server.address or "localhost", server.port, panel)
            )
        if not server_info:
            return "state(servers=[])"
        return "state(servers=[\n  {}\n])".format(",\n  ".join(server_info))

    @property
    def _ioloop(self) -> 'IOLoop':
        if state._is_pyodide:
            return asyncio.get_running_loop()
        else:
            from tornado.ioloop import IOLoop
            return IOLoop.current()

    @property
    def _is_pyodide(self) -> bool:
        return '_pyodide' in sys.modules

    @property
    def _thread_id(self) -> int | None:
        return self._thread_id_.get(self.curdoc) if self.curdoc else None

    @_thread_id.setter
    def _thread_id(self, thread_id: int) -> None:
        if self.curdoc:
            self._thread_id_[self.curdoc] = thread_id

    def _unblocked(self, doc: Document) -> bool:
        thread = threading.current_thread()
        thread_id = thread.ident if thread else None
        return doc is self.curdoc and self._thread_id in (thread_id, None)

    @param.depends('busy', watch=True)
    def _update_busy(self) -> None:
        for indicator in self._indicators:
            indicator.value = self.busy

    def _init_session(self, event):
        if not self.curdoc.session_context:
            return
        from .server import logger
        session_id = self.curdoc.session_context.id
        session_info = self.session_info['sessions'].get(session_id, {})
        if session_info.get('rendered') is not None:
            return
        logger.info(LOG_SESSION_RENDERED, id(self.curdoc))
        self.session_info['live'] += 1
        session_info.update({
            'rendered': dt.datetime.now().timestamp()
        })
        self.param.trigger('session_info')

    def _destroy_session(self, session_context):
        session_id = session_context.id
        sessions = self.session_info['sessions']
        if session_id in sessions and sessions[session_id]['ended'] is None:
            session = sessions[session_id]
            if session['rendered'] is not None:
                self.session_info['live'] -= 1
            session['ended'] = dt.datetime.now().timestamp()
            self.param.trigger('session_info')
        doc = session_context._document

        # Cleanup periodic callbacks
        if doc in self._periodic:
            for cb in self._periodic[doc]:
                try:
                    cb._cleanup(session_context)
                except Exception:
                    pass
            del self._periodic[doc]

        # Cleanup Locations
        if doc in self._locations:
            loc = state._locations[doc]
            loc._server_destroy(session_context)
            del state._locations[doc]

        # Cleanup Notifications
        if doc in self._notifications:
            notification = self._notifications[doc]
            notification._server_destroy(session_context)
            del state._notifications[doc]

        # Clean up templates
        if doc in self._templates:
            del self._templates[doc]

    @property
    def _current_stack(self):
        current_thread = threading.current_thread()
        stack = self._stacks.get(current_thread, None)
        if stack is None:
            from .cache import _Stack
            stack = _Stack()
            self._stacks[current_thread] = stack
        return stack

    def _get_callback(self, endpoint: str):
        _updating: Dict[int, bool] = {}
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
                if id(parameterized) in _updating:
                    continue
                try:
                    parameterized.param.update(**values)
                except Exception:
                    raise
                finally:
                    if id(obj) in _updating:
                        not_updated = [p for p in _updating[id(obj)] if p not in values]
                        if not_updated:
                            _updating[id(obj)] = not_updated
                        else:
                            del _updating[id(obj)]
        return link

    def _schedule_on_load(self, doc: Document, event) -> None:
        if self._thread_pool:
            self._thread_pool.submit(self._on_load, doc)
        else:
            self._on_load(doc)

    def _on_load(self, doc: Optional[Document] = None) -> None:
        doc = doc or self.curdoc
        callbacks = self._onload.pop(doc, [])
        if not callbacks:
            return

        from ..config import config
        from .profile import profile_ctx
        with set_curdoc(doc):
            if (doc and doc in self._launching) or not config.profiler:
                for cb in callbacks:
                    self.execute(cb, schedule=False)
                return
            with profile_ctx(config.profiler) as sessions:
                for cb in callbacks:
                    self.execute(cb, schedule=False)
            path = doc.session_context.request.path
            self._profiles[(path+':on_load', config.profiler)] += sessions
            self.param.trigger('_profiles')

    async def _scheduled_cb(self, name: str) -> None:
        if name not in self._scheduled:
            return
        diter, cb = self._scheduled[name]
        try:
            at = next(diter)
        except Exception:
            at = None
            del self._scheduled[name]
        if at is not None:
            now = dt.datetime.now().timestamp()
            call_time_seconds = (at - now)
            self._ioloop.call_later(delay=call_time_seconds, callback=partial(self._scheduled_cb, name))
        res = cb()
        if inspect.isawaitable(res):
            await res

    #----------------------------------------------------------------
    # Public Methods
    #----------------------------------------------------------------

    def as_cached(self, key: str, fn: Callable[[], T], ttl: int = None, **kwargs) -> T:
        """
        Caches the return value of a function, memoizing on the given
        key and supplied keyword arguments.

        Note: Keyword arguments must be hashable.

        Example:

        >>> def load_dataset(name):
        >>>     # some slow operation that uses name to load a dataset....
        >>>     return dataset
        >>> penguins = pn.state.as_cached('dataset-penguins', load_dataset, name='penguins')

        Arguments
        ---------
        key: (str)
          The key to cache the return value under.
        fn: (callable)
          The function or callable whose return value will be cached.
        ttl: (int)
          The number of seconds to keep an item in the cache, or None
          if the cache should not expire. The default is None.
        **kwargs: dict
          Additional keyword arguments to supply to the function,
          which will be memoized over as well.

        Returns
        -------
        Returns the value returned by the cache or the value in
        the cache.
        """
        key = (key,)+tuple((k, v) for k, v in sorted(kwargs.items()))
        new_expiry = time.monotonic() + ttl if ttl else None
        with self._cache_locks['main']:
            if key in self._cache_locks:
                lock = self._cache_locks[key]
            else:
                self._cache_locks[key] = lock = threading.Lock()
        try:
            with lock:
                if key in self.cache:
                    ret, expiry = self.cache.get(key)
                else:
                    ret, expiry = _Undefined, None
                if ret is _Undefined or (expiry is not None and expiry < time.monotonic()):
                    ret, _ = self.cache[key] = (fn(**kwargs), new_expiry)
        finally:
            if not lock.locked() and key in self._cache_locks:
                del self._cache_locks[key]
        return ret

    def add_periodic_callback(
        self, callback: Callable[[], None] | Coroutine[Any, Any, None],
        period: int=500, count: Optional[int] = None, timeout: int = None,
        start: bool=True
    ) -> PeriodicCallback:
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
        cb = PeriodicCallback(
            callback=callback, period=period, count=count, timeout=timeout
        )
        if start:
            if self._thread_id is not None:
                thread = threading.current_thread()
                thread_id = thread.ident if thread else None
                if self._thread_id != thread_id:
                    self.curdoc.add_next_tick_callback(cb.start)
                    return cb
            cb.start()
        if self.curdoc:
            if self.curdoc not in self._periodic:
                self._periodic[self.curdoc] = []
            self._periodic[self.curdoc].append(cb)
        return cb

    def cancel_task(self, name: str, wait: bool=False):
        """
        Cancel a task scheduled using the `state.schedule_task` method by name.

        Arguments
        ---------
        name: str
            The name of the scheduled task.
        wait: boolean
            Whether to wait until after the next execution.
        """
        if name not in self._scheduled:
            raise KeyError(f'No task with the name {name!r} has been scheduled.')
        if wait:
            self._scheduled[name] = (None, self._scheduled[name][1])
        else:
            del self._scheduled[name]

    def clear_caches(self):
        """
        Clears caches generated by panel.io.cache function.
        """
        for cache in self._memoize_cache.values():
            cache.clear()
            if hasattr(cache, 'directory'):
                cache.cache.close()
                try:
                    shutil.rmtree(cache.directory)
                except OSError:  # Windows wonkiness
                    pass
        self._memoize_cache.clear()

    def execute(
        self,
        callback: Callable([], None),
        schedule: bool | Literal['auto'] = 'auto'
    ) -> None:
        """
        Executes both synchronous and asynchronous callbacks
        appropriately depending on the context the application is
        running in. When running on the server callbacks are scheduled
        on the event loop ensuring the Bokeh Document lock is acquired
        and models can be modified directly.

        Arguments
        ---------
        callback: Callable[[], None]
          Callback to execute
        schedule: boolean | Literal['auto']
          Whether to schedule synchronous callback on the event loop
          or execute it immediately.
        """
        cb = callback
        while isinstance(cb, functools.partial):
            cb = cb.func
        doc = self.curdoc
        if param.parameterized.iscoroutinefunction(cb):
            param.parameterized.async_executor(callback)
        elif doc and doc.session_context and (schedule == True or (schedule == 'auto' and self._unblocked(doc))):
            doc.add_next_tick_callback(callback)
        else:
            callback()

    def get_profile(self, profile: str):
        """
        Returns the requested profiling output.

        Arguments
        ---------
        profile: str
          The name of the profiling output to return.

        Returns
        -------
        Profiling output wrapped in a pane.
        """
        from .profile import get_profiles
        return get_profiles({(n, e): ps for (n, e), ps in state._profiles.items()
                             if n == profile})[0][1]

    def kill_all_servers(self) -> None:
        """
        Stop all servers and clear them from the current state.
        """
        for thread in self._threads.values():
            try:
                thread.stop()
            except Exception:
                pass
        self._threads = {}
        for server_id in self._servers:
            try:
                self._servers[server_id][0].stop()
            except AssertionError:  # can't stop a server twice
                pass
        self._servers = {}

    def log(self, msg: str, level: str = 'info') -> None:
        """
        Logs user messages to the Panel logger.

        Arguments
        ---------
        msg: str
          Log message
        level: str
          Log level as a string, i.e. 'debug', 'info', 'warning' or 'error'.
        """
        args = ()
        if self.curdoc:
            args = (id(self.curdoc),)
            msg = LOG_USER_MSG.format(msg=msg)
        getattr(_state_logger, level.lower())(msg, *args)

    def onload(self, callback: Callable[[], None] | Coroutine[Any, Any, None]):
        """
        Callback that is triggered when a session has been served.

        Arguments
        ---------
        callback: Callable[[], None] | Coroutine[Any, Any, None]
           Callback that is executed when the application is loaded
        """
        if self.curdoc is None:
            if self._thread_pool:
                self._thread_pool.submit(partial(self.execute, callback, schedule=False))
            else:
                self.execute(callback, schedule=False)
            return
        elif self.curdoc not in self._onload:
            self._onload[self.curdoc] = []
            try:
                self.curdoc.on_event('document_ready', partial(self._schedule_on_load, self.curdoc))
            except AttributeError:
                pass # Document already cleaned up
        self._onload[self.curdoc].append(callback)

    def on_session_created(self, callback: Callable[[BokehSessionContext], None]) -> None:
        """
        Callback that is triggered when a session is created.
        """
        self._on_session_created.append(callback)

    def on_session_destroyed(self, callback: Callable[[BokehSessionContext], None]) -> None:
        """
        Callback that is triggered when a session is destroyed.
        """
        doc = self._curdoc or curdoc_locked()
        if doc:
            doc.on_session_destroyed(callback)
        else:
            raise RuntimeError(
                "Could not add session destroyed callback since no "
                "document to attach it to could be found."
            )

    def publish(
        self, endpoint: str, parameterized: param.Parameterized,
        parameters: Optional[List[str]] = None
    ) -> None:
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
            values = {k: v for k, v in parameterizeds[0].param.values().items() if k in parameters}
            parameterized.param.update(**values)
            parameterizeds.append(parameterized)
        else:
            cb = self._get_callback(endpoint)
            self._rest_endpoints[endpoint] = ([parameterized], parameters, cb)
        parameterized.param.watch(cb, parameters)


    def schedule_task(
        self, name: str, callback: Callable[[], None], at: Tat =None,
        period: str | dt.timedelta = None, cron: Optional[str] = None
    ) -> None:
        """
        Schedules a task at a specific time or on a schedule.

        By default the starting time is immediate but may be
        overridden with the `at` keyword argument. The scheduling may
        be declared using the `period` argument or a cron expression
        (which requires the `croniter` library). Note that the `at`
        time should be in local time but if a callable is provided it
        must return a UTC time.

        Note that the scheduled callback must not be defined within a
        script served using `panel serve` because the script and all
        its contents are cleaned up when the user session is
        destroyed. Therefore the callback must be imported from a
        separate module or should be scheduled from a setup script
        (provided to `panel serve` using the `--setup` argument). Note
        also that scheduling is idempotent, i.e.  if a callback has
        already been scheduled under the same name subsequent calls
        will have no effect. This is ensured that even if you schedule
        a task from within your application code, the task is only
        scheduled once.

        Arguments
        ---------
        name: str
          Name of the scheduled task
        callback: callable
          Callback to schedule
        at: datetime.datetime, Iterator or callable
          Declares a time to schedule the task at. May be given as a
          datetime or an Iterator of datetimes in the local timezone
          declaring when to execute the task. Alternatively may also
          declare a callable which is given the current UTC time and
          must return a datetime also in UTC.
        period: str or datetime.timedelta
          The period between executions, may be expressed as a
          timedelta or a string:

            - Week:   '1w'
            - Day:    '1d'
            - Hour:   '1h'
            - Minute: '1m'
            - Second: '1s'

        cron: str
          A cron expression (requires croniter to parse)
        """
        if name in self._scheduled:
            if callback is not self._scheduled[name][1]:
                self.param.warning(
                    "A separate task was already scheduled under the "
                    f"name {name!r}. The new task will be ignored. If "
                    "you want to replace the existing task cancel it "
                    f"with `state.cancel_task({name!r})` before adding "
                    "adding a new task under the same name."
                )
            return
        if getattr(callback, '__module__', '').startswith('bokeh_app_'):
            raise RuntimeError(
                "Cannot schedule a task from within the context of an "
                "application. Either import the task callback from a "
                "separate module or schedule the task from a setup "
                "script that you provide to `panel serve` using the "
                "--setup commandline argument."
            )
        if cron is None:
            if isinstance(period, str):
                period = parse_timedelta(period)
            def dgen():
                if isinstance(at, Iterator):
                    while True:
                        new = next(at)
                        yield new.timestamp()
                elif callable(at):
                    while True:
                        new = at(dt.datetime.utcnow())
                        if new is None:
                            raise StopIteration
                        yield new.replace(tzinfo=dt.timezone.utc).astimezone().timestamp()
                elif period is None:
                    yield at.timestamp()
                    raise StopIteration
                new_time = at or dt.datetime.now()
                while True:
                    yield new_time.timestamp()
                    new_time += period
            diter = dgen()
        else:
            from croniter import croniter
            base = dt.datetime.now() if at is None else at
            diter = croniter(cron, base)
        now = dt.datetime.now().timestamp()
        try:
            call_time_seconds = (next(diter) - now)
        except StopIteration:
            return
        self._scheduled[name] = (diter, callback)
        self._ioloop.call_later(
            delay=call_time_seconds, callback=partial(self._scheduled_cb, name)
        )

    def sync_busy(self, indicator: BooleanIndicator) -> None:
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
        if indicator not in self._indicators:
            self._indicators.append(indicator)

    #----------------------------------------------------------------
    # Public Properties
    #----------------------------------------------------------------

    @property
    def access_token(self) -> str | None:
        from tornado.web import decode_signed_value

        from ..config import config
        access_token = self.cookies.get('access_token')
        if access_token is None:
            return None
        access_token = decode_signed_value(config.cookie_secret, 'access_token', access_token)
        if self.encryption is None:
            return access_token.decode('utf-8')
        return self.encryption.decrypt(access_token).decode('utf-8')

    @property
    def app_url(self) -> str | None:
        if not self.curdoc:
            return
        app_url = self.curdoc.session_context.server_context.application_context.url
        app_url = app_url[1:] if app_url.startswith('/') else app_url
        return urljoin(self.base_url, app_url)

    @property
    def curdoc(self) -> Document | None:
        try:
            doc = curdoc_locked()
            if doc.session_context or self._is_pyodide:
                return doc
        finally:
            curdoc = self._curdoc
            if curdoc:
                return curdoc

    @curdoc.setter
    def curdoc(self, doc: Document) -> None:
        self._curdoc = doc

    @property
    def _curdoc(self) -> Document | None:
        """
        Required to make overrides to curdoc (e.g. using the
        set_curdoc context manager) thread-safe and asyncio task
        local. Otherwise two threads may independently override the
        curdoc and end up in a confused final state.
        """
        thread = threading.current_thread()
        thread_id = thread.ident if thread else None
        if thread_id not in self._curdoc_:
            return None
        curdocs = self._curdoc_[thread_id]
        try:
            task = asyncio.current_task()
        except Exception:
            task = None
        while True:
            if task in curdocs:
                return curdocs[task or self]
            elif task is None:
                break
            try:
                task = task.parent_task
            except Exception:
                task = None
        return curdocs[self] if self in curdocs else None

    @_curdoc.setter
    def _curdoc(self, doc: Document | None) -> None:
        thread = threading.current_thread()
        thread_id = thread.ident if thread else None
        if thread_id not in self._curdoc_ and doc is None:
            return None
        curdocs = self._curdoc_[thread_id]
        try:
            task = asyncio.current_task()
        except Exception:
            task = None
        key = task or self
        if doc is None:
            # Do not clean up curdocs for tasks since they may have
            # children that are still running
            if key in curdocs and task is None:
                del curdocs[key]
            if not len(curdocs):
                del self._curdoc_[thread_id]
        else:
            curdocs[key] = doc

    @property
    def cookies(self) -> Dict[str, str]:
        return self.curdoc.session_context.request.cookies if self.curdoc and self.curdoc.session_context else {}

    @property
    def headers(self) -> Dict[str, str | List[str]]:
        return self.curdoc.session_context.request.headers if self.curdoc and self.curdoc.session_context else {}

    @property
    def location(self) -> Location | None:
        if self.curdoc and self.curdoc not in self._locations:
            from .location import Location
            loc = self._locations[self.curdoc] = Location()
        elif self.curdoc is None:
            loc = self._location
        else:
            loc = self._locations.get(self.curdoc) if self.curdoc else None
        if loc is None:
            return loc

        if '?' in self.base_url:
            try:
                loc.search = f'?{self.base_url.split("?")[-1].strip("/")}'
            except Exception:
                pass
        if '#' in self.base_url:
            try:
                loc.hash = f'#{self.base_url.split("#")[-1].strip("/")}'
            except Exception:
                pass

        return loc

    @property
    def notifications(self) -> NotificationArea | None:
        from ..config import config
        if config.notifications and self.curdoc and self.curdoc not in self._notifications:
            from .notifications import NotificationArea
            self._notifications[self.curdoc] = notifications = NotificationArea()
            return notifications
        elif self.curdoc is None:
            return self._notification
        else:
            return self._notifications.get(self.curdoc) if self.curdoc else None

    @property
    def log_terminal(self):
        from .admin import log_terminal
        return log_terminal

    @property
    def session_args(self) -> Dict[str, List[bytes]]:
        return self.curdoc.session_context.request.arguments if self.curdoc and self.curdoc.session_context else {}

    @property
    def template(self) -> BaseTemplate | None:
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
    def user(self) -> str | None:
        from tornado.web import decode_signed_value

        from ..config import config
        user = self.cookies.get('user')
        if user is None or config.cookie_secret is None:
            return None
        return decode_signed_value(config.cookie_secret, 'user', user).decode('utf-8')

    @property
    def user_info(self) -> Dict[str, Any] | None:
        from tornado.web import decode_signed_value

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
