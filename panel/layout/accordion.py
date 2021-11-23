import param

from bokeh.models import Column as BkColumn, CustomJS

from .base import NamedListPanel
from .card import Card


class Accordion(NamedListPanel):
    
    active_header_background = param.String(default='#ccc', doc="""
        Color for currently active headers.""")

    active = param.List(default=[], doc="""
        List of indexes of active cards.""")

    header_color = param.String(doc="""
        A valid CSS color to apply to the expand button.""")

    header_background = param.String(doc="""
        A valid CSS color for the header background.""")

    toggle = param.Boolean(default=False, doc="""
        Whether to toggle between active cards or allow multiple cards""")

    _bokeh_model = BkColumn
    
    _rename = {'active': None, 'active_header_background': None,
               'header_background': None, 'objects': 'children',
               'dynamic': None, 'toggle': None, 'header_color': None}

    _toggle = """
    for (var child of accordion.children) {
      if ((child.id !== cb_obj.id) && (child.collapsed == cb_obj.collapsed) && !cb_obj.collapsed) {
        child.collapsed = !cb_obj.collapsed
      }
    }
    """

    _synced_properties = [
        'active_header_background', 'header_background', 'width',
        'sizing_mode', 'width_policy', 'height_policy', 'header_color'
    ]

    def __init__(self, *objects, **params):
        super().__init__(*objects, **params)
        self._updating_active = False
        self.param.watch(self._update_active, ['active'])
        self.param.watch(self._update_cards, self._synced_properties)

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
                self._panels[id(obj)]._cleanup(root)

        params = {k: v for k, v in self.param.get_param_values()
                  if k in self._synced_properties}

        ref = root.ref['id']
        current_objects = list(self)
        for i, (name, pane) in enumerate(zip(self._names, self)):
            params.update(self._apply_style(i))
            if id(pane) in self._panels:
                card = self._panels[id(pane)]
            else:
                card = Card(
                    pane, title=name, css_classes=['accordion'],
                    header_css_classes=['accordion-header'],
                    margin=self.margin
                )
                card.param.watch(self._set_active, ['collapsed'])
                self._panels[id(pane)] = card
            card.param.set_param(**params)
            if ref in card._models:
                panel = card._models[ref][0]
            else:
                try:
                    panel = card._get_model(doc, root, model, comm)
                    if self.toggle:
                        cb = CustomJS(args={'accordion': model}, code=self._toggle)
                        panel.js_on_change('collapsed', cb)
                except RerenderError:
                    return self._get_objects(model, current_objects[:i], doc, root, comm)
            new_models.append(panel)
        self._update_cards()
        self._update_active()
        return new_models

    def _cleanup(self, root):
        for panel in self._panels.values():
            panel._cleanup(root)
        super()._cleanup(root)

    def _apply_style(self, i):
        if i == 0:
            margin = (5, 5, 0, 5)
        elif i == (len(self)-1):
            margin = (0, 5, 5, 5)
        else:
            margin = (0, 5, 0, 5)
        return dict(margin=margin, collapsed = i not in self.active)

    def _set_active(self, *events):
        if self._updating_active:
            return
        self._updating_active = True
        try:
            if self.toggle and not events[0].new:
                active = [list(self._panels.values()).index(events[0].obj)]
            else:
                active = []
                for i, pane in enumerate(self.objects):
                    if id(pane) not in self._panels:
                        continue
                    elif not self._panels[id(pane)].collapsed:
                        active.append(i)
            
            if not self.toggle or active:
                self.active = active
        finally:
            self._updating_active = False

    def _update_active(self, *events):
        if self._updating_active:
            return
        self._updating_active = True
        try:
            for i, pane in enumerate(self.objects):
                if id(pane) not in self._panels:
                    continue
                self._panels[id(pane)].collapsed = i not in self.active
        finally:
            self._updating_active = False

    def _update_cards(self, *events):
        params = {k: v for k, v in self.param.get_param_values()
                  if k in self._synced_properties}
        for panel in self._panels.values():
            panel.param.set_param(**params)
