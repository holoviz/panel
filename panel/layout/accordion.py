from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, ClassVar

import param

from bokeh.models import Column as BkColumn, CustomJS

from ..reactive import Reactive
from .base import NamedListPanel
from .card import Card

if TYPE_CHECKING:
    from bokeh.model import Model

    from ..viewable import Viewable


class Accordion(NamedListPanel):
    """
    The `Accordion` layout is a type of `Card` layout that allows switching
    between multiple objects by clicking on the corresponding card header.

    The labels for each card will default to the `name` parameter of the card’s
    contents, but may also be defined explicitly as part of a tuple.

    Like `Column` and `Row`, `Accordion` has a list-like API that allows
    interactively updating and modifying the cards using the methods `append`,
    `extend`, `clear`, `insert`, `pop`, `remove` and `__setitem__`.

    Reference: https://panel.holoviz.org/reference/layouts/Accordion.html

    :Example:

    >>> pn.Accordion(some_pane_with_a_name, ("Plot", some_plot))
    """

    active_header_background = param.String(default=None, doc="""
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

    _direction: ClassVar[str | None] = 'vertical'

    _rename: ClassVar[Mapping[str, str | None]] = {
        'active': None, 'active_header_background': None,
        'header_background': None, 'objects': 'children',
        'dynamic': None, 'toggle': None, 'header_color': None
    }

    _toggle = """
    for (var child of accordion.children) {
      if ((child.id !== cb_obj.id) && (child.collapsed == cb_obj.collapsed) && !cb_obj.collapsed) {
        child.collapsed = !cb_obj.collapsed
      }
    }
    """

    _synced_properties = [
        'active_header_background', 'header_background', 'width',
        'sizing_mode', 'width_policy', 'height_policy', 'header_color',
        'min_width', 'max_width'
    ]

    def __init__(self, *objects, **params):
        super().__init__(*objects, **params)
        self._panels = {}
        self._updating_active = False
        self.param.watch(self._update_active, ['active'])
        self.param.watch(self._update_cards, self._synced_properties)

    def _process_property_change(self, props):
        props.pop('children', None)
        return super()._process_property_change(props)

    def _get_objects(self, model, old_objects, doc, root, comm=None):
        """
        Returns new child models for the layout while reusing unchanged
        models and cleaning up any dropped objects.
        """
        from panel.pane.base import RerenderError, panel
        new_models, old_models = [], []
        if len(self._names) != len(self):
            raise ValueError(
                'Accordion names do not match objects, ensure that the '
                'Accordion.objects are not modified directly. Found '
                f'{len(self._names)} names, expected {len(self)}.'
            )
        for i, (name, pane) in enumerate(zip(self._names, self)):
            pane = panel(pane, name=name)
            self.objects[i] = pane

        for obj in old_objects:
            if obj not in self.objects and id(obj) in self._panels:
                self._panels[id(obj)]._cleanup(root)
                del self._panels[id(obj)]

        params = {
            k: v for k, v in self.param.values().items()
            if k in self._synced_properties
        }

        ref = root.ref['id']
        current_objects = list(self)
        self._updating_active = True
        for i, (name, pane) in enumerate(zip(self._names, self)):
            child_params = dict(params, title=name)
            child_params.update(self._apply_style(i))
            if id(pane) in self._panels:
                card = self._panels[id(pane)]
                card.param.update(**child_params)
            else:
                card = Card(
                    pane,
                    css_classes=['accordion'],
                    header_css_classes=['accordion-header'],
                    **child_params
                )
                card.param.watch(self._set_active, ['collapsed'])
                self._panels[id(pane)] = card
            if ref in card._models:
                panel = card._models[ref][0]
                old_models.append(panel)
            else:
                try:
                    panel = card._get_model(doc, root, model, comm)
                    if self.toggle:
                        cb = CustomJS(args={'accordion': model}, code=self._toggle)
                        panel.js_on_change('collapsed', cb)
                except RerenderError as e:
                    if e.layout is not None and e.layout is not self:
                        raise e
                    e.layout = None
                    return self._get_objects(
                        model, current_objects[:i], doc, root, comm
                    )
            new_models.append(panel)

        self._updating_active = False
        self._set_active()
        self._update_cards()
        self._update_active()
        return new_models, old_models

    def _compute_sizing_mode(self, children, props):
        children = [subchild for child in children for subchild in child.children[1:]]
        return super()._compute_sizing_mode(children, props)

    def _cleanup(self, root: Model | None = None) -> None:
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
            if self.toggle and events and not events[0].new:
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
        params = {
            k: v for k, v in self.param.values().items()
            if k in self._synced_properties
        }
        for panel in self._panels.values():
            panel.param.update(**params)

    # Public API

    def select(
        self, selector: type | Callable[[Viewable], bool] | None = None
    ) -> list[Viewable]:
        selected = Reactive.select(self, selector)
        if self._panels:
            for card in self._panels.values():
                selected += card.select(selector)
            return selected
        return selected
