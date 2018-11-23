"""
Interact with functions using widgets.

The interact Pane implemented in this module mirrors
ipywidgets.interact in its API and implementation. Large parts of the
code were copied directly from ipywidgets:

Copyright (c) Jupyter Development Team and PyViz Development Team.
Distributed under the terms of the Modified BSD License.
"""
from __future__ import absolute_import

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

from .layout import WidgetBox, Panel, Column, Row
from .pane import PaneBase, Pane
from .util import basestring, as_unicode
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


def _yield_abbreviations_for_parameter(parameter, kwargs):
    """Get an abbreviation for a function parameter."""
    name = parameter.name
    kind = parameter.kind
    ann = parameter.annotation
    default = parameter.default
    not_found = (name, empty, empty)
    if kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY):
        if name in kwargs:
            value = kwargs.pop(name)
        elif ann is not empty:
            param.main.warning("Using function annotations to implicitly specify interactive controls is deprecated. Use an explicit keyword argument for the parameter instead.", DeprecationWarning)
            value = ann
        elif default is not empty:
            value = default
            if isinstance(value, (Iterable, Mapping)):
                value = fixed(value)
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


class interactive(PaneBase):

    default_layout = param.ClassSelector(default=Column, class_=(Panel),
                                         is_instance=False)

    manual_update = param.Boolean(default=False, doc="""
        Whether to update manually by clicking on button.""")

    manual_name = param.String(default='Run Interact')

    def __init__(self, object, params={}, **kwargs):
        super(interactive, self).__init__(object, **params)

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

        widgets = self.widgets_from_abbreviations(new_kwargs)
        if self.manual_update:
            widgets.append(('manual', Button(name=self.manual_name)))
        self._widgets = OrderedDict(widgets)
        self._pane = Pane(self.object(**self.kwargs), name=self.name,
                          _temporary=True)
        self._inner_layout = Row(self._pane)
        self.widget_box = WidgetBox(*(widget for _, widget in widgets
                                      if isinstance(widget, Widget)))
        self.layout.objects = [self.widget_box, self._inner_layout]
        self._link_widgets()

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

        for parameter in sig.parameters.values():
            for name, value, default in _yield_abbreviations_for_parameter(parameter, kwargs):
                if value is empty:
                    raise ValueError('cannot find widget or abbreviation for argument: {!r}'.format(name))
                new_kwargs.append((name, value, default))
        return new_kwargs

    def _get_model(self, doc, root=None, parent=None, comm=None):
        layout = self._inner_layout._get_model(doc, root, parent, comm)
        return layout

    def _link_widgets(self):
        if self.manual_update:
            widgets = [('manual', self._widgets['manual'])]
        else:
            widgets = self._widgets.items()

        for name, widget in widgets:
            def update_pane(change):
                # Try updating existing pane
                new_object = self.object(**self.kwargs)
                pane_type = self.get_pane_type(new_object)
                if type(self._pane) is pane_type:
                    if isinstance(new_object, (PaneBase, Panel)):
                        new_params = {k: v for k, v in new_object.get_param_values()
                                      if k != 'name'}
                        try:
                            self._pane.set_param(**new_params)
                        except:
                            raise
                        finally:
                            new_object._cleanup(final=new_object._temporary)
                    else:
                        self._pane.object = new_object
                    return

                # Replace pane entirely
                self._pane = Pane(new_object, _temporary=True)
                self._inner_layout[0] = self._pane

            pname = 'clicks' if name == 'manual' else 'value'
            watcher = widget.param.watch(update_pane, pname)
            self._callbacks['instance'].append(watcher)

    def _cleanup(self, root=None, final=False):
        self._inner_layout._cleanup(root, final)
        super(interactive, self)._cleanup(root, final)

    def widgets_from_abbreviations(self, seq):
        """Given a sequence of (name, abbrev, default) tuples, return a sequence of Widgets."""
        result = []
        for name, abbrev, default in seq:
            if isinstance(abbrev, fixed):
                widget = abbrev
            else:
                widget = self.widget_from_abbrev(abbrev, name, default)
            if not (isinstance(widget, Widget) or isinstance(widget, fixed)):
                if widget is None:
                    continue
                else:
                    raise TypeError("{!r} is not a ValueWidget".format(widget))
            result.append((name, widget))
        return result

    @classmethod
    def applies(cls, object):
        return isinstance(object, types.FunctionType)

    @classmethod    
    def widget_from_abbrev(cls, abbrev, name, default=empty):
        """Build a ValueWidget instance given an abbreviation or Widget."""
        if isinstance(abbrev, Widget):
            return abbrev

        if isinstance(abbrev, tuple):
            widget = cls.widget_from_tuple(abbrev, name, default)
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
            return TextInput(value=as_unicode(o), name=name)
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
                raise ValueError("step must be >= 0, not %r" % step)
            min, max, value = _get_min_max_value(o[0], o[1], step=step)
            if all(isinstance(_, Integral) for _ in o) and int_default:
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
        if isinstance(o, (list, dict)):
            return widget_type(options=o, name=name)
        elif isinstance(o, Mapping):
            return widget_type(options=list(o.items()), name=name)
        else:
            return widget_type(options=list(o), name=name)

    # Return a factory for interactive functions
    @classmethod
    def factory(cls):
        options = dict(manual_update=False, manual_name="Run Interact")
        return _InteractFactory(cls, options)


