"""
Layout component to lay out objects in a set of tabs.
"""
import param

from bokeh.models import (
    Spacer as BkSpacer, Panel as BkPanel, Tabs as BkTabs
)

from .base import ListPanel


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
    for (var t of value) {{ ids.push(t.id) }};
    var value = ids;
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

    def _init_properties(self):
        return {k: v for k, v in self.param.get_param_values()
                if v is not None and k != 'closable'}

    #----------------------------------------------------------------
    # Callback API
    #----------------------------------------------------------------

    def _process_close(self, ref, attr, old, new):
        """
        Handle closed tabs.
        """
        model, _ = self._models.get(ref)
        if model:
            inds = [old.index(tab) for tab in new]
            old = self.objects
            new = [old[i] for i in inds]
        return old, new

    def _comm_change(self, doc, ref, attr, old, new):
        if attr in self._changing.get(ref, []):
            self._changing[ref].remove(attr)
            return
        if attr == 'tabs':
            old, new = self._process_close(ref, attr, old, new)
        super(Tabs, self)._comm_change(doc, ref, attr, old, new)

    def _server_change(self, doc, ref, attr, old, new):
        if attr in self._changing.get(ref, []):
            self._changing[ref].remove(attr)
            return
        if attr == 'tabs':
            old, new = self._process_close(ref, attr, old, new)
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
        msg = dict(msg)
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
        from ..pane.base import RerenderError, panel
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
            hidden = self.dynamic and i != self.active
            if (pane in old_objects and id(pane) in panels and
                ((hidden and isinstance(panels[id(pane)].child, BkSpacer)) or
                 (not hidden and not isinstance(panels[id(pane)].child, BkSpacer)))):
                panel = panels[id(pane)]
                new_models.append(panel)
                continue
            elif self.dynamic and i != self.active:
                child = BkSpacer(**{k: v for k, v in pane.param.get_param_values()
                                    if k in Layoutable.param})
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
