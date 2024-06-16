"""Functionality to enable easy interaction with dataclass like instances or classes via familiar APIs from Param like watch, bind, depends, and rx.

## Libraries Supported

- **ipywidgets**: A library for creating interactive widgets for notebooks. Its base class `Widget` derives from traitlets `HasTraitlets`.
- **Pydantic**: A library for creating dataclass like models with very fast validation and serialization.
- **Traitlets**: A library for creating dataclass like models (`HasTraits`) with observable fields (called *traits*).

In the future dataclasses, attrs or other dataclass like libraries may be supported.

## Terminology

- **Param**: A library for creating dataclass like models (`Parameterized`) with watchable attributes (called *parameters*).
- **model**: A child class of one of the libraries listed above.
- **fields**: The attributes of the model class or instance. Derives from `dataclass.field()`.
- **names**: The names of the model attributes/ Parameterized parameters.

## Classes

- `ModelParameterized`: An abstract Parameterized base class for observing a model class or instance.
- `ModelViewer`: An abstract Layoutable Viewer base class for observing a model class or instance.

## Functions

- `create_rx`: Creates `rx` values from fields of a model.
- `sync_with_parameterized`: Syncs the fields of a model with the parameters of a Parameterized object.
- `sync_with_widget`: Syncs an iterable or dictionary of named fields of a model with the named parameters of a Parameterized object.
- `sync_with_rx`: Syncs a single field of a model with an `rx` value.

## Support

| Library | Sync Parameterized -> Model | Sync Model -> Parameterized | `create_rx` | `sync_with_parameterized` | `sync_with_widget` | `sync_with_rx` | `ModelParameterized` | `ModelViewer` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ipywidgets | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Pydantic   | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Traitlets  | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |

""" # noqa: E501
from inspect import isclass
from typing import Any, Iterable

import param

from param import Parameterized

from ._dataclasses.base import ModelUtils
from ._dataclasses.ipywidget import HasTraits, TraitletsUtils
from ._dataclasses.pydantic import BaseModel, PydanticUtils
from .viewable import Layoutable, Viewer
from .widgets import Widget

DataClassLike = HasTraits | BaseModel

def _get_utils(model: DataClassLike)->type[ModelUtils]:
    if hasattr(model, "model_fields"):
        return PydanticUtils
    return TraitletsUtils

def sync_with_parameterized(
    model: DataClassLike,
    parameterized: Parameterized,
    names: Iterable[str] | dict[str, str] = (),
):
    """Syncs the fields of the model with the parameters of the Parameterized object.

    Args:
        model: The model to synchronize.
        parameterized: The Parameterized object to synchronize.
        names: The names of the fields/parameters to synchronize. If none are
            specified, all public and relevant fields of the model will be synced. If a dict is
            specified it maps from field names to parameter names.

    Example:

    ```python
    import panel as pn
    import ipyleaflet as ipyl
    import param

    pn.extension("ipywidgets")

    leaflet_map = ipyl.Map()

    class Map(param.Parameterized):
        center = param.List(default=[52.204793, 360.121558])
        zoom = param.Number(default=4, bounds=(0, 24), step=1)

    parameterized = Map()

    pn.dataclass.sync_with_parameterized(
        model=leaflet_map, parameterized=parameterized
    )
    pn.Column(leaflet_map, parameterized.param.zoom, parameterized.param.center).servable()
    ```

    """
    _get_utils(model).sync_with_parameterized(model, parameterized, names)

