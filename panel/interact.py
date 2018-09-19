"""
Interact with functions using widgets.

The interact Pane implemented in this module mirrors
ipywidgets.interact in its API and implementation. Large parts of the
code were copied directly from ipywidgets:

Copyright (c) Jupyter Development Team and PyViz Development Team.
Distributed under the terms of the Modified BSD License.
"""

import types
from numbers import Real, Integral
from collections import Iterable, Mapping, OrderedDict
from inspect import getcallargs

try:  # Python >= 3.3
    from inspect import signature, Parameter
except ImportError:
    from IPython.utils.signatures import signature, Parameter

try:
    from inspect import getfullargspec as check_argspec
except ImportError:
    from inspect import getargspec as check_argspec # py2

empty = Parameter.empty

import param

from .layout import WidgetBox, Layout, Column
from .pane import PaneBase, Pane
from .util import basestring
from .widgets import (Checkbox, TextInput, Widget, IntSlider, FloatSlider,
                      Select, DiscreteSlider, Button)


def _get_min_max_value(min, max, value=None, step=None):
    """Return min, max, value given input values with possible None."""
    # Either min and max need to be given, or value needs to be given
    if value is None:
        if min is None or max is None:
            raise ValueError('unable to infer range, value from: ({0}, {1}, {2})'.format(min, max, value))
        diff = max - min
        value = min + (diff / 2)
        # Ensure that value has the same type as diff
        if not isinstance(value, type(diff)):
            value = min + (diff // 2)
    else:  # value is not None
        if not isinstance(value, Real):
            raise TypeError('expected a real number, got: %r' % value)
        # Infer min/max from value
        if value == 0:
            # This gives (0, 1) of the correct type
            vrange = (value, value + 1)
        elif value > 0:
            vrange = (-value, 3*value)
        else:
            vrange = (3*value, -value)
        if min is None:
            min = vrange[0]
        if max is None:
            max = vrange[1]
    if step is not None:
        # ensure value is on a step
        tick = int((value - min) / step)
        value = min + tick * step
    if not min <= value <= max:
        raise ValueError('value must be between min and max (min={0}, value={1}, max={2})'.format(min, value, max))
    return min, max, value


def _yield_abbreviations_for_parameter(param, kwargs):
    """Get an abbreviation for a function parameter."""
    name = param.name
    kind = param.kind
    ann = param.annotation
    default = param.default
    not_found = (name, empty, empty)
    if kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY):
        if name in kwargs:
            value = kwargs.pop(name)
        elif ann is not empty:
            warn("Using function annotations to implicitly specify interactive controls is deprecated. Use an explicit keyword argument for the parameter instead.", DeprecationWarning)
            value = ann
        elif default is not empty:
            value = default
        else:
            yield not_found
        yield (name, value, default)
    elif kind == Parameter.VAR_KEYWORD:
        # In this case name=kwargs and we yield the items in kwargs with their keys.
        for k, v in kwargs.copy().items():
            kwargs.pop(k)
            yield k, v, empty


def _matches(o, pattern):
    """Match a pattern of types in a sequence."""
    if not len(o) == len(pattern):
        return False
    comps = zip(o,pattern)
    return all(isinstance(obj,kind) for obj,kind in comps)


