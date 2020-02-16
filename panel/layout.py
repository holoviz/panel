"""
Defines Layout classes which may be used to arrange panes and widgets
in flexible ways to build complex dashboards.
"""
from __future__ import absolute_import, division, unicode_literals

import math

from collections import OrderedDict, defaultdict, namedtuple
from functools import partial

import param
import numpy as np

from bokeh.models import (
    Box as BkBox, Column as BkColumn, Div as BkDiv, GridBox as BkGridBox,
    Row as BkRow, Spacer as BkSpacer
)
from bokeh.models.widgets import Tabs as BkTabs, Panel as BkPanel

from .util import param_name, param_reprs
from .viewable import Layoutable, Reactive

_row = namedtuple("row", ["children"])
_col = namedtuple("col", ["children"])


class Panel(Reactive):
    """
    Abstract baseclass for a layout of Viewables.
    """

    _bokeh_model = None

    __abstract = True

    _rename = {'objects': 'children'}

    _linked_props = []

    def __repr__(self, depth=0, max_depth=10):
        if depth > max_depth:
            return '...'
        spacer = '\n' + ('    ' * (depth+1))
        cls = type(self).__name__
        params = param_reprs(self, ['objects'])
        objs = ['[%d] %s' % (i, obj.__repr__(depth+1)) for i, obj in enumerate(self)]
        if not params and not objs:
            return super(Panel, self).__repr__(depth+1)
        elif not params:
            template = '{cls}{spacer}{objs}'
        elif not objs:
            template = '{cls}({params})'
        else:
            template = '{cls}({params}){spacer}{objs}'
        return template.format(
            cls=cls, params=', '.join(params),
            objs=('%s' % spacer).join(objs), spacer=spacer)

    #----------------------------------------------------------------
    # Callback API
    #----------------------------------------------------------------

    def _update_model(self, events, msg, root, model, doc, comm=None):
        filtered = {}
        for k, v in msg.items():
            try:
                change = (
                    k not in self._changing or self._changing[k] != v or
                    self._changing['id'] != model.ref['id']
                )
            except Exception:
                change = True
            if change:
                filtered[k] = v

        if self._rename['objects'] in filtered:
            old = events['objects'].old
            filtered[self._rename['objects']] = self._get_objects(model, old, doc, root, comm)

        held = doc._hold
        if comm is None and not held:
            doc.hold()

        model.update(**filtered)

        from .io import state
        ref = root.ref['id']
        if ref in state._views:
            state._views[ref][0]._preprocess(root)

        if comm is None and not held:
            doc.unhold()

    #----------------------------------------------------------------
    # Model API
    #----------------------------------------------------------------

    def _init_properties(self):
        properties = {k: v for k, v in self.param.get_param_values()
                      if v is not None}
        del properties['objects']
        return self._process_param_change(properties)

    def _get_objects(self, model, old_objects, doc, root, comm=None):
        """
        Returns new child models for the layout while reusing unchanged
        models and cleaning up any dropped objects.
        """
        from .pane.base import panel, RerenderError
        new_models = []
        for i, pane in enumerate(self.objects):
            pane = panel(pane)
            self.objects[i] = pane

        for obj in old_objects:
            if obj not in self.objects:
                obj._cleanup(root)

        current_objects = list(self.objects)
        for i, pane in enumerate(self.objects):
            if pane in old_objects:
                child, _ = pane._models[root.ref['id']]
            else:
                try:
                    child = pane._get_model(doc, root, model, comm)
                except RerenderError:
                    return self._get_objects(model, current_objects[:i], doc, root, comm)
            new_models.append(child)
        return new_models

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = self._bokeh_model()
        if root is None:
            root = model
        objects = self._get_objects(model, [], doc, root, comm)
        props = dict(self._init_properties(), objects=objects)
        model.update(**self._process_param_change(props))
        self._models[root.ref['id']] = (model, parent)
        self._link_props(model, self._linked_props, doc, root, comm)
        return model

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def select(self, selector=None):
        """
        Iterates over the Viewable and any potential children in the
        applying the Selector.

        Arguments
        ---------
        selector: type or callable or None
          The selector allows selecting a subset of Viewables by
          declaring a type or callable function to filter by.

        Returns
        -------
        viewables: list(Viewable)
        """
        objects = super(Panel, self).select(selector)
        for obj in self:
            objects += obj.select(selector)
        return objects



