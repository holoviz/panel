from __future__ import annotations

import typing as t

from collections.abc import Iterable, Mapping
from inspect import Parameter
from numbers import Integral, Real

empty = Parameter.empty

import param

from .base import Widget
from .input import Checkbox, TextInput
from .select import Select
from .slider import DiscreteSlider, FloatSlider, IntSlider


class fixed(param.Parameterized):
    """
    A pseudo-widget whose value is fixed and never synced to the client.
    """

    description = param.String(default='')

    value: t.Any = param.Parameter(doc="Any Python object")  # type: ignore[assignment]

    def __init__(self, value: t.Any, **kwargs: t.Any):
        super().__init__(value=value, **kwargs)

    def get_interact_value(self):
        """
        Return the value for this widget which should be passed to
        interactive functions. Custom widgets can change this method
        to process the raw value ``self.value``.
        """
        return self.value


def _get_min_max_value(
    minimum: int | float | None,
    maximum: int | float | None,
    value: int | float | None = None,
    step: int | float | None = None
) -> tuple[int | float, int | float, int | float]:
    """Return min, max, value given input values with possible None."""
    # Either min and max need to be given, or value needs to be given
    if value is None:
        if minimum is None or maximum is None:
            raise ValueError(f'unable to infer range, value from: ({minimum}, {maximum}, {value})')

        min_val, max_val = minimum, maximum
        diff = maximum - minimum
        value = minimum + (diff / 2)
        # Ensure that value has the same type as diff
        if not isinstance(value, type(diff)):
            value = minimum + (diff // 2)
    else:  # value is not None
        if not isinstance(value, Real):
            raise TypeError(f'expected a real number, got: {value!r}')
        # Infer min/max from value
        if value == 0:
            # This gives (0, 1) of the correct type
            vrange = (value, value + 1)
        elif value > 0:
            vrange = (-value, 3*value)
        else:
            vrange = (3*value, -value)
        min_val = vrange[0] if minimum is None else minimum
        max_val = vrange[1] if maximum is None else maximum
    if step is not None:
        # ensure value is on a step
        tick = int((value - min_val) / step)
        value = min_val + tick * step
    if not (min_val <= value <= max_val):
        raise ValueError(f'value must be between min and max (min={min_val}, value={value}, max={max_val})')
    return min_val, max_val, value


def _matches(o: tuple[t.Any, ...], pattern: tuple[type, ...]) -> bool:
    """Match a pattern of types in a sequence."""
    if not len(o) == len(pattern):
        return False
    comps = zip(o, pattern)
    return all(isinstance(obj, kind) for obj, kind in comps)


class widget(param.ParameterizedFunction):
    """
    Attempts to find a widget appropriate for a given value.

    Parameters
    ----------
    name: str
        The name of the resulting widget.
    value: Any
        The value to deduce a widget from.
    default: Any
        The default value for the resulting widget.
    **params: Any
        Additional keyword arguments to pass to the widget.

    Returns
    -------
    Widget
    """

    def __call__(self, value: t.Any, name: str, default=empty, **params):
        """Build a ValueWidget instance given an abbreviation or Widget."""
        if isinstance(value, Widget):
            widget = value
        elif isinstance(value, tuple):
            widget = self.widget_from_tuple(value, name, default)
            if default is not empty:
                try:
                    widget.value = default
                except Exception:
                    # ignore failure to set default
                    pass
        else:
            # Try single value
            widget = self.widget_from_single_value(value, name)

            # Something iterable (list, dict, generator, ...). Note that str and
            # tuple should be handled before, that is why we check this case last.
            if widget is None and isinstance(value, Iterable):
                widget = self.widget_from_iterable(value, name)
                if default is not empty:
                    try:
                        widget.value = default
                    except Exception:
                        # ignore failure to set default
                        pass
        if widget is None:
            widget = fixed(value)
        if params:
            widget.param.update(**params)
        return widget

    @staticmethod
    def widget_from_single_value(o, name):
        """Make widgets from single values, which can be used as parameter defaults."""
        if isinstance(o, str):
            return TextInput(value=str(o), name=name)
        elif isinstance(o, bool):
            return Checkbox(value=o, name=name)
        elif isinstance(o, Integral):
            min, max, value = _get_min_max_value(None, None, o)
            return IntSlider(value=o, start=min, end=max, name=name)
        elif isinstance(o, Real):
            min, max, value = _get_min_max_value(None, None, o)
            return FloatSlider(value=o, start=min, end=max, name=name)
        else:
            return None

    @staticmethod
    def widget_from_tuple(o, name, default=empty):
        """Make widgets from a tuple abbreviation."""
        int_default = (default is empty or isinstance(default, int))
        if _matches(o, (Real, Real)):
            min, max, value = _get_min_max_value(o[0], o[1])
            if all(isinstance(_, Integral) for _ in o) and int_default:
                cls = IntSlider
            else:
                cls = FloatSlider
            return cls(value=value, start=min, end=max, name=name)
        elif _matches(o, (Real, Real, Real)):
            step = o[2]
            if step <= 0:
                raise ValueError(f"step must be >= 0, not {step!r}")
            min, max, value = _get_min_max_value(o[0], o[1], step=step)
            if all(isinstance(_, Integral) for _ in o) and int_default:
                cls = IntSlider
            else:
                cls = FloatSlider
            return cls(value=value, start=min, end=max, step=step, name=name)
        elif _matches(o, (Real, Real, Real, Real)):
            step = o[2]
            if step <= 0:
                raise ValueError(f"step must be >= 0, not {step!r}")
            min, max, value = _get_min_max_value(o[0], o[1], value=o[3], step=step)
            if all(isinstance(_, Integral) for _ in o):
                cls = IntSlider
            else:
                cls = FloatSlider
            return cls(value=value, start=min, end=max, step=step, name=name)
        elif len(o) == 4:
            min, max, value = _get_min_max_value(o[0], o[1], value=o[3])
            if all(isinstance(_, Integral) for _ in [o[0], o[1], o[3]]):
                cls = IntSlider
            else:
                cls = FloatSlider
            return cls(value=value, start=min, end=max, name=name)

    @staticmethod
    def widget_from_iterable(o, name):
        """Make widgets from an iterable. This should not be done for
        a string or tuple."""
        # Select expects a dict or list, so we convert an arbitrary
        # iterable to either of those.
        values = list(o.values()) if isinstance(o, Mapping) else list(o)
        widget_type = DiscreteSlider if all(param._is_number(v) for v in values) else Select
        if isinstance(o, (list, dict)):
            return widget_type(options=o, name=name)
        elif isinstance(o, Mapping):
            return widget_type(options=list(o.items()), name=name)
        else:
            return widget_type(options=list(o), name=name)
