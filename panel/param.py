"""
Defines the Param pane which converts Parameterized classes into a
set of widgets.
"""
from __future__ import annotations

import asyncio
import inspect
import itertools
import json
import os
import sys
import textwrap
import threading
import types

from collections import defaultdict, namedtuple
from collections.abc import Callable, Generator
from contextlib import contextmanager
from functools import partial
from types import FunctionType
from typing import TYPE_CHECKING, Any, ClassVar

import param

try:
    from param import Skip
except Exception:
    class Skip(Exception):  # type: ignore
        """
        Exception that allows skipping an update for function-level updates.
        """
from param.parameterized import (
    Undefined, bothmethod, classlist, discard_events, edit_constant,
    eval_function_with_deps, get_method_owner, iscoroutinefunction,
    resolve_ref, resolve_value,
)
from param.reactive import rx

from .config import config
from .io import state
from .layout import (
    Column, HSpacer, ListLike, Panel, Row, Spacer, Tabs, WidgetBox,
)
from .pane import DataFrame as DataFramePane
from .pane.base import Pane, ReplacementPane
from .reactive import Reactive
from .util import (
    abbreviated_repr, flatten, full_groupby, fullpath, is_parameterized,
    param_name, recursive_parameterized, to_async_gen,
)
from .util.checks import is_dataframe, is_mpl_axes, is_series
from .viewable import Layoutable, Viewable
from .widgets import (
    ArrayInput, Button, Checkbox, ColorPicker, DataFrame, DatePicker,
    DateRangeSlider, DatetimeInput, DatetimeRangeSlider, DiscreteSlider,
    FileInput, FileSelector, FloatInput, FloatSlider, IntInput, IntSlider,
    LiteralInput, MultiSelect, RangeSlider, Select, StaticText, Tabulator,
    TextInput, Toggle, Widget, WidgetBase,
)
from .widgets.button import _ButtonBase

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


def SingleFileSelector(pobj: param.Parameter) -> type[Widget]:
    """
    Determines whether to use a TextInput or Select widget for FileSelector
    """
    if pobj.path:
        return Select
    else:
        return TextInput


def LiteralInputTyped(pobj: param.Parameter) -> type[Widget]:
    if isinstance(pobj, param.Tuple):
        return type('TupleInput', (LiteralInput,), {'type': tuple})
    elif isinstance(pobj, param.Number):
        return type('NumberInput', (LiteralInput,), {'type': (int, float)})
    elif isinstance(pobj, param.Dict):
        return type('DictInput', (LiteralInput,), {'type': dict})
    elif isinstance(pobj, param.List):
        return type('ListInput', (LiteralInput,), {'type': list})
    return LiteralInput


def DataFrameWidget(pobj: param.DataFrame) -> type[Widget]:
    if 'panel.models.tabulator' in sys.modules:
        return Tabulator
    else:
        return DataFrame


@contextmanager
def set_values(*parameterizeds, **param_values):
    """
    Temporarily sets parameter values to the specified values on all
    supplied Parameterized objects.

    Parameters
    ----------
    parameterizeds: tuple(param.Parameterized)
        Any number of parameterized objects.
    param_values: dict
        A dictionary of parameter names and temporary values.
    """
    old = []
    for parameterized in parameterizeds:
        old_values = {p: getattr(parameterized, p) for p in param_values}
        old.append((parameterized, old_values))
        parameterized.param.update(**param_values)
    try:
        yield
    finally:
        for parameterized, old_values in old:
            parameterized.param.update(**old_values)


