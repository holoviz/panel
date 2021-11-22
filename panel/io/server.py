"""
Utilities for creating bokeh Server instances.
"""
import datetime as dt
import html
import inspect
import os
import pathlib
import signal
import sys
import traceback
import threading
import uuid

from collections import OrderedDict
from contextlib import contextmanager
from functools import partial, wraps
from types import FunctionType, MethodType
from urllib.parse import urljoin, urlparse

import param
import bokeh
import bokeh.command.util

# Bokeh imports
from bokeh.application import Application as BkApplication
from bokeh.application.handlers.code import CodeHandler, _monkeypatch_io, patch_curdoc
from bokeh.application.handlers.function import FunctionHandler
from bokeh.command.util import build_single_handler_application
from bokeh.core.templates import AUTOLOAD_JS
from bokeh.document.events import ModelChangedEvent
from bokeh.embed.bundle import Script
from bokeh.embed.elements import html_page_for_render_items, script_for_render_items
from bokeh.embed.util import RenderItem
from bokeh.io import curdoc
from bokeh.server.server import Server
from bokeh.server.urls import per_app_patterns, toplevel_patterns
from bokeh.server.views.autoload_js_handler import AutoloadJsHandler as BkAutoloadJsHandler
from bokeh.server.views.doc_handler import DocHandler as BkDocHandler
from bokeh.server.views.root_handler import RootHandler as BkRootHandler
from bokeh.server.views.static_handler import StaticHandler

# Tornado imports
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler, StaticFileHandler, authenticated
from tornado.wsgi import WSGIContainer

# Internal imports
from ..util import edit_readonly
from .reload import autoreload_watcher
from .resources import BASE_TEMPLATE, Resources, bundle_resources
from .state import state

#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------

INDEX_HTML = os.path.join(os.path.dirname(__file__), '..', '_templates', "index.html")

def _origin_url(url):
    if url.startswith("http"):
        url = url.split("//")[1]
    return url

def _server_url(url, port):
    if url.startswith("http"):
        return '%s:%d%s' % (url.rsplit(':', 1)[0], port, "/")
    else:
        return 'http://%s:%d%s' % (url.split(':')[0], port, "/")

def _eval_panel(panel, server_id, title, location, doc):
    from ..template import BaseTemplate
    from ..pane import panel as as_panel

    with set_curdoc(doc):
        if isinstance(panel, (FunctionType, MethodType)):
            panel = panel()
        if isinstance(panel, BaseTemplate):
            doc = panel._modify_doc(server_id, title, doc, location)
        else:
            doc = as_panel(panel)._modify_doc(server_id, title, doc, location)
        return doc

def async_execute(func):
    """
    Wrap async event loop scheduling to ensure that with_lock flag
    is propagated from function to partial wrapping it.
    """
    if not state.curdoc or not state.curdoc.session_context:
        ioloop = IOLoop.current()
        event_loop = ioloop.asyncio_loop
        if event_loop.is_running():
            ioloop.add_callback(func)
        else:
            event_loop.run_until_complete(func())
        return

    if isinstance(func, partial) and hasattr(func.func, 'lock'):
        unlock = not func.func.lock
    else:
        unlock = not getattr(func, 'lock', False)
    curdoc = state.curdoc
    @wraps(func)
    async def wrapper(*args, **kw):
        with set_curdoc(curdoc):
            return await func(*args, **kw)
    if unlock:
        wrapper.nolock = True
    state.curdoc.add_next_tick_callback(wrapper)

param.parameterized.async_executor = async_execute

def _initialize_session_info(session_context):
    from ..config import config
    session_id = session_context.id
    sessions = state.session_info['sessions']
    if config.session_history == 0 or session_id in sessions:
        return

    state.session_info['total'] += 1
    if config.session_history > 0 and len(sessions) >= config.session_history:
        old_history = list(sessions.items())
        sessions = OrderedDict(old_history[-(config.session_history-1):])
        state.session_info['sessions'] = sessions
    sessions[session_id] = {
        'launched': dt.datetime.now().timestamp(),
        'started': None,
        'rendered': None,
        'ended': None,
        'user_agent': session_context.request.headers.get('User-Agent')
    }

