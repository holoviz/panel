"""
Various utilities for recording and embedding state in a rendered app.
"""
from __future__ import absolute_import, division, unicode_literals

import threading

import param

from bokeh.document import Document
from bokeh.io import curdoc as _curdoc
from pyviz_comms import CommManager as _CommManager


class _state(param.Parameterized):
    """
    Holds global state associated with running apps, allowing running
    apps to indicate their state to a user.
    """

    cache = param.Dict(default={}, doc="""
       Global location you can use to cache large datasets or expensive computation results
       across multiple client sessions for a given server.""") 

    webdriver = param.Parameter(default=None, doc="""
        Selenium webdriver used to export bokeh models to pngs.""")

    _curdoc = param.ClassSelector(class_=Document, doc="""
        The bokeh Document for which a server event is currently being
        processed.""")

    # Whether to hold comm events
    _hold = False

    # Used to ensure that events are not scheduled from the wrong thread
    _thread_id = None

    # Temporary flag to allow using Div model on static export
    _html_escape = True

    _comm_manager = _CommManager

    # An index of all currently active views
    _views = {}

    # An index of all currently active servers
    _servers = {}

    # Jupyter display handles
    _handles = {}

    def __repr__(self):
        server_info = []
        for server, panel, docs in self._servers.values():
            server_info.append("{}:{:d} - {!r}".format(
                server.address or "localhost", server.port, panel)
            )
        if not server_info:
            return "state(servers=[])"
        return "state(servers=[\n  {}\n])".format(",\n  ".join(server_info))

    def kill_all_servers(self):
        """Stop all servers and clear them from the current state."""
        for server_id in self._servers:
            try:
                self._servers[server_id][0].stop()
            except AssertionError:  # can't stop a server twice
                pass
        self._servers = {}

    def _unblocked(self, doc):
        thread = threading.current_thread()
        thread_id = thread.ident if thread else None
        return (doc is self.curdoc and self._thread_id == thread_id)

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
    def session_args(self):
        return self.curdoc.session_context.request.arguments if self.curdoc else {}


state = _state()