class Param(Pane):
    """
    Param panes render a Parameterized class into a set of interactive widgets
    that are dynamically linked to the parameter values of the class.

    Reference: https://panel.holoviz.org/reference/panes/Param.html

    Example:

    >>> import param
    >>> import panel as pn
    >>> pn.extension()

    >>> class App(param.Parameterized):
    >>>     some_text = param.String(default="Hello")
    >>>     some_float = param.Number(default=1, bounds=(0, 10), step=0.1)
    >>>     some_boolean = param.Boolean(default=True)

    >>> app = App()

    >>> pn.Param(app, parameters=["some_text", "some_float"], show_name=False).servable()
    """

    display_threshold = param.Number(default=0, precedence=-10, doc="""
        Parameters with precedence below this value are not displayed.""")

    default_layout = param.ClassSelector(default=Column, class_=ListLike,
                                         is_instance=False)

    default_precedence = param.Number(default=1e-8, precedence=-10, doc="""
        Precedence value to use for parameters with no declared
        precedence.  By default, zero predecence is available for
        forcing some parameters to the top of the list, and other
        values above the default_precedence values can be used to sort
        or group parameters arbitrarily.""")

    expand = param.Boolean(default=False, doc="""
        Whether parameterized subobjects are expanded or collapsed on
        instantiation.""")

    expand_button = param.Boolean(default=None, doc="""
        Whether to add buttons to expand and collapse sub-objects.""")

    expand_layout = param.Parameter(default=Column, doc="""
        Layout to expand sub-objects into.""")

    height = param.Integer(default=None, bounds=(0, None), doc="""
        Height of widgetbox the parameter widgets are displayed in.""")

    hide_constant = param.Boolean(default=False, doc="""
        Whether to hide widgets of constant parameters.""")

    initializer = param.Callable(default=None, doc="""
        User-supplied function that will be called on initialization,
        usually to update the default Parameter values of the
        underlying parameterized object.""")

    name = param.String(default='', constant=False, doc="""
        Title of the pane.""")

    object = param.Parameter(default=None, allow_refs=False, doc="""
        The object being wrapped, which will be converted to a
        Bokeh model.""")

    parameters = param.List(default=[], allow_None=True, doc="""
        If set this serves as a allowlist of parameters to display on
        the supplied Parameterized object.""")

    show_labels = param.Boolean(default=True, doc="""
        Whether to show labels for each widget""")

    show_name = param.Boolean(default=True, doc="""
        Whether to show the parameterized object's name""")

    sort = param.ClassSelector(default=False, class_=(bool, Callable), doc="""
        If True the widgets will be sorted alphabetically by label.
        If a callable is provided it will be used to sort the Parameters,
        for example lambda x: x[1].label[::-1] will sort by the reversed
        label.""")

    width = param.Integer(default=None, allow_None=True, bounds=(0, None), doc="""
        Width of widgetbox the parameter widgets are displayed in.""")

    widgets = param.Dict(doc="""
        Dictionary of widget overrides, mapping from parameter name
        to widget class.""")

    mapping: ClassVar[dict[param.Parameter, type[WidgetBase] | Callable[[param.Parameter], type[WidgetBase]]]] = {
        param.Action:            Button,
        param.Array:             ArrayInput,
        param.Boolean:           Checkbox,
        param.Bytes:             FileInput,
        param.CalendarDate:      DatePicker,
        param.Color:             ColorPicker,
        param.Date:              DatetimeInput,
        param.DateRange:         DatetimeRangeSlider,
        param.CalendarDateRange: DateRangeSlider,
        param.DataFrame:         DataFrameWidget,
        param.Dict:              LiteralInputTyped,
        param.FileSelector:      SingleFileSelector,
        param.Filename:          TextInput,
        param.Foldername:        TextInput,
        param.Integer:           IntSlider,
        param.List:              LiteralInputTyped,
        param.MultiFileSelector: FileSelector,
        param.ListSelector:      MultiSelect,
        param.Number:            FloatSlider,
        param.ObjectSelector:    Select,
        param.Parameter:         LiteralInputTyped,
        param.Range:             RangeSlider,
        param.Selector:          Select,
        param.String:            TextInput,
    }

    input_widgets: ClassVar[dict[Any, type[WidgetBase] | Callable[[param.Parameter], type[WidgetBase]]]]  = {
        float: FloatInput,
        int: IntInput,
        "literal": LiteralInput,
    }

    if hasattr(param, 'Event'):
        mapping[param.Event] = Button

    _ignored_refs: ClassVar[tuple[str,...]] = ('object',)

    _linkable_properties: ClassVar[tuple[str,...]] = ()

    _rerender_params: ClassVar[list[str]] = []

    _unpack: ClassVar[bool] = True

    def __init__(self, object=None, **params):
        if isinstance(object, param.Parameter):
            if 'show_name' not in params:
                params['show_name'] = False
            params['parameters'] = [object.name]
            object = object.owner
        if isinstance(object, param.parameterized.Parameters):
            object = object.cls if object.self is None else object.self

        if 'parameters' not in params and object is not None:
            params['parameters'] = [p for p in object.param if p != 'name']
            self._explicit_parameters = False
        else:
            self._explicit_parameters = object is not None

        if object and 'name' not in params:
            params['name'] = param_name(object.name)
        super().__init__(object, **params)
        self._updating = []

        # Construct Layout
        kwargs = {p: v for p, v in self.param.values().items()
                  if p in Layoutable.param and v is not None}
        self._widget_box = self.default_layout(**kwargs)

        layout = self.expand_layout
        if isinstance(layout, Panel):
            self._expand_layout = layout
            self.layout = self._widget_box
        elif isinstance(self._widget_box, layout):
            self.layout = self._expand_layout = self._widget_box
        elif isinstance(layout, type) and issubclass(layout, Panel):
            self.layout = self._expand_layout = layout(self._widget_box, **kwargs)
        else:
            raise ValueError('expand_layout expected to be a panel.layout.Panel'
                             f'type or instance, found {type(layout).__name__} type.')
        self.param.watch(self._update_widgets, [
            'object', 'parameters', 'name', 'display_threshold', 'expand_button',
            'expand', 'expand_layout', 'widgets', 'show_labels', 'show_name',
            'hide_constant'])
        self._update_widgets()

    def __repr__(self, depth=0):
        cls = type(self).__name__
        obj_cls = type(self.object).__name__
        params = [] if self.object is None else list(self.object.param)
        parameters = [k for k in params if k != 'name']
        params = []
        for p, v in sorted(self.param.values().items()):
            if v == self.param[p].default: continue
            elif v is None: continue
            elif isinstance(v, str) and v == '': continue
            elif p == 'object' or (p == 'name' and v.startswith((obj_cls, cls))): continue
            elif p == 'parameters' and v == parameters: continue
            try:
                params.append(f'{p}={abbreviated_repr(v)}')
            except RuntimeError:
                params.append('{}={}'.format(p, '...'))
        obj = 'None' if self.object is None else f'{type(self.object).__name__}'
        template = '{cls}({obj}, {params})' if params else '{cls}({obj})'
        return template.format(cls=cls, params=', '.join(params), obj=obj)

    #----------------------------------------------------------------
    # Callback API
    #----------------------------------------------------------------

    @property
    def _synced_params(self):
        ignored_params = ['default_layout', 'loading', 'background']
        return [p for p in Layoutable.param if p not in ignored_params]

    def _update_widgets(self, *events):
        parameters = []
        for event in sorted(events, key=lambda x: x.name):
            if event.name == 'object':
                if isinstance(event.new, param.parameterized.Parameters):
                    # Setting object will trigger this method a second time
                    self.object = event.new.cls if event.new.self is None else event.new.self
                    return

                if self._explicit_parameters:
                    parameters = self.parameters
                elif event.new is None:
                    parameters = []
                else:
                    parameters = [p for p in event.new.param if p != 'name']
                if event.new is not None:
                    self.name = param_name(event.new.name)
            if event.name == 'parameters':
                if event.new is None:
                    self._explicit_parameters = False
                    if self.object is not None:
                        parameters = [p for p in self.object.param if p != 'name']
                else:
                    self._explicit_parameters = True
                    parameters = [] if event.new == [] else event.new

        if parameters != [] and parameters != self.parameters:
            # Setting parameters will trigger this method a second time
            self.parameters = parameters
            return

        for cb in list(self._internal_callbacks):
            if cb.inst in self._widget_box.objects:
                cb.inst.param.unwatch(cb)
                self._internal_callbacks.remove(cb)

        # Construct widgets
        if self.object is None:
            self._widgets = {}
        else:
            self._widgets = self._get_widgets()

        alias = {'_title': 'name'}
        widgets = [widget for p, widget in self._widgets.items()
                   if (self.object.param[alias.get(p, p)].precedence is None)
                   or (self.object.param[alias.get(p, p)].precedence >= self.display_threshold)]
        self._widget_box.objects = widgets
        if not (self.expand_button == False and not self.expand):
            self._link_subobjects()

    def _link_subobjects(self):
        for pname, widget in self._widgets.items():
            widgets = [widget] if isinstance(widget, WidgetBase) else widget
            if not any(is_parameterized(getattr(w, 'value', None)) or
                       any(is_parameterized(o) for o in getattr(w, 'options', []))
                       for w in widgets):
                continue
            if (isinstance(widgets, Row) and isinstance(widgets[1], Toggle)):
                selector, toggle = (widgets[0], widgets[1])
            else:
                selector, toggle = (widget, None)

            def toggle_pane(change, parameter=pname):
                "Adds or removes subpanel from layout"
                parameterized = getattr(self.object, parameter)
                existing = [p for p in self._expand_layout.objects
                            if isinstance(p, Param) and
                            p.object in recursive_parameterized(parameterized)]
                if not change.new:
                    self._expand_layout[:] = [
                        e for e in self._expand_layout.objects
                        if e not in existing
                    ]
                elif change.new:
                    kwargs = {k: v for k, v in self.param.values().items()
                              if k not in ['name', 'object', 'parameters']}
                    pane = Param(parameterized, name=parameterized.name,
                                 **kwargs)
                    if isinstance(self._expand_layout, Tabs):
                        title = self.object.param[parameter].label
                        pane = (title, pane)
                    self._expand_layout.append(pane)

            def update_pane(change, parameter=pname, toggle=toggle):
                "Adds or removes subpanel from layout"
                layout = self._expand_layout
                existing = [p for p in layout.objects if isinstance(p, Param)
                            and p.object is change.old]

                if toggle:
                    toggle.disabled = not is_parameterized(change.new)
                if not existing:
                    return
                elif is_parameterized(change.new):
                    parameterized = change.new
                    kwargs = {k: v for k, v in self.param.values().items()
                              if k not in ['name', 'object', 'parameters']}
                    pane = Param(parameterized, name=parameterized.name,
                                 **kwargs)
                    layout[layout.objects.index(existing[0])] = pane
                else:
                    layout.remove(existing[0])

            watchers = [selector.param.watch(update_pane, 'value')]
            if toggle:
                watchers.append(toggle.param.watch(toggle_pane, 'value'))
            self._internal_callbacks += watchers

            if self.expand:
                if self.expand_button:
                    toggle.value = True
                else:
                    toggle_pane(namedtuple('Change', 'new')(True))

    @bothmethod
    def widget(self_or_cls, p_name: str, parameterized: param.Parameterized | None = None, widget_spec: type[WidgetBase] | dict | None = None):
        """Get widget for param_name"""
        parameterized = self_or_cls.object if parameterized is None else parameterized
        p_obj = parameterized.param[p_name]
        kw_widget = {}

        widget_class_overridden = True
        if widget_spec is None and self_or_cls.widgets is not None:
            widget_spec = self_or_cls.widgets.get(p_name)
        if widget_spec is None:
            widget_class_overridden = False
            widget_class = self_or_cls.widget_type(p_obj)
        elif isinstance(widget_spec, dict):
            kw_widget = dict(widget_spec)
            if 'widget_type' in widget_spec:
                widget_class = kw_widget.pop('widget_type')
            elif 'type' in widget_spec:
                widget_class = kw_widget.pop('type')
            else:
                widget_class_overridden = False
                widget_class = self_or_cls.widget_type(p_obj)
        else:
            widget_class = widget_spec

        if not self_or_cls.show_labels and not issubclass(widget_class, _ButtonBase):
            label = ''
        else:
            label = p_obj.label
        kw = dict(disabled=p_obj.constant, name=label)
        if self_or_cls.hide_constant:
            kw['visible'] = not p_obj.constant

        value = getattr(parameterized, p_name)
        allow_None = p_obj.allow_None or False
        if isinstance(widget_class, type) and issubclass(widget_class, WidgetBase):
            allow_None &= widget_class.param.value.allow_None
        if value is not None or allow_None:
            kw['value'] = value

        if hasattr(p_obj, 'get_range'):
            options = p_obj.get_range()
            # This applies to widgets whose `options` Parameter is a List type,
            # such as AutoCompleteInput.
            if ('options' in widget_class.param
                and isinstance(widget_class.param['options'], param.List)):
                options = list(options.values())
            if not options and value is not None:
                options = [value]
            kw['options'] = options
        if hasattr(p_obj, 'get_soft_bounds'):
            bounds = p_obj.get_soft_bounds()
            is_int = isinstance(p_obj, param.Integer)
            start, end = bounds
            istart, iend = getattr(p_obj, 'inclusive_bounds', (True, True))
            if is_int and not istart:
                start += 1
            if start is not None:
                kw['start'] = start
            if is_int and not iend:
                end -= 1
            if end is not None:
                kw['end'] = end
            if (('start' not in kw or 'end' not in kw) and
                not isinstance(p_obj, (param.Date, param.CalendarDate))):
                # Do not change widget class if mapping was overridden
                if not widget_class_overridden:
                    if isinstance(p_obj, param.Number):
                        widget_class = self_or_cls.input_widgets[float]
                        if is_int:
                            widget_class = self_or_cls.input_widgets[int]
                    elif not issubclass(widget_class, LiteralInput):
                        widget_class = self_or_cls.input_widgets['literal']
                    if isinstance(widget_class, FunctionType):
                        widget_class = widget_class(p_obj)
            if hasattr(widget_class, 'step') and getattr(p_obj, 'step', None):
                kw['step'] = p_obj.step
            if hasattr(widget_class, 'fixed_start') and getattr(p_obj, 'bounds', None):
                kw['fixed_start'] = p_obj.bounds[0]
            if hasattr(widget_class, 'fixed_end') and getattr(p_obj, 'bounds', None):
                kw['fixed_end'] = p_obj.bounds[1]

        if p_obj.doc:
            kw['description'] = textwrap.dedent(p_obj.doc).strip()

        # Update kwargs
        onkeyup = kw_widget.pop('onkeyup', False)
        throttled = kw_widget.pop('throttled', False)
        kw.update(kw_widget)
        kwargs = {k: v for k, v in kw.items() if k in widget_class.param}
        non_param_kwargs = {k: v for k, v in kw_widget.items() if k not in widget_class.param}

        if isinstance(widget_class, type) and issubclass(widget_class, Button):
            kwargs.pop('value', None)

        if isinstance(widget_class, WidgetBase):
            widget = widget_class
        else:
            widget = widget_class(**kwargs, **non_param_kwargs)
        widget._param_pane = self_or_cls
        widget._param_name = p_name

        is_instance = isinstance(self_or_cls, param.Parameterized)
        if is_instance:
            watchers = self_or_cls._internal_callbacks
            updating = self_or_cls._updating
        else:
            watchers, updating = [], []
            widgets = {p_name: widget}

        def link_widget(change):
            p_key = p_name if config.nthreads is None else (threading.get_ident(), p_name)
            if p_key in updating:
                return
            new = change.new
            reset = False
            if isinstance(p_obj, param.Number) and not isinstance(p_obj, param.Integer):
                istart, iend = getattr(p_obj, 'inclusive_bounds', (True, True))
                bounds = p_obj.get_soft_bounds()
                if (not istart and new == bounds[0]) or (not iend and new == bounds[1]):
                    new = change.old
                    reset = True
            elif isinstance(p_obj, param.Range):
                istart, iend = getattr(p_obj, 'inclusive_bounds', (True, True))
                bounds = p_obj.get_soft_bounds()
                if (not istart and new[0] == bounds[0]) or (not iend and new[1] == bounds[1]):
                    new = change.old
                    reset = True
            try:
                updating.append(p_key)
                parameterized.param.update(**{p_name: new})
            finally:
                updating.remove(p_key)
                if reset:
                    widget.value = new

        if hasattr(param, 'Event') and isinstance(p_obj, param.Event):
            def event(change):
                parameterized.param.trigger(p_name)
            watcher = widget.param.watch(event, 'value')
        elif isinstance(p_obj, param.Action):
            def action(change):
                value(parameterized)
            watcher = widget.param.watch(action, 'value')
        elif onkeyup and hasattr(widget, 'value_input'):
            watcher = widget.param.watch(link_widget, 'value_input')
        elif throttled and hasattr(widget, 'value_throttled'):
            watcher = widget.param.watch(link_widget, 'value_throttled')
        else:
            watcher = widget.param.watch(link_widget, 'value')
        watchers.append(watcher)

        def link(change, watchers=[watcher]):
            updates = {}
            if is_instance and p_name not in self_or_cls._widgets:
                return
            if is_instance:
                widget = self_or_cls._widgets[p_name]
            else:
                widget = widgets[p_name]
            p_key = p_name if config.nthreads is None else (threading.get_ident(), p_name)
            if change.what == 'constant':
                updates['disabled'] = change.new
                if self_or_cls.hide_constant:
                    updates['visible'] = not change.new
            elif change.what == 'precedence':
                if change.new is change.old or not is_instance:
                    return
                elif change.new is None:
                    self_or_cls._rerender()
                elif (change.new < self_or_cls.display_threshold and
                      widget in self_or_cls._widget_box.objects):
                    self_or_cls._widget_box.remove(widget)
                elif change.new >= self_or_cls.display_threshold:
                    self_or_cls._rerender()
                return
            elif change.what == 'objects':
                options = p_obj.get_range()
                if ('options' in widget.param and
                    isinstance(widget.param['options'], param.List)):
                    options = list(options)
                updates['options'] = options
            elif change.what == 'bounds':
                start, end = p_obj.get_soft_bounds()
                supports_bounds = hasattr(widget, 'start')
                if start is None or end is None:
                    rerender = supports_bounds
                else:
                    rerender = not supports_bounds
                if supports_bounds:
                    updates['start'] = start
                    updates['end'] = end
                if rerender and is_instance:
                    self_or_cls._rerender_widget(p_name)
                    return
            elif change.what == 'step':
                updates['step'] = p_obj.step
            elif change.what == 'label':
                updates['name'] = p_obj.label
            elif p_key in updating or isinstance(p_obj, param.Event):
                return
            elif isinstance(p_obj, param.Action):
                prev_watcher = watchers[0]
                widget.param.unwatch(prev_watcher)
                def action(event):
                    change.new(parameterized)
                watchers[0] = widget.param.watch(action, 'clicks')
                return
            elif throttled and hasattr(widget, 'value_throttled'):
                updates['value_throttled'] = change.new
                updates['value'] = change.new
            elif isinstance(widget, Row) and len(widget) == 2:
                updates['value'] = change.new
                widget = widget[0]
            else:
                updates['value'] = change.new

            try:
                updating.append(p_key)
                if change.type == 'triggered':
                    with discard_events(widget):
                        widget.param.update(**updates)
                    widget.param.trigger(*updates)
                elif 'value_throttled' in updates:
                    with edit_constant(widget):
                        widget.param.update(**updates)
                else:
                    widget.param.update(**updates)
            finally:
                updating.remove(p_key)

        # Set up links to parameterized object
        watchers.append(parameterized.param.watch(link, p_name, 'constant'))
        watchers.append(parameterized.param.watch(link, p_name, 'precedence'))
        watchers.append(parameterized.param.watch(link, p_name, 'label'))
        if hasattr(p_obj, 'get_range'):
            watchers.append(parameterized.param.watch(link, p_name, 'objects'))
        if hasattr(p_obj, 'get_soft_bounds'):
            watchers.append(parameterized.param.watch(link, p_name, 'bounds'))
        if 'step' in kw:
            watchers.append(parameterized.param.watch(link, p_name, 'step'))
        watchers.append(parameterized.param.watch(link, p_name))

        options = resolve_value(kwargs.get('options', []), recursive=False)
        if isinstance(options, dict):
            options = options.values()
        if ((is_parameterized(value) or any(is_parameterized(o) for o in options))
            and (self_or_cls.expand_button or (self_or_cls.expand_button is None and not self_or_cls.expand))):
            toggle = Toggle(
                name='\u22EE', button_type='primary',
                disabled=not is_parameterized(value), max_height=30,
                max_width=20, height_policy='fit', align='end',
                margin=(0, 0, 5, 10)
            )
            width = widget.width
            widget.param.update(
                margin=(5, 0, 5, 10),
                sizing_mode='stretch_width',
                width=None
            )
            return Row(widget, toggle, width=width, margin=0)
        else:
            return widget

    @property
    def _ordered_params(self):
        params = [(p, pobj) for p, pobj in self.object.param.objects('existing').items()
                  if p in self.parameters or p == 'name']
        if self.sort:
            if callable(self.sort):
                key_fn = self.sort
            else:
                key_fn = lambda x: x[1].label
            sorted_params = sorted(params, key=key_fn)
            sorted_params = [el[0] for el in sorted_params if (el[0] != 'name' or el[0] in self.parameters)]
            return sorted_params

        key_fn = lambda x: x[1].precedence if x[1].precedence is not None else self.default_precedence
        sorted_precedence = sorted(params, key=key_fn)
        filtered = [(k, p) for k, p in sorted_precedence]
        groups = itertools.groupby(filtered, key=key_fn)
        # Params preserve definition order in Python 3.6+
        ordered_groups = [list(grp) for (_, grp) in groups]
        ordered_params = [el[0] for group in ordered_groups for el in group
                          if (el[0] != 'name' or el[0] in self.parameters)]
        return ordered_params

    #----------------------------------------------------------------
    # Model API
    #----------------------------------------------------------------

    def _rerender(self):
        precedence = lambda k: self.object.param['name' if k == '_title' else k].precedence
        params = self._ordered_params
        if self.show_name:
            params.insert(0, '_title')
        widgets = []
        for k in params:
            if precedence(k) is None or precedence(k) >= self.display_threshold:
                widgets.append(self._widgets[k])
        self._widget_box.objects = widgets

    def _rerender_widget(self, p_name):
        watchers = []
        for w in self._internal_callbacks:
            if w.inst is self._widgets[p_name]:
                w.inst.param.unwatch(w)
            else:
                watchers.append(w)
        self._widgets[p_name] = self.widget(p_name)
        self._rerender()

    def _get_widgets(self):
        """Return name,widget boxes for all parameters (i.e., a property sheet)"""
        # Format name specially
        if self.expand_layout is Tabs:
            widgets = []
        elif self.show_name:
            widgets = [('_title', StaticText(value=f'<b>{self.name}</b>'))]
        else:
            widgets = []
        widgets += [(pname, self.widget(pname)) for pname in self._ordered_params]
        return dict(widgets)

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        model = self.layout._get_model(doc, root, parent, comm)
        root = root or model
        self._models[root.ref['id']] = (model, parent)
        return model

    def _cleanup(self, root: Model | None = None) -> None:
        self.layout._cleanup(root)
        super()._cleanup(root)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        if isinstance(obj, param.parameterized.Parameters):
            return 0.8
        elif (is_parameterized(obj) or (isinstance(obj, param.Parameter) and obj.owner is not None)):
            return 0.1
        return False

    @classmethod
    def widget_type(cls, pobj):
        ptype = type(pobj)
        for t in classlist(ptype)[::-1]:
            if t not in cls.mapping:
                continue
            wtype = cls.mapping[t]
            if isinstance(wtype, types.FunctionType):
                return wtype(pobj)
            return wtype

    def get_root(
        self, doc: Document | None = None, comm: Comm | None = None,
        preprocess: bool = True
    ) -> Model:
        root = super().get_root(doc, comm, preprocess)
        ref = root.ref['id']
        self._models[ref] = (root, None)
        return root

    def select(self, selector=None):
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
        return super().select(selector) + self.layout.select(selector)