state.on_session_created(_initialize_session_info)

#---------------------------------------------------------------------
# Bokeh patches
#---------------------------------------------------------------------

def server_html_page_for_session(session, resources, title, template=BASE_TEMPLATE,
                                 template_variables=None):
    render_item = RenderItem(
        token = session.token,
        roots = session.document.roots,
        use_for_title = False,
    )

    if template_variables is None:
        template_variables = {}

    bundle = bundle_resources(session.document.roots, resources)
    return html_page_for_render_items(bundle, {}, [render_item], title,
        template=template, template_variables=template_variables)

def autoload_js_script(doc, resources, token, element_id, app_path, absolute_url):
    resources = Resources.from_bokeh(resources)
    bundle = bundle_resources(doc.roots, resources)

    render_items = [RenderItem(token=token, elementid=element_id, use_for_title=False)]
    bundle.add(Script(script_for_render_items({}, render_items, app_path=app_path, absolute_url=absolute_url)))

    return AUTOLOAD_JS.render(bundle=bundle, elementid=element_id)

# Patch Application to handle session callbacks
class Application(BkApplication):

    async def on_session_created(self, session_context):
        for cb in state._on_session_created:
            cb(session_context)
        await super().on_session_created(session_context)

    def initialize_document(self, doc):
        super().initialize_document(doc)
        if doc in state._templates:
            template = state._templates[doc]
            template.server_doc(title=template.title, location=True, doc=doc)

bokeh.command.util.Application = Application


class SessionPrefixHandler:

    @contextmanager
    def _session_prefix(self):
        prefix = self.request.uri.replace(self.application_context._url, '')
        if not prefix.endswith('/'):
            prefix += '/'
        base_url = urljoin('/', prefix)
        rel_path = '/'.join(['..'] * self.application_context._url.strip('/').count('/'))
        old_url, old_rel = state.base_url, state.rel_path

        # Handle autoload.js absolute paths
        abs_url = self.get_argument('bokeh-absolute-url', default=None)
        if abs_url is not None:
            app_path = self.get_argument('bokeh-app-path', default=None)
            rel_path = abs_url.replace(app_path, '')

        with edit_readonly(state):
            state.base_url = base_url
            state.rel_path = rel_path
        try:
            yield
        finally:
            with edit_readonly(state):
                state.base_url = old_url
                state.rel_path = old_rel

# Patch Bokeh DocHandler URL
class DocHandler(BkDocHandler, SessionPrefixHandler):

    @authenticated
    async def get(self, *args, **kwargs):
        with self._session_prefix():
            session = await self.get_session()
            state.curdoc = session.document
            try:
                resources = Resources.from_bokeh(self.application.resources())
                page = server_html_page_for_session(
                    session, resources=resources, title=session.document.title,
                    template=session.document.template,
                    template_variables=session.document.template_variables
                )
            finally:
                state.curdoc = None
        self.set_header("Content-Type", 'text/html')
        self.write(page)

per_app_patterns[0] = (r'/?', DocHandler)

# Patch Bokeh Autoload handler
class AutoloadJsHandler(BkAutoloadJsHandler, SessionPrefixHandler):
    ''' Implements a custom Tornado handler for the autoload JS chunk

    '''

    async def get(self, *args, **kwargs):
        element_id = self.get_argument("bokeh-autoload-element", default=None)
        if not element_id:
            self.send_error(status_code=400, reason='No bokeh-autoload-element query parameter')
            return

        app_path = self.get_argument("bokeh-app-path", default="/")
        absolute_url = self.get_argument("bokeh-absolute-url", default=None)

        if absolute_url:
            server_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(absolute_url))
        else:
            server_url = None

        with self._session_prefix():
            session = await self.get_session()
            state.curdoc = session.document
            try:
                resources = Resources.from_bokeh(self.application.resources(server_url))
                js = autoload_js_script(
                    session.document, resources, session.token, element_id,
                    app_path, absolute_url
                )
            finally:
                state.curdoc = None

        self.set_header("Content-Type", 'application/javascript')
        self.write(js)

