"""
Layout component to lay out objects in a set of tabs.
"""
from collections import defaultdict

import param

from bokeh.models import (
    Spacer as BkSpacer, Panel as BkPanel
)

from ..models import Tabs as BkTabs
from ..viewable import Layoutable
from .base import NamedListPanel


class Tabs(NamedListPanel):
    """
    The `Tabs` layout allows switching between multiple objects by clicking
    on the corresponding tab header.

    Tab labels may be defined explicitly as part of a tuple or will be
    inferred from the `name` parameter of the tab’s contents.

    Like `Column` and `Row`, `Tabs` has a list-like API with methods to
    `append`, `extend`, `clear`, `insert`, `pop`, `remove` and `__setitem__`,
    which make it possible to interactively update and modify the tabs.

    Reference: https://panel.holoviz.org/reference/layouts/Tabs.html

    :Example:

    >>> pn.Tabs(('Scatter', plot1), some_pane_with_a_name)
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

    _js_transforms = {'tabs': """
    var ids = [];
    for (var t of value) {{ ids.push(t.id) }};
    var value = ids;
    """}

    _linked_props = ['active', 'tabs']

    _manual_params = ['closable']

    _rename = {'name': None, 'objects': 'tabs', 'dynamic': None}

    _source_transforms = {'dynamic': None, 'objects': None}

    def __init__(self, *objects, **params):
        super().__init__(*objects, **params)
        self._rendered = defaultdict(dict)
        self.param.active.bounds = (0, len(self)-1)
        self.param.watch(self._update_active, ['dynamic', 'active'])

    def _update_names(self, event):
        self.param.active.bounds = (0, len(event.new)-1)
        super()._update_names(event)

    def _cleanup(self, root):
        super()._cleanup(root)
        if root.ref['id'] in self._panels:
            del self._panels[root.ref['id']]
        if root.ref['id'] in self._rendered:
            del self._rendered[root.ref['id']]

    @property
    def _preprocess_params(self):
        return NamedListPanel._preprocess_params + (['active'] if self.dynamic else [])

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

    def _comm_change(self, doc, ref, comm, subpath, attr, old, new):
        if attr in self._changing.get(ref, []):
            self._changing[ref].remove(attr)
            return
        if attr == 'tabs':
            old, new = self._process_close(ref, attr, old, new)
            if new is None:
                return
        super()._comm_change(doc, ref, comm, subpath, attr, old, new)

    def _server_change(self, doc, ref, subpath, attr, old, new):
        if attr in self._changing.get(ref, []):
            self._changing[ref].remove(attr)
            return
        if attr == 'tabs':
            old, new = self._process_close(ref, attr, old, new)
            if new is None:
                return
        super()._server_change(doc, ref, subpath, attr, old, new)

    def _update_active(self, *events):
        for event in events:
            if event.name == 'dynamic' or (self.dynamic and event.name == 'active'):
                self.param.trigger('objects')
                return

    #----------------------------------------------------------------
    # Model API
    #----------------------------------------------------------------

    def _manual_update(self, events, model, doc, root, parent, comm):
        for event in events:
            if event.name == 'closable':
                for child in model.tabs:
                    child.closable = event.new

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

        ref = root.ref['id']
        panels = self._panels[ref]
        rendered = self._rendered[ref]
        for obj in old_objects:
            if obj in self.objects:
                continue
            obj._cleanup(root)
            panels.pop(id(obj), None)
            rendered.pop(id(obj), None)

        current_objects = list(self)
        for i, (name, pane) in enumerate(zip(self._names, self)):
            pref = id(pane)
            hidden = self.dynamic and i != self.active
            panel = panels.get(pref)
            prev_hidden = (
                hasattr(panel, 'child') and isinstance(panel.child, BkSpacer) and
                panel.child.tags == ['hidden']
            )

            # If object has not changed, we have not toggled between
            # hidden and unhidden state or the tabs are not
            # dynamic then reuse the panel
            if (pane in old_objects and pref in panels and
                (not (hidden ^ prev_hidden) or not (self.dynamic or prev_hidden))):
                new_models.append(panel)
                continue

            if prev_hidden and not hidden and pref in rendered:
                child = rendered[pref]
            elif hidden:
                child = BkSpacer(**{k: v for k, v in pane.param.values().items()
                                    if k in Layoutable.param and v is not None})
                child.tags = ['hidden']
            else:
                try:
                    rendered[pref] = child = pane._get_model(doc, root, model, comm)
                except RerenderError:
                    return self._get_objects(model, current_objects[:i], doc, root, comm)

            panel = panels[pref] = BkPanel(
                title=name, name=pane.name, child=child, closable=self.closable
            )
            new_models.append(panel)
        return new_models
