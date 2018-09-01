"""
Defines Layout classes which may be used to arrange panels and widgets
in flexible ways to build complex dashboards.
"""
from __future__ import absolute_import

import param

from bokeh.layouts import Column as BkColumn, Row as BkRow, WidgetBox as BkWidgetBox
from bokeh.models.widgets import Tabs as BkTabs, Panel as BkPanel

from .panels import Panel
from .util import push
from .viewable import Reactive


class Layout(Reactive):
    """
    Abstract baseclass for a layout of Panels.
    """

    panels = param.List(default=[], doc="""
        The list of child panels that make up the layout.""")

    _bokeh_model = None

    __abstract = True

    _rename = {'panels': 'children'}

    def __init__(self, *panels, **params):
        panels = [Panel(panel) for panel in panels]
        super(Layout, self).__init__(panels=panels, **params)

    def _init_properties(self):
        properties = {k: v for k, v in self.param.get_param_values()
                      if v is not None}
        del properties['panels']
        return self._process_param_change(properties)

    def _link_params(self, model, params, doc, root, comm=None):
        for p in params:
            def set_value(change, parameter=p):
                msg = {parameter: change.new}
                if parameter == 'panels':
                    msg['panels'] = self._get_panels(model, change.old, doc, root, comm)
                msg = self._process_param_change(msg)
                def update_model(msg=msg):
                    model.update(**msg)
                if comm:
                    update_model()
                    push(doc, comm)
                else:
                    doc.add_next_tick_callback(update_model)
            self.param.watch(set_value, p)

    def _get_panels(self, model, old_panels, doc, root, comm=None):
        """
        Returns new child models for the layout while reusing unchanged
        models and cleaning up any dropped panels.
        """
        old_children = getattr(model, self._rename.get('panels', 'panels'))
        new_models = []
        for i, panel in enumerate(self.panels):
            panel = Panel(panel)
            self.panels[i] = panel
            if panel in old_panels:
                child = old_children[old_panels.index(panel)]
            else:
                child = panel._get_model(doc, root, model, comm)
            new_models.append(child)

        for panel, old_child in zip(old_panels, old_children):
            if old_child not in new_models:
                panel._cleanup(old_child)
        return new_models

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = self._bokeh_model()
        root = model if root is None else root
        panels = self._get_panels(model, [], doc, root, comm)
        props = dict(self._init_properties(), panels=panels)
        model.update(**self._process_param_change(props))
        params = [p for p in self.params() if p != 'name']
        self._link_params(model, params, doc, root, comm)
        return model

    def __setitem__(self, index, panel):
        new_panels = list(self.panels)
        new_panels[index] = Panel(panel)
        self.panels = new_panels

    def append(self, panel):
        new_panels = list(self.panels)
        new_panels.append(Panel(panel))
        self.panels = new_panels


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

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    _bokeh_model = BkWidgetBox


class Tabs(Layout):
    """
    Tabs allows selecting between the supplied panels.
    """

    panels = param.List(default=[], doc="""
        The list of child panels that make up the tabs.""")

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    _bokeh_model = BkTabs

    _rename = {'panels': 'tabs'}

    def __init__(self, *items, **params):
        panels = []
        for panel in items:
            if isinstance(panel, tuple):
                name, panel = panel
            else:
                name = None
            panels.append(Panel(panel, name=name))
        super(Tabs, self).__init__(*panels, **params)

    def _get_panels(self, model, old_panels, doc, root, comm=None):
        """
        Returns new child models for the layout while reusing unchanged
        models and cleaning up any dropped panels.
        """
        old_children = getattr(model, self._rename.get('panels', 'panels'))
        new_models = []
        for i, panel in enumerate(self.panels):
            if panel in old_panels:
                child = old_children[old_panels.index(panel)]
            else:
                child = panel._get_model(doc, root, model, comm)
                child = BkPanel(title=panel.name, child=child)
            new_models.append(child)

        for panel, old_child in zip(old_panels, old_children):
            if old_child not in new_models:
                panel._cleanup(old_child)

        return new_models

    def __setitem__(self, index, panel):
        name = None
        if isinstance(panel, tuple):
            name, panel = panel
        new_panels = list(self.panels)
        new_panels[index] = Panel(panel, name=name)
        self.panels = new_panels

    def append(self, panel):
        name = None
        if isinstance(panel, tuple):
            name, panel = panel
        new_panels = list(self.panels)
        new_panels.append(Panel(panel, name=name))
        self.panels = new_panels
