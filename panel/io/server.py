"""
Utilities for creating bokeh Server instances.
"""
from __future__ import absolute_import, division, unicode_literals

import os
import signal
import threading
import uuid

from contextlib import contextmanager
from functools import partial
from types import FunctionType

from bokeh.document.events import ModelChangedEvent
from bokeh.server.server import Server
from tornado.websocket import WebSocketHandler

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

def _eval_panel(panel, server_id, title, doc):
    from ..template import Template
    from ..pane import panel as as_panel

    if isinstance(panel, FunctionType):
        panel = panel()
    if isinstance(panel, Template):
        return panel._modify_doc(server_id, title, doc)
    return as_panel(panel)._modify_doc(server_id, title, doc)
    
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
    if curdoc is None or curdoc.session_context is None:
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


def serve(panels, port=0, websocket_origin=None, loop=None, show=True,
          start=True, title=None, verbose=True, **kwargs):
    """
    Allows serving one or more panel objects on a single server.
    The panels argument should be either a Panel object or a function
    returning a Panel object or a dictionary of these two. If a 
    dictionary is supplied the keys represent the slugs at which
    each app is served, e.g. `serve({'app': panel1, 'app2': panel2})`
    will serve apps at /app and /app2 on the server.

    Arguments
    ---------
    panel: Viewable, function or {str: Viewable}
      A Panel object, a function returning a Panel object or a
      dictionary mapping from the URL slug to either.
    port: int (optional, default=0)
      Allows specifying a specific port
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
    title: str (optional, default=None)
      An HTML title for the application
    verbose: boolean (optional, default=True)
      Whether to print the address and port
    kwargs: dict
      Additional keyword arguments to pass to Server instance
    """
    return get_server(panels, port, websocket_origin, loop, show, start,
                      title, verbose, **kwargs)


def get_server(panel, port=0, websocket_origin=None, loop=None,
               show=False, start=False, title=None, verbose=False, **kwargs):
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
    title: str (optional, default=None)
      An HTML title for the application
    verbose: boolean (optional, default=False)
      Whether to report the address and port
    kwargs: dict
      Additional keyword arguments to pass to Server instance

    Returns
    -------
    server : bokeh.server.server.Server
      Bokeh Server instance running this panel
    """
    from tornado.ioloop import IOLoop

    server_id = kwargs.pop('server_id', uuid.uuid4().hex)
    if isinstance(panel, dict):
        apps = {slug if slug.startswith('/') else '/'+slug:
                partial(_eval_panel, p, server_id, title)
                for slug, p in panel.items()}
    else:
        apps = {'/': partial(_eval_panel, panel, server_id, title)}

    opts = dict(kwargs)
    if loop:
        loop.make_current()
        opts['io_loop'] = loop
    else:
        opts['io_loop'] = IOLoop.current()

    if 'index' not in opts:
        opts['index'] = INDEX_HTML

    if websocket_origin:
        if not isinstance(websocket_origin, list):
            websocket_origin = [websocket_origin]
        opts['allow_websocket_origin'] = websocket_origin

    server = Server(apps, port=port, **opts)
    if verbose:
        address = server.address or 'localhost'
        print("Launching server at http://%s:%s" % (address, server.port))

    state._servers[server_id] = (server, panel, [])

    if show:
        def show_callback():
            server.show('/')
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

    def __init__(self, io_loop=None, timeout=1000, **kwargs):
        from tornado import ioloop
        super(StoppableThread, self).__init__(**kwargs)
        self._stop_event = threading.Event()
        self.io_loop = io_loop
        self._cb = ioloop.PeriodicCallback(self._check_stopped, timeout)
        self._cb.start()

    def _check_stopped(self):
        if self.stopped:
            self._cb.stop()
            self.io_loop.stop()

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
        self._stop_event.set()

    @property
    def stopped(self):
        return self._stop_event.is_set()
