from collections import defaultdict

import param

from bokeh.models import Column as BkColumn, CustomJS

from .base import NamedListPanel
from .card import Card


class Accordion(NamedListPanel):
    
    active_header_background = param.String(default='#ccc', doc="""
        Color for currently active headers.""")

    toggle = param.Boolean(default=False, doc="""
        Whether to toggle between active cards or allow multiple cards""")
    
    _bokeh_model = BkColumn
    
    _rename = {'active': None, 'active_header_background': None,
               'objects': 'children', 'dynamic': None, 'toggle': None}

    _toggle = """
    for (var child of accordion.children) {
        if ((child.id !== cb_obj.id) && (child.collapsed == cb_obj.collapsed) && !cb_obj.collapsed) {
            child.collapsed = !cb_obj.collapsed
        }
    }
    """

    def _get_objects(self, model, old_objects, doc, root, comm=None):
        """
        Returns new child models for the layout while reusing unchanged
        models and cleaning up any dropped objects.
        """
        from panel.pane.base import RerenderError, panel
        new_models = []
        if len(self._names) != len(self):
            raise ValueError('Accordion names do not match objects, ensure '
                             'that the Tabs.objects are not modified '
                             'directly. Found %d names, expected %d.' %
                             (len(self._names), len(self)))
        for i, (name, pane) in enumerate(zip(self._names, self)):
            pane = panel(pane, name=name)
            self.objects[i] = pane

        for obj in old_objects:
            if obj not in self.objects:
                obj._cleanup(root)
                
        params = {k: v for k, v in self.param.get_param_values() if k in ['width', 'sizing_mode', 'width_policy', 'height_policy']}

        current_objects = list(self)
        panels = self._panels[root.ref['id']]
        for i, (name, pane) in enumerate(zip(self._names, self)):
            hidden = self.dynamic and i != self.active
            if (pane in old_objects and id(pane) in panels and
                ((hidden and isinstance(panels[id(pane)][1].children[1], BkSpacer)) or
                 (not hidden and not isinstance(panels[id(pane)][1].children[1], BkSpacer)))):
                panel = panels[id(pane)][1]
                new_models.append(panel)
                continue
            elif self.dynamic and i != self.active:
                child = BkSpacer(**{k: v for k, v in pane.param.get_param_values()
                                    if k in Layoutable.param})
            else:
                child = pane
            card = Card(child, title=name, active_header_background=self.active_header_background,
                        css_classes=['accordion'], header_css_classes=['accordion-header'], **params)
            try:
                (_, panel) = panels[id(pane)] = (card, card._get_model(doc, root, model, comm))
                if self.toggle:
                    cb = CustomJS(args={'accordion': model}, code=self._toggle)
                    panel.js_on_change('collapsed', cb)
            except RerenderError:
                return self._get_objects(model, current_objects[:i], doc, root, comm)
            if i == 0:
                panel.margin = (5, 5, 0, 5)
            else:
                panel.margin = (0, 5, 0, 5)
            panel.collapsed = i != self.active 
            
            new_models.append(panel)
        return new_models