per_app_patterns[3] = (r'/autoload.js', AutoloadJsHandler)

class RootHandler(BkRootHandler):

    @authenticated
    async def get(self, *args, **kwargs):
        if self.index and not self.index.endswith('.html'):
            prefix = "" if self.prefix is None else self.prefix
            redirect_to = prefix + '.'.join(self.index.split('.')[:-1])
            self.redirect(redirect_to)
        await super().get(*args, **kwargs)

toplevel_patterns[0] = (r'/?', RootHandler)
bokeh.server.tornado.RootHandler = RootHandler

def modify_document(self, doc):
    from bokeh.io.doc import set_curdoc as bk_set_curdoc
    from ..config import config

    if config.autoreload:
        path = self._runner.path
        argv = self._runner._argv
        handler = type(self)(filename=path, argv=argv)
        self._runner = handler._runner

    module = self._runner.new_module()

    # If no module was returned it means the code runner has some permanent
    # unfixable problem, e.g. the configured source code has a syntax error
    if module is None:
        return

    # One reason modules are stored is to prevent the module
    # from being gc'd before the document is. A symptom of a
    # gc'd module is that its globals become None. Additionally
    # stored modules are used to provide correct paths to
    # custom models resolver.
    sys.modules[module.__name__] = module
    doc.modules._modules.append(module)

    old_doc = curdoc()
    bk_set_curdoc(doc)

    if config.autoreload:
        set_curdoc(doc)
        state.onload(autoreload_watcher)

    try:
        def post_check():
            newdoc = curdoc()
            # Do not let curdoc track modules when autoreload is enabled
            # otherwise it will erroneously complain that there is
            # a memory leak
            if config.autoreload:
                newdoc.modules._modules = []

            # script is supposed to edit the doc not replace it
            if newdoc is not doc:
                raise RuntimeError("%s at '%s' replaced the output document" % (self._origin, self._runner.path))

        def handle_exception(handler, e):
            from bokeh.application.handlers.handler import handle_exception
            from ..pane import HTML

            # Clean up
            del sys.modules[module.__name__]

            if hasattr(doc, 'modules'):
                doc.modules._modules.remove(module)
            else:
                doc._modules.remove(module)
            bokeh.application.handlers.code_runner.handle_exception = handle_exception
            tb = html.escape(traceback.format_exc())

            # Serve error
            HTML(
                f'<b>{type(e).__name__}</b>: {e}</br><pre style="overflow-y: scroll">{tb}</pre>',
                css_classes=['alert', 'alert-danger'], sizing_mode='stretch_width'
            ).servable()

        if config.autoreload:
            bokeh.application.handlers.code_runner.handle_exception = handle_exception
        with _monkeypatch_io(self._loggers):
            with patch_curdoc(doc):
                self._runner.run(module, post_check)
    finally:
        bk_set_curdoc(old_doc)

CodeHandler.modify_document = modify_document

# Copied from bokeh 2.4.0, to fix directly in bokeh at some point.
def create_static_handler(prefix, key, app):
    # patch
    key = '/__patchedroot' if key == '/' else key

    route = prefix
    route += "/static/(.*)" if key == "/" else key + "/static/(.*)"
    if app.static_path is not None:
        return (route, StaticFileHandler, {"path" : app.static_path})
    return (route, StaticHandler, {})

bokeh.server.tornado.create_static_handler = create_static_handler

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def init_doc(doc):
    doc = doc or curdoc()
    if not doc.session_context:
        return doc

    session_id = doc.session_context.id
    sessions = state.session_info['sessions']
    if session_id not in sessions:
        return doc

    sessions[session_id].update({
        'started': dt.datetime.now().timestamp()
    })
    doc.on_event('document_ready', state._init_session)
    return doc

@contextmanager
def set_curdoc(doc):
    state.curdoc = doc
    yield
    state.curdoc = None

