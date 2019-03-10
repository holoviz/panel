"""
Defines Layout classes which may be used to arrange panes and widgets
in flexible ways to build complex dashboards.
"""
from __future__ import absolute_import, division, unicode_literals

import param

from bokeh.models import (Column as BkColumn, Row as BkRow,
                          Spacer as BkSpacer)
from bokeh.models.widgets import Tabs as BkTabs, Panel as BkPanel

from .util import param_name, param_reprs
from .viewable import Reactive


class Panel(Reactive):
    """
    Abstract baseclass for a layout of Viewables.
    """

    objects = param.List(default=[], doc="""
        The list of child objects that make up the layout.""")

    _bokeh_model = None

    __abstract = True

    _rename = {'objects': 'children'}

    _linked_props = []

    def __init__(self, *objects, **params):
        from .pane import panel
        objects = [panel(pane) for pane in objects]
        super(Panel, self).__init__(objects=objects, **params)

    def _update_model(self, events, msg, root, model, doc, comm=None):
        if self._rename['objects'] in msg:
            old = events['objects'].old
            msg[self._rename['objects']] = self._get_objects(model, old, doc, root, comm)
            for pane in old:
                if pane not in self.objects:
                    pane._cleanup(root)
        model.update(**msg)
        self._preprocess(root) #preprocess links between new elements

    def _cleanup(self, root):
        super(Panel, self)._cleanup(root)
        for p in self.objects:
            p._cleanup(root)

    def _get_objects(self, model, old_objects, doc, root, comm=None):
        """
        Returns new child models for the layout while reusing unchanged
        models and cleaning up any dropped objects.
        """
        from .pane import panel
        new_models = []
        for i, pane in enumerate(self.objects):
            pane = panel(pane)
            self.objects[i] = pane
            if pane in old_objects:
                child, _ = pane._models[root.ref['id']]
            else:
                child = pane._get_model(doc, root, model, comm)
            new_models.append(child)
        for obj in old_objects:
            if obj not in self.objects:
                obj._cleanup(root)
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
            objs=('%s' % spacer).join(objs), spacer=spacer
        )

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
        for obj in self.objects:
            objects += obj.select(selector)
        return objects

    def append(self, pane):
        from .pane import panel
        new_objects = list(self)
        new_objects.append(panel(pane))
        self.objects = new_objects

    def clear(self):
        self.objects = []

    def extend(self, panes):
        from .pane import panel
        new_objects = list(self)
        new_objects.extend(list(map(panel, panes)))
        self.objects = new_objects

    def insert(self, index, pane):
        from .pane import panel
        new_objects = list(self)
        new_objects.insert(index, panel(pane))
        self.objects = new_objects

    def pop(self, index):
        new_objects = list(self)
        if index in new_objects:
            index = new_objects.index(index)
        new_objects.pop(index)
        self.objects = new_objects

    def remove(self, pane):
        new_objects = list(self)
        new_objects.remove(pane)
        self.objects = new_objects

    def reverse(self):
        new_objects = list(self)
        new_objects.reverse()
        self.objects = new_objects


class Row(Panel):
    """
    Horizontal layout of Viewables.
    """

    _bokeh_model = BkRow


class Column(Panel):
    """
    Vertical layout of Viewables.
    """

    _bokeh_model = BkColumn


class Tabs(Panel):
    """
    Panel of Viewables to be displayed in separate tabs.
    """

    active = param.Integer(default=0, doc="""
        Number of the currently active tab.""")

    objects = param.List(default=[], doc="""
        The list of child objects that make up the tabs.""")

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    _bokeh_model = BkTabs

    _rename = {'objects': 'tabs'}

    _linked_props = ['active']

    def __init__(self, *items, **params):
        objects, self._names = self._to_objects_and_names(items)
        super(Tabs, self).__init__(*objects, **params)
        self.param.watch(self._update_names, 'objects')
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

    def _update_names(self, event):
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

    def _get_objects(self, model, old_objects, doc, root, comm=None):
        """
        Returns new child models for the layout while reusing unchanged
        models and cleaning up any dropped objects.
        """
        from .pane import panel
        new_models = []
        if len(self._names) != len(self):
            raise ValueError('Tab names do not match objects, ensure '
                             'that the Tabs.objects are not modified '
                             'directly. Found %d names, expected %d.' %
                             (len(self._names), len(self)))
        for i, (name, pane) in enumerate(zip(self._names, self)):
            pane = panel(pane, name=name)
            self.objects[i] = pane
            if pane in old_objects:
                child, _ = pane._models[root.ref['id']]
            else:
                child = pane._get_model(doc, root, model, comm)
            child = BkPanel(title=name, name=pane.name, child=child)
            new_models.append(child)
        for obj in old_objects:
            if obj not in self.objects:
                obj._cleanup(root)
        return new_models

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

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def append(self, pane):
        new_object, new_name = self._to_object_and_name(pane)
        new_objects = list(self)
        new_objects.append(new_object)
        self._names.append(new_name)
        self.objects = new_objects

    def clear(self):
        self._names = []
        self.objects = []

    def extend(self, panes):
        new_objects, new_names = self._to_objects_and_names(panes)
        objects = list(self)
        objects.extend(new_objects)
        self._names.extend(new_names)
        self.objects = objects

    def insert(self, index, pane):
        new_object, new_name = self._to_object_and_name(pane)
        new_objects = list(self.objects)
        new_objects.insert(index, new_object)
        self._names.insert(index, new_name)
        self.objects = new_objects

    def pop(self, index):
        new_objects = list(self)
        if index in new_objects:
            index = new_objects.index(index)
        new_objects.pop(index)
        self._names.pop(index)
        self.objects = new_objects

    def remove(self, pane):
        new_objects = list(self)
        if pane in new_objects:
            index = new_objects.index(pane)
        new_objects.remove(pane)
        self._names.pop(index)
        self.objects = new_objects

    def reverse(self):
        new_objects = list(self)
        new_objects.reverse()
        self._names.reverse()
        self.objects = new_objects


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

