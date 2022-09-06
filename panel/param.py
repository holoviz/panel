"""
Defines the Param pane which converts Parameterized classes into a
set of widgets.
"""
from __future__ import annotations

import inspect
import itertools
import json
import os
import types

from collections import OrderedDict, defaultdict, namedtuple
from collections.abc import Callable
from contextlib import contextmanager
from functools import partial
from typing import (
    TYPE_CHECKING, Any, ClassVar, List, Mapping, Optional,
)

import param

from packaging.version import Version
from param.parameterized import classlist, discard_events

from .io import init_doc, state
from .layout import (
    Column, Panel, Row, Spacer, Tabs,
)
from .pane.base import PaneBase, ReplacementPane
from .reactive import Reactive
from .util import (
    abbreviated_repr, bokeh_version, classproperty, full_groupby, fullpath,
    get_method_owner, is_parameterized, param_name, recursive_parameterized,
)
from .viewable import Layoutable, Viewable
from .widgets import (
    ArrayInput, Button, Checkbox, ColorPicker, DataFrame, DatePicker,
    DateRangeSlider, DatetimeInput, DatetimeRangeSlider, DiscreteSlider,
    FileSelector, FloatInput, FloatSlider, IntInput, IntSlider, LiteralInput,
    MultiSelect, RangeSlider, Select, StaticText, TextInput, Toggle, Widget,
)
from .widgets.button import _ButtonBase

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


def SingleFileSelector(pobj: param.Parameter) -> Widget:
    """
    Determines whether to use a TextInput or Select widget for FileSelector
    """
    if pobj.path:
        return Select
    else:
        return TextInput


def LiteralInputTyped(pobj: param.Parameter) -> Widget:
    if isinstance(pobj, param.Tuple):
        return type(str('TupleInput'), (LiteralInput,), {'type': tuple})
    elif isinstance(pobj, param.Number):
        return type(str('NumberInput'), (LiteralInput,), {'type': (int, float)})
    elif isinstance(pobj, param.Dict):
        return type(str('DictInput'), (LiteralInput,), {'type': dict})
    elif isinstance(pobj, param.List):
        return type(str('ListInput'), (LiteralInput,), {'type': list})
    return LiteralInput