def with_lock(func):
    """
    Wrap a callback function to execute with a lock allowing the
    function to modify bokeh models directly.

    Arguments
    ---------
    func: callable
      The callable to wrap

    Returns
    -------
    wrapper: callable
      Function wrapped to execute without a Document lock.
    """
    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def wrapper(*args, **kw):
            return await func(*args, **kw)
    else:
        @wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
    wrapper.lock = True
    return wrapper


@contextmanager
def unlocked():
    """
    Context manager which unlocks a Document and dispatches
    ModelChangedEvents triggered in the context body to all sockets
    on current sessions.
    """
    curdoc = state.curdoc
    if curdoc is None or curdoc.session_context is None or curdoc.session_context.session is None:
        yield
        return
    connections = curdoc.session_context.session._subscribed_connections

    hold = curdoc.callbacks.hold_value
    if hold:
        old_events = list(curdoc.callbacks._held_events)
    else:
        old_events = []
        curdoc.hold()
    try:
        yield
        events = []
        for conn in connections:
            socket = conn._socket
            if hasattr(socket, 'write_lock') and socket.write_lock._block._value == 0:
                state._locks.add(socket)
            locked = socket in state._locks
            for event in curdoc.callbacks._held_events:
                if (isinstance(event, ModelChangedEvent) and event not in old_events
                    and hasattr(socket, 'write_message') and not locked):
                    msg = conn.protocol.create('PATCH-DOC', [event])
                    WebSocketHandler.write_message(socket, msg.header_json)
                    WebSocketHandler.write_message(socket, msg.metadata_json)
                    WebSocketHandler.write_message(socket, msg.content_json)
                    for header, payload in msg._buffers:
                        WebSocketHandler.write_message(socket, header)
                        WebSocketHandler.write_message(socket, payload, binary=True)
                elif event not in events:
                    events.append(event)
        curdoc.callbacks._held_events = events
    finally:
        if not hold:
            curdoc.unhold()


def serve(panels, port=0, address=None, websocket_origin=None, loop=None,
          show=True, start=True, title=None, verbose=True, location=True,
          threaded=False, **kwargs):
    """
    Allows serving one or more panel objects on a single server.
    The panels argument should be either a Panel object or a function
    returning a Panel object or a dictionary of these two. If a
    dictionary is supplied the keys represent the slugs at which
    each app is served, e.g. `serve({'app': panel1, 'app2': panel2})`
    will serve apps at /app and /app2 on the server.

    Arguments
    ---------
    panel: Viewable, function or {str: Viewable or function}
      A Panel object, a function returning a Panel object or a
      dictionary mapping from the URL slug to either.
    port: int (optional, default=0)
      Allows specifying a specific port
    address : str
      The address the server should listen on for HTTP requests.
    websocket_origin: str or list(str) (optional)
      A list of hosts that can connect to the websocket.

      This is typically required when embedding a server app in
      an external web site.

      If None, "localhost" is used.
    loop : tornado.ioloop.IOLoop (optional, default=IOLoop.current())
      The tornado IOLoop to run the Server on
    show : boolean (optional, default=True)
      Whether to open the server in a new browser tab on start
    start : boolean(optional, default=True)
      Whether to start the Server
    title: str or {str: str} (optional, default=None)
      An HTML title for the application or a dictionary mapping
      from the URL slug to a customized title
    verbose: boolean (optional, default=True)
      Whether to print the address and port
    location : boolean or panel.io.location.Location
      Whether to create a Location component to observe and
      set the URL location.
    threaded: boolean (default=False)
      Whether to start the server on a new Thread
    kwargs: dict
      Additional keyword arguments to pass to Server instance
    """
    kwargs = dict(kwargs, **dict(
        port=port, address=address, websocket_origin=websocket_origin,
        loop=loop, show=show, start=start, title=title, verbose=verbose,
        location=location
    ))
    if threaded:
        from tornado.ioloop import IOLoop
        kwargs['loop'] = loop = IOLoop() if loop is None else loop
        server = StoppableThread(
            target=get_server, io_loop=loop, args=(panels,), kwargs=kwargs
        )
        server_id = kwargs.get('server_id', uuid.uuid4().hex)
        state._threads[server_id] = server
        server.start()
    else:
        server = get_server(panels, **kwargs)
    return server