class ListPanel(Panel):
    """
    An abstract baseclass for Panel objects with list-like children.
    """

    margin = param.Parameter(default=0, doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""")

    objects = param.List(default=[], doc="""
        The list of child objects that make up the layout.""")

    scroll = param.Boolean(default=False, doc="""
        Whether to add scrollbars if the content overflows the size
        of the container.""")

    _source_transforms = {'scroll': None}

    __abstract = True

    def __init__(self, *objects, **params):
        from .pane import panel
        if objects:
            if 'objects' in params:
                raise ValueError("A %s's objects should be supplied either "
                                 "as positional arguments or as a keyword, "
                                 "not both." % type(self).__name__)
            params['objects'] = [panel(pane) for pane in objects]
        super(Panel, self).__init__(**params)

    def _process_param_change(self, params):
        scroll = params.pop('scroll', None)
        css_classes = self.css_classes or []
        if scroll:
            params['css_classes'] = css_classes + ['scrollable']
        elif scroll == False:
            params['css_classes'] = css_classes
        return super(ListPanel, self)._process_param_change(params)

    def _cleanup(self, root):
        super(ListPanel, self)._cleanup(root)
        for p in self.objects:
            p._cleanup(root)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def __getitem__(self, index):
        return self.objects[index]

    def __len__(self):
        return len(self.objects)

    def __iter__(self):
        for obj in self.objects:
            yield obj

    def __contains__(self, obj):
        return obj in self.objects

    def __setitem__(self, index, panes):
        from .pane import panel
        new_objects = list(self)
        if not isinstance(index, slice):
            start, end = index, index+1
            if start > len(self.objects):
                raise IndexError('Index %d out of bounds on %s '
                                 'containing %d objects.' %
                                 (end, type(self).__name__, len(self.objects)))
            panes = [panes]
        else:
            start = index.start or 0
            end = len(self) if index.stop is None else index.stop
            if index.start is None and index.stop is None:
                if not isinstance(panes, list):
                    raise IndexError('Expected a list of objects to '
                                     'replace the objects in the %s, '
                                     'got a %s type.' %
                                     (type(self).__name__, type(panes).__name__))
                expected = len(panes)
                new_objects = [None]*expected
                end = expected
            elif end > len(self.objects):
                raise IndexError('Index %d out of bounds on %s '
                                 'containing %d objects.' %
                                 (end, type(self).__name__, len(self.objects)))
            else:
                expected = end-start
            if not isinstance(panes, list) or len(panes) != expected:
                raise IndexError('Expected a list of %d objects to set '
                                 'on the %s to match the supplied slice.' %
                                 (expected, type(self).__name__))
        for i, pane in zip(range(start, end), panes):
            new_objects[i] = panel(pane)

        self.objects = new_objects

    def clone(self, *objects, **params):
        """
        Makes a copy of the layout sharing the same parameters.

        Arguments
        ---------
        objects: Objects to add to the cloned layout.
        params: Keyword arguments override the parameters on the clone.

        Returns
        -------
        Cloned layout object
        """
        if not objects:
            if 'objects' in params:
                objects = params.pop('objects')
            else:
                objects = self.objects
        elif 'objects' in params:
            raise ValueError("A %s's objects should be supplied either "
                             "as arguments or as a keyword, not both."
                             % type(self).__name__)
        p = dict(self.param.get_param_values(), **params)
        del p['objects']
        return type(self)(*objects, **params)

    def append(self, obj):
        """
        Appends an object to the layout.

        Arguments
        ---------
        obj (object): Panel component to add to the layout.
        """
        from .pane import panel
        new_objects = list(self)
        new_objects.append(panel(obj))
        self.objects = new_objects

    def clear(self):
        """
        Clears the objects on this layout.
        """
        self.objects = []

    def extend(self, objects):
        """
        Extends the objects on this layout with a list.

        Arguments
        ---------
        objects (list): List of panel components to add to the layout.
        """
        from .pane import panel
        new_objects = list(self)
        new_objects.extend(list(map(panel, objects)))
        self.objects = new_objects

    def insert(self, index, obj):
        """
        Inserts an object in the layout at the specified index.

        Arguments
        ---------
        index (int): Index at which to insert the object.
        object (object): Panel components to insert in the layout.
        """
        from .pane import panel
        new_objects = list(self)
        new_objects.insert(index, panel(obj))
        self.objects = new_objects

    def pop(self, index):
        """
        Pops an item from the layout by index.

        Arguments
        ---------
        index (int): The index of the item to pop from the layout.
        """
        new_objects = list(self)
        if index in new_objects:
            index = new_objects.index(index)
        obj = new_objects.pop(index)
        self.objects = new_objects
        return obj

    def remove(self, obj):
        """
        Removes an object from the layout.

        Arguments
        ---------
        obj (object): The object to remove from the layout.
        """
        new_objects = list(self)
        new_objects.remove(obj)
        self.objects = new_objects

    def reverse(self):
        """
        Reverses the objects in the layout.
        """
        new_objects = list(self)
        new_objects.reverse()
        self.objects = new_objects


class Row(ListPanel):
    """
    Horizontal layout of Viewables.
    """

    _bokeh_model = BkRow


class Column(ListPanel):
    """
    Vertical layout of Viewables.
    """

    _bokeh_model = BkColumn



class GridBox(ListPanel):
    """
    List-like Grid which wraps depending on the specified number of
    rows or columns.
    """

    nrows = param.Integer(default=None, bounds=(0, None), doc="""
      Number of rows to reflow the layout into.""")

    ncols = param.Integer(default=None, bounds=(0, None),  doc="""
      Number of columns to reflow the layout into.""")

    _bokeh_model = BkGridBox

    _rename = {'objects': 'children'}

    _source_transforms = {'scroll': None, 'objects': None,
                         'nrows': None, 'ncols': None}

    @classmethod
    def _flatten_grid(cls, layout, nrows=None, ncols=None):
        Item = namedtuple("Item", ["layout", "r0", "c0", "r1", "c1"])
        Grid = namedtuple("Grid", ["nrows", "ncols", "items"])

        def gcd(a, b):
            a, b = abs(a), abs(b)
            while b != 0:
                a, b = b, a % b
            return a

        def lcm(a, *rest):
            for b in rest:
                a = (a*b) // gcd(a, b)
            return a

        nonempty = lambda child: child.nrows != 0 and child.ncols != 0

        def _flatten(layout, nrows=None, ncols=None):
            _flatten_ = partial(_flatten, nrows=nrows, ncols=ncols)
            if isinstance(layout, _row):
                children = list(filter(nonempty, map(_flatten_, layout.children)))
                if not children:
                    return Grid(0, 0, [])

                nrows = lcm(*[ child.nrows for child in children ])
                if not ncols: # This differs from bokeh.layout.grid
                    ncols = sum([ child.ncols for child in children ])

                items = []
                offset = 0
                for child in children:
                    factor = nrows//child.nrows

                    for (layout, r0, c0, r1, c1) in child.items:
                        items.append((layout, factor*r0, c0 + offset, factor*r1, c1 + offset))

                    offset += child.ncols

                return Grid(nrows, ncols, items)
            elif isinstance(layout, _col):
                children = list(filter(nonempty, map(_flatten_, layout.children)))
                if not children:
                    return Grid(0, 0, [])

                if not nrows: # This differs from bokeh.layout.grid
                    nrows = sum([ child.nrows for child in children ])
                ncols = lcm(*[ child.ncols for child in children ])

                items = []
                offset = 0
                for child in children:
                    factor = ncols//child.ncols

                    for (layout, r0, c0, r1, c1) in child.items:
                        items.append((layout, r0 + offset, factor*c0, r1 + offset, factor*c1))

                    offset += child.nrows

                return Grid(nrows, ncols, items)
            else:
                return Grid(1, 1, [Item(layout, 0, 0, 1, 1)])

        grid = _flatten(layout, nrows, ncols)

        children = []
        for (layout, r0, c0, r1, c1) in grid.items:
            if layout is not None:
                children.append((layout, r0, c0, r1 - r0, c1 - c0))
        return children

    @classmethod
    def _get_children(cls, children, nrows=None, ncols=None):
        """
        This is a copy of parts of the bokeh.layouts.grid implementation
        to avoid distributing non-filled columns.
        """
        if nrows is not None or ncols is not None:
            N = len(children)
            if ncols is None:
                ncols = int(math.ceil(N/nrows))
            layout = _col([ _row(children[i:i+ncols]) for i in range(0, N, ncols) ])
        else:
            def traverse(children, level=0):
                if isinstance(children, list):
                    container = _col if level % 2 == 0 else _row
                    return container([ traverse(child, level+1) for child in children ])
                else:
                    return children
            layout = traverse(children)
        return cls._flatten_grid(layout, nrows, ncols)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = self._bokeh_model()
        if root is None:
            root = model
        objects = self._get_objects(model, [], doc, root, comm)
        model.children = self._get_children(objects, self.nrows, self.ncols)
        props = {k: v for k, v in self._init_properties().items()
                 if k not in ('nrows', 'ncols')}
        model.update(**self._process_param_change(props))
        self._models[root.ref['id']] = (model, parent)
        self._link_props(model, self._linked_props, doc, root, comm)
        return model

    def _update_model(self, events, msg, root, model, doc, comm=None):
        if self._rename['objects'] in msg or 'ncols' in msg or 'nrows' in msg:
            if 'objects' in events:
                old = events['objects'].old
            else:
                old = self.objects
            objects = self._get_objects(model, old, doc, root, comm)
            children = self._get_children(objects, self.nrows, self.ncols)
            msg[self._rename['objects']] = children

        held = doc._hold
        if comm is None and not held:
            doc.hold()
        model.update(**{k: v for k, v in msg.items() if k not in ('nrows', 'ncols')})

        from .io import state
        ref = root.ref['id']
        if ref in state._views:
            state._views[ref][0]._preprocess(root)

        if comm is None and not held:
            doc.unhold()



class WidgetBox(ListPanel):
    """
    Vertical layout of widgets.
    """

    css_classes = param.List(default=['widget-box'], doc="""
        CSS classes to apply to the layout.""")

    disabled = param.Boolean(default=False, doc="""
       Whether the widget is disabled.""")

    horizontal = param.Boolean(default=False, doc="""Whether to lay out the
                    widgets in a Row layout as opposed to a Column layout.""")

    margin = param.Parameter(default=5, doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""")

    _source_transforms = {'disabled': None, 'horizontal': None}

    _rename = {'objects': 'children', 'horizontal': None}

    @property
    def _bokeh_model(self):
        return BkRow if self.horizontal else BkColumn

    @param.depends('disabled', 'objects', watch=True)
    def _disable_widgets(self):
        for obj in self:
            if hasattr(obj, 'disabled'):
                obj.disabled = self.disabled

    def __init__(self, *objects, **params):
        super(WidgetBox, self).__init__(*objects, **params)
        if self.disabled:
            self._disable_widgets()