class interact(PaneBase):

    layout = param.ClassSelector(default=Column, class_=Layout, is_instance=False)

    manual = param.Boolean(default=False, doc="""
        Whether to update manually by clicking on button.""")

    manual_name = param.String(default='Run Interact')

    def __init__(self, object, **kwargs):
        params = {k: v for k, v in kwargs.items() if k in self.params()}
        kwargs = {k: v for k, v in kwargs.items() if k not in params}
        super(interact, self).__init__(object, **params)

        new_kwargs = self.find_abbreviations(kwargs)
        # Before we proceed, let's make sure that the user has passed a set of args+kwargs
        # that will lead to a valid call of the function. This protects against unspecified
        # and doubly-specified arguments.
        try:
            check_argspec(object)
        except TypeError:
            # if we can't inspect, we can't validate
            pass
        else:
            getcallargs(object, **{n:v for n,v,_ in new_kwargs})

        widgets = [(k, self.widget_from_abbrev(v, k)) for k, v, _ in new_kwargs]
        if self.manual:
            widgets.append(('manual', Button(name=self.manual_name)))
        self._widgets = OrderedDict(widgets)
        self._pane = Pane(self.object(**self.kwargs), name=self.name,
                          _temporary=True)
        self._widget_box = WidgetBox(*(widget for _, widget in widgets))
        self._layout = self.layout(self._widget_box, self._pane)

    @property
    def kwargs(self):
        return {k: widget.value for k, widget in self._widgets.items()
                if k != 'manual'}

    def signature(self):
        return signature(self.object)

    def find_abbreviations(self, kwargs):
        """Find the abbreviations for the given function and kwargs.
        Return (name, abbrev, default) tuples.
        """
        new_kwargs = []
        try:
            sig = self.signature()
        except (ValueError, TypeError):
            # can't inspect, no info from function; only use kwargs
            return [ (key, value, value) for key, value in kwargs.items() ]

        for param in sig.parameters.values():
            for name, value, default in _yield_abbreviations_for_parameter(param, kwargs):
                if value is empty:
                    raise ValueError('cannot find widget or abbreviation for argument: {!r}'.format(name))
                new_kwargs.append((name, value, default))
        return new_kwargs

    def _get_model(self, doc, root=None, parent=None, comm=None):
        layout = self._layout._get_model(doc, root, parent, comm)
        self._link_widgets(layout, doc, root, parent, comm)
        return layout

    def _link_widgets(self, layout, doc, root, parent, comm):
        history = [layout.children[1]]
        if self.manual:
            widgets = [('manual', self._widgets['manual'])]
        else:
            widgets = self._widgets.items()

        for name, widget in widgets:
            def update_pane(change, history=history):
                if change.what != 'value': return

                # Try updating existing pane
                old_model = history[0]
                new_object = self.object(**self.kwargs)
                pane_type = self.get_pane_type(new_object)
                if type(self._pane) is pane_type:
                    if isinstance(new_object, PaneBase):
                        new_params = {k: v for k, v in new_object.get_param_values()
                                      if k != 'name'}
                        self._pane.set_param(**new_params)
                        new_object._cleanup(None, final=True)
                    else:
                        self._pane.object = new_object
                    return

                # Replace pane entirely
                self._pane._cleanup(old_model)
                self._pane = Pane(new_object, _temporary=True, **self._kwargs)
                new_model = self._pane._get_model(doc, root, parent, comm)
                def update_models():
                    if old_model is new_model: return
                    index = layout.children.index(old_model)
                    layout.children[index] = new_model
                    history[0] = new_model

                if comm:
                    update_models()
                    push(doc, comm)
                else:
                    doc.add_next_tick_callback(update_models)

            widget.param.watch(update_pane, 'clicks' if name == 'manual' else 'value')

    @classmethod
    def applies(cls, object):
        return isinstance(object, types.FunctionType)

    @classmethod    
    def widget_from_abbrev(cls, abbrev, name, default=empty):
        """Build a ValueWidget instance given an abbreviation or Widget."""
        if isinstance(abbrev, Widget):
            return abbrev

        if isinstance(abbrev, tuple):
            widget = cls.widget_from_tuple(abbrev, name)
            if default is not empty:
                try:
                    widget.value = default
                except Exception:
                    # ignore failure to set default
                    pass
            return widget

        # Try single value
        widget = cls.widget_from_single_value(abbrev, name)
        if widget is not None:
            return widget

        # Something iterable (list, dict, generator, ...). Note that str and
        # tuple should be handled before, that is why we check this case last.
        if isinstance(abbrev, Iterable):
            widget = cls.widget_from_iterable(abbrev, name)
            if default is not empty:
                try:
                    widget.value = default
                except Exception:
                    # ignore failure to set default
                    pass
            return widget

        # No idea...
        return None

    @staticmethod
    def widget_from_single_value(o, name):
        """Make widgets from single values, which can be used as parameter defaults."""
        if isinstance(o, basestring):
            return TextInput(value=unicode_type(o), name=name)
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
    def widget_from_tuple(o, name):
        """Make widgets from a tuple abbreviation."""
        if _matches(o, (Real, Real)):
            min, max, value = _get_min_max_value(o[0], o[1])
            if all(isinstance(_, Integral) for _ in o):
                cls = IntSlider
            else:
                cls = FloatSlider
            return cls(value=value, start=min, end=max, name=name)
        elif _matches(o, (Real, Real, Real)):
            step = o[2]
            if step <= 0:
                raise ValueError("step must be >= 0, not %r" % step)
            min, max, value = _get_min_max_value(o[0], o[1], step=step)
            if all(isinstance(_, Integral) for _ in o):
                cls = IntSlider
            else:
                cls = FloatSlider
            return cls(value=value, start=min, end=max, step=step, name=name)

    @staticmethod
    def widget_from_iterable(o, name):
        """Make widgets from an iterable. This should not be done for
        a string or tuple."""
        # Select expects a dict or list, so we convert an arbitrary
        # iterable to either of those.
        values = list(o.values()) if isinstance(o, Mapping) else list(o)
        widget_type = DiscreteSlider if all(param._is_number(v) for v in values) else Select
        kws = {'name': name}
        if isinstance(o, (list, dict)):
            return widget_type(options=o, name=name)
        elif isinstance(o, Mapping):
            return widget_type(options=list(o.items()), name=name)
        else:
            return widget_type(options=list(o), name=name)
