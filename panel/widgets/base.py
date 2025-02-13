"""
Defines the Widget base class which provides bi-directional
communication between the rendered dashboard and the Widget
parameters.
"""
from __future__ import annotations

import math

from collections.abc import Callable, Mapping
from typing import (
    TYPE_CHECKING, Any, ClassVar, TypeVar,
)

import numpy as np
import param  # type: ignore

from bokeh.models import ImportedStyleSheet, Tooltip
from bokeh.models.dom import HTML
from param.parameterized import register_reference_transform

from .._param import Margin
from ..layout.base import Row
from ..reactive import Reactive
from ..util import unique_iterator
from ..viewable import Layoutable, Viewable

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm

    from ..layout.base import ListPanel

    T = TypeVar('T')


class WidgetBase(param.Parameterized):
    """
    WidgetBase provides an abstract baseclass for widget components
    which can be used to implement a custom widget-like type without
    implementing the methods associated with a Reactive Panel component,
    e.g. it may be used as a mix-in to a PyComponent or JSComponent.
    """

    value = param.Parameter(allow_None=True, doc="""
        The widget value which the widget type resolves to when used
        as a reactive param reference.""")

    __abstract = True

    @classmethod
    def from_param(cls: type[T], parameter: param.Parameter, **params) -> T:
        """
        Construct a widget from a Parameter and link the two
        bi-directionally.

        Parameters
        ----------
        parameter: param.Parameter
          A parameter to create the widget from.

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

    @classmethod
    def _infer_params(cls, values, **params):
        if 'name' not in params and getattr(values, 'name', None):
            params['name'] = values.name
        if 'start' in cls.param and 'start' not in params:
            params['start'] = np.nanmin(values)
        if 'end' in cls.param and 'end' not in params:
            params['end'] = np.nanmax(values)
        if 'options' in cls.param and 'options' not in params:
            if isinstance(values, dict):
                params['options'] = values
            else:
                params['options'] = list(unique_iterator(values))
        if 'value' not in params:
            p = cls.param['value']
            if isinstance(p, param.Tuple):
                params['value'] = (params['start'], params['end'])
            elif 'start' in params:
                params['value'] = params['start']
            elif ('options' in params and not isinstance(p, (param.List, param.ListSelector))
                  and not getattr(cls, '_allows_none', False)):
                params['value'] = params['options'][0]
        return params

    @classmethod
    def from_values(cls, values, **params):
        """
        Creates an instance of this Widget where the parameters are
        inferred from the data.

        Parameters
        ----------
        values: Iterable
            The values to infer the parameters from.
        params: dict
            Additional parameters to pass to the widget.
        """
        return cls(**cls._infer_params(values, **params))

    @property
    def rx(self):
        return self.param.value.rx


class Widget(Reactive, WidgetBase):
    """
    Widgets allow syncing changes in bokeh widget models with the
    parameters on the Widget instance.
    """

    disabled = param.Boolean(default=False, doc="""
       Whether the widget is disabled.""")

    name = param.String(default='', constant=False)

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    margin = Margin(default=(5, 10), doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""")

    _rename: ClassVar[Mapping[str, str | None]] = {'name': 'title'}

    # Whether the widget supports embedding
    _supports_embed: bool = False

    # Declares the Bokeh model type of the widget
    _widget_type: ClassVar[type[Model] | None] = None

    __abstract = True

    def __init__(self, **params: Any):
        if 'name' not in params:
            params['name'] = ''
        if '_supports_embed' in params:
            self._supports_embed = params.pop('_supports_embed')
        if '_param_pane' in params:
            self._param_pane = params.pop('_param_pane')
        else:
            self._param_pane = None
        super().__init__(**params)

    @property
    def _linked_properties(self) -> tuple[str, ...]:
        props = list(super()._linked_properties)
        if 'description' in props:
            props.remove('description')
        return tuple(props)

    def _process_param_change(self, params: dict[str, Any]) -> dict[str, Any]:
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
                parser = Markdown._get_parser('markdown-it', (), Markdown.hard_line_break, **renderer_options)
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
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        if self._widget_type is None:
            raise NotImplementedError(
                'Widget {type(self).__name__} did not define a _widget_type'
            )
        model = self._widget_type(**self._get_properties(doc))
        root = root or model
        self._models[root.ref['id']] = (model, parent)
        self._link_props(model, self._linked_properties, doc, root, comm)
        return model

    def _get_embed_state(
        self, root: Model, values: list[Any] | None = None, max_opts: int = 3
    ) -> tuple[Widget, Model, list[Any], Callable[[Model], Any], str, str]:
        """
        Returns the bokeh model and a discrete set of value states
        for the widget.

        Parameters
        ----------
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
        raise NotImplementedError()


class CompositeWidget(Widget):
    """
    A baseclass for widgets which are made up of two or more other
    widgets
    """

    _composite_type: ClassVar[type[ListPanel]] = Row

    _linked_properties: tuple[str, ...] = ()

    __abstract = True

    def __init__(self, **params):
        self._composite = self._composite_type()
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
        self._composite.param.update(**layout)
        self._models = self._composite._models
        self._internal_callbacks.append(
            self.param.watch(self._update_layout_params, layout_params)
        )

    def _update_layout_params(self, *events: param.parameterized.Event) -> None:
        updates = {event.name: event.new for event in events}
        self._composite.param.update(**updates)

    def select(
        self, selector: type | Callable[[Viewable], bool] | None = None
    ) -> list[Viewable]:
        """
        Iterates over the Viewable and any potential children in the
        applying the Selector.

        Parameters
        ----------
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
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        model = self._composite._get_model(doc, root, parent, comm)
        root = model if root is None else root
        self._models[root.ref['id']] = (model, parent)
        return model

    def __contains__(self, object: Any) -> bool:
        return object in self._composite.objects

    @property
    def _synced_params(self) -> list[str]:
        return []


def _widget_transform(obj):
    return obj.param.value if isinstance(obj, WidgetBase) else obj

register_reference_transform(_widget_transform)