class ParamRef(ReplacementPane):
    """
    ParamRef wraps any valid parameter reference and resolves it
    dynamically, re-rendering the output. If enabled it will attempt
    to update the previously rendered component inplace.
    """

    defer_load = param.Boolean(default=None, doc="""
        Whether to defer load until after the page is rendered.
        Can be set as parameter or by setting panel.config.defer_load.""")

    generator_mode = param.Selector(default='replace', objects=['append', 'replace'], doc="""
        Whether generators should 'append' to or 'replace' existing output.""")

    lazy = param.Boolean(default=False, doc="""
        Whether to lazily evaluate the contents of the object
        only when it is required for rendering.""")

    loading_indicator = param.Boolean(default=config.loading_indicator, doc="""
        Whether to show a loading indicator while the pane is updating.
        Can be set as parameter or by setting panel.config.loading_indicator.""")

    priority: ClassVar[float | bool | None] = 0

    def __init__(self, object=None, **params):
        if 'defer_load' not in params:
            params['defer_load'] = config.defer_load
        if 'loading_indicator' not in params:
            params['loading_indicator'] = ParamMethod.loading_indicator
        super().__init__(object, **params)
        self._async_task = None
        self._evaled = not (self.lazy or self.defer_load)
        self._link_object_params()
        if object is not None:
            self._validate_object()
            if not self.defer_load:
                self._replace_pane()

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        return bool(resolve_ref(obj))

    def _validate_object(self):
        return

    #----------------------------------------------------------------
    # Callback API
    #----------------------------------------------------------------

    @classmethod
    def eval(cls, ref):
        return resolve_value(ref)

    async def _eval_async(self, awaitable):
        if self._async_task:
            self._async_task.cancel()
        self._async_task = task = asyncio.current_task()
        curdoc = state.curdoc
        has_context = bool(curdoc.session_context) if curdoc else False
        if has_context:
            curdoc.on_session_destroyed(lambda context: task.cancel())
        try:
            if isinstance(awaitable, types.AsyncGeneratorType):
                append_mode = self.generator_mode == 'append'
                if append_mode:
                    self._inner_layout[:] = []
                async for new_obj in awaitable:
                    if append_mode:
                        self._inner_layout.append(new_obj)
                        self._pane = self._inner_layout[-1]
                    else:
                        try:
                            self._update_inner(new_obj)
                        except Skip:
                            pass
            else:
                try:
                    new = await awaitable
                    if new is Skip or new is Undefined:
                        raise Skip
                    self._update_inner(new)
                except Skip:
                    self.param.log(
                        param.DEBUG, 'Skip event was raised, skipping update.'
                    )
        except Exception as e:
            if not curdoc or (has_context and curdoc.session_context):
                raise e
        finally:
            self._async_task = None
            self._inner_layout.loading = False

    def _replace_pane(self, *args, force=False):
        deferred = self.defer_load and not state.loaded
        if not self._inner_layout.loading:
            self._inner_layout.loading = bool(self.loading_indicator or deferred)
        self._evaled |= force or not (self.lazy or deferred)
        if not self._evaled:
            return
        try:
            if self.object is None:
                new_object = Spacer()
            else:
                try:
                    new_object = self.eval(self.object)
                    if new_object is Skip and new_object is Undefined:
                        self._inner_layout.loading = False
                        raise Skip
                except Skip:
                    self.param.log(
                        param.DEBUG, 'Skip event was raised, skipping update.'
                    )
                    return
            if isinstance(new_object, Generator):
                new_object = to_async_gen(new_object)
            if inspect.isawaitable(new_object) or isinstance(new_object, types.AsyncGeneratorType):
                param.parameterized.async_executor(partial(self._eval_async, new_object))
                return
            else:
                self._update_inner(new_object)
        finally:
            self._inner_layout.loading = False

    def _update_pane(self, *events):
        callbacks = []
        for watcher in self._internal_callbacks:
            obj = watcher.cls if watcher.inst is None else watcher.inst
            if obj is self:
                callbacks.append(watcher)
                continue
            obj.param.unwatch(watcher)
        self._internal_callbacks = callbacks
        self._link_object_params()
        self._replace_pane()

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        if not self._evaled:
            deferred = self.defer_load and not state.loaded
            if deferred:
                state.onload(
                    partial(self._replace_pane, force=True),
                    threaded=bool(state._thread_pool)
                )
            self._replace_pane(force=not deferred)
        return super()._get_model(doc, root, parent, comm)

    def _link_object_params(self):
        dep_params = resolve_ref(self.object)
        if callable(self.object) and not (dep_params or self.lazy or self.defer_load or iscoroutinefunction(self.object)):
            fn = getattr(self.object, '__bound_function__', self.object)
            fn_name = getattr(fn, '__name__', repr(self.object))
            self.param.warning(
                f"The function {fn_name!r} does not have any dependencies "
                "and will never update. Are you sure you did not intend "
                "to depend on or bind a parameter or widget to this function? "
                "If not simply call the function before passing it to Panel. "
                "Otherwise, when passing a parameter as an argument, "
                "ensure you pass at least one parameter and reference the "
                "actual parameter object not the current value, i.e. use "
                "object.param.parameter not object.parameter."
            )
        grouped = defaultdict(list)
        for dep in dep_params:
            grouped[id(dep.owner)].append(dep)
        for group in grouped.values():
            pobj = group[0].owner
            watcher = pobj.param.watch(self._replace_pane, [dep.name for dep in group])
            if isinstance(pobj, Reactive) and self.loading_indicator:
                props = {dep.name: 'loading' for dep in group
                         if dep.name in pobj._linkable_params}
                if props:
                    pobj.jslink(self._inner_layout, **props)
            self._internal_callbacks.append(watcher)


