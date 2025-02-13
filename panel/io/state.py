"""
Various utilities for recording and embedding state in a rendered app.
"""
from __future__ import annotations

import asyncio
import datetime as dt
import inspect
import logging
import os
import shutil
import sys
import threading
import time

from collections import Counter, defaultdict
from collections.abc import (
    Callable, Coroutine, Hashable, Iterator, Iterator as TIterator,
)
from contextlib import contextmanager, suppress
from contextvars import ContextVar
from functools import partial, wraps
from typing import (
    TYPE_CHECKING, Any, ClassVar, Literal, TypeAlias, TypeVar,
)
from urllib.parse import urljoin
from weakref import WeakKeyDictionary

import param

from bokeh.document import Document
from bokeh.document.locking import UnlockedDocumentProxy
from bokeh.io import curdoc as _curdoc
from param.parameterized import Event, Parameterized
from pyviz_comms import CommManager as _CommManager

from ..util import decode_token, parse_timedelta
from .logging import LOG_SESSION_RENDERED, LOG_USER_MSG

_state_logger = logging.getLogger('panel.state')

if TYPE_CHECKING:
    from concurrent.futures import Future

    from bokeh.application.application import SessionContext
    from bokeh.model import Model
    from bokeh.models import ImportedStyleSheet
    from bokeh.server.contexts import BokehSessionContext
    from bokeh.server.session import ServerSession
    from IPython.display import DisplayHandle
    from pyviz_comms import Comm
    from tornado.ioloop import IOLoop

    from ..template.base import BaseTemplate
    from ..viewable import Viewable
    from ..widgets.indicators import BooleanIndicator
    from .application import TViewableFuncOrPath
    from .browser import BrowserInfo
    from .cache import _Stack
    from .callbacks import PeriodicCallback
    from .location import Location
    from .notifications import NotificationArea
    from .server import StoppableThread

    T = TypeVar("T")
    K = TypeVar('K', bound=Hashable)


@contextmanager
def set_curdoc(doc: Document | None):
    if doc:
        token = state._curdoc.set(doc)
    try:
        yield
    finally:
        if doc:
            # If _curdoc has been reset it will raise a ValueError
            with suppress(ValueError):
                state._curdoc.reset(token)

def curdoc_locked() -> Document | None:
    try:
        doc = _curdoc()
    except RuntimeError:
        return None
    if isinstance(doc, UnlockedDocumentProxy):
        doc = doc._doc
    return doc

class _Undefined: pass

Tat: TypeAlias = dt.datetime | Callable[[dt.datetime], dt.datetime] | TIterator[dt.datetime]

