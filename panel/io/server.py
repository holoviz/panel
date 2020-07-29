"""
Utilities for creating bokeh Server instances.
"""
from __future__ import absolute_import, division, unicode_literals

import os
import signal
import sys
import threading
import uuid

from contextlib import contextmanager
from functools import partial
from types import FunctionType, MethodType

from bokeh.document.events import ModelChangedEvent
from bokeh.embed.server import server_html_page_for_session
from bokeh.server.server import Server
from bokeh.server.views.session_handler import SessionHandler
from bokeh.server.views.static_handler import StaticHandler
from bokeh.server.urls import per_app_patterns
from bokeh.settings import settings
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler, StaticFileHandler, authenticated
from tornado.wsgi import WSGIContainer

from .resources import PanelResources
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


@contextmanager
def set_curdoc(doc):
    state.curdoc = doc
    yield
    state.curdoc = None


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


class PanelDocHandler(SessionHandler):
    """
    Implements a custom Tornado handler for document display page
    overriding the default bokeh DocHandler to replace the default
    resources with a Panel resources object.
    """

    @authenticated
    async def get(self, *args, **kwargs):
        session = await self.get_session()

        mode = settings.resources(default="server")
        css_files = session.document.template_variables.get('template_css_files')
        resource_opts = dict(mode=mode, extra_css_files=css_files)
        if mode == "server":
            resource_opts.update({
                'root_url': self.application._prefix,
                'path_versioner': StaticHandler.append_version
            })
        resources = PanelResources(**resource_opts)

        page = server_html_page_for_session(
            session, resources=resources, title=session.document.title,
            template=session.document.template,
            template_variables=session.document.template_variables
        )

        self.set_header("Content-Type", 'text/html')
        self.write(page)

per_app_patterns[0] = (r'/?', PanelDocHandler)

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------


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

    hold = curdoc._hold
    if hold:
        old_events = list(curdoc._held_events)
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
            for event in curdoc._held_events:
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
        curdoc._held_events = events
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
    show : boolean (optional, default=False)
      Whether to open the server in a new browser tab on start
    start : boolean(optional, default=False)
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
               oauth_encryption_key=None, **kwargs):
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
    kwargs: dict
      Additional keyword arguments to pass to Server instance.

    Returns
    -------
    server : bokeh.server.server.Server
      Bokeh Server instance running this panel
    """
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
                        "title dictionnary.") 
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
            apps[slug] = partial(_eval_panel, app, server_id, title_, location)
    else:
        apps = {'/': partial(_eval_panel, panel, server_id, title, location)}

    dist_dir = os.path.join(os.path.split(os.path.dirname(__file__))[0], 'dist')
    static_dirs = dict(static_dirs, panel_dist=dist_dir)

    extra_patterns += get_static_routes(static_dirs)

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
        print("Launching server at http://%s:%s" % (address, server.port))

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
        super(StoppableThread, self).__init__(**kwargs)
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