@param.depends(config.param.defer_load, watch=True)
def _update_defer_load_default(default_value):
    ParamRef.param.defer_load.default = default_value

@param.depends(config.param.loading_indicator, watch=True)
def _update_loading_indicator_default(default_value):
    ParamRef.param.loading_indicator.default = default_value


class ParamMethod(ParamRef):
    """
    ParamMethod panes wrap methods on parameterized classes and
    rerenders the plot when any of the method's parameters change. By
    default ParamMethod will watch all parameters on the class owning
    the method or can be restricted to certain parameters by annotating
    the method using the param.depends decorator. The method may
    return any object which itself can be rendered as a Pane.
    """

    priority: ClassVar[float | bool | None] = 0.5

    @param.depends('object', watch=True)
    def _validate_object(self):
        dependencies = getattr(self.object, '_dinfo', {})
        if not dependencies or not dependencies.get('watch'):
            return
        self.param.warning(
            "The method supplied for Panel to display was declared "
            "with `watch=True`, which will cause the method to be "
            "called twice for any change in a dependent Parameter. "
            "`watch` should be False when Panel is responsible for "
            "displaying the result of the method call, while "
            "`watch=True` should be reserved for methods that work "
            "via side-effects, e.g. by modifying internal state of a "
            "class or global state in an application's namespace."
        )

    def _link_object_params(self):
        parameterized = get_method_owner(self.object)
        params = parameterized.param.method_dependencies(self.object.__name__)
        deps = params

        def update_pane(*events):
            # Update nested dependencies if parameterized object events
            if any(is_parameterized(event.new) for event in events):
                new_deps = parameterized.param.method_dependencies(self.object.__name__)
                for p in list(deps):
                    if p in new_deps: continue
                    watchers = self._internal_callbacks
                    for w in list(watchers):
                        if (w.inst is p.inst and w.cls is p.cls and
                            p.name in w.parameter_names):
                            obj = p.cls if p.inst is None else p.inst
                            obj.param.unwatch(w)
                            watchers.remove(w)
                    deps.remove(p)

                new_deps = [dep for dep in new_deps if dep not in deps]
                for _, params in full_groupby(new_deps, lambda x: (x.inst or x.cls, x.what)):
                    p = params[0]
                    pobj = p.cls if p.inst is None else p.inst
                    ps = [_p.name for _p in params]
                    watcher = pobj.param.watch(update_pane, ps, p.what)
                    self._internal_callbacks.append(watcher)
                    for p in params:
                        deps.append(p)
            self._replace_pane()

        for _, sub_params in full_groupby(params, lambda x: (x.inst or x.cls, x.what)):
            p = sub_params[0]
            pobj = (p.inst or p.cls)
            ps = [_p.name for _p in sub_params]
            if isinstance(pobj, Reactive) and self.loading_indicator:
                props = {p: 'loading' for p in ps if p in pobj._linkable_params}
                if props:
                    pobj.jslink(self._inner_layout, **props)
            watcher = pobj.param.watch(update_pane, ps, p.what)
            self._internal_callbacks.append(watcher)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        return inspect.ismethod(obj) and isinstance(get_method_owner(obj), param.Parameterized)

    @classmethod
    def eval(cls, ref):
        return eval_function_with_deps(ref)


