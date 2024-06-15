"""Functionality to enable easy interaction with Traitlets models and ipywidgets via familiar APIs from Param like watch, bind, depends, and rx.

## Terminology

- **Traitlets**: A library for creating classes (`HasTraits`) with observable attributes (called *traits*).
- **Param**: A library similar to Traitlets, for creating classes (`Parameterized`) with watchable attributes (called *parameters*).
- **ipywidgets**: Builds on Traitlets to create interactive widgets for Jupyter notebooks.
- **widget**: Refers to ipywidgets.
- **model**: Refers to Traitlets classes including ipywidgets.

## Functionality

- `create_parameterized`: Creates a Parameterized object from a model with parameters synced to the model's traits.
- `create_viewer`: Creates a Viewer object from a widget with parameters synced to the widget's traits and displaying the widget when rendered.
- `create_rx`: Creates `rx` values from traits of a model, each synced to a trait of the model.
- `sync_with_parameterized`: Syncs the traits of a model with parameters of a Parameterized object.
- `sync_with_rx`: Syncs a single trait of a model with an `rx` value.

All synchronization is bidirectional.
"""
# I've tried to implement this in a way that would extend to similar APIs for other *model* libraries like dataclasses, Pydantic, attrs etc.
# Todo: Replace widget usage with model usage
# Todo: Supporting specifying names as dicionatry mapping from trait to parameter

from inspect import isclass
from typing import TYPE_CHECKING, Any, Iterable

import param

from param import Parameterized
from param.reactive import bind

from .pane import IPyWidget
from .viewable import Layoutable, Viewer

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


def sync_with_parameterized(model: HasTraits, parameterized: Parameterized, *names):
    """Syncs the traits of the model with the parameters of the Parameterized object bidirectionally.

    Args:
        model: The model to synchronize.
        parameterized: The Parameterized object to synchronize.
        names: The names of the traits/parameters to synchronize. If none are
            specified, all public and relevant traits of the model will be synced.
    """
    # Todo: Support specifying names as dictionary mapping from trait to parameter
    if not names:
        names = _get_public_and_relevant_trait_names(model)

    with param.edit_constant(parameterized):
        for name in names:
            setattr(parameterized, name, getattr(model, name))

    for name in names:
        def _handle_trait_change(_, model=model, parameterized=parameterized, parameter=name):
            with param.edit_constant(parameterized):
                setattr(parameterized, parameter, getattr(model, parameter))
        model.observe(_handle_trait_change, names=name)

        read_only_traits = set()

        def _handle_parameter_change(_, model=model, attribute=name, read_only_traits=read_only_traits):
            if attribute not in read_only_traits:
                try:
                    setattr(model, attribute, getattr(parameterized, attribute))
                except Exception:
                    read_only_traits.add(attribute)

        bind(_handle_parameter_change, parameterized.param[name], watch=True)


class ModelWrapper(Parameterized):
    """An abstract Parameterized base class for wrapping a HasTraits class."""

    _model = param.Parameter(allow_None=False)
    _names = param.Parameter(allow_None=False)

    def __init__(self, **params):
        super().__init__(**params)
        sync_with_parameterized(self._model, self, *self._names)


_cache_of_model_classes = {}


def _to_tuple(bases: None | Parameterized | Iterable[Parameterized]) -> tuple[Parameterized]:
    if not bases:
        bases = ()
    if isclass(bases) and issubclass(bases, Parameterized):
        bases = (bases,)
    return tuple(item for item in bases)


def create_parameterized(model: HasTraits, *names, bases: Iterable[Parameterized] | Parameterized | None = None, **kwargs) -> Parameterized:
    """Returns a Parameterized object from a model with names synced bidirectionally to the model's traits.

    Args:
        model: The model to create the Parameterized object from.
        names: The names of the parameters to add to the Parameterized object and to sync.
            If no names are specified, all public and relevant traits on the model will be added and synchronized.
        bases: Additional base classes to add to the base `IpyWidgetViewer` class.
        kwargs: Additional keyword arguments to pass to the Parameterized constructor.
    """
    # Todo: Support specifying names as dictionary mapping from trait to parameter
    if not names:
        names = _get_public_and_relevant_trait_names(model)
    bases = _to_tuple(bases) + (ModelWrapper,)
    name = type(model).__name__
    key = (name, names, bases)
    if name in _cache_of_model_classes:
        parameterized = _cache_of_model_classes[key]
    else:
        existing_params = ()
        for base in bases:
            existing_params += tuple(base.param)
        params = {
            name: param.Parameterized()
            for name in names
            if name not in existing_params
        }

        parameterized = param.parameterized_class(name, params=params, bases=bases)
        for parameter in params:
            if parameter not in parameterized.param:
                parameterized.param.add_parameter(parameter, param.Parameter())

    _cache_of_model_classes[key] = parameterized
    instance = parameterized(_model=model, _names=names, **kwargs)

    return instance


class WidgetViewer(Layoutable, Viewer):
    """An abstract base class for creating a Layoutable Viewer that wraps an ipywidget Widget."""

    _model = param.Parameter(allow_None=False)

    def __init__(self, **params):
        super().__init__(**params)

        widget = self._model
        if hasattr(widget, "layout"):
            widget.layout.height = "100%"
            widget.layout.width = "100%"
        if not self.width and not self.sizing_mode:
            self.width = 300

        layout_params = {name: self.param[name] for name in Layoutable.param}
        self._layout = IPyWidget(widget, **layout_params)

    def __panel__(self):
        return self._layout


def create_viewer(widget: Widget, *names, bases: Iterable[Parameterized] | Parameterized | None = None, **kwargs) -> Viewer:
    """Returns a Viewer object from a widget with parameters synced bidirectionally to the widget's traits and displaying the widget when rendered.

    Args:
        widget: The widget to create the Viewer from.
        names: The names of the parameters to add to the Viewer and to sync bidirectionally.
            If no names are specified, all public and relevant traits on the widget will be added and synced.
        bases: Additional base classes to add to the base `IpyWidgetViewer` class.
        kwargs: Additional keyword arguments to pass to the Parameterized constructor.
    """
    bases = _to_tuple(bases) + (WidgetViewer,)
    return create_parameterized(widget, *names, bases=bases, **kwargs)


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
    """
    rx_values = []
    for name in names:
        rx = param.rx()
        sync_with_rx(model, name, rx)
        rx_values.append(rx)
    if len(rx_values) == 1:
        return rx_values[0]
    return tuple(rx_values)