@contextmanager
def set_values(*parameterizeds, **param_values):
    """
    Temporarily sets parameter values to the specified values on all
    supplied Parameterized objects.

    Arguments
    ---------
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


class Param(PaneBase):
    """
    Param panes render a Parameterized class to a set of widgets which
    are linked to the parameter values on the class.
    """

    display_threshold = param.Number(default=0, precedence=-10, doc="""
        Parameters with precedence below this value are not displayed.""")

    default_layout = param.ClassSelector(default=Column, class_=Panel,
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

    name = param.String(default='', doc="""
        Title of the pane.""")

    parameters = param.List(default=[], allow_None=True, doc="""
        If set this serves as a whitelist of parameters to display on
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

    width = param.Integer(default=300, allow_None=True, bounds=(0, None), doc="""
        Width of widgetbox the parameter widgets are displayed in.""")

    widgets = param.Dict(doc="""
        Dictionary of widget overrides, mapping from parameter name
        to widget class.""")

    mapping: ClassVar[Mapping[param.Parameter, Widget | Callable[[param.Parameter], Widget]]] = {
        param.Action:            Button,
        param.Array:             ArrayInput,
        param.Boolean:           Checkbox,
        param.CalendarDate:      DatePicker,
        param.Color:             ColorPicker,
        param.Date:              DatetimeInput,
        param.DateRange:         DateRangeSlider,
        param.CalendarDateRange: DateRangeSlider,
        param.DataFrame:         DataFrame,
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

    if hasattr(param, 'Event'):
        mapping[param.Event] = Button

    if bokeh_version >= Version('2.4.3'):
        mapping[param.DateRange] = DatetimeRangeSlider

    priority: ClassVar[float | bool | None] = 0.1

    _unpack: ClassVar[bool] = True

    _rerender_params: ClassVar[List[str]] = []

    def __init__(self, object=None, **params):
        if isinstance(object, param.Parameter):
            if not 'show_name' in params:
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
                             'type or instance, found %s type.' %
                             type(layout).__name__)
        self.param.watch(self._update_widgets, [
            'object', 'parameters', 'name', 'display_threshold', 'expand_button',
            'expand', 'expand_layout', 'widgets', 'show_labels', 'show_name',
            'hide_constant'])
        self._update_widgets()

    @classproperty
    def _mapping(cls):
        cls.param.warning(
            "Param._mapping is now deprecated in favor of the public "
            "Param.mapping attribute. Update your code accordingly."
        )
        return cls.mapping

    def __repr__(self, depth=0):
        cls = type(self).__name__
        obj_cls = type(self.object).__name__
        params = [] if self.object is None else list(self.object.param)
        parameters = [k for k in params if k != 'name']
        params = []
        for p, v in sorted(self.param.values().items()):
            if v is self.param[p].default: continue
            elif v is None: continue
            elif isinstance(v, str) and v == '': continue
            elif p == 'object' or (p == 'name' and (v.startswith(obj_cls) or v.startswith(cls))): continue
            elif p == 'parameters' and v == parameters: continue
            try:
                params.append('%s=%s' % (p, abbreviated_repr(v)))
            except RuntimeError:
                params.append('%s=%s' % (p, '...'))
        obj = 'None' if self.object is None else '%s' % type(self.object).__name__
        template = '{cls}({obj}, {params})' if params else '{cls}({obj})'
        return template.format(cls=cls, params=', '.join(params), obj=obj)

    #----------------------------------------------------------------
    # Callback API
    #----------------------------------------------------------------

    @property
    def _synced_params(self):
        ignored_params = ['default_layout', 'loading']
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

        for cb in list(self._callbacks):
            if cb.inst in self._widget_box.objects:
                cb.inst.param.unwatch(cb)
                self._callbacks.remove(cb)

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
            widgets = [widget] if isinstance(widget, Widget) else widget
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
                        title = self.object.param[pname].label
                        pane = (title, pane)
                    self._expand_layout.append(pane)

            def update_pane(change, parameter=pname):
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
            self._callbacks += watchers

            if self.expand:
                if self.expand_button:
                    toggle.value = True
                else:
                    toggle_pane(namedtuple('Change', 'new')(True))

    def widget(self, p_name):
        """Get widget for param_name"""
        p_obj = self.object.param[p_name]
        kw_widget = {}

        widget_class_overridden = True
        if self.widgets is None or p_name not in self.widgets:
            widget_class_overridden = False
            widget_class = self.widget_type(p_obj)
        elif isinstance(self.widgets[p_name], dict):
            kw_widget = dict(self.widgets[p_name])
            if 'widget_type' in self.widgets[p_name]:
                widget_class = kw_widget.pop('widget_type')
            elif 'type' in self.widgets[p_name]:
                widget_class = kw_widget.pop('type')
            else:
                widget_class_overridden = False
                widget_class = self.widget_type(p_obj)
        else:
            widget_class = self.widgets[p_name]

        if not self.show_labels and not issubclass(widget_class, _ButtonBase):
            label = ''
        else:
            label = p_obj.label
        kw = dict(disabled=p_obj.constant, name=label)
        if self.hide_constant:
            kw['visible'] = not p_obj.constant

        value = getattr(self.object, p_name)
        allow_None = p_obj.allow_None or False
        if isinstance(widget_class, type) and issubclass(widget_class, Widget):
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
            if bounds[0] is not None:
                kw['start'] = bounds[0]
            if bounds[1] is not None:
                kw['end'] = bounds[1]
            if (('start' not in kw or 'end' not in kw) and
                not isinstance(p_obj, (param.Date, param.CalendarDate))):
                # Do not change widget class if mapping was overridden
                if not widget_class_overridden:
                    if isinstance(p_obj, param.Number):
                        widget_class = FloatInput
                        if isinstance(p_obj, param.Integer):
                            widget_class = IntInput
                    elif not issubclass(widget_class, LiteralInput):
                        widget_class = LiteralInput
            if hasattr(widget_class, 'step') and getattr(p_obj, 'step', None):
                kw['step'] = p_obj.step
            if hasattr(widget_class, 'fixed_start') and getattr(p_obj, 'bounds', None):
                kw['fixed_start'] = p_obj.bounds[0]
            if hasattr(widget_class, 'fixed_end') and getattr(p_obj, 'bounds', None):
                kw['fixed_end'] = p_obj.bounds[1]

        # Update kwargs
        kw.update(kw_widget)

        kwargs = {k: v for k, v in kw.items() if k in widget_class.param}

        if isinstance(widget_class, type) and issubclass(widget_class, Button):
            kwargs.pop('value', None)

        if isinstance(widget_class, Widget):
            widget = widget_class
        else:
            widget = widget_class(**kwargs)
        widget._param_pane = self
        widget._param_name = p_name

        watchers = self._callbacks

        def link_widget(change):
            if p_name in self._updating:
                return
            try:
                self._updating.append(p_name)
                self.object.param.update(**{p_name: change.new})
            finally:
                self._updating.remove(p_name)

        if hasattr(param, 'Event') and isinstance(p_obj, param.Event):
            def event(change):
                self.object.param.trigger(p_name)
            watcher = widget.param.watch(event, 'clicks')
        elif isinstance(p_obj, param.Action):
            def action(change):
                value(self.object)
            watcher = widget.param.watch(action, 'clicks')
        elif kw_widget.get('throttled', False) and hasattr(widget, 'value_throttled'):
            watcher = widget.param.watch(link_widget, 'value_throttled')
        else:
            watcher = widget.param.watch(link_widget, 'value')
        watchers.append(watcher)

        def link(change, watchers=[watcher]):
            updates = {}
            if p_name not in self._widgets:
                return
            widget = self._widgets[p_name]
            if change.what == 'constant':
                updates['disabled'] = change.new
                if self.hide_constant:
                    updates['visible'] = not change.new
            elif change.what == 'precedence':
                if change.new is change.old:
                    return
                elif change.new is None:
                    self._rerender()
                elif (change.new < self.display_threshold and
                      widget in self._widget_box.objects):
                    self._widget_box.remove(widget)
                elif change.new >= self.display_threshold:
                    self._rerender()
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
                if rerender:
                    self._rerender_widget(p_name)
                    return
            elif change.what == 'step':
                updates['step'] = p_obj.step
            elif change.what == 'label':
                updates['name'] = p_obj.label
            elif p_name in self._updating:
                return
            elif hasattr(param, 'Event') and isinstance(p_obj, param.Event):
                return
            elif isinstance(p_obj, param.Action):
                prev_watcher = watchers[0]
                widget.param.unwatch(prev_watcher)
                def action(event):
                    change.new(self.object)
                watchers[0] = widget.param.watch(action, 'clicks')
                idx = self._callbacks.index(prev_watcher)
                self._callbacks[idx] = watchers[0]
                return
            elif kw_widget.get('throttled', False) and hasattr(widget, 'value_throttled'):
                updates['value_throttled'] = change.new
                updates['value'] = change.new
            elif isinstance(widget, Row) and len(widget) == 2:
                updates['value'] = change.new
                widget = widget[0]
            else:
                updates['value'] = change.new

            try:
                self._updating.append(p_name)
                if change.type == 'triggered':
                    with discard_events(widget):
                        widget.param.update(**updates)
                    widget.param.trigger(*updates)
                else:
                    widget.param.update(**updates)
            finally:
                self._updating.remove(p_name)

        # Set up links to parameterized object
        watchers.append(self.object.param.watch(link, p_name, 'constant'))
        watchers.append(self.object.param.watch(link, p_name, 'precedence'))
        watchers.append(self.object.param.watch(link, p_name, 'label'))
        if hasattr(p_obj, 'get_range'):
            watchers.append(self.object.param.watch(link, p_name, 'objects'))
        if hasattr(p_obj, 'get_soft_bounds'):
            watchers.append(self.object.param.watch(link, p_name, 'bounds'))
        if 'step' in kw:
            watchers.append(self.object.param.watch(link, p_name, 'step'))
        watchers.append(self.object.param.watch(link, p_name))

        options = kwargs.get('options', [])
        if isinstance(options, dict):
            options = options.values()
        if ((is_parameterized(value) or any(is_parameterized(o) for o in options))
            and (self.expand_button or (self.expand_button is None and not self.expand))):
            widget.margin = (5, 0, 5, 10)
            toggle = Toggle(name='\u22EE', button_type='primary',
                            disabled=not is_parameterized(value), max_height=30,
                            max_width=20, height_policy='fit', align='end',
                            margin=(0, 0, 5, 10))
            widget.width = self._widget_box.width-60
            return Row(widget, toggle, width_policy='max', margin=0)
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
        for w in self._callbacks:
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
            widgets = [('_title', StaticText(value='<b>{0}</b>'.format(self.name)))]
        else:
            widgets = []
        widgets += [(pname, self.widget(pname)) for pname in self._ordered_params]
        return OrderedDict(widgets)

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        model = self.layout._get_model(doc, root, parent, comm)
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
        return (is_parameterized(obj) or
                isinstance(obj, param.parameterized.Parameters) or
                (isinstance(obj, param.Parameter) and obj.owner is not None))

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

    def select(self, selector=None):
        """
        Iterates over the Viewable and any potential children in the
        applying the Selector.

        Arguments
        ---------
        selector: type or callable or None
          The selector allows selecting a subset of Viewables by
          declaring a type or callable function to filter by.

        Returns
        -------
        viewables: list(Viewable)
        """
        return super().select(selector) + self.layout.select(selector)

    def get_root(
        self, doc: Optional[Document] = None, comm: Optional[Comm] = None,
        preprocess: bool = True
    ) -> Model:
        """
        Returns the root model and applies pre-processing hooks

        Arguments
        ---------
        doc: bokeh.Document
          Bokeh document the bokeh model will be attached to.
        comm: pyviz_comms.Comm
          Optional pyviz_comms when working in notebook
        preprocess: boolean (default=True)
          Whether to run preprocessing hooks

        Returns
        -------
        Returns the bokeh model corresponding to this panel object
        """
        doc = init_doc(doc)
        root = self.layout.get_root(doc, comm, preprocess)
        ref = root.ref['id']
        self._models[ref] = (root, None)
        state._views[ref] = (self, root, doc, comm)
        return root