class ParamFunction(ParamRef):
    """
    ParamFunction panes wrap functions decorated with the param.depends
    decorator and rerenders the output when any of the function's
    dependencies change. This allows building reactive components into
    a Panel which depend on other parameters, e.g. tying the value of
    a widget to some other output.
    """

    priority: ClassVar[float | bool | None] = 0.6

    _applies_kw: ClassVar[bool] = True

    @param.depends('object', watch=True)
    def _validate_object(self):
        dependencies = getattr(self.object, '_dinfo', {})
        if not dependencies or not dependencies.get('watch'):
            return
        self.param.warning(
            "The function supplied for Panel to display was declared "
            "with `watch=True`, which will cause the function to be "
            "called twice for any change in a dependent Parameter. "
            "`watch` should be False when Panel is responsible for "
            "displaying the result of the function call, while "
            "`watch=True` should be reserved for functions that work "
            "via side-effects, e.g. by modifying internal state of a "
            "class or global state in an application's namespace."
        )

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    @classmethod
    def applies(cls, obj: Any, **kwargs) -> float | bool | None:
        if isinstance(obj, types.FunctionType):
            if hasattr(obj, '_dinfo'):
                return True
            if (
                kwargs.get('defer_load') or cls.param.defer_load.default or
                (cls.param.defer_load.default is None and config.defer_load) or
                iscoroutinefunction(obj)
            ):
                return True
            return None
        return False

    @classmethod
    def eval(self, ref):
        return eval_function_with_deps(ref)


