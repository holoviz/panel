"""
Interact with functions using widgets.

The interact Pane implemented in this module mirrors
ipywidgets.interact in its API and implementation. Large parts of the
code were copied directly from ipywidgets:

Copyright (c) Jupyter Development Team and PyViz Development Team.
Distributed under the terms of the Modified BSD License.
"""
from __future__ import annotations

import types

from collections.abc import Iterable, Mapping
from inspect import (
    Parameter, getcallargs, getfullargspec as check_argspec, signature,
)
from typing import TYPE_CHECKING, ClassVar

import param

from .layout import Column, Panel, Row
from .pane import HTML, Pane, panel
from .pane.base import ReplacementPane
from .viewable import Viewable
from .widgets import Button, WidgetBase
from .widgets.widget import fixed, widget

if TYPE_CHECKING:
    from bokeh.model import Model

empty = Parameter.empty


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
            param.main.param.warning("Using function annotations to implicitly specify interactive controls is deprecated. "
                               "Use an explicit keyword argument for the parameter instead.", DeprecationWarning)
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


class interactive(Pane):

    default_layout = param.ClassSelector(default=Column, class_=(Panel),
                                         is_instance=False)

    manual_update = param.Boolean(default=False, doc="""
        Whether to update manually by clicking on button.""")

    manual_name = param.String(default='Run Interact')

    _pane = param.ClassSelector(class_=Viewable)

    _rename: ClassVar[Mapping[str, str | None]] = {'_pane': None}

    def __init__(self, object, params={}, **kwargs):
        if signature is None:
            raise ImportError('interact requires either recent Python version '
                              '(>=3.3 or IPython to inspect function signatures.')

        super().__init__(object, **params)

        self.throttled = kwargs.pop('throttled', False)
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
        self._widgets = dict(widgets)
        pane = self.object(**self.kwargs)
        if isinstance(pane, Viewable):
            self._pane = pane
            self._internal = False
        else:
            self._pane = panel(pane, name=self.name)
            self._internal = True
        self._inner_layout = Row(self._pane)
        widgets = [widget for _, widget in widgets if isinstance(widget, WidgetBase)]
        if 'name' in params:
            widgets.insert(0, HTML(f'<h2>{self.name}</h2>'))
        self.widget_box = Column(*widgets)
        self.layout.objects = [self.widget_box, self._inner_layout]
        self._link_widgets()
        self._sync_layout()

    #----------------------------------------------------------------
    # Model API
    #----------------------------------------------------------------

    def _get_model(self, doc, root=None, parent=None, comm=None):
        return self._inner_layout._get_model(doc, root, parent, comm)

    @param.depends('_pane', '_pane.sizing_mode', '_pane.width_policy', '_pane.height_policy', watch=True)
    def _sync_layout(self):
        if not hasattr(self, '_inner_layout'):
            return
        opts = {
            k: v for k, v in self._pane.param.values().items()
            if k in ('sizing_mode', 'width_policy', 'height_policy')
        }
        self._inner_layout.param.update(opts)
        self.layout.param.update(opts)

    #----------------------------------------------------------------
    # Callback API
    #----------------------------------------------------------------

    @property
    def _synced_params(self):
        return []

    def _link_widgets(self):
        if self.manual_update:
            widgets = [('manual', self._widgets['manual'])]
        else:
            widgets = self._widgets.items()

        for name, widget_obj in widgets:
            def update_pane(change):
                # Try updating existing pane
                new_object = self.object(**self.kwargs)
                new_pane, internal = ReplacementPane._update_from_object(
                    new_object, self._pane, self._internal
                )
                if new_pane is None:
                    return

                # Replace pane entirely
                self._pane = new_pane
                self._inner_layout[0] = new_pane
                self._internal = internal

            if self.throttled and hasattr(widget_obj, 'value_throttled'):
                v = 'value_throttled'
            else:
                v = 'value'

            pname = 'clicks' if name == 'manual' else v
            watcher = widget_obj.param.watch(update_pane, pname)
            self._internal_callbacks.append(watcher)

    def _cleanup(self, root: Model | None = None) -> None:
        self._inner_layout._cleanup(root)
        super()._cleanup(root)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

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
                    raise ValueError(f'cannot find widget or abbreviation for argument: {name!r}')
                new_kwargs.append((name, value, default))
        return new_kwargs

    def widgets_from_abbreviations(self, seq):
        """Given a sequence of (name, abbrev, default) tuples, return a sequence of Widgets."""
        result = []
        for name, abbrev, default in seq:
            if isinstance(abbrev, fixed):
                widget_obj = abbrev
            else:
                widget_obj = widget(abbrev, name=name, default=default)
            if not (isinstance(widget_obj, WidgetBase) or isinstance(widget_obj, fixed)):
                if widget_obj is None:
                    continue
                else:
                    raise TypeError(f"{widget!r} is not a ValueWidget")
            result.append((name, widget_obj))
        return result

    @classmethod
    def applies(cls, object):
        return isinstance(object, types.FunctionType)

    # Return a factory for interactive functions
    @classmethod
    def factory(cls):
        options = dict(manual_update=False, manual_name="Run Interact")
        return _InteractFactory(cls, options)


class _InteractFactory:
    """
    Factory for instances of :class:`interactive`.

    Parameters
    ----------
    cls: class
      The subclass of :class:`interactive` to construct.
    options: dict
      A dict of options used to construct the interactive
      function. By default, this is returned by
      ``cls.default_options()``.
    kwargs: dict
      A dict of **kwargs to use for widgets.
    """
    def __init__(self, cls, options, kwargs=None):
        self.cls = cls
        self.opts = options
        self.kwargs = kwargs or {}

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
            params = list(interactive.param)
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
        elif 'throttled' in check_argspec(f).args:
            raise ValueError('A function cannot have "throttled" as an argument')

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
                raise ValueError(f"invalid option {k!r}")
            opts[k] = kwds[k]
        return type(self)(self.cls, opts, self.kwargs)


interact = interactive.factory()
interact_manual = interact.options(manual_update=True, manual_name="Run Interact")


__all__ = ["interact", "interact_manual", "interactive"]
