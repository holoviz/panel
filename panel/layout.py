"""
Defines Layout classes which may be used to arrange panes and widgets
in flexible ways to build complex dashboards.
"""
from __future__ import absolute_import

import param

import numpy as np
from bokeh.layouts import (Column as BkColumn, Row as BkRow,
                           WidgetBox as BkWidgetBox, Spacer as BkSpacer)
from bokeh.models.widgets import Tabs as BkTabs, Panel as BkPanel

from .pane import Pane, PaneBase
from .util import push, is_rectangle
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


class GridSpec(Reactive):

    nrows = param.Integer()

    ncols = param.Integer()

    width = param.Integer(default=600)

    height = param.Integer(default=600)

    def __init__(self, nrows, ncols, **params):
        super(GridSpec, self).__init__(nrows=nrows, ncols=ncols, **params)
        self._objects = []
        self._grid = np.zeros((nrows, ncols))
        self._bounds = {}
        self._shapes = {}

    @property
    def _cell_width(self):
        return (self.width/self.ncols)

    @property
    def _cell_height(self):
        return (self.height/self.nrows)

    @property
    def _full(self):
        """
        Whether the grid is fully populated.
        """
        return np.sum(self._grid) == (self.nrows*self.ncols)

    def __setitem__(self, index, obj):
        xidx, yidx = index
        x0, x1 = (xidx.start, xidx.stop) if isinstance(xidx, slice) else (xidx, xidx+1)
        y0, y1 = (yidx.start, yidx.stop) if isinstance(yidx, slice) else (yidx, yidx+1)
        if obj in self._objects:
            raise ValueError()
        elif x1 > self.ncols or y1 > self.nrows:
            raise IndexError()
        shape = np.zeros((self.ncols, self.nrows))
        shape[index[::-1]] = 1
        index = len(self._objects)
        self._objects.append(obj)
        self._bounds[index] = {'rows': (y0, y1), 'cols': (x0, x1)}
        obj.width = int(self._cell_width * (x1-x0))
        obj.height = int(self._cell_height * (y1-y0))
        for x in range(x0, x1):
            for y in range(y0, y1):
                if self._grid[y, x]:
                    raise IndexError('(%d, %d) already populated' % ((x, y)) )
                self._grid[y, x] = True
        self._shapes[index] = shape

    def _full_grid(self):
        new_gs = GridSpec(**dict(self.get_param_values()))
        for i, bounds in self._bounds.items():
            x0, x1 = bounds['cols']
            y0, y1 = bounds['rows']
            new_gs[x0: x1, y0: y1] = self._objects[i]
        width, height = self.width/self.ncols, self.height/self.nrows
        for x in range(self.ncols):
            for y in range(self.nrows):
                if new_gs._grid[y, x]: continue
                new_gs[(x, y)] = Spacer(width=int(width), height=int(height))
        return new_gs

    def _find_block(self, start=0):
        """
        Iteratively searches for blocks to combine into a row or column.
        """
        shapes = list(self._shapes.items())
        index, shape = shapes.pop(start)
        combined_shape = shape
        items = [index]
        for i, oshape in shapes:
            candidate = combined_shape + oshape
            if is_rectangle(candidate):
                combined_shape = candidate
                items.append(i)
                break
            else:
                continue
        if len(items) == 1:
            return self._find_block(start+1)
        return items

    def _combine_items(self, objects):
        """
        Combine the supplied objects into a row or column
        """
        new_gs = GridSpec(**dict(self.get_param_values()))
        rows = [(i, max(self._bounds[i]['rows'])) for i in objects]
        cols = [(i, max(self._bounds[i]['cols'])) for i in objects]
        is_row = len(set([r for _, r in cols])) == len(cols)
        layout, order = (Row, cols) if is_row else (Column, rows)

        items = [i for i, _ in sorted(order, key=lambda x: x[1])]
        obj = layout(*[self._objects[i] for i in items])

        x0 = min([min(self._bounds[i]['cols']) for i in objects])
        x1 = max([max(self._bounds[i]['cols']) for i in objects])
        y0 = min([min(self._bounds[i]['rows']) for i in objects])
        y1 = max([max(self._bounds[i]['rows']) for i in objects])
        new_gs[x0: x1, y0: y1] = obj

        for i, bounds in self._bounds.items():
            if i in objects: continue
            x0, x1 = bounds['cols']
            y0, y1 = bounds['rows']
            new_gs[x0: x1, y0: y1] = self._objects[i]
        return new_gs

    def _recursively_combine(self):
        """
        Iteratively combine objects into rows or columns until
        only a single Row/Column is left.
        """
        if not self._full:
            reduced_gs = self._full_grid()
        else:
            reduced_gs = self
        while len(reduced_gs._objects) > 1:
            items = reduced_gs._find_block()
            reduced_gs = reduced_gs._combine_items(items)
        return reduced_gs

    def _get_model(self, doc, root=None, parent=None, comm=None):
        gs = self._recursively_combine()
        return gs._objects[0]._get_model(doc, root, parent, comm)
