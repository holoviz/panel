"""
Defines Layout classes which may be used to arrange panes and widgets
in flexible ways to build complex dashboards.
"""
from __future__ import absolute_import

import param

from bokeh.layouts import (Column as BkColumn, Row as BkRow,
                           WidgetBox as BkWidgetBox, Spacer as BkSpacer)
from bokeh.models.widgets import Tabs as BkTabs, Panel as BkPanel

from .panes import Pane, PaneBase
from .util import push
from .viewable import Reactive


class Layout(Reactive):
    """
    Abstract baseclass for a layout of Panes.
    """

    objects = param.List(default=[], doc="""
        The list of child objects that make up the layout.""")

    _bokeh_model = None

    __abstract = True

    _rename = {'objects': 'children'}

    def __init__(self, *objects, **params):
        objects = [Pane(pane) for pane in objects]
        super(Layout, self).__init__(objects=objects, **params)

    def _init_properties(self):
        properties = {k: v for k, v in self.param.get_param_values()
                      if v is not None}
        del properties['objects']
        return self._process_param_change(properties)

    def _link_params(self, model, params, doc, root, comm=None):
        for p in params:
            def set_value(change, parameter=p):
                msg = {parameter: change.new}
                if parameter == 'objects':
                    msg['objects'] = self._get_objects(model, change.old, doc, root, comm)
                msg = self._process_param_change(msg)
                def update_model(msg=msg):
                    model.update(**msg)
                if comm:
                    update_model()
                    push(doc, comm)
                else:
                    doc.add_next_tick_callback(update_model)
            self.param.watch(set_value, p)

    def _cleanup(self, model, final=False):
        super(Layout, self)._cleanup(model, final)
        for p, c in zip(self.objects, model.children):
            p._cleanup(c, final)

    def _get_objects(self, model, old_objects, doc, root, comm=None):
        """
        Returns new child models for the layout while reusing unchanged
        models and cleaning up any dropped objects.
        """
        old_children = getattr(model, self._rename.get('objects', 'objects'))
        new_models = []
        for i, pane in enumerate(self.objects):
            pane = Pane(pane, _temporary=True)
            self.objects[i] = pane
            if pane in old_objects:
                child = old_children[old_objects.index(pane)]
            else:
                child = pane._get_model(doc, root, model, comm)
            new_models.append(child)

        for pane, old_child in zip(old_objects, old_children):
            if old_child not in new_models:
                pane._cleanup(old_child)
        return new_models

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = self._bokeh_model()
        root = model if root is None else root
        objects = self._get_objects(model, [], doc, root, comm)
        props = dict(self._init_properties(), objects=objects)
        model.update(**self._process_param_change(props))
        params = [p for p in self.params() if p != 'name']
        self._link_params(model, params, doc, root, comm)
        return model

    def __setitem__(self, index, pane):
        new_objects = list(self.objects)
        new_objects[index] = Pane(pane)
        self.objects = new_objects

    def append(self, pane):
        new_objects = list(self.objects)
        new_objects.append(Pane(pane))
        self.objects = new_objects

    def insert(self, index, pane):
        new_objects = list(self.objects)
        new_objects.insert(index, Pane(pane))
        self.objects = new_objects

    def pop(self, index):
        new_objects = list(self.objects)
        if index in new_objects:
            index = new_objects.index(index)
        new_objects.pop(index)
        self.objects = new_objects


class Row(Layout):
    """
    Horizontal layout of Panes.
    """

    _bokeh_model = BkRow


class Column(Layout):
    """
    Vertical layout of Panes.
    """

    _bokeh_model = BkColumn


class WidgetBox(Layout):
    """
    Box to group widgets.
    """

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    _bokeh_model = BkWidgetBox

    def _get_objects(self, model, old_objects, doc, root, comm=None):
        """
        Returns new child models for the layout while reusing unchanged
        models and cleaning up any dropped objects.
        """
        old_children = getattr(model, self._rename.get('objects', 'objects'))
        new_models = []
        for i, pane in enumerate(self.objects):
            pane = Pane(pane)
            self.objects[i] = pane
            if pane in old_objects:
                child = old_children[old_objects.index(pane)]
            else:
                child = pane._get_model(doc, root, model, comm)
            if isinstance(child, BkWidgetBox):
                new_models += child.children
            else:
                new_models.append(child)

        for pane, old_child in zip(old_objects, old_children):
            if old_child not in new_models:
                pane._cleanup(old_child)
        return new_models


class Tabs(Layout):
    """
    Tabs allows selecting between the supplied panes.
    """

    objects = param.List(default=[], doc="""
        The list of child objects that make up the tabs.""")

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    _bokeh_model = BkTabs

    _rename = {'objects': 'tabs'}

    def __init__(self, *items, **params):
        objects = []
        for pane in items:
            if isinstance(pane, tuple):
                name, pane = pane
            elif isinstance(pane, PaneBase):
                name = pane.name
            else:
                name = None
            objects.append(Pane(pane, name=name))
        super(Tabs, self).__init__(*objects, **params)

    def _get_objects(self, model, old_objects, doc, root, comm=None):
        """
        Returns new child models for the layout while reusing unchanged
        models and cleaning up any dropped objects.
        """
        old_children = getattr(model, self._rename.get('objects', 'objects'))
        new_models = []
        for i, pane in enumerate(self.objects):
            if pane in old_objects:
                child = old_children[old_objects.index(pane)]
            else:
                child = pane._get_model(doc, root, model, comm)
                child = BkPanel(title=pane.name, child=child)
            new_models.append(child)

        for pane, old_child in zip(old_objects, old_children):
            if old_child not in new_models:
                pane._cleanup(old_child.child)

        return new_models

    def __setitem__(self, index, pane):
        name = None
        if isinstance(pane, tuple):
            name, pane = pane
        new_objects = list(self.objects)
        new_objects[index] = Pane(pane, name=name)
        self.objects = new_objects

    def append(self, pane):
        name = None
        if isinstance(pane, tuple):
            name, pane = pane
        new_objects = list(self.objects)
        new_objects.append(Pane(pane, name=name))
        self.objects = new_objects

    def insert(self, index, pane):
        name = None
        if isinstance(pane, tuple):
            name, pane = pane
        new_objects = list(self.objects)
        new_objects.insert(index, Pane(pane))
        self.objects = new_objects

    def pop(self, index):
        new_objects = list(self.objects)
        if index in new_objects:
            index = new_objects.index(index)
        new_objects.pop(index)
        self.objects = new_objects

    def _cleanup(self, model, final=False):
        super(Layout, self)._cleanup(model, final)
        for p, c in zip(self.objects, model.tabs):
            p._cleanup(c.child, final)


class Spacer(Reactive):

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    _bokeh_model = BkSpacer

    def _init_properties(self):
        properties = {k: v for k, v in self.param.get_param_values()
                      if v not in [None, 'name']}
        return self._process_param_change(properties)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = self._bokeh_model(**self._init_properties())
        self._link_params(model, ['width', 'height'], doc, root, comm)
        return model