class Tabs(ListPanel):
    """
    Panel of Viewables to be displayed in separate tabs.
    """

    active = param.Integer(default=0, bounds=(0, None), doc="""
        Number of the currently active tab.""")

    closable = param.Boolean(default=False, doc="""
        Whether it should be possible to close tabs.""")

    dynamic = param.Boolean(default=False, doc="""
        Dynamically populate only the active tab.""")

    objects = param.List(default=[], doc="""
        The list of child objects that make up the tabs.""")

    tabs_location = param.ObjectSelector(
        default='above', objects=['above', 'below', 'left', 'right'], doc="""
        The location of the tabs relative to the tab contents.""")

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    _bokeh_model = BkTabs

    _source_transforms = {'dynamic': None, 'objects': None}

    _rename = {'name': None, 'objects': 'tabs', 'dynamic': None}

    _linked_props = ['active', 'tabs']

    _js_transforms = {'tabs': """
    var ids = [];
    for (t of value) {{ ids.push(t.id) }};
    value = ids;
    """}

    def __init__(self, *items, **params):
        if 'objects' in params:
            if items:
                raise ValueError('Tabs objects should be supplied either '
                                 'as positional arguments or as a keyword, '
                                 'not both.')
            items = params['objects']
        objects, self._names = self._to_objects_and_names(items)
        super(Tabs, self).__init__(*objects, **params)
        self._panels = defaultdict(dict)
        self.param.watch(self._update_names, 'objects')
        self.param.watch(self._update_active, ['dynamic', 'active'])
        self.param.active.bounds = (0, len(self)-1)
        # ALERT: Ensure that name update happens first, should be
        #        replaced by watch precedence support in param
        self._param_watchers['objects']['value'].reverse()

    def _to_object_and_name(self, item):
        from .pane import panel
        if isinstance(item, tuple):
            name, item = item
        else:
            name = getattr(item, 'name', None)
        pane = panel(item, name=name)
        name = param_name(pane.name) if name is None else name
        return pane, name

    def _to_objects_and_names(self, items):
        objects, names = [], []
        for item in items:
            pane, name = self._to_object_and_name(item)
            objects.append(pane)
            names.append(name)
        return objects, names

    def _init_properties(self):
        return {k: v for k, v in self.param.get_param_values()
                if v is not None and k != 'closable'}

    #----------------------------------------------------------------
    # Callback API
    #----------------------------------------------------------------

    def _comm_change(self, msg, ref=None):
        """
        Handle closed tabs.
        """
        if 'tabs' in msg:
            tab_refs = msg.pop('tabs')
            model, _ = self._models.get(ref)
            if model:
                tabs = {t.ref['id']: i for i, t in enumerate(model.tabs)}
                inds = [tabs[tref] for tref in tab_refs]
                msg['tabs'] = [self.objects[i] for i in inds]
        super(Tabs, self)._comm_change(msg)

    def _server_change(self, doc, ref, attr, old, new):
        """
        Handle closed tabs.
        """
        if attr == 'tabs':
            model, _ = self._models.get(ref)
            if model:
                inds = [i for i, t in enumerate(model.tabs) if t in new]
                old = self.objects
                new = [old[i] for i in inds]
        super(Tabs, self)._server_change(doc, ref, attr, old, new)

    def _update_names(self, event):
        self.param.active.bounds = (0, len(event.new)-1)
        if len(event.new) == len(self._names):
            return
        names = []
        for obj in event.new:
            if obj in event.old:
                index = event.old.index(obj)
                name = self._names[index]
            else:
                name = obj.name
            names.append(name)
        self._names = names

    def _update_active(self, *events):
        for event in events:
            if event.name == 'dynamic' or (self.dynamic and event.name == 'active'):
                self.param.trigger('objects')
                return

    #----------------------------------------------------------------
    # Model API
    #----------------------------------------------------------------

    def _update_model(self, events, msg, root, model, doc, comm=None):
        if 'closable' in msg:
            closable = msg.pop('closable')
            for child in model.tabs:
                child.closable = closable
        super(Tabs, self)._update_model(events, msg, root, model, doc, comm)

    def _get_objects(self, model, old_objects, doc, root, comm=None):
        """
        Returns new child models for the layout while reusing unchanged
        models and cleaning up any dropped objects.
        """
        from .pane.base import RerenderError, panel
        new_models = []
        if len(self._names) != len(self):
            raise ValueError('Tab names do not match objects, ensure '
                             'that the Tabs.objects are not modified '
                             'directly. Found %d names, expected %d.' %
                             (len(self._names), len(self)))
        for i, (name, pane) in enumerate(zip(self._names, self)):
            pane = panel(pane, name=name)
            self.objects[i] = pane

        for obj in old_objects:
            if obj not in self.objects:
                obj._cleanup(root)

        current_objects = list(self)
        panels = self._panels[root.ref['id']]
        for i, (name, pane) in enumerate(zip(self._names, self)):
            if self.dynamic and i != self.active:
                child = BkSpacer(**{k: v for k, v in pane.param.get_param_values()
                                    if k in Layoutable.param})
            elif pane in old_objects and id(pane) in pane._models:
                panel = panels[id(pane)]
                new_models.append(panel)
                continue
            else:
                try:
                    child = pane._get_model(doc, root, model, comm)
                except RerenderError:
                    return self._get_objects(model, current_objects[:i], doc, root, comm)
            panel = panels[id(pane)] = BkPanel(
                title=name, name=pane.name, child=child, closable=self.closable
            )
            new_models.append(panel)
        return new_models

    def _cleanup(self, root):
        super(Tabs, self)._cleanup(root)
        if root.ref['id'] in self._panels:
            del self._panels[root.ref['id']]

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def __setitem__(self, index, panes):
        new_objects = list(self)
        if not isinstance(index, slice):
            if index > len(self.objects):
                raise IndexError('Index %d out of bounds on %s '
                                 'containing %d objects.' %
                                 (index, type(self).__name__, len(self.objects)))
            start, end = index, index+1
            panes = [panes]
        else:
            start = index.start or 0
            end = len(self.objects) if index.stop is None else index.stop
            if index.start is None and index.stop is None:
                if not isinstance(panes, list):
                    raise IndexError('Expected a list of objects to '
                                     'replace the objects in the %s, '
                                     'got a %s type.' %
                                     (type(self).__name__, type(panes).__name__))
                expected = len(panes)
                new_objects = [None]*expected
                self._names = [None]*len(panes)
                end = expected
            else:
                expected = end-start
                if end > len(self.objects):
                    raise IndexError('Index %d out of bounds on %s '
                                     'containing %d objects.' %
                                     (end, type(self).__name__, len(self.objects)))
            if not isinstance(panes, list) or len(panes) != expected:
                raise IndexError('Expected a list of %d objects to set '
                                 'on the %s to match the supplied slice.' %
                                 (expected, type(self).__name__))
        for i, pane in zip(range(start, end), panes):
            new_objects[i], self._names[i] = self._to_object_and_name(pane)
        self.objects = new_objects

    def clone(self, *objects, **params):
        """
        Makes a copy of the Tabs sharing the same parameters.

        Arguments
        ---------
        objects: Objects to add to the cloned Tabs object.
        params: Keyword arguments override the parameters on the clone.

        Returns
        -------
        Cloned Tabs object
        """
        if not objects:
            if 'objects' in params:
                objects = params.pop('objects')
            else:
                objects = zip(self._names, self.objects)
        elif 'objects' in params:
            raise ValueError('Tabs objects should be supplied either '
                             'as positional arguments or as a keyword, '
                             'not both.')
        p = dict(self.param.get_param_values(), **params)
        del p['objects']
        return type(self)(*objects, **params)

    def append(self, pane):
        """
        Appends an object to the tabs.

        Arguments
        ---------
        obj (object): Panel component to add as a tab.
        """
        new_object, new_name = self._to_object_and_name(pane)
        new_objects = list(self)
        new_objects.append(new_object)
        self._names.append(new_name)
        self.objects = new_objects

    def clear(self):
        """
        Clears the tabs.
        """
        self._names = []
        self.objects = []

    def extend(self, panes):
        """
        Extends the the tabs with a list.

        Arguments
        ---------
        objects (list): List of panel components to add as tabs.
        """
        new_objects, new_names = self._to_objects_and_names(panes)
        objects = list(self)
        objects.extend(new_objects)
        self._names.extend(new_names)
        self.objects = objects

    def insert(self, index, pane):
        """
        Inserts an object in the tabs at the specified index.

        Arguments
        ---------
        index (int): Index at which to insert the object.
        object (object): Panel components to insert as tabs.
        """
        new_object, new_name = self._to_object_and_name(pane)
        new_objects = list(self.objects)
        new_objects.insert(index, new_object)
        self._names.insert(index, new_name)
        self.objects = new_objects

    def pop(self, index):
        """
        Pops an item from the tabs by index.

        Arguments
        ---------
        index (int): The index of the item to pop from the tabs.
        """
        new_objects = list(self)
        if index in new_objects:
            index = new_objects.index(index)
        new_objects.pop(index)
        self._names.pop(index)
        self.objects = new_objects

    def remove(self, pane):
        """
        Removes an object from the tabs.

        Arguments
        ---------
        obj (object): The object to remove from the tabs.
        """
        new_objects = list(self)
        if pane in new_objects:
            index = new_objects.index(pane)
        new_objects.remove(pane)
        self._names.pop(index)
        self.objects = new_objects

    def reverse(self):
        """
        Reverses the tabs.
        """
        new_objects = list(self)
        new_objects.reverse()
        self._names.reverse()
        self.objects = new_objects


