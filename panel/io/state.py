"""
Various utilities for recording and embedding state in a rendered app.
"""
from __future__ import absolute_import, division, unicode_literals


import param

from bokeh.document import Document
from pyviz_comms import CommManager as _CommManager


class state(param.Parameterized):
    """
    Holds global state associated with running apps, allowing running
    apps to indicate their state to a user.
    """

    curdoc = param.ClassSelector(class_=Document, doc="""
        The bokeh Document for which a server event is currently being
        processed.""")

    webdriver = param.Parameter(default=None, doc="""
        Selenium webdriver used to export bokeh models to pngs.""")

    # Whether to hold comm events
    _hold = False

    _comm_manager = _CommManager

    # An index of all currently active views
    _views = {}

    # An index of all curently active servers
    _servers = {}
