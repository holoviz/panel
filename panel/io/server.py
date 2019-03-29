"""
Utilities for creating bokeh Server instances.
"""
from __future__ import absolute_import, division, unicode_literals

import signal
import threading

from functools import partial

from bokeh.server.server import Server

from .state import state


#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------

def _origin_url(url):
    if url.startswith("http"):
        url = url.split("//")[1]
    return url


def _server_url(url, port):
    if url.startswith("http"):
        return '%s:%d%s' % (url.rsplit(':', 1)[0], port, "/")
    else:
        return 'http://%s:%d%s' % (url.split(':')[0], port, "/")

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def get_server(panel, port=0, websocket_origin=None, loop=None,
               show=False, start=False, **kwargs):
    """
    Returns a Server instance with this panel attached as the root
    app.

    Arguments
    ---------
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
    kwargs: dict
      Additional keyword arguments to pass to Server instance

    Returns
    -------
    server : bokeh.server.server.Server
      Bokeh Server instance running this panel
    """
    from tornado.ioloop import IOLoop
    opts = dict(kwargs)
    if loop:
        loop.make_current()
        opts['io_loop'] = loop
    else:
        opts['io_loop'] = IOLoop.current()

    if websocket_origin:
        if not isinstance(websocket_origin, list):
            websocket_origin = [websocket_origin]
        opts['allow_websocket_origin'] = websocket_origin

    server_id = kwargs.pop('server_id', None)
    server = Server({'/': partial(panel._modify_doc, server_id)}, port=port, **opts)
    if server_id:
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

    def stop(self):
        self._stop_event.set()

    @property
    def stopped(self):
        return self._stop_event.is_set()
