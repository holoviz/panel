"""
Various utilities for recording and embedding state in a rendered app.
"""
from __future__ import absolute_import, division, unicode_literals


import param

from bokeh.document import Document
from bokeh.io import curdoc as _curdoc
from pyviz_comms import CommManager as _CommManager


class _state(param.Parameterized):
    """
    Holds global state associated with running apps, allowing running
    apps to indicate their state to a user.
    """

    _curdoc = param.ClassSelector(class_=Document, doc="""
        The bokeh Document for which a server event is currently being
        processed.""")

    webdriver = param.Parameter(default=None, doc="""
        Selenium webdriver used to export bokeh models to pngs.""")

    # Whether to hold comm events
    _hold = False

    # Used to ensure that events are not scheduled from the wrong thread
    _thread_id = None

    _comm_manager = _CommManager

    # An index of all currently active views
    _views = {}

    # An index of all curently active servers
    _servers = {}

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
        return self.curdoc.session_context.arguments if self.curdoc else {}


state = _state()