class _state(param.Parameterized):
    """
    Holds global state associated with running apps, allowing running
    apps to indicate their state to a user.
    """

    busy = param.Boolean(default=False, readonly=True, doc="""
       Whether the application is currently busy processing a user
       callback.""")

    cache = param.Dict(default={}, doc="""
       Global location you can use to cache large datasets or expensive computation results
       across multiple client sessions for a given server.""")

    encryption = param.Parameter(default=None, doc="""
       Object with encrypt and decrypt methods to support encryption
       of secret variables including OAuth information.""")

    session_info = param.Dict(default={'total': 0, 'live': 0,
                                       'sessions': {}}, doc="""
       Tracks information and statistics about user sessions.""")

    webdriver = param.Parameter(default=None, doc="""
      Selenium webdriver used to export bokeh models to pngs.""")

    _base_url = param.String(default='/', readonly=True, doc="""
       Base URL for all server paths.""")

    _busy_counter = param.Integer(default=0, doc="""
       Count of active callbacks current being processed.""")

    _memoize_cache = param.Dict(default={}, doc="""
       A dictionary used by the cache decorator.""")

    _rel_path = param.String(default='', readonly=True, doc="""
       Relative path from the current app being served to the root URL.
       If application is embedded in a different server via autoload.js
       this will instead reflect an absolute path.""")

    # Holds temporary curdoc overrides per thread
    _curdoc: ContextVar[Document | None] = ContextVar('curdoc', default=None)

    # Whether to hold comm events
    _hold: bool = False

    # Used to ensure that events are not scheduled from the wrong thread
    _thread_id_: ClassVar[WeakKeyDictionary[Document, int]] = WeakKeyDictionary()
    _thread_pool = None

    # Admin application (remove in Panel 1.0 / Bokeh 3.0)
    _admin_context = None

    # Jupyter communication
    _comm_manager: type[_CommManager] = _CommManager
    _jupyter_kernel_context: BokehSessionContext | None = None
    _kernels: ClassVar[dict[str, tuple[Any, str, str, bool]]] = {}
    _ipykernels: ClassVar[WeakKeyDictionary[Document, Any]] = WeakKeyDictionary()

    # Locations
    _browser: ClassVar[BrowserInfo | None] = None # Global BrowserInfo, e.g. for notebook context
    _browsers: ClassVar[WeakKeyDictionary[Document, BrowserInfo]] = WeakKeyDictionary() # Server browser indexed by document

    # Locations
    _location: ClassVar[Location | None] = None # Global location, e.g. for notebook context
    _locations: ClassVar[WeakKeyDictionary[Document, Location]] = WeakKeyDictionary() # Server locations indexed by document

    # Notifications
    _notification: ClassVar[NotificationArea | None] = None # Global location, e.g. for notebook context
    _notifications: ClassVar[WeakKeyDictionary[Document, NotificationArea]] = WeakKeyDictionary() # Server notifications indexed by document

    # Templates
    _template: ClassVar[BaseTemplate | None] = None
    _templates: ClassVar[WeakKeyDictionary[Document, BaseTemplate]] = WeakKeyDictionary() # Server templates indexed by document

    # An index of all currently active views
    _views: ClassVar[dict[str, tuple[Viewable, Model, Document, Comm | None]]] = {}

    # For templates to keep reference to their main root
    _fake_roots: ClassVar[list[str]] = []

    # An index of all currently active servers
    _servers: ClassVar[dict[str, tuple[Any, TViewableFuncOrPath | dict[str, TViewableFuncOrPath], list[Document]]]] = {}
    _threads: ClassVar[dict[str, StoppableThread]] = {}
    _server_config: ClassVar[WeakKeyDictionary[Any, dict[str, Any]]] = WeakKeyDictionary()

    # Jupyter display handles
    _handles: ClassVar[dict[str, tuple[DisplayHandle, list[str]]]] = {}

    # Stacks for hashing
    _stacks: WeakKeyDictionary[threading.Thread, _Stack] = WeakKeyDictionary()

    # Dictionary of callbacks to be triggered on app load
    _onload: ClassVar[WeakKeyDictionary[Document, list[tuple[Callable[[], None | Coroutine[Any, Any, None]], bool]]]] = WeakKeyDictionary()
    _on_session_created: ClassVar[list[Callable[[SessionContext], None]]] = []
    _on_session_created_internal: ClassVar[list[Callable[[SessionContext], None]]] = []
    _on_session_destroyed: ClassVar[list[Callable[[SessionContext], None]]] = []
    _loaded: ClassVar[WeakKeyDictionary[Document, bool]] = WeakKeyDictionary()

    # Module that was run during setup
    _setup_module = None

    # Scheduled callbacks
    _scheduled: ClassVar[dict[str, tuple[TIterator[int] | None, Callable[[], None]]]] = {}
    _periodic: ClassVar[WeakKeyDictionary[Document, list[PeriodicCallback]]] = WeakKeyDictionary()

    # Indicators listening to the busy state
    _indicators: ClassVar[list[BooleanIndicator]] = []

    # Profilers
    _launching: ClassVar[set[Document]] = set()
    _profiles = param.Dict(default=defaultdict(list))

    # Endpoints
    _rest_endpoints: ClassVar[dict[str, tuple[list[Parameterized], list[str], Callable[[Event], Any]]]] = {}

    # Style cache
    _stylesheets: ClassVar[WeakKeyDictionary[Document, dict[str, ImportedStyleSheet]]] = WeakKeyDictionary()

    # Loaded extensions
    _extensions_: ClassVar[WeakKeyDictionary[Document, list[str]]] = WeakKeyDictionary()

    # Locks
    _cache_locks: ClassVar[dict[str | tuple[Any, ...], threading.Lock]] = {'main': threading.Lock()}

    # Sessions
    _sessions: ClassVar[dict[Hashable, ServerSession]] = {}
    _session_key_funcs: ClassVar[dict[str, Callable[[Any], Any]]] = {}

    # Layout editor
    _cell_outputs: ClassVar[defaultdict[Hashable, list[Any]]] = defaultdict(list)
    _cell_layouts: ClassVar[defaultdict[Hashable, dict[str, dict]]] = defaultdict(dict)
    _session_outputs: ClassVar[WeakKeyDictionary[Document, dict[str, Any]]] = WeakKeyDictionary()

    # Override user info
    _oauth_user_overrides: ClassVar[dict[str, dict[str, Any]]] = {}
    _active_users: ClassVar[Counter[str]] = Counter()

    # Paths
    _rel_paths: ClassVar[WeakKeyDictionary[Document, str]] = WeakKeyDictionary()
    _base_urls: ClassVar[WeakKeyDictionary[Document, str]] = WeakKeyDictionary()

    # Watchers
    _watch_events: ClassVar[list[asyncio.Event]] = []

    def __repr__(self) -> str:
        server_info = []
        for server, panel, _docs in self._servers.values():
            server_info.append(
                "{}:{:d} - {!r}".format(server.address or "localhost", server.port or 0, panel)
            )
        if not server_info:
            return "state(servers=[])"
        return "state(servers=[\n  {}\n])".format(",\n  ".join(server_info))

    @property
    def _ioloop(self) -> IOLoop | asyncio.AbstractEventLoop:
        if state._is_pyodide:
            return asyncio.get_running_loop()
        else:
            from tornado.ioloop import IOLoop
            return IOLoop.current()

    @property
    def _extensions(self):
        doc = self.curdoc
        if not (doc and doc in self._extensions_):
            return
        return self._extensions_[doc]

    @property
    def _current_thread(self) -> int | None:
        return threading.get_ident()

    @property
    def _is_launching(self) -> bool:
        curdoc = self.curdoc
        if not curdoc or not curdoc.session_context or not curdoc.session_context.server_context:
            return False
        return not bool(curdoc.session_context.server_context.sessions)

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
        """
        Indicates whether Document events can be dispatched or have
        to scheduled on the event loop. Events can only be safely
        dispatched if:

        1. The Document to be modified is the same one that the server
           is currently processing.
        2. We are on the same thread that the Document was created on.
        3. The application has fully loaded and the Websocket is open.
        """
        return bool(
            doc is self.curdoc and
            self._thread_id in (self._current_thread, None) and
            (not (doc and doc.session_context and getattr(doc.session_context, 'session', None))
             or self._loaded.get(doc))
        )

    @param.depends('_busy_counter', watch=True)
    def _update_busy_counter(self):
        self.busy = self._busy_counter >= 1

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
        _updating: dict[int, bool] = {}
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
            future = self._thread_pool.submit(self._on_load, doc)
            future.add_done_callback(partial(self._handle_future_exception, doc=doc))
        else:
            self._on_load(doc)

    def _on_load(self, doc: Document | None = None) -> None:
        doc = doc or self.curdoc
        if not doc:
            return
        elif doc not in self._onload:
            self._loaded[doc] = True
            return

        from ..config import config
        from .profile import profile_ctx
        with set_curdoc(doc):
            if (doc and doc in self._launching) or not config.profiler:
                while doc in self._onload:
                    for cb, threaded in self._onload.pop(doc):
                        self.execute(cb, schedule='thread' if threaded else False)
                self._loaded[doc] = True
                return

            with profile_ctx(config.profiler) as sessions:
                while doc in self._onload:
                    for cb, threaded in self._onload.pop(doc):
                        self.execute(cb, schedule='thread' if threaded else False)
            if doc.session_context:
                path = doc.session_context.request.path
                self._profiles[(path+':on_load', config.profiler)] += sessions
                self.param.trigger('_profiles')
        self._loaded[doc] = True

    async def _scheduled_cb(self, name: str, threaded: bool = False) -> None:
        if name not in self._scheduled:
            return
        diter, cb = self._scheduled[name]
        if diter:
            try:
                at = next(diter)
            except Exception:
                at = None
                del self._scheduled[name]
        else:
            at = None
            del self._scheduled[name]
        if at is not None:
            now = dt.datetime.now().timestamp()
            call_time_seconds = (at - now)
            self._ioloop.call_later(delay=call_time_seconds, callback=partial(self._scheduled_cb, name))
        try:
            self.execute(cb, schedule='thread' if threaded else 'auto')
        except Exception as e:
            self._handle_exception(e)

    def _handle_exception_wrapper(self, callback):
        @wraps(callback)
        def wrapper(*args, **kw):
            try:
                return callback(*args, **kw)
            except Exception as e:
                self._handle_exception(e)
        return wrapper

    def _handle_future_exception(self, future: Future, doc: Document | None = None) -> None:
        exception = future.exception()
        if exception is None:
            return

        with set_curdoc(doc):
            self._handle_exception(exception)

    def _handle_exception(self, exception: BaseException) -> None:
        from ..config import config
        if config.exception_handler:
            config.exception_handler(exception)
        elif isinstance(exception, BaseException):
            raise exception
        else:
            self.log(f'Exception of unknown type raised: {exception}', level='error')

    def _register_session_destroyed(self, session_context: SessionContext):
        for cb in self._on_session_destroyed:
            session_context._document.on_session_destroyed(cb)

    #----------------------------------------------------------------
    # Public Methods
    #----------------------------------------------------------------

    def as_cached(self, key: str, fn: Callable[[], T], ttl: int | None = None, **kwargs) -> T:
        """
        Caches the return value of a function globally across user sessions, memoizing on the given
        key and supplied keyword arguments.

        Note: Keyword arguments must be hashable.

        Pandas Example:

        >>> data = pn.state.as_cached('data', pd.read_csv, filepath_or_buffer=DATA_URL)

        Function Example:

        >>> def load_dataset(name):
        >>>     # some slow operation that uses name to load a dataset....
        >>>     return dataset
        >>> penguins = pn.state.as_cached('dataset-penguins', load_dataset, name='penguins')

        Parameters
        ----------
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
        cache_key = (key,)+tuple((k, v) for k, v in sorted(kwargs.items()))
        new_expiry = time.monotonic() + ttl if ttl else None
        with self._cache_locks['main']:
            if cache_key in self._cache_locks:
                lock = self._cache_locks[cache_key]
            else:
                self._cache_locks[cache_key] = lock = threading.Lock()
        try:
            with lock:
                if cache_key in self.cache:
                    ret, expiry = self.cache.get(cache_key)
                else:
                    ret, expiry = _Undefined, None
                if ret is _Undefined or (expiry is not None and expiry < time.monotonic()):
                    ret, _ = self.cache[cache_key] = (fn(**kwargs), new_expiry)
        finally:
            if not lock.locked() and cache_key in self._cache_locks:
                del self._cache_locks[cache_key]
        return ret

    def add_periodic_callback(
        self, callback: Callable[[], None] | Coroutine[Any, Any, None],
        period: int = 500, count: int | None = None, timeout: int | None = None,
        start: bool = True
    ) -> PeriodicCallback:
        """
        Schedules a periodic callback to be run at an interval set by
        the period. Returns a PeriodicCallback object with the option
        to stop and start the callback.

        Parameters
        ----------
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
            cb.start()
        if self.curdoc:
            if self.curdoc not in self._periodic:
                self._periodic[self.curdoc] = []
            self._periodic[self.curdoc].append(cb)
        return cb

    def cancel_task(self, name: str, wait: bool=False):
        """
        Cancel a task scheduled using the `state.schedule_task` method by name.

        Parameters
        ----------
        name: str
            The name of the scheduled task.
        wait: boolean
            Whether to wait until after the next execution.
        """
        key = f"{os.getpid()}_{name}"
        if key not in self._scheduled:
            raise KeyError(f'No task with the name {name!r} has been scheduled.')
        if wait:
            self._scheduled[key] = (None, self._scheduled[key][1])
        else:
            del self._scheduled[key]

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

    def _execute_on_thread(self, doc, callback):
        with set_curdoc(doc):
            if param.parameterized.iscoroutinefunction(callback):
                param.parameterized.async_executor(callback)
            else:
                self.execute(callback, schedule=False)

    def execute(
        self,
        callback: Callable[[], None | Coroutine[Any, Any, None]],
        schedule: bool | Literal['auto', 'thread'] = 'auto'
    ) -> None:
        """
        Executes both synchronous and asynchronous callbacks
        appropriately depending on the context the application is
        running in. When running on the server callbacks are scheduled
        on the event loop ensuring the Bokeh Document lock is acquired
        and models can be modified directly.

        Parameters
        ----------
        callback: Callable[[], None]
          Callback to execute
        schedule: boolean | Literal['auto', 'thread']
          Whether to schedule the callback on the event loop, on a thread
          or execute them immediately.
        """
        doc = self.curdoc
        if schedule == 'thread':
            if not state._thread_pool:
                raise RuntimeError(
                    'Cannot execute callback on thread. Ensure you have '
                    'enabled threading setting `config.nthreads`.'
                )
            future = state._thread_pool.submit(partial(self._execute_on_thread, doc, callback))
            future.add_done_callback(self._handle_future_exception)
        elif param.parameterized.iscoroutinefunction(callback):
            param.parameterized.async_executor(callback)
        elif doc and doc.session_context and (schedule == True or (schedule == 'auto' and not self._unblocked(doc))):
            doc.add_next_tick_callback(self._handle_exception_wrapper(callback))
        else:
            try:
                callback()
            except Exception as e:
                state._handle_exception(e)

    def get_profile(self, profile: str):
        """
        Returns the requested profiling output.

        Parameters
        ----------
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
        for server_id in self._servers:
            if server_id in self._threads:
                self._threads[server_id].stop()
            else:
                try:
                    self._servers[server_id][0].stop()
                except AssertionError:  # can't stop a server twice
                    pass
        self._servers.clear()
        self._threads.clear()

    def log(self, msg: str, level: str = 'info') -> None:
        """
        Logs user messages to the Panel logger.

        Parameters
        ----------
        msg: str
          Log message
        level: str
          Log level as a string, i.e. 'debug', 'info', 'warning' or 'error'.
        """
        args: tuple[()] | tuple[int] = ()
        if self.curdoc:
            args = (id(self.curdoc),)
            msg = LOG_USER_MSG.format(msg=msg)
        getattr(_state_logger, level.lower())(msg, *args)

    def onload(self, callback: Callable[[], None | Coroutine[Any, Any, None]], threaded: bool = False):
        """
        Callback that is triggered when a session has been served.

        Parameters
        ----------
        callback: Callable[[], None] | Coroutine[Any, Any, None]
           Callback that is executed when the application is loaded
        threaded: bool
          Whether the onload callback can be threaded
        """
        if self.curdoc is None or self._is_pyodide or self.loaded:
            if self._thread_pool:
                self.execute(callback, schedule='threaded')
            else:
                self.execute(callback, schedule=False)
        elif self.curdoc in self._onload:
            self._onload[self.curdoc].append((callback, threaded))
        else:
            self._onload[self.curdoc] = [(callback, threaded)]

    def on_session_created(self, callback: Callable[[SessionContext], None]) -> None:
        """
        Callback that is triggered when a session is created.
        """
        if self.curdoc and self.curdoc.session_context:
            raise RuntimeError(
                "Cannot register session creation callback from within a session. "
                "If running a Panel application from the CLI set up the callback "
                "in a --setup script, if starting a server dynamically set it up "
                "before starting the server."
            )
        self._on_session_created.append(callback)

    def on_session_destroyed(self, callback: Callable[[SessionContext], None]) -> None:
        """
        Callback that is triggered when a session is destroyed.
        """
        doc = self.curdoc
        if doc:
            doc.on_session_destroyed(callback)
        else:
            if self._register_session_destroyed not in self._on_session_created:
                self._on_session_created.append(self._register_session_destroyed)
            self._on_session_destroyed.append(callback)

    def publish(
        self, endpoint: str, parameterized: param.Parameterized,
        parameters: list[str] | None = None
    ) -> None:
        """
        Publish parameters on a Parameterized object as a REST API.

        Parameters
        ----------
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

    def reset(self):
        """
        Resets the state object killing running servers and clearing
        any other state held by the server.
        """
        self.kill_all_servers()
        self._curdoc = ContextVar('curdoc', default=None)
        self._indicators.clear()
        self._location = None
        self._locations.clear()
        self._templates.clear()
        self._views.clear()
        self._loaded.clear()
        self.cache.clear()
        self._scheduled.clear()
        if self._thread_pool is not None:
            self._thread_pool.shutdown(wait=False)
            self._thread_pool = None
        self._sessions.clear()
        self._session_key_funcs.clear()
        self._on_session_created.clear()
        self._on_session_destroyed.clear()
        self._stylesheets.clear()
        self._scheduled.clear()
        self._periodic.clear()

    def schedule_task(
        self,
        name: str,
        callback: Callable[[], None],
        at: Tat | None = None,
        period: str | dt.timedelta | None = None,
        cron: str | None = None,
        threaded : bool = False
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

        Parameters
        ----------
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
        threaded: bool
          Whether the callback should be run on a thread (requires
          config.nthreads to be set).
        """
        key = f"{os.getpid()}_{name}"
        if key in self._scheduled:
            if callback is not self._scheduled[key][1]:
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
                        new = at(dt.datetime.now(dt.timezone.utc).replace(tzinfo=None))
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
        elif isinstance(at, Iterator) or callable(at):
            raise ValueError(
                "When scheduling a task with croniter the at value must "
                "be a concrete datetime value."
            )
        else:
            from croniter import croniter
            base = dt.datetime.now() if at is None else at
            diter = croniter(cron, base)
        now = dt.datetime.now().timestamp()
        try:
            call_time_seconds = (next(diter) - now)
        except StopIteration:
            return
        self._scheduled[key] = (diter, callback)
        self._ioloop.call_later(
            delay=call_time_seconds, callback=partial(self._scheduled_cb, key, threaded)
        )

    def sync_busy(self, indicator: BooleanIndicator) -> None:
        """
        Syncs the busy state with an indicator with a boolean value
        parameter.

        Parameters
        ----------
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

    def _decode_cookie(self, cookie_name, cookie=None):
        from tornado.web import decode_signed_value

        from ..config import config
        cookie = self.cookies.get(cookie_name)
        if cookie is None:
            return None
        cookie = decode_signed_value(config.cookie_secret, cookie_name, cookie)
        return self._decrypt_cookie(cookie)

    def _decrypt_cookie(self, cookie):
        if self.encryption is None:
            return cookie.decode('utf-8')
        return self.encryption.decrypt(cookie).decode('utf-8')

    @property
    def access_token(self) -> str | None:
        """
        Returns the OAuth access_token if enabled.
        """
        if self.user in self._oauth_user_overrides and 'access_token' in self._oauth_user_overrides[self.user]:
            return self._oauth_user_overrides[self.user]['access_token']
        access_token = self._decode_cookie('access_token')
        if not access_token:
            return None
        try:
            decoded_token = decode_token(access_token)
        except Exception:
            return access_token
        if decoded_token['exp'] <= dt.datetime.now(dt.timezone.utc).timestamp():
            return None
        return access_token

    @property
    def app_url(self) -> str | None:
        """
        Returns the URL of the app that is currently being executed.
        """
        if not (self.curdoc and self.curdoc.session_context):
            return None
        app_url = self.curdoc.session_context.server_context.application_context.url
        app_url = app_url[1:] if app_url.startswith('/') else app_url
        return urljoin(self.base_url, app_url)

    @property
    def browser_info(self) -> BrowserInfo | None:
        from ..config import config
        from .browser import BrowserInfo
        if (config.browser_info and self.curdoc and self.curdoc.session_context and
            self.curdoc not in self._browsers):
            browser = self._browsers[self.curdoc] = BrowserInfo()
        elif self.curdoc is None:
            if self._browser is None and config.browser_info:
                _state._browser = BrowserInfo()
            browser = self._browser  # type: ignore
        else:
            browser = self._browsers.get(self.curdoc) if self.curdoc else None  # type: ignore
        return browser

    @property
    def curdoc(self) -> Document | None:
        """
        Returns the Document that is currently being executed.
        """
        curdoc = self._curdoc.get()
        if curdoc:
            return curdoc
        try:
            doc = curdoc_locked()
            pyodide_session = self._is_pyodide and 'pyodide_kernel' not in sys.modules
            if doc and (doc.session_context or pyodide_session):
                return doc
        except Exception:
            return None
        return None

    @curdoc.setter
    def curdoc(self, doc: Document) -> None:
        """
        Overrides the current Document.
        """
        self._curdoc.set(doc)

    @property
    def cookies(self) -> dict[str, str]:
        """
        Returns the cookies associated with the request that started the session.
        """
        return self.curdoc.session_context.request.cookies if self.curdoc and self.curdoc.session_context else {}

    @property
    def headers(self) -> dict[str, str | list[str]]:
        """
        Returns the header associated with the request that started the session.
        """
        return self.curdoc.session_context.request.headers if self.curdoc and self.curdoc.session_context else {}

    @property
    def base_url(self) -> str:
        base_url = self._base_url
        if self.curdoc:
            return self._base_urls.get(self.curdoc, base_url)
        return base_url

    @base_url.setter
    def base_url(self, value: str):
        if self.curdoc:
            self._base_urls[self.curdoc] = value
        else:
            self._base_url = value

    @property
    def rel_path(self) -> str | None:
        rel_path = self._rel_path
        if self.curdoc:
            return self._rel_paths.get(self.curdoc, rel_path)
        return rel_path

    @rel_path.setter
    def rel_path(self, value: str | None):
        if value is None:
            return
        elif self.curdoc:
            self._rel_paths[self.curdoc] = value
        else:
            self._rel_path = value

    @property
    def loaded(self) -> bool:
        """
        Whether the application has been fully loaded.
        """
        curdoc = self.curdoc
        if curdoc:
            if curdoc in self._loaded:
                return self._loaded[curdoc]
            elif curdoc.session_context:
                return False
        return True

    @property
    def location(self) -> Location | None:
        if self.curdoc and self.curdoc not in self._locations:
            from .location import Location
            if self.curdoc.session_context:
                loc = Location.from_request(self.curdoc.session_context.request)
            else:
                loc = Location()
            self._locations[self.curdoc] = loc
        elif self.curdoc is None:
            loc = self._location
        else:
            loc = self._locations.get(self.curdoc) if self.curdoc else None
        return loc

    @property
    def log_terminal(self):
        from .admin import log_terminal
        return log_terminal

    @property
    def notifications(self) -> NotificationArea | None:
        if self.curdoc is None:
            return self._notification

        is_session = (self.curdoc.session_context is not None or self._is_pyodide)
        if self.curdoc in self._notifications:
            return self._notifications[self.curdoc]

        from panel.config import config
        if not (config.notifications and is_session):
            return None if is_session else self._notification

        from panel.io.notifications import NotificationArea
        js_events = {}
        if config.ready_notification:
            js_events['document_ready'] = {'type': 'success', 'message': config.ready_notification, 'duration': 3000}
        if config.disconnect_notification:
            js_events['connection_lost'] = {'type': 'error', 'message': config.disconnect_notification}
        self._notifications[self.curdoc] = notifications = NotificationArea(js_events=js_events)
        return notifications

    @property
    def refresh_token(self) -> str | None:
        """
        Returns the OAuth refresh_token if enabled and available.
        """
        if self.user in self._oauth_user_overrides and 'refresh_token' in self._oauth_user_overrides:
            return self._oauth_user_overrides[self.user]['refresh_token']
        refresh_token = self._decode_cookie('refresh_token')
        if not refresh_token:
            return None
        try:
            decoded_token = decode_token(refresh_token)
        except ValueError:
            return refresh_token
        if decoded_token['exp'] <= dt.datetime.now(dt.timezone.utc).timestamp():
            return None
        return refresh_token

    @property
    def served(self):
        """
        Whether we are currently inside a script or notebook that is
        being served using `panel serve`.
        """
        try:
            return inspect.stack()[1].frame.f_globals['__name__'].startswith('bokeh_app_')
        except Exception:
            return False

    @property
    def session_args(self) -> dict[str, list[bytes]]:
        """
        Returns the request arguments associated with the request that started the session.
        """
        return self.curdoc.session_context.request.arguments if self.curdoc and self.curdoc.session_context else {}

    @property
    def template(self) -> BaseTemplate | None:
        from ..config import config
        if self.curdoc and self.curdoc in self._templates:
            return self._templates[self.curdoc]
        elif self.curdoc is None and self._template:
            return self._template
        template = config.template(theme=config.theme)
        if not config.design:
            config.design = template.design
        if self.curdoc is None:
            _state._template = template
        else:
            self._templates[self.curdoc] = template
        return template

    @property
    def user(self) -> str | None:
        """
        Returns the OAuth user if enabled.
        """
        from tornado.web import decode_signed_value

        from ..config import config
        is_guest = self.cookies.get('is_guest')
        if is_guest:
            return "guest"

        user = self.cookies.get('user')
        if user is None or config.cookie_secret is None:
            return None
        decoded = decode_signed_value(config.cookie_secret, 'user', user)
        return None if decoded is None else decoded.decode('utf-8')

    @property
    def user_info(self) -> dict[str, Any] | None:
        """
        Returns the OAuth user information if enabled.
        """
        is_guest = self.cookies.get('is_guest')
        if is_guest:
            return {"user": "guest", "username": "guest"}
        id_token = self._decode_cookie('id_token')
        if id_token is None:
            return None
        return decode_token(id_token)

state = _state()