def sync_with_widget(
    model: DataClassLike,
    widget: Widget,
    name: str="value",
):
    """Syncs the named field of the model with value parameter of the widget.

    Args:
        model: The model to synchronize.
        widget: The Panel widget to synchronize.
        name: The name of the field to synchronize. Default is 'value'.

    Example:

    ```python
    import panel as pn
    import ipyleaflet as ipyl

    pn.extension("ipywidgets")

    leaflet_map = ipyl.Map()

    zoom_widget = pn.widgets.FloatSlider(value=2.0, start=1.0, end=24.0, name="Zoom")
    zoom_control_widget = pn.widgets.Checkbox(name="Show Zoom Control")

    pn.dataclass.sync_with_widget(leaflet_map, zoom_widget, name="zoom")
    pn.dataclass.sync_with_widget(leaflet_map, zoom_control_widget, name="zoom_control")
    pn.Column(leaflet_map, zoom_widget, zoom_control_widget).servable()
    ```
    """
    sync_with_parameterized(model, widget, names={name: "value"})

class ModelParameterized(Parameterized):
    """An abstract Parameterized base class for wrapping a traitlets HasTraits class or instance."""

    model: DataClassLike = param.Parameter(allow_None=False, constant=True)
    # Todo: consider renaming to names or model_names because it will be used publicly
    _model_names: Iterable[str] | dict[str, str] = ()

    def __init__(self, **params):
        if "model" not in params and hasattr(self, "_model_class"):
            params["model"] = self._model_class()

        model = params["model"]
        names = params.pop("names", self._model_names)
        utils = _get_utils(model)
        if not names:
            names = utils.get_public_and_relevant_field_names(model)
        names = utils.ensure_dict(names)
        self._model_names = names
        for parameter in names.values():
            if parameter not in self.param:
                self.param.add_parameter(parameter, param.Parameter())

        super().__init__(**params)
        utils.sync_with_parameterized(self.model, self, names=names)

_cache_of_model_classes: dict[Any, Parameterized] = {}


def _to_tuple(
    bases: None | Parameterized | Iterable[Parameterized],
) -> tuple[Parameterized]:
    if not bases:
        bases = ()
    if isclass(bases) and issubclass(bases, Parameterized):
        bases = (bases,)
    return tuple(item for item in bases)


def create_parameterized(
    model: HasTraits,
    names: Iterable[str] | dict[str, str] = (),
    bases: Iterable[Parameterized] | Parameterized | None = None,
    **kwargs,
) -> Parameterized:
    """Returns a Parameterized object from a model with names synced bidirectionally to the model's traits.

    Args:
        model: The model to create the Parameterized object from.
        names: The names of the parameters to add to the Parameterized object and to sync.
            If no names are specified, all public and relevant traits on the model will be added and synchronized.
        bases: Additional base classes to add to the base `IpyWidgetViewer` class.
        kwargs: Additional keyword arguments to pass to the Parameterized constructor.
    """
    if not names:
        names = _get_utils(model).get_public_and_relevant_field_names(model)
    names = _get_utils(model).ensure_dict(names)

    bases = _to_tuple(bases) + (ModelParameterized,)
    name = type(model).__name__
    key = (name, tuple(names.items()), bases)
    if name in _cache_of_model_classes:
        parameterized = _cache_of_model_classes[key]
    else:
        existing_params = ()
        for base in bases:
            existing_params += tuple(base.param)
        params = {
            name: param.Parameterized()
            for name in names.values()
            if name not in existing_params
        }
        parameterized = param.parameterized_class(name, params=params, bases=bases)

    _cache_of_model_classes[key] = parameterized
    instance = parameterized(model=model, names=names, **kwargs)

    return instance