class ParamMethod(ReplacementPane):
    """
    ParamMethod panes wrap methods on parameterized classes and
    rerenders the plot when any of the method's parameters change. By
    default ParamMethod will watch all parameters on the class owning
    the method or can be restricted to certain parameters by annotating
    the method using the param.depends decorator. The method may
    return any object which itself can be rendered as a Pane.
    """

    lazy = param.Boolean(default=False, doc="""
        Whether to lazily evaluate the contents of the object
        only when it is required for rendering.""")

    loading_indicator = param.Boolean(default=False, doc="""
        Whether to show loading indicator while pane is updating.""")

    def __init__(self, object=None, **params):
        super().__init__(object, **params)
        self._evaled = not self.lazy
        self._link_object_params()
        if object is not None:
            self._validate_object()
            self._replace_pane()

    @param.depends('object', watch=True)
    def _validate_object(self):
        dependencies = getattr(self.object, '_dinfo', None)
        if not dependencies or not dependencies.get('watch'):
            return
        fn_type = 'method' if type(self) is ParamMethod else 'function'
        self.param.warning(
            f"The {fn_type} supplied for Panel to display was declared "
            f"with `watch=True`, which will cause the {fn_type} to be "
            "called twice for any change in a dependent Parameter. "
            "`watch` should be False when Panel is responsible for "
            f"displaying the result of the {fn_type} call, while "
            f"`watch=True` should be reserved for {fn_type}s that work "
            "via side-effects, e.g. by modifying internal state of a "
            "class or global state in an application's namespace."
        )

    #----------------------------------------------------------------
    # Callback API
    #----------------------------------------------------------------

    @classmethod
    def eval(self, function):
        args, kwargs = (), {}
        if hasattr(function, '_dinfo'):
            arg_deps = function._dinfo['dependencies']
            kw_deps = function._dinfo.get('kw', {})
            if kw_deps or any(isinstance(d, param.Parameter) for d in arg_deps):
                args = (getattr(dep.owner, dep.name) for dep in arg_deps)
                kwargs = {n: getattr(dep.owner, dep.name) for n, dep in kw_deps.items()}
        return function(*args, **kwargs)

    async def _eval_async(self, awaitable):
        try:
            new_object = await awaitable
            self._update_inner(new_object)
        finally:
            self._inner_layout.loading = False

    def _replace_pane(self, *args, force=False):
        self._evaled = bool(self._models) or force or not self.lazy
        if self._evaled:
            self._inner_layout.loading = self.loading_indicator
            try:
                if self.object is None:
                    new_object = Spacer()
                else:
                    new_object = self.eval(self.object)
                if inspect.isawaitable(new_object):
                    param.parameterized.async_executor(partial(self._eval_async, new_object))
                    return
                self._update_inner(new_object)
            finally:
                self._inner_layout.loading = False

    def _update_pane(self, *events):
        callbacks = []
        for watcher in self._callbacks:
            obj = watcher.inst if watcher.inst is None else watcher.cls
            if obj is self:
                callbacks.append(watcher)
                continue
            obj.param.unwatch(watcher)
        self._callbacks = callbacks
        self._link_object_params()
        self._replace_pane()

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
                    watchers = self._callbacks
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
                    self._callbacks.append(watcher)
                    for p in params:
                        deps.append(p)
            self._replace_pane()

        for _, params in full_groupby(params, lambda x: (x.inst or x.cls, x.what)):
            p = params[0]
            pobj = (p.inst or p.cls)
            ps = [_p.name for _p in params]
            if isinstance(pobj, Reactive) and self.loading_indicator:
                props = {p: 'loading' for p in ps if p in pobj._linkable_params}
                if props:
                    pobj.jslink(self._inner_layout, **props)
            watcher = pobj.param.watch(update_pane, ps, p.what)
            self._callbacks.append(watcher)

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        if not self._evaled:
            self._replace_pane(force=True)
        return super()._get_model(doc, root, parent, comm)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        return inspect.ismethod(obj) and isinstance(get_method_owner(obj), param.Parameterized)



