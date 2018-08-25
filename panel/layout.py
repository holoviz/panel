"""
Defines Layout classes which may be used to arrange panels and widgets
in flexible ways to build complex dashboards.
"""

import param

from bokeh.layouts import Column as BkColumn, Row as BkRow, WidgetBox as BkWidgetBox

from .panels import Panel
from .viewable import Viewable


class Layout(Viewable):
    """
    Abstract baseclass for a layout of Panels.
    """

    children = param.List(default=[])

    _bokeh_model = None

    __abstract = True

    def __init__(self, *children, **params):
        children = [Panel.to_panel(child) for child in children]
        super(Layout, self).__init__(children=children, **params)

    def _get_root(self, doc, comm=None):
        return self._get_model(doc, comm=comm)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = self._bokeh_model()
        root = model if root is None else root
        children = []
        for child in self.children:
            children.append(child._get_model(doc, root, model, comm))
        model.children = children
        return model


class Row(Layout):
    """
    Horizontal layout of Panels.
    """

    _bokeh_model = BkRow


class Column(Layout):
    """
    Vertical layout of Panels.
    """

    _bokeh_model = BkColumn


class WidgetBox(Layout):
    """
    Box to group widgets.
    """

    _bokeh_model = BkWidgetBox

