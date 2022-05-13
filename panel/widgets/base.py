"""
Defines the Widget base class which provides bi-directional
communication between the rendered dashboard and the Widget
parameters.
"""
from __future__ import annotations

import math

from typing import (
    TYPE_CHECKING, Any, Callable, List, Mapping, Optional, Tuple
)

import param # type: ignore

from ..layout import Row
from ..reactive import Reactive
from ..viewable import Layoutable, Viewable

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm

    from ..layout import Panel


class Widget(Reactive):
    """
    Widgets allow syncing changes in bokeh widget models with the
    parameters on the Widget instance.
    """

    disabled = param.Boolean(default=False, doc="""
       Whether the widget is disabled.""")

    name = param.String(default='')

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    margin = param.Parameter(default=(5, 10), doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""")

    _rename: Mapping[str, str | None] = {'name': 'title'}

    # Whether the widget supports embedding
    _supports_embed: bool = False

    # Declares the Bokeh model type of the widget
    _widget_type: 'Model' = None

    __abstract = True

    def __init__(self, **params):
        if 'name' not in params:
            params['name'] = ''
        if '_supports_embed' in params:
            self._supports_embed = params.pop('_supports_embed')
        if '_param_pane' in params:
            self._param_pane = params.pop('_param_pane')
        else:
            self._param_pane = None
        super().__init__(**params)

    @classmethod
    def from_param(cls, parameter: param.Parameter, **params) -> Viewable:
        """
        Construct a widget from a Parameter and link the two
        bi-directionally.

        Parameters
        ----------
        parameter: param.Parameter
          A parameter to create the widget from.
        params: dict
          Keyword arguments to be passed to the widget constructor

        Returns
        -------
        Widget instance linked to the supplied parameter
        """
        from ..param import Param
        layout = Param(
            parameter, widgets={parameter.name: dict(type=cls, **params)},
            display_threshold=-math.inf
        )
        return layout[0]

    def _get_model(
        self, doc: 'Document', root: Optional['Model'] = None,
        parent: Optional['Model'] = None, comm: Optional['Comm'] = None
    ) -> 'Model':
        model = self._widget_type(**self._process_param_change(self._init_params()))
        if root is None:
            root = model
        # Link parameters and bokeh model
        values = self.param.values()
        properties = self._filter_properties(list(self._process_param_change(values)))
        self._models[root.ref['id']] = (model, parent)
        self._link_props(model, properties, doc, root, comm)
        return model

    def _filter_properties(self, properties: List[str]) -> List[str]:
        ignored = list(Layoutable.param)+['loading']
        return [p for p in properties if p not in ignored]

    def _get_embed_state(
        self, root: 'Model', values: Optional[List[Any]] = None, max_opts: int = 3
    ) -> Tuple['Widget', 'Model', List[Any], Callable[['Model'], Any], str, str]:
        """
        Returns the bokeh model and a discrete set of value states
        for the widget.

        Arguments
        ---------
        root: bokeh.model.Model
          The root model of the widget
        values: list (optional)
          An explicit list of value states to embed
        max_opts: int
          The maximum number of states the widget should return

        Returns
        -------
        widget: panel.widget.Widget
          The Panel widget instance to modify to effect state changes
        model: bokeh.model.Model
          The bokeh model to record the current value state on
        values: list
          A list of value states to explore.
        getter: callable
          A function that returns the state value given the model
        on_change: string
          The name of the widget property to attach a callback on
        js_getter: string
          JS snippet that returns the state value given the model
        """


class CompositeWidget(Widget):
    """
    A baseclass for widgets which are made up of two or more other
    widgets
    """

    _composite_type: 'Panel' = Row

    __abstract = True

    def __init__(self, **params):
        super().__init__(**params)
        layout_params = [p for p in Layoutable.param if p != 'name']
        layout = {p: getattr(self, p) for p in layout_params
                  if getattr(self, p) is not None}
        if layout.get('width', self.width) is None and not 'sizing_mode' in layout:
            layout['sizing_mode'] = 'stretch_width'
        self._composite = self._composite_type(**layout)
        self._models = self._composite._models
        self.param.watch(self._update_layout_params, layout_params)

    def _update_layout_params(self, *events: param.parameterized.Event) -> None:
        updates = {event.name: event.new for event in events}
        self._composite.param.update(**updates)

    def select(
        self, selector: Optional[type | Callable[['Viewable'], bool]] = None
    ) -> List[Viewable]:
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
        for obj in self._composite.objects:
            objects += obj.select(selector)
        return objects

    def _cleanup(self, root: 'Model') -> None:
        self._composite._cleanup(root)
        super()._cleanup(root)

    def _get_model(
        self, doc: 'Document', root: Optional['Model'] = None,
        parent: Optional['Model'] = None, comm: Optional['Comm'] = None
    ) -> 'Model':
        model = self._composite._get_model(doc, root, parent, comm)
        if root is None:
            root = parent = model
        self._models[root.ref['id']] = (model, parent)
        return model

    def __contains__(self, object: Any) -> bool:
        return object in self._composite.objects

    @property
    def _synced_params(self) -> List[str]:
        return []