class ReactiveExpr(Pane):
    """
    ReactiveExpr generates a UI for param.rx objects by rendering the
    widgets and outputs.
    """

    center = param.Boolean(default=False, doc="""
        Whether to center the output.""")

    object = param.Parameter(default=None, allow_refs=False, doc="""
        The object being wrapped, which will be converted to a
        Bokeh model.""")

    show_widgets = param.Boolean(default=True, doc="""
        Whether to display the widget inputs.""")

    widget_layout = param.ClassSelector(
        class_=ListLike, constant=True, is_instance=False, default=WidgetBox, doc="""
        The layout object to display the widgets in.""")

    widget_location = param.Selector(default='left_top', objects=[
        'left', 'right', 'top', 'bottom', 'top_left',
        'top_right', 'bottom_left', 'bottom_right',
        'left_top', 'right_top', 'right_bottom'], doc="""
        The location of the widgets relative to the output
        of the reactive expression.""")

    priority: ClassVar[float | bool | None] = 1

    _layouts = {
        'left': (Row, ('start', 'center'), True),
        'right': (Row, ('end', 'center'), False),
        'top': (Column, ('center', 'start'), True),
        'bottom': (Column, ('center', 'end'), False),
        'top_left': (Column, 'start', True),
        'top_right': (Column, ('end', 'start'), True),
        'bottom_left': (Column, ('start', 'end'), False),
        'bottom_right': (Column, 'end', False),
        'left_top': (Row, 'start', True),
        'left_bottom': (Row, ('start', 'end'), True),
        'right_top': (Row, ('end', 'start'), False),
        'right_bottom': (Row, 'end', False)
    }

    _unpack: ClassVar[bool] = False

    def __init__(self, object=None, **params):
        super().__init__(object=object, **params)
        self._update_layout()

    @param.depends('center', 'object', 'widget_layout', 'widget_location', watch=True)
    def _update_layout(self, *events):
        if self.object is None:
            self.layout[:] = []
        else:
            self.layout[:] = [self._generate_layout()]

    @classmethod
    def applies(cls, object):
        return isinstance(object, param.rx)

    @classmethod
    def _find_widgets(cls, op):
        widgets = []
        op_args = list(op['args']) + list(op['kwargs'].values())
        op_args = flatten(op_args)
        for op_arg in op_args:
            # Find widgets introduced as `widget` in an expression
            if isinstance(op_arg, Widget) and op_arg not in widgets:
                widgets.append(op_arg)
                continue

            # Find Ipywidgets
            if 'ipywidgets' in sys.modules:
                from ipywidgets import Widget as IPyWidget
                if isinstance(op_arg, IPyWidget) and op_arg not in widgets:
                    widgets.append(op_arg)
                    continue

            # Find widgets introduced as `widget.param.value` in an expression
            if (isinstance(op_arg, param.Parameter) and
                isinstance(op_arg.owner, Widget) and
                op_arg.owner not in widgets):
                widgets.append(op_arg.owner)
                continue

            # Recurse into object
            if hasattr(op_arg, '_dinfo'):
                dinfo = op_arg._dinfo
                args = list(dinfo.get('dependencies', []))
                kwargs = dinfo.get('kw', {})
                nested_op = {"args": args, "kwargs": kwargs}
            elif isinstance(op_arg, slice):
                nested_op = {"args": [op_arg.start, op_arg.stop, op_arg.step], "kwargs": {}}
            elif isinstance(op_arg, (list, tuple)):
                nested_op = {"args": op_arg, "kwargs": {}}
            elif isinstance(op_arg, dict):
                nested_op = {"args": (), "kwargs": op_arg}
            elif isinstance(op_arg, param.rx):
                nested_op = {"args": op_arg._params, "kwargs": {}}
            else:
                continue
            for widget in cls._find_widgets(nested_op):
                if widget not in widgets:
                    widgets.append(widget)
        return widgets

    @property
    def widgets(self):
        widgets = []
        if self.object is None:
            return []
        for p in self.object._fn_params:
            if (isinstance(p.owner, Widget) and
                p.owner not in widgets):
                widgets.append(p.owner)

        operations = []
        prev = self.object
        while prev is not None:
            if prev._operation:
                operations.append(prev._operation)
            prev = prev._prev

        for op in operations[::-1]:
            for w in self._find_widgets(op):
                if w not in widgets:
                    widgets.append(w)
        return self.widget_layout(*widgets)

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        return self.layout._get_model(doc, root, parent, comm)

    def _generate_layout(self):
        panel = ParamFunction(self.object._callback)
        if not self.show_widgets:
            return panel
        widget_box = self.widgets
        loc = self.widget_location
        layout, align, widget_first = self._layouts[loc]
        widget_box.align = align
        if not len(widget_box):
            if self.center:
                components = [HSpacer(), panel, HSpacer()]
            else:
                components = [panel]
            return Row(*components)

        items = (widget_box, panel) if widget_first else (panel, widget_box)
        if not self.center:
            if layout is Row:
                components = list(items)
            else:
                components = [layout(*items, sizing_mode=self.sizing_mode)]
        elif layout is Column:
            components = [HSpacer(), layout(*items, sizing_mode=self.sizing_mode), HSpacer()]
        elif loc.startswith('left'):
            components = [widget_box, HSpacer(), panel, HSpacer()]
        else:
            components = [HSpacer(), panel, HSpacer(), widget_box]
        return Row(*components)