class ModelViewer(Layoutable, Viewer, ModelParameterized):
    """An abstract base class for creating a Layoutable Viewer that wraps an ipywidget Widget class or instance.

    Args:
        model: An ipywidget instance to display.
        names: An optional iterable or dictionary of traits/parameters to synchronize. If none are
            specified, all public and relevant traits of the model will be synced. If a dict is
            specified it maps from trait names to parameter names.
        params: Other arguments including model arguments and arguments for layout and styling of the Viewer.

    Examples:

    To wrap a widget instance:

    ```python
    import panel as pn
    import ipyleaflet as ipyl

    pn.extension("ipywidgets")

    leaflet_map = ipyl.Map()

    viewer = pn.dataclass.ModelViewer(
        model=leaflet_map, sizing_mode="stretch_both"
    )
    pn.Row(pn.Column(viewer.param, scroll=True), viewer, height=400).servable()
    ```

    To wrap a widget class:

    ```python
    import panel as pn
    import ipyleaflet as ipyl
    import param

    pn.extension("ipywidgets")


    class MapViewer(pn.dataclass.ModelViewer):
        _model_class = ipyl.Map
        _model_names = ["center", "zoom"]

        zoom = param.Number(4, bounds=(0, 24), step=1)

    viewer = MapViewer(sizing_mode="stretch_both")

    pn.Row(pn.Column(viewer.param, scroll=True), viewer, height=400).servable()
    ```

    The `_model_names` is optional and can be used to specify which traits/ parameters to synchronize.
    """

    model: Widget = param.Parameter(allow_None=False, constant=True)

    def __init__(self, **params):
        super().__init__(**params)

        layout_params = {name: self.param[name] for name in Layoutable.param}
        model = self.model
        utils = _get_utils(self.model)

        self._layout = utils.get_layout(model, self, layout_params)
        utils.adjust_sizing(self)

    def __panel__(self):
        return self._layout


def create_viewer(
    widget: Widget,
    names: Iterable[str] | dict[str, str] = (),
    bases: Iterable[Parameterized] | Parameterized | None = None,
    **kwargs,
) -> ModelViewer:
    """Returns a Viewer object from a widget with parameters synced bidirectionally to the widget's traits and displaying the widget when rendered.

    Args:
        widget: The widget to create the Viewer from.
        names: The names of the parameters to add to the Viewer and to sync bidirectionally.
            If no names are specified, all public and relevant traits on the widget will be added and synced.
        bases: Additional base classes to add to the base `IpyWidgetViewer` class.
        kwargs: Additional keyword arguments to pass to the Parameterized constructor.
    """
    bases = _to_tuple(bases) + (ModelViewer,)
    return create_parameterized(widget, names, bases=bases, **kwargs)


def sync_with_rx(model: HasTraits, name: str, rx: param.rx):
    """Syncs a single trait of a model with an `rx` value.

    Args:
        model: The model to sync with.
        name: The name of the trait to sync the `rx` value with.
        rx: The `rx` value to sync with the trait.
    """
    rx.rx.value = getattr(model, name)

    def set_value(event, rx=rx):
        rx.rx.value = event["new"]

    _get_utils(model).observe_field(model, name, set_value)

    def set_name(value, element=model, name=name):
        setattr(element, name, value)

    rx.rx.watch(set_name)


def create_rx(model: HasTraits, *names) -> param.rx | tuple[param.rx]:
    """Returns `rx` values from traits of a model, each synced to a trait of the model bidirectionally.

    Args:
        model: The model to create the `rx` parameters from.
        names: The traits to create `rx` values from.
            If a single parameter is specified, a single reactive parameter is returned.
            If no names are specified, all public and relevant traits of the model will be used.

    Example:

    ```python
    import panel as pn
    import ipyleaflet as ipyl

    pn.extension("ipywidgets")

    leaflet_map = ipyl.Map(zoom=4)
    zoom, zoom_control = pn.dataclass.create_rx(
        leaflet_map, "zoom", "zoom_control"
    )

    pn.Column(
        leaflet_map,
        zoom.rx.pipe(
            lambda x: f"**Value**: {x}, **Zoom Control**: " + zoom_control.rx.pipe(str)
        ),
    ).servable()
    ```
    """
    rx_values = []
    for name in names:
        rx = param.rx()
        sync_with_rx(model, name, rx)
        rx_values.append(rx)
    if len(rx_values) == 1:
        return rx_values[0]
    return tuple(rx_values)

__all__=["create_rx", "sync_with_parameterized", "sync_with_widget", "sync_with_rx", "ModelParameterized", "ModelViewer"]
