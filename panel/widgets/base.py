"""
Defines the Widget base class which provides bi-directional
communication between the rendered dashboard and the Widget
parameters.
"""
from __future__ import annotations

import math

from typing import (
    TYPE_CHECKING, Any, Callable, ClassVar, Dict, List, Mapping, Optional,
    Tuple, Type,
)

import param  # type: ignore

from bokeh.models import ImportedStyleSheet, Tooltip
from bokeh.models.dom import HTML

from .._param import Margin
from ..layout.base import Row
from ..reactive import Reactive
from ..viewable import Layoutable, Viewable

if TYPE_CHECKING:

    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm
    from typing_extensions import Self

    from ..layout.base import ListPanel


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

    margin = Margin(default=(5, 10), doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""")

    _rename: ClassVar[Mapping[str, str | None]] = {'name': 'title'}

    # Whether the widget supports embedding
    _supports_embed: ClassVar[bool] = False

    # Declares the Bokeh model type of the widget
    _widget_type: ClassVar[Type[Model] | None] = None

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
    def from_param(cls, parameter: param.Parameter, **params) -> Self:
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

    @property
    def _linked_properties(self) -> Tuple[str]:
        props = list(super()._linked_properties)
        if 'description' in props:
            props.remove('description')
        return tuple(props)

    def _process_param_change(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params = super()._process_param_change(params)
        if self._widget_type is not None and 'stylesheets' in params:
            css = getattr(self._widget_type, '__css__', [])
            params['stylesheets'] = [
                ImportedStyleSheet(url=ss) for ss in css
            ] + params['stylesheets']
        if "description" in params:
            description = params["description"]
            renderer_options = params.pop("renderer_options", {})
            if isinstance(description, str):
                from ..pane.markup import Markdown
                parser = Markdown._get_parser('markdown-it', (), **renderer_options)
                html = parser.render(description)
                params['description'] = Tooltip(
                    content=HTML(html), position='right',
                    stylesheets=[':host { white-space: initial; max-width: 300px; }'],
                    syncable=False
                )
            elif isinstance(description, Tooltip):
                description.syncable = False
        return params

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        model = self._widget_type(**self._get_properties(doc))
        root = root or model
        self._models[root.ref['id']] = (model, parent)
        self._link_props(model, self._linked_properties, doc, root, comm)
        return model

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

    _composite_type: ClassVar[Type[ListPanel]] = Row

    _linked_properties: ClassVar[Tuple[str]] = ()

    __abstract = True

    def __init__(self, **params):
        super().__init__(**params)
        layout_params = [p for p in Layoutable.param if p != 'name']
        layout = {p: getattr(self, p) for p in layout_params
                  if getattr(self, p) is not None}
        if layout.get('width', self.width) is None and 'sizing_mode' not in layout:
            layout['sizing_mode'] = 'stretch_width'
        if layout.get('sizing_mode') not in (None, 'fixed') and layout.get('width'):
            min_width = layout.pop('width')
            if not layout.get('min_width'):
                layout['min_width'] = min_width
        self._composite = self._composite_type(**layout)
        self._models = self._composite._models
        self._internal_callbacks.append(
            self.param.watch(self._update_layout_params, layout_params)
        )

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

    def _cleanup(self, root: Model | None = None) -> None:
        self._composite._cleanup(root)
        super()._cleanup(root)

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        model = self._composite._get_model(doc, root, parent, comm)
        root = root or model
        self._models[root.ref['id']] = (model, parent)
        return model

    def __contains__(self, object: Any) -> bool:
        return object in self._composite.objects

    @property
    def _synced_params(self) -> List[str]:
        return []
