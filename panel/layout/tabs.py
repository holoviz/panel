"""
Layout component to lay out objects in a set of tabs.
"""
import param

from bokeh.models import (
    Spacer as BkSpacer, Panel as BkPanel, Tabs as BkTabs
)

from ..viewable import Layoutable
from .base import NamedListPanel


class Tabs(NamedListPanel):
    """
    Panel of Viewables to be displayed in separate tabs.
    """

    closable = param.Boolean(default=False, doc="""
        Whether it should be possible to close tabs.""")

    dynamic = param.Boolean(default=False, doc="""
        Dynamically populate only the active tab.""")

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

    def __init__(self, *objects, **params):
        super(Tabs, self).__init__(*objects, **params)
        self.param.active.bounds = (0, len(self)-1)
        self.param.watch(self._update_active, ['dynamic', 'active'])

    def _init_properties(self):
        return {k: v for k, v in self.param.get_param_values()
                if v is not None and k != 'closable'}


    def _update_names(self, event):
        self.param.active.bounds = (0, len(event.new)-1)
        super(Tabs, self)._update_names(event)

    def _cleanup(self, root):
        super(Tabs, self)._cleanup(root)
        if root.ref['id'] in self._panels:
            del self._panels[root.ref['id']]

    #----------------------------------------------------------------
    # Callback API
    #----------------------------------------------------------------

    def _process_close(self, ref, attr, old, new):
        """
        Handle closed tabs.
        """
        model, _ = self._models.get(ref)
        if model:
            try:
                inds = [old.index(tab) for tab in new]
            except Exception:
                return old, None
            old = self.objects
            new = [old[i] for i in inds]
        return old, new

    def _comm_change(self, doc, ref, comm, attr, old, new):
        if attr in self._changing.get(ref, []):
            self._changing[ref].remove(attr)
            return
        if attr == 'tabs':
            old, new = self._process_close(ref, attr, old, new)
            if new is None:
                return
        super(Tabs, self)._comm_change(doc, ref, comm, attr, old, new)

    def _server_change(self, doc, ref, attr, old, new):
        if attr in self._changing.get(ref, []):
            self._changing[ref].remove(attr)
            return
        if attr == 'tabs':
            old, new = self._process_close(ref, attr, old, new)
            if new is None:
                return
        super(Tabs, self)._server_change(doc, ref, attr, old, new)

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
