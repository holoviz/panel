"""Functionality to enable easily interacting with ipywidgets via familiar APIs like pn.bind,
@pn.depends and pn.rx"""

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


def sync_parameterized(widget: HasTraits, parameterized: Parameterized, *parameters):
    """Syncs the parameters of the widget and the parameters of the parameterized

    Please note we don't sync to a readonly widget parameter. We do sync to a constant
    parameterized parameter though.

    Args:
        widget: The widget to keep synced
        parameterized: The Parameterized to keep synced
        parameters: The names of the parameters to keep synced. If none are specified all public and
            relevant parameters of the widget will be synced.
    """
    if not parameters:
        parameters = _get_public_and_relevant_trait_names(widget)

    with param.edit_constant(parameterized):
        for parameter in parameters:
            setattr(parameterized, parameter, getattr(widget, parameter))

    for parameter in parameters:
        # Observe widget parameter
        def _handle_widget_change(_, widget=widget, parameter=parameter):
            with param.edit_constant(parameterized):
                setattr(parameterized, parameter, getattr(widget, parameter))
        widget.observe(_handle_widget_change, names=parameter)

        # Bind to parameterized parameter
        read_only = set()

        def _handle_observer_change(_, widget=widget, parameter=parameter, read_only=read_only):
            if parameter not in read_only:
                try:
                    setattr(widget, parameter, getattr(parameterized, parameter))
                except Exception:
                    read_only.add(parameter)

        bind(_handle_observer_change, parameterized.param[parameter], watch=True)

class HasTraitsParameterized(Parameterized):
    """An abstract base class for creating a Parameterized that wraps a HasTraits"""

    _widget = param.Parameter(allow_None=False)
    _parameters = param.Parameter(allow_None=False)

    def __init__(self, **params):
        super().__init__(**params)

        sync_parameterized(self._widget, self, *self._parameters)

_ipywidget_classes = {}


def _to_tuple(
    bases: None | Parameterized | Iterable[Parameterized],
) -> tuple[Parameterized]:
    if not bases:
        bases = ()
    if isclass(bases) and issubclass(bases, Parameterized):
        bases = (bases,)
    return tuple(item for item in bases)


def to_parameterized(
    widget: HasTraits,
    *parameters,
    bases: Iterable[Parameterized] | Parameterized | None = None,
    **kwargs,
) -> Parameterized:
    """Returns a Parameterized object with parameters synced to the ipywidget widget parameters

    Args:
        widget: The ipywidget to create the Viewer from.
        parameters: The parameters to add to the Parameterized and to sync.
            If no parameters are specified all public parameters on the widget will be added
            and synced.
    """
    if not parameters:
        parameters = _get_public_and_relevant_trait_names(widget)
    bases = _to_tuple(bases) + (HasTraitsParameterized,)
    name = type(widget).__name__
    key = (name, parameters, bases)
    if name in _ipywidget_classes:
        parameterized = _ipywidget_classes[key]
    else:
        existing_params = ()
        for base in bases:
            existing_params += tuple(base.param)
        params = {
            name: param.Parameterized()
            for name in parameters
            if name not in existing_params
        }

        parameterized = param.parameterized_class(name, params=params, bases=bases)
        # Todo: Figure out why not all parameters are added
        for parameter in params:
            if parameter not in parameterized.param:
                parameterized.param.add_parameter(parameter, param.Parameter())

    _ipywidget_classes[key] = parameterized
    instance = parameterized(_widget=widget, _parameters=parameters, **kwargs)

    return instance


class IpyWidgetViewer(Layoutable, Viewer):
    """An abstract base class for creating a Layoutable Viewer that wraps an ipywidget"""

    _widget = param.Parameter(allow_None=False)

    def __init__(self, **params):
        super().__init__(**params)

        widget = self._widget
        widget.height = "100%"
        widget.width = "100%"
        layout_params = {name: self.param[name] for name in Layoutable.param}

        self._layout = IPyWidget(widget, **layout_params)

    def __panel__(self):
        return self._layout


def to_viewer(
    widget: Widget,
    *parameters,
    bases: Parameterized | None = None,
    **kwargs,
) -> Viewer:
    """Returns a Parameterized object with parameters synced to the ipywidget widget parameters

    Args:
        widget: The ipywidget to create the Viewer from.
        parameters: The parameters to add to the Parameterized and to sync.
            If no parameters are specified all public parameters on the widget will be added
            and synced.
    """
    bases = _to_tuple(bases) + (IpyWidgetViewer,)

    return to_parameterized(widget, *parameters, bases=bases, **kwargs)


def sync_rx(element: HasTraits, name: str, target: param.rx):
    """Syncs the element name attribute and the target.rx.value"""
    target.rx.value = getattr(element, name)

    def set_value(event, target=target):
        target.rx.value = event["new"]

    element.observe(set_value, names=name)

    def set_name(value, element=element, name=name):
        setattr(element, name, value)

    target.rx.watch(set_name)


def to_rx(widget: HasTraits, *parameters) -> param.rx | tuple[param.rx]:
    """Returns a tuple of `rx` parameters. Each one synced to a parameter of the widget.

    Args:
        widget: The widget to create the `rx` parameters from.
        parameters: The parameter or parameters to create `rx` parameters from and to sync.
            If a single parameter is specified a single reactive parameter is returned.
            If no parameters are specified all public and relevant parameters of the widget will be
            used.
    """
    rx_values = []
    for name in parameters:
        rx = param.rx()
        sync_rx(widget, name, rx)
        rx_values.append(rx)
    if len(rx_values) == 1:
        return rx_values[0]
    return tuple(rx_values)
