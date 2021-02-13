"""
Defines Layout classes which may be used to arrange panes and widgets
in flexible ways to build complex dashboards.
"""
from collections import defaultdict, namedtuple

import param

from bokeh.models import Column as BkColumn, Row as BkRow

from ..io.model import hold
from ..io.state import state
from ..reactive import Reactive
from ..util import param_name, param_reprs

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

    _batch_update = False

    def __repr__(self, depth=0, max_depth=10):
        if depth > max_depth:
            return '...'
        spacer = '\n' + ('    ' * (depth+1))
        cls = type(self).__name__
        params = param_reprs(self, ['objects'])
        objs = ['[%d] %s' % (i, obj.__repr__(depth+1)) for i, obj in enumerate(self)]
        if not params and not objs:
            return super().__repr__(depth+1)
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
        msg = dict(msg)
        if self._rename['objects'] in msg:
            old = events['objects'].old
            msg[self._rename['objects']] = self._get_objects(model, old, doc, root, comm)

        with hold(doc):
            update = Panel._batch_update
            Panel._batch_update = True
            try:
                super()._update_model(events, msg, root, model, doc, comm)
                if update:
                    return
                from ..io import state
                ref = root.ref['id']
                if ref in state._views:
                    state._views[ref][0]._preprocess(root)
            finally:
                Panel._batch_update = update

    #----------------------------------------------------------------
    # Model API
    #----------------------------------------------------------------

    def _get_objects(self, model, old_objects, doc, root, comm=None):
        """
        Returns new child models for the layout while reusing unchanged
        models and cleaning up any dropped objects.
        """
        from ..pane.base import panel, RerenderError
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
        props = dict(self._init_params(), objects=objects)
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
        objects = super().select(selector)
        for obj in self:
            objects += obj.select(selector)
        return objects



class ListLike(param.Parameterized):

    objects = param.List(default=[], doc="""
        The list of child objects that make up the layout.""")
    
    def __getitem__(self, index):
        return self.objects[index]

    def __len__(self):
        return len(self.objects)

    def __iter__(self):
        for obj in self.objects:
            yield obj

    def __iadd__(self, other):
        self.extend(other)
        return self

    def __add__(self, other):
        if isinstance(other, ListLike):
            other = other.objects
        if not isinstance(other, list):
            stype = type(self).__name__
            otype = type(other).__name__
            raise ValueError("Cannot add items of type %s and %s, can only "
                             "combine %s.objects with list or ListLike object."
                             % (stype, otype, stype))
        return self.clone(*(self.objects+other))

    def __radd__(self, other):
        if isinstance(other, ListLike):
            other = other.objects
        if not isinstance(other, list):
            stype = type(self).__name__
            otype = type(other).__name__
            raise ValueError("Cannot add items of type %s and %s, can only "
                             "combine %s.objects with list or ListLike object."
                             % (otype, stype, stype))
        return self.clone(*(other+self.objects))

    def __contains__(self, obj):
        return obj in self.objects

    def __setitem__(self, index, panes):
        from ..pane import panel
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
        return type(self)(*objects, **p)

    def append(self, obj):
        """
        Appends an object to the layout.

        Arguments
        ---------
        obj (object): Panel component to add to the layout.
        """
        from ..pane import panel
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
        from ..pane import panel
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
        from ..pane import panel
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

    

class ListPanel(ListLike, Panel):
    """
    An abstract baseclass for Panel objects with list-like children.
    """

    margin = param.Parameter(default=0, doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""")

    scroll = param.Boolean(default=False, doc="""
        Whether to add scrollbars if the content overflows the size
        of the container.""")

    _source_transforms = {'scroll': None}

    __abstract = True

    def __init__(self, *objects, **params):
        from ..pane import panel
        if objects:
            if 'objects' in params:
                raise ValueError("A %s's objects should be supplied either "
                                 "as positional arguments or as a keyword, "
                                 "not both." % type(self).__name__)
            params['objects'] = [panel(pane) for pane in objects]
        elif 'objects' in params:
            params['objects'] = [panel(pane) for pane in params['objects']]
        super(Panel, self).__init__(**params)

    def _process_param_change(self, params):
        scroll = params.pop('scroll', None)
        css_classes = self.css_classes or []
        if scroll:
            params['css_classes'] = css_classes + ['scrollable']
        elif scroll == False:
            params['css_classes'] = css_classes
        return super()._process_param_change(params)

    def _cleanup(self, root):
        if root.ref['id'] in state._fake_roots:
            state._fake_roots.remove(root.ref['id'])
        super()._cleanup(root)
        for p in self.objects:
            p._cleanup(root)


class NamedListPanel(ListPanel):

    active = param.Integer(default=0, bounds=(0, None), doc="""
        Index of the currently displayed objects.""")

    objects = param.List(default=[], doc="""
        The list of child objects that make up the tabs.""")

    def __init__(self, *items, **params):
        if 'objects' in params:
            if items:
                raise ValueError('%s objects should be supplied either '
                                 'as positional arguments or as a keyword, '
                                 'not both.' % type(self).__name__)
            items = params['objects']
        objects, self._names = self._to_objects_and_names(items)
        super().__init__(*objects, **params)
        self._panels = defaultdict(dict)
        self.param.watch(self._update_names, 'objects')
        # ALERT: Ensure that name update happens first, should be
        #        replaced by watch precedence support in param
        self._param_watchers['objects']['value'].reverse()

    def _to_object_and_name(self, item):
        from ..pane import panel
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

    def _update_active(self, *events):
        pass

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def __add__(self, other):
        if isinstance(other, NamedListPanel):
            other = list(zip(other._names, other.objects))
        elif isinstance(other, ListLike):
            other = other.objects
        if not isinstance(other, list):
            stype = type(self).__name__
            otype = type(other).__name__
            raise ValueError("Cannot add items of type %s and %s, can only "
                             "combine %s.objects with list or ListLike object."
                             % (stype, otype, stype))
        objects = list(zip(self._names, self.objects))
        return self.clone(*(objects+other))

    def __radd__(self, other):
        if isinstance(other, NamedListPanel):
            other = list(zip(other._names, other.objects))
        elif isinstance(other, ListLike):
            other = other.objects
        if not isinstance(other, list):
            stype = type(self).__name__
            otype = type(other).__name__
            raise ValueError("Cannot add items of type %s and %s, can only "
                             "combine %s.objects with list or ListLike object."
                             % (otype, stype, stype))
        objects = list(zip(self._names, self.objects))
        return self.clone(*(other+objects))

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



class Row(ListPanel):
    """
    Horizontal layout of Viewables.
    """

    col_sizing = param.Parameter()

    _bokeh_model = BkRow

    _rename = dict(ListPanel._rename, col_sizing='cols')


class Column(ListPanel):
    """
    Vertical layout of Viewables.
    """

    row_sizing = param.Parameter()

    _bokeh_model = BkColumn

    _rename = dict(ListPanel._rename, row_sizing='rows')


class WidgetBox(ListPanel):
    """
    Vertical layout of widgets.
    """

    css_classes = param.List(default=['panel-widget-box'], doc="""
        CSS classes to apply to the layout.""")

    disabled = param.Boolean(default=False, doc="""
        Whether the widget is disabled.""")

    horizontal = param.Boolean(default=False, doc="""
        Whether to lay out the widgets in a Row layout as opposed 
        to a Column layout.""")

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
        super().__init__(*objects, **params)
        if self.disabled:
            self._disable_widgets()
