from __future__ import absolute_import, division, unicode_literals

from bokeh.io import curdoc as _curdoc

from .io.server import StoppableThread, get_server


class ServableMixin(object):

    def _get_server(self, port=0, websocket_origin=None, loop=None,
                   show=False, start=False, **kwargs):
        return get_server(self, port, websocket_origin, loop, show,
                          start, **kwargs)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def servable(self, title=None):
        """
        Serves the object if in a `panel serve` context and returns
        the Panel object to allow it to display itself in a notebook
        context.

        Arguments
        ---------
        title : str
          A string title to give the Document (if served as an app)

        Returns
        -------
        The Panel object itself
        """
        if _curdoc().session_context:
            self.server_doc(title=title)
        return self

    def show(self, port=0, websocket_origin=None, threaded=False, title=None):
        """
        Starts a Bokeh server and displays the Viewable in a new tab

        Arguments
        ---------
        port: int (optional, default=0)
          Allows specifying a specific port
        websocket_origin: str or list(str) (optional)
          A list of hosts that can connect to the websocket.

          This is typically required when embedding a server app in
          an external web site.

          If None, "localhost" is used.
        threaded: boolean (optional, default=False)
          Whether to launch the Server on a separate thread, allowing
          interactive use.

        Returns
        -------
        server: bokeh.server.Server or threading.Thread
          Returns the Bokeh server instance or the thread the server
          was launched on (if threaded=True)
        """
        if threaded:
            from tornado.ioloop import IOLoop
            loop = IOLoop()
            server = StoppableThread(
                target=self._get_server, io_loop=loop,
                args=(port, websocket_origin, loop, True, True))
            server.start()
        else:
            self.server_doc(title=title)
            server = self._get_server(port, websocket_origin, show=True, start=True)

        return server
