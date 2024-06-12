"""
Defines custom jsTree bokeh model to render Ace editor.
"""
from __future__ import absolute_import

from bokeh.core.properties import (
    Any, Bool, List, Nullable,
)
from bokeh.events import ModelEvent
from bokeh.models.layouts import LayoutDOM

from ..config import config
from ..io.resources import JS_URLS, bundled_files
from ..util import classproperty


class NodeEvent(ModelEvent):

    event_name = 'node_event'

    def __init__(self, model, data=None):
        self.data = data
        super().__init__(model=model)


class jsTree(LayoutDOM):
    """
    A Bokeh model that wraps around a jsTree editor and renders it inside
    a Bokeh plot.
    """

    __css_raw__ = [
        f"{config.npm_cdn}/jstree@3.3.16/dist/themes/default/style.min.css",
    ]

    __resources__ = [
        f"{config.npm_cdn}/jstree@3.3.16/dist/themes/default/32px.png",
        f"{config.npm_cdn}/jstree@3.3.16/dist/themes/default/throbber.gif"
    ]

    @classproperty
    def __css__(cls):
        cls.__css_raw__ = cls.__css_raw__[:1]
        return bundled_files(cls, 'css')

    __javascript_raw__ = [
        JS_URLS['jQuery'],
        f"{config.npm_cdn}/jstree@3.3.16/dist/jstree.min.js"
    ]

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    plugins = List(Any)
    cascade = Bool(default=True)
    checkbox = Bool(default=True)
    multiple = Bool(default=True)
    show_icons = Bool(default=True)
    show_dots = Bool(default=False)
    show_stripes = Bool(default=True)
    sort = Bool(default=True)
    _new_nodes = Nullable(List(Any))

    # Callback properties
    checked = List(Any)
    nodes = List(Any)