class _InteractFactory(object):
    """
    Factory for instances of :class:`interactive`.

    Parameters
    ----------
    cls : class
        The subclass of :class:`interactive` to construct.
    options : dict
        A dict of options used to construct the interactive
        function. By default, this is returned by
        ``cls.default_options()``.
    kwargs : dict
        A dict of **kwargs to use for widgets.
    """
    def __init__(self, cls, options, kwargs={}):
        self.cls = cls
        self.opts = options
        self.kwargs = kwargs

    def widget(self, f):
        """
        Return an interactive function widget for the given function.
        The widget is only constructed, not displayed nor attached to
        the function.
        Returns
        -------
        An instance of ``self.cls`` (typically :class:`interactive`).
        Parameters
        ----------
        f : function
            The function to which the interactive widgets are tied.
        """
        return self.cls(f, self.opts, **self.kwargs)

    def __call__(self, __interact_f=None, **kwargs):
        """
        Make the given function interactive by adding and displaying
        the corresponding :class:`interactive` widget.
        Expects the first argument to be a function. Parameters to this
        function are widget abbreviations passed in as keyword arguments
        (``**kwargs``). Can be used as a decorator (see examples).
        Returns
        -------
        f : __interact_f with interactive widget attached to it.
        Parameters
        ----------
        __interact_f : function
            The function to which the interactive widgets are tied. The `**kwargs`
            should match the function signature. Passed to :func:`interactive()`
        **kwargs : various, optional
            An interactive widget is created for each keyword argument that is a
            valid widget abbreviation. Passed to :func:`interactive()`
        Examples
        --------
        Render an interactive text field that shows the greeting with the passed in
        text::
            # 1. Using interact as a function
            def greeting(text="World"):
                print("Hello {}".format(text))
            interact(greeting, text="IPython Widgets")
            # 2. Using interact as a decorator
            @interact
            def greeting(text="World"):
                print("Hello {}".format(text))
            # 3. Using interact as a decorator with named parameters
            @interact(text="IPython Widgets")
            def greeting(text="World"):
                print("Hello {}".format(text))
        Render an interactive slider widget and prints square of number::
            # 1. Using interact as a function
            def square(num=1):
                print("{} squared is {}".format(num, num*num))
            interact(square, num=5)
            # 2. Using interact as a decorator
            @interact
            def square(num=2):
                print("{} squared is {}".format(num, num*num))
            # 3. Using interact as a decorator with named parameters
            @interact(num=5)
            def square(num=2):
                print("{} squared is {}".format(num, num*num))
        """
        # If kwargs are given, replace self by a new
        # _InteractFactory with the updated kwargs
        if kwargs:
            params = interactive.params()
            kw = dict(self.kwargs)
            kw.update({k: v for k, v in kwargs.items() if k not in params})
            opts = dict(self.opts, **{k: v for k, v in kwargs.items() if k in params})
            self = type(self)(self.cls, opts, kw)

        f = __interact_f
        if f is None:
            # This branch handles the case 3
            # @interact(a=30, b=40)
            # def f(*args, **kwargs):
            #     ...
            #
            # Simply return the new factory
            return self

        # positional arg support in: https://gist.github.com/8851331
        # Handle the cases 1 and 2
        # 1. interact(f, **kwargs)
        # 2. @interact
        #    def f(*args, **kwargs):
        #        ...
        w = self.widget(f)
        try:
            f.widget = w
        except AttributeError:
            # some things (instancemethods) can't have attributes attached,
            # so wrap in a lambda
            f = lambda *args, **kwargs: __interact_f(*args, **kwargs)
            f.widget = w
        return w.layout

    def options(self, **kwds):
        """
        Change options for interactive functions.
        Returns
        -------
        A new :class:`_InteractFactory` which will apply the
        options when called.
        """
        opts = dict(self.opts)
        for k in kwds:
            if k not in opts:
                raise ValueError("invalid option {!r}".format(k))
            opts[k] = kwds[k]
        return type(self)(self.cls, opts, self.kwargs)


interact = interactive.factory()
interact_manual = interact.options(manual_update=True, manual_name="Run Interact")


class fixed(param.Parameterized):
    """A pseudo-widget whose value is fixed and never synced to the client."""
    value = param.Parameter(doc="Any Python object")
    description = param.String(default='')

    def __init__(self, value, **kwargs):
        super(fixed, self).__init__(value=value, **kwargs)

    def get_interact_value(self):
        """Return the value for this widget which should be passed to
        interactive functions. Custom widgets can change this method
        to process the raw value ``self.value``.
        """
        return self.value