class JSONInit(param.Parameterized):
    """
    Callable that can be passed to Widgets.initializer to set Parameter
    values using JSON. There are three approaches that may be used:
    1. If the json_file argument is specified, this takes precedence.
    2. The JSON file path can be specified via an environment variable.
    3. The JSON can be read directly from an environment variable.
    Here is an easy example of setting such an environment variable on
    the commandline:
    PARAM_JSON_INIT='{"p1":5}' jupyter notebook
    This addresses any JSONInit instances that are inspecting the
    default environment variable called PARAM_JSON_INIT, instructing it to set
    the 'p1' parameter to 5.
    """

    varname = param.String(default='PARAM_JSON_INIT', doc="""
        The name of the environment variable containing the JSON
        specification.""")

    target = param.String(default=None, doc="""
        Optional key in the JSON specification dictionary containing the
        desired parameter values.""")

    json_file = param.String(default=None, doc="""
        Optional path to a JSON file containing the parameter settings.""")

    def __call__(self, parameterized):
        warnobj = param.main.param if isinstance(parameterized, type) else parameterized.param
        param_class = (parameterized if isinstance(parameterized, type)
                       else parameterized.__class__)

        target = self.target if self.target is not None else param_class.__name__

        env_var = os.environ.get(self.varname, None)
        if env_var is None and self.json_file is None: return

        if self.json_file or env_var.endswith('.json'):
            try:
                fname = self.json_file if self.json_file else env_var
                with open(fullpath(fname)) as f:
                    spec = json.load(f)
            except Exception:
                warnobj.warning(f'Could not load JSON file {spec!r}')
        else:
            spec = json.loads(env_var)

        if not isinstance(spec, dict):
            warnobj.warning('JSON parameter specification must be a dictionary.')
            return

        if target in spec:
            params = spec[target]
        else:
            params = spec

        for name, value in params.items():
            try:
                parameterized.param.update(**{name:value})
            except ValueError as e:
                warnobj.warning(str(e))