class ProxyFallbackHandler(RequestHandler):
    """A `RequestHandler` that wraps another HTTP server callback and
    proxies the subpath.
    """

    def initialize(self, fallback, proxy=None):
        self.fallback = fallback
        self.proxy = proxy

    def prepare(self):
        if self.proxy:
            self.request.path = self.request.path.replace(self.proxy, '')
        self.fallback(self.request)
        self._finished = True
        self.on_finish()


def get_static_routes(static_dirs):
    """
    Returns a list of tornado routes of StaticFileHandlers given a
    dictionary of slugs and file paths to serve.
    """
    patterns = []
    for slug, path in static_dirs.items():
        if not slug.startswith('/'):
            slug = '/' + slug
        if slug == '/static':
            raise ValueError("Static file route may not use /static "
                             "this is reserved for internal use.")
        path = os.path.abspath(path)
        if not os.path.isdir(path):
            raise ValueError("Cannot serve non-existent path %s" % path)
        patterns.append(
            (r"%s/(.*)" % slug, StaticFileHandler, {"path": path})
        )
    return patterns


def get_server(panel, port=0, address=None, websocket_origin=None,
               loop=None, show=False, start=False, title=None,
               verbose=False, location=True, static_dirs={},
               oauth_provider=None, oauth_key=None, oauth_secret=None,
               oauth_extra_params={}, cookie_secret=None,
               oauth_encryption_key=None, session_history=None, **kwargs):
    """
    Returns a Server instance with this panel attached as the root
    app.

    Arguments
    ---------
    panel: Viewable, function or {str: Viewable}
      A Panel object, a function returning a Panel object or a
      dictionary mapping from the URL slug to either.
    port: int (optional, default=0)
      Allows specifying a specific port
    address : str
      The address the server should listen on for HTTP requests.
    websocket_origin: str or list(str) (optional)
      A list of hosts that can connect to the websocket.

      This is typically required when embedding a server app in
      an external web site.

      If None, "localhost" is used.
    loop : tornado.ioloop.IOLoop (optional, default=IOLoop.current())
      The tornado IOLoop to run the Server on.
    show : boolean (optional, default=False)
      Whether to open the server in a new browser tab on start.
    start : boolean(optional, default=False)
      Whether to start the Server.
    title : str or {str: str} (optional, default=None)
      An HTML title for the application or a dictionary mapping
      from the URL slug to a customized title.
    verbose: boolean (optional, default=False)
      Whether to report the address and port.
    location : boolean or panel.io.location.Location
      Whether to create a Location component to observe and
      set the URL location.
    static_dirs: dict (optional, default={})
      A dictionary of routes and local paths to serve as static file
      directories on those routes.
    oauth_provider: str
      One of the available OAuth providers
    oauth_key: str (optional, default=None)
      The public OAuth identifier
    oauth_secret: str (optional, default=None)
      The client secret for the OAuth provider
    oauth_extra_params: dict (optional, default={})
      Additional information for the OAuth provider
    cookie_secret: str (optional, default=None)
      A random secret string to sign cookies (required for OAuth)
    oauth_encryption_key: str (optional, default=False)
      A random encryption key used for encrypting OAuth user
      information and access tokens.
    session_history: int (optional, default=None)
      The amount of session history to accumulate. If set to non-zero
      and non-None value will launch a REST endpoint at
      /rest/session_info, which returns information about the session
      history.
    kwargs: dict
      Additional keyword arguments to pass to Server instance.

    Returns
    -------
    server : bokeh.server.server.Server
      Bokeh Server instance running this panel
    """
    from ..config import config
    from .rest import REST_PROVIDERS

    server_id = kwargs.pop('server_id', uuid.uuid4().hex)
    kwargs['extra_patterns'] = extra_patterns = kwargs.get('extra_patterns', [])
    if isinstance(panel, dict):
        apps = {}
        for slug, app in panel.items():
            if isinstance(title, dict):
                try:
                    title_ = title[slug]
                except KeyError:
                    raise KeyError(
                        "Keys of the title dictionnary and of the apps "
                        f"dictionary must match. No {slug} key found in the "
                        "title dictionary.")
            else:
                title_ = title
            slug = slug if slug.startswith('/') else '/'+slug
            if 'flask' in sys.modules:
                from flask import Flask
                if isinstance(app, Flask):
                    wsgi = WSGIContainer(app)
                    if slug == '/':
                        raise ValueError('Flask apps must be served on a subpath.')
                    if not slug.endswith('/'):
                        slug += '/'
                    extra_patterns.append(('^'+slug+'.*', ProxyFallbackHandler,
                                           dict(fallback=wsgi, proxy=slug)))
                    continue
            if isinstance(app, pathlib.Path):
                app = str(app) # enables serving apps from Paths
            if (isinstance(app, str) and (app.endswith(".py") or app.endswith(".ipynb"))
                and os.path.isfile(app)):
                apps[slug] = build_single_handler_application(app)
            else:
                handler = FunctionHandler(partial(_eval_panel, app, server_id, title_, location))
                apps[slug] = Application(handler)
    else:
        handler = FunctionHandler(partial(_eval_panel, panel, server_id, title, location))
        apps = {'/': Application(handler)}

    extra_patterns += get_static_routes(static_dirs)

    if session_history is not None:
        config.session_history = session_history
    if config.session_history != 0:
        pattern = REST_PROVIDERS['param']([], 'rest')
        extra_patterns.extend(pattern)
        state.publish('session_info', state, ['session_info'])

    opts = dict(kwargs)
    if loop:
        loop.make_current()
        opts['io_loop'] = loop
    elif opts.get('num_procs', 1) == 1:
        opts['io_loop'] = IOLoop.current()

    if 'index' not in opts:
        opts['index'] = INDEX_HTML

    if address is not None:
        opts['address'] = address

    if websocket_origin:
        if not isinstance(websocket_origin, list):
            websocket_origin = [websocket_origin]
        opts['allow_websocket_origin'] = websocket_origin

    # Configure OAuth
    from ..config import config
    if config.oauth_provider:
        from ..auth import OAuthProvider
        opts['auth_provider'] = OAuthProvider()
    if oauth_provider:
        config.oauth_provider = oauth_provider
    if oauth_key:
        config.oauth_key = oauth_key
    if oauth_extra_params:
        config.oauth_extra_params = oauth_extra_params
    if cookie_secret:
        config.cookie_secret = cookie_secret
    opts['cookie_secret'] = config.cookie_secret

    server = Server(apps, port=port, **opts)
    if verbose:
        address = server.address or 'localhost'
        url = f"http://{address}:{server.port}{server.prefix}"
        print(f"Launching server at {url}")

    state._servers[server_id] = (server, panel, [])

    if show:
        def show_callback():
            server.show('/login' if config.oauth_provider else '/')
        server.io_loop.add_callback(show_callback)

    def sig_exit(*args, **kwargs):
        server.io_loop.add_callback_from_signal(do_stop)

    def do_stop(*args, **kwargs):
        server.io_loop.stop()

    try:
        signal.signal(signal.SIGINT, sig_exit)
    except ValueError:
        pass # Can't use signal on a thread

    if start:
        server.start()
        try:
            server.io_loop.start()
        except RuntimeError:
            pass
    return server


class StoppableThread(threading.Thread):
    """Thread class with a stop() method."""

    def __init__(self, io_loop=None, **kwargs):
        super().__init__(**kwargs)
        self.io_loop = io_loop

    def run(self):
        if hasattr(self, '_target'):
            target, args, kwargs = self._target, self._args, self._kwargs
        else:
            target, args, kwargs = self._Thread__target, self._Thread__args, self._Thread__kwargs
        if not target:
            return
        bokeh_server = None
        try:
            bokeh_server = target(*args, **kwargs)
        finally:
            if isinstance(bokeh_server, Server):
                bokeh_server.stop()
            if hasattr(self, '_target'):
                del self._target, self._args, self._kwargs
            else:
                del self._Thread__target, self._Thread__args, self._Thread__kwargs

    def stop(self):
        self.io_loop.add_callback(self.io_loop.stop)