class ParamFunction(ParamMethod):
    """
    ParamFunction panes wrap functions decorated with the param.depends
    decorator and rerenders the output when any of the function's
    dependencies change. This allows building reactive components into
    a Panel which depend on other parameters, e.g. tying the value of
    a widget to some other output.
    """

    priority: ClassVar[float | bool | None] = 0.6

    def _link_object_params(self):
        deps = getattr(self.object, '_dinfo', {})
        dep_params = list(deps.get('dependencies', [])) + list(deps.get('kw', {}).values())
        if not dep_params and not self.lazy:
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
            self._callbacks.append(watcher)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        if isinstance(obj, types.FunctionType):
            if hasattr(obj, '_dinfo'):
                return True
            return None
        return False


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
        warnobj = param.main if isinstance(parameterized, type) else parameterized
        param_class = (parameterized if isinstance(parameterized, type)
                       else parameterized.__class__)

        target = self.target if self.target is not None else param_class.__name__

        env_var = os.environ.get(self.varname, None)
        if env_var is None and self.json_file is None: return

        if self.json_file or env_var.endswith('.json'):
            try:
                fname = self.json_file if self.json_file else env_var
                with open(fullpath(fname), 'r') as f:
                    spec = json.load(f)
            except Exception:
                warnobj.warning('Could not load JSON file %r' % spec)
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
            for cb in method._callbacks:
                pobj = cb.cls if cb.inst is None else cb.inst
                if widget._param_pane.object is pobj and widget._param_name in cb.parameter_names:
                    if isinstance(widget, DiscreteSlider):
                        w = widget._slider
                    else:
                        w = widget
                    if 'value' in w._linkable_params:
                        w.jslink(method._inner_layout, value='loading')


Viewable._preprocessing_hooks.insert(0, link_param_method)

__all__= (
    "Param",
    "ParamFunction",
    "ParamMethod",
    "set_values"
)