class GridSpec(Panel):

    objects = param.Dict(default={}, doc="""
        The dictionary of child objects that make up the grid.""")

    mode = param.ObjectSelector(
        default='warn', objects=['warn', 'error', 'override'], doc="""
        Whether to warn, error or simply override on overlapping assignment.""")

    width = param.Integer(default=600)

    height = param.Integer(default=600)

    _bokeh_model = BkGridBox

    _source_transforms = {'objects': None, 'mode': None}

    _rename = {'objects': 'children', 'mode': None}

    def __init__(self, **params):
        if 'objects' not in params:
            params['objects'] = OrderedDict()
        super(GridSpec, self).__init__(**params)

    def _init_properties(self):
        properties = super(GridSpec, self)._init_properties()
        if self.sizing_mode not in ['fixed', None]:
            if 'min_width' not in properties and 'width' in properties:
                properties['min_width'] = properties['width']
            if 'min_height' not in properties and 'height' in properties:
                properties['min_height'] = properties['height']
        return properties

    def _get_objects(self, model, old_objects, doc, root, comm=None):
        from .pane.base import RerenderError

        if self.ncols:
            width = int(float(self.width)/self.ncols)
        else:
            width = 0

        if self.nrows:
            height = int(float(self.height)/self.nrows)
        else:
            height = 0

        current_objects = list(self.objects.values())
        if isinstance(old_objects, dict):
            old_objects = list(old_objects.values())

        for old in old_objects:
            if old not in current_objects:
                old._cleanup(root)

        children = []
        for i, ((y0, x0, y1, x1), obj) in enumerate(self.objects.items()):
            x0 = 0 if x0 is None else x0
            x1 = (self.ncols) if x1 is None else x1
            y0 = 0 if y0 is None else y0
            y1 = (self.nrows) if y1 is None else y1
            r, c, h, w = (y0, x0, y1-y0, x1-x0)

            if self.sizing_mode in ['fixed', None]:
                properties = {'width': w*width, 'height': h*height}
            else:
                properties = {'sizing_mode': self.sizing_mode}
                if 'width' in self.sizing_mode:
                    properties['height'] = h*height
                elif 'height' in self.sizing_mode:
                    properties['width'] = w*width
            obj.param.set_param(**properties)

            if obj in old_objects:
                child, _ = obj._models[root.ref['id']]
            else:
                try:
                    child = obj._get_model(doc, root, model, comm)
                except RerenderError:
                    return self._get_objects(model, current_objects[:i], doc, root, comm)

            if isinstance(child, BkBox) and len(child.children) == 1:
                child.children[0].update(**properties)
            else:
                child.update(**properties)
            children.append((child, r, c, h, w))
        return children

    @property
    def _xoffset(self):
        min_xidx = [x0 for (_, x0, _, _) in self.objects if x0 is not None]
        return min(min_xidx) if min_xidx and len(min_xidx) == len(self.objects) else 0

    @property
    def _yoffset(self):
        min_yidx = [y0 for (y0, x0, _, _) in self.objects if y0 is not None]
        return min(min_yidx) if min_yidx and len(min_yidx) == len(self.objects) else 0

    @property
    def _object_grid(self):
        grid = np.full((self.nrows, self.ncols), None, dtype=object)
        for i, ((y0, x0, y1, x1), obj) in enumerate(self.objects.items()):
            l = 0 if x0 is None else x0
            r = self.ncols if x1 is None else x1
            t = 0 if y0 is None else y0
            b = self.nrows if y1 is None else y1
            for y in range(t, b):
                for x in range(l, r):
                    grid[y, x] = {((y0, x0, y1, x1), obj)}
        return grid

    def _cleanup(self, root):
        super(GridSpec, self)._cleanup(root)
        for p in self.objects.values():
            p._cleanup(root)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    @property
    def nrows(self):
        max_yidx = [y1 for (_, _, y1, _) in self.objects if y1 is not None]
        return max(max_yidx) if max_yidx else (1 if len(self.objects) else 0)

    @property
    def ncols(self):
        max_xidx = [x1 for (_, _, _, x1) in self.objects if x1 is not None]
        return max(max_xidx) if max_xidx else (1 if len(self.objects) else 0)

    @property
    def grid(self):
        grid = np.zeros((self.nrows, self.ncols), dtype='uint8')
        for (y0, x0, y1, x1) in self.objects:
            x0 = 0 if x0 is None else x0
            x1 = self.ncols if x1 is None else x1
            y0 = 0 if y0 is None else y0
            y1 = self.nrows if y1 is None else y1
            grid[y0:y1, x0:x1] += 1
        return grid

    def clone(self, **params):
        """
        Makes a copy of the GridSpec sharing the same parameters.

        Arguments
        ---------
        params: Keyword arguments override the parameters on the clone.

        Returns
        -------
        Cloned GridSpec object
        """
        p = dict(self.param.get_param_values(), **params)
        return type(self)(**p)

    def __iter__(self):
        for obj in self.objects.values():
            yield obj

    def __delitem__(self, index):
        if isinstance(index, tuple):
            yidx, xidx = index
        else:
            yidx, xidx = index, slice(None)

        subgrid = self._object_grid[yidx, xidx]
        if isinstance(subgrid, np.ndarray):
            deleted = OrderedDict([list(o)[0] for o in subgrid.flatten()])
        else:
            deleted = [list(subgrid)[0][0]]
        for key in deleted:
            del self.objects[key]
        self.param.trigger('objects')

    def __getitem__(self, index):
        if isinstance(index, tuple):
            yidx, xidx = index
        else:
            yidx, xidx = index, slice(None)

        subgrid = self._object_grid[yidx, xidx]
        if isinstance(subgrid, np.ndarray):
            params = dict(self.param.get_param_values())
            params['objects'] = OrderedDict([list(o)[0] for o in subgrid.flatten()])
            gspec = GridSpec(**params)
            xoff, yoff = gspec._xoffset, gspec._yoffset
            adjusted = []
            for (y0, x0, y1, x1), obj in gspec.objects.items():
                if y0 is not None: y0 -= yoff
                if y1 is not None: y1 -= yoff
                if x0 is not None: x0 -= xoff
                if x1 is not None: x1 -= xoff
                if ((y0, x0, y1, x1), obj) not in adjusted:
                    adjusted.append(((y0, x0, y1, x1), obj))
            gspec.objects = OrderedDict(adjusted)
            width_scale = gspec.ncols/float(self.ncols)
            height_scale = gspec.nrows/float(self.nrows)
            if gspec.width:
                gspec.width = int(gspec.width * width_scale)
            if gspec.height:
                gspec.height = int(gspec.height * height_scale)
            if gspec.max_width:
                gspec.max_width = int(gspec.max_width * width_scale)
            if gspec.max_height:
                gspec.max_height = int(gspec.max_height * height_scale)
            return gspec
        else:
            return list(subgrid)[0][1]

    def __setitem__(self, index, obj):
        from .pane.base import panel
        if not isinstance(index, tuple):
            raise IndexError('Must supply a 2D index for GridSpec assignment.')

        yidx, xidx = index
        if isinstance(xidx, slice):
            x0, x1 = (xidx.start, xidx.stop)
        else:
            x0, x1 = (xidx, xidx+1)

        if isinstance(yidx, slice):
            y0, y1 = (yidx.start, yidx.stop)
        else:
            y0, y1 = (yidx, yidx+1)

        l = 0 if x0 is None else x0
        r = self.nrows if x1 is None else x1
        t = 0 if y0 is None else y0
        b = self.ncols if y1 is None else y1

        key = (y0, x0, y1, x1)
        overlap = key in self.objects
        clone = self.clone(objects=OrderedDict(self.objects), mode='override')
        if not overlap:
            clone.objects[key] = panel(obj)
            grid = clone.grid
        else:
            grid = clone.grid
            grid[t:b, l:r] += 1

        overlap_grid = grid>1
        if (overlap_grid).any():
            overlapping = ''
            objects = []
            for (yidx, xidx) in zip(*np.where(overlap_grid)):
                try:
                    old_obj = self[yidx, xidx]
                except Exception:
                    continue
                if old_obj not in objects:
                    objects.append(old_obj)
                    overlapping += '    (%d, %d): %s\n\n' % (yidx, xidx, old_obj)
            overlap_text = ('Specified region overlaps with the following '
                            'existing object(s) in the grid:\n\n'+overlapping+
                            'The following shows a view of the grid '
                            '(empty: 0, occupied: 1, overlapping: 2):\n\n'+
                            str(grid.astype('uint8')))
            if self.mode == 'error':
                raise IndexError(overlap_text)
            elif self.mode == 'warn':
                self.param.warning(overlap_text)

            subgrid = self._object_grid[index]
            if isinstance(subgrid, set):
                objects = [list(subgrid)[0][0]] if subgrid else []
            else:
                objects = [list(o)[0][0] for o in subgrid.flatten()]
            for dkey in objects:
                del self.objects[dkey]
        self.objects[key] = panel(obj)
        self.param.trigger('objects')


class Spacer(Reactive):
    """Empty object used to control formatting (using positive or negative space)"""

    _bokeh_model = BkSpacer

    def _get_model(self, doc, root=None, parent=None, comm=None):
        properties = self._process_param_change(self._init_properties())
        model = self._bokeh_model(**properties)
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model


class VSpacer(Spacer):
    """
    Spacer which automatically fills all available vertical space.
    """

    sizing_mode = param.Parameter(default='stretch_height', readonly=True)


class HSpacer(Spacer):
    """
    Spacer which automatically fills all available horizontal space.
    """

    sizing_mode = param.Parameter(default='stretch_width', readonly=True)


class Divider(Reactive):
    """A Divider line"""

    width_policy = param.ObjectSelector(default="fit", readonly=True)

    _bokeh_model = BkDiv

    def _get_model(self, doc, root=None, parent=None, comm=None):
        properties = self._process_param_change(self._init_properties())
        properties['style'] = {'width': '100%', 'height': '100%'}
        model = self._bokeh_model(text='<hr style="margin: 0px">', **properties)
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model