def link_param_method(root_view, root_model):
    """
    This preprocessor jslinks ParamMethod loading parameters to any
    widgets generated from those parameters ensuring that the loading
    indicator is enabled client side.
    """
    methods = root_view.select(lambda p: isinstance(p, ParamMethod) and p.loading_indicator)
    widgets = root_view.select(lambda w: isinstance(w, Widget) and getattr(w, '_param_pane', None) is not None)

    for widget in widgets:
        for method in methods:
            for cb in method._internal_callbacks:
                pobj = cb.cls if cb.inst is None else cb.inst
                if widget._param_pane.object is pobj and widget._param_name in cb.parameter_names:
                    if isinstance(widget, DiscreteSlider):
                        w = widget._slider
                    else:
                        w = widget
                    if 'value' in w._linkable_params:
                        w.jslink(method._inner_layout, value='loading')


Viewable._preprocessing_hooks.insert(0, link_param_method)


class FigureWrapper(param.Parameterized):

    figure = param.Parameter()

    def get_ax(self):
        from matplotlib.backends.backend_agg import FigureCanvas
        from matplotlib.pyplot import Figure
        self.figure = fig = Figure()
        FigureCanvas(fig)
        return fig.subplots()

    def _repr_mimebundle_(self, include=[], exclude=[]):
        return self.layout()._repr_mimebundle_()

    def __panel__(self):
        return self.layout()


def _plot_handler(reactive):
    fig_wrapper = FigureWrapper()
    def plot(obj, *args, **kwargs):
        if 'ax' not in kwargs:
            kwargs['ax'] = fig_wrapper.get_ax()
        obj.plot(*args, **kwargs)
        return fig_wrapper.figure
    return plot


rx.register_display_handler(is_dataframe, handler=DataFramePane, max_rows=100)
rx.register_display_handler(is_series, handler=DataFramePane, max_rows=100)
rx.register_display_handler(is_mpl_axes, handler=lambda ax: ax.get_figure())
rx.register_method_handler('plot', _plot_handler)


__all__= (
    "Param",
    "ParamFunction",
    "ParamMethod",
    "ReactiveExpr",
    "set_values"
)
