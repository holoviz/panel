"""Functionality to enable easy interaction with Traitlets models and ipywidgets via familiar APIs from Param like watch, bind, depends, and rx.

## Terminology

- **Traitlets**: A library for creating classes (`HasTraits`) with observable attributes (called *traits*).
- **Param**: A library similar to Traitlets, for creating classes (`Parameterized`) with watchable attributes (called *parameters*).
- **ipywidgets**: Builds on Traitlets to create interactive widgets for Jupyter notebooks.
- **widget**: Refers to ipywidgets.
- **model**: Refers to Traitlets classes including ipywidgets.

## Classes

- `ModelParameterized`: An abstract Parameterized base class for wrapping a traitlets HasTraits class or instance.
- `ModelViewer`: An abstract base class for creating a Layoutable Viewer that wraps an ipywidget Widget class or instance.

## Functions

- `create_rx`: Creates `rx` values from traits of a model, each synced to a trait of the model.
- `sync_with_widget`: Syncs the named trait of the model with the value of a Panel widget.
- `sync_with_parameterized`: Syncs the traits of a model with the parameters of a Parameterized object.
- `sync_with_rx`: Syncs a single trait of a model with an `rx` value.

All synchronization is bidirectional. We only synchronize the top-level traits/ parameters and not the nested ones.
"""

# I've tried to implement this in a way that would generalize to similar APIs for other *dataclass like* libraries like dataclasses, Pydantic, attrs etc.

from inspect import isclass
from typing import TYPE_CHECKING, Any, Iterable

import param

from param import Parameterized
from param.reactive import bind

from ..pane import IPyWidget
from ..viewable import Layoutable, Viewer
from ..widgets import Widget as PanelWidget

if TYPE_CHECKING:
    try:
        from traitlets import HasTraits
    except ModuleNotFoundError:
        HasTraits = Any

    try:
        from ipywidgets import Widget
    except ModuleNotFoundError:
        Widget = Any
else:
    HasTraits = Any
    Widget = Any


def _is_custom_trait(name):
    if name.startswith("_"):
        return False
    if name in {"comm", "tabbable", "keys", "log", "layout"}:
        return False
    return True


def _get_public_and_relevant_trait_names(widget):
    return tuple(name for name in widget.traits() if _is_custom_trait(name))


def _ensure_dict(names: Iterable[str] | dict[str, str] = ()) -> dict[str, str]:
    if isinstance(names, dict):
        return names
    return dict(zip(names, names))

def _ensure_exists(model, parameterized, names: dict[str, str])->dict[str,str]:
    return {trait: parameter for trait, parameter in names.items() if trait in model.traits() and parameter in parameterized.param}

def _clean_names(model, parameterized, names: Iterable[str] | dict[str, str])->dict[str,str]:
    if not names:
        names = _get_public_and_relevant_trait_names(model)
    names = _ensure_dict(names)
    return _ensure_exists(model, parameterized, names)

def sync_with_parameterized(
    model: HasTraits,
    parameterized: Parameterized,
    names: Iterable[str] | dict[str, str] = (),
):
    """Syncs the traits of the model with the parameters of the Parameterized object bidirectionally.

    Args:
        model: The model to synchronize.
        parameterized: The Parameterized object to synchronize.
        names: The names of the traits/parameters to synchronize. If none are
            specified, all public and relevant traits of the model will be synced. If a dict is
            specified it maps from trait names to parameter names.

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
    names = _clean_names(model, parameterized, names)

    for trait, parameter in names.items():
        model_trait = getattr(model, trait)
        parameterized_value = getattr(parameterized, parameter)
        if parameter!="name" and parameterized_value is not None:
            try:
                setattr(model, trait, parameterized_value)
            except Exception:
                with param.edit_constant(parameterized):
                    setattr(parameterized, parameter, model_trait)
        else:
            with param.edit_constant(parameterized):
                setattr(parameterized, parameter, model_trait)

        def _handle_trait_change(
            _,
            model=model,
            trait=trait,
            parameterized=parameterized,
            parameter=parameter,
        ):
            with param.edit_constant(parameterized):
                setattr(parameterized, parameter, getattr(model, trait))

        model.observe(_handle_trait_change, names=trait)

        read_only_traits: set[str] = set()

        def _handle_parameter_change(
            _,
            model=model,
            trait=trait,
            parameter=parameter,
            read_only_traits=read_only_traits,
        ):
            if trait not in read_only_traits:
                try:
                    setattr(model, trait, getattr(parameterized, parameter))
                except Exception:
                    read_only_traits.add(trait)

        bind(_handle_parameter_change, parameterized.param[parameter], watch=True)

def sync_with_widget(
    model: HasTraits,
    widget: PanelWidget,
    name: str="value",
):
    """Syncs the named trait of the model with value parameter of the widget.

    Args:
        model: The traitlets or ipywidgets model to synchronize.
        widget: The Panel widget to synchronize.
        name: The name of the trait to synchronize. Default is 'value'.

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

    model: HasTraits = param.Parameter(allow_None=False, constant=True)
    # Todo: consider renaming to names or model_names because it will be used publicly
    _names: Iterable[str] | dict[str, str] = ()

    def __init__(self, **params):
        if "model" not in params and hasattr(self, "_model_class"):
            params["model"] = self._model_class()

        model = params["model"]
        names = params.pop("_names", self._names)
        if not names:
            names = _get_public_and_relevant_trait_names(model)
        names = _ensure_dict(names)
        self._names = names

        for parameter in names.values():
            if parameter not in self.param:
                self.param.add_parameter(parameter, param.Parameter())

        super().__init__(**params)
        sync_with_parameterized(self.model, self, names=self._names)


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
) -> ModelParameterized:
    """Returns a Parameterized object from a model with names synced bidirectionally to the model's traits.

    Args:
        model: The model to create the Parameterized object from.
        names: The names of the parameters to add to the Parameterized object and to sync.
            If no names are specified, all public and relevant traits on the model will be added and synchronized.
        bases: Additional base classes to add to the base `IpyWidgetViewer` class.
        kwargs: Additional keyword arguments to pass to the Parameterized constructor.
    """
    if not names:
        names = _get_public_and_relevant_trait_names(model)
    names = _ensure_dict(names)

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
    instance = parameterized(model=model, _names=names, **kwargs)

    return instance


class ModelViewer(Layoutable, Viewer, ModelParameterized):
    """An abstract base class for creating a Layoutable Viewer that wraps an ipywidget Widget class or instance.

    Args:
        model: An ipywidget instance to display.
        _names: An optional iterable or dictionary of traits/parameters to synchronize. If none are
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
        _names = ["center", "zoom"]

        zoom = param.Number(4, bounds=(0, 24), step=1)

    viewer = MapViewer(sizing_mode="stretch_both")

    pn.Row(pn.Column(viewer.param, scroll=True), viewer, height=400).servable()
    ```

    The `_names` is optional and can be used to specify which traits/ parameters to synchronize.
    """

    model: Widget = param.Parameter(allow_None=False, constant=True)

    def __init__(self, **params):
        super().__init__(**params)

        widget = self.model
        if hasattr(widget, "layout"):
            widget.layout.height = "100%"
            widget.layout.width = "100%"
        if not self.width and self.sizing_mode not in ["stretch_width", "stretch_both"]:
            self.width = 300

        if not self.height and self.sizing_mode not in [
            "stretch_height",
            "stretch_both",
        ]:
            self.height = 300

        layout_params = {name: self.param[name] for name in Layoutable.param}
        self._layout = IPyWidget(widget, **layout_params)

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

    model.observe(set_value, names=name)

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
