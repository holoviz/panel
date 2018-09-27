"""
Defines the Param pane which converts Parameterized classes into a
set of widgets.
"""
from __future__ import absolute_import

import os
import json
import types
import itertools
from collections import OrderedDict

import param
from param.parameterized import classlist

from .pane import PaneBase
from .layout import WidgetBox, Row, Layout, Tabs
from .util import default_label_formatter, is_parameterized
from .widgets import (
    LiteralInput, Select, Checkbox, FloatSlider, IntSlider, RangeSlider,
    MultiSelect, StaticText, Button, Toggle, TextInput, DiscreteSlider,
    DatetimeInput
)


def ObjectSelector(pobj):
    """
    Determines param.ObjectSelector widget depending on whether all values
    are numeric.
    """
    options = list(pobj.objects.values()) if isinstance(pobj.objects, dict) else pobj.objects
    if all(param._is_number(o) for o in options):
        return DiscreteSlider
    else:
        return Select


class Param(PaneBase):
    """
    Param panes render a Parameterized class to a set of widgets which
    are linked to the parameter values on the class.
    """

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    show_labels = param.Boolean(default=True)

    subpanel_layout = param.ClassSelector(default=Row, class_=Layout,
                                          is_instance=False, doc="""
        Layout of subpanels.""")

    display_threshold = param.Number(default=0,precedence=-10,doc="""
        Parameters with precedence below this value are not displayed.""")

    default_precedence = param.Number(default=1e-8,precedence=-10,doc="""
        Precedence value to use for parameters with no declared precedence.
        By default, zero predecence is available for forcing some parameters
        to the top of the list, and other values above the default_precedence
        values can be used to sort or group parameters arbitrarily.""")

    initializer = param.Callable(default=None, doc="""
        User-supplied function that will be called on initialization,
        usually to update the default Parameter values of the
        underlying parameterized object.""")

    width = param.Integer(default=300, bounds=(0, None), doc="""
        Width of widgetbox the parameter widgets are displayed in.""")

    label_formatter = param.Callable(default=default_label_formatter, allow_None=True,
        doc="Callable used to format the parameter names into widget labels.")

    precedence = 0.1

    _mapping = {
        param.Action:         Button,
        param.Parameter:      LiteralInput,
        param.Dict:           LiteralInput,
        param.Selector:       Select,
        param.ObjectSelector: ObjectSelector,
        param.Boolean:        Checkbox,
        param.Number:         FloatSlider,
        param.Integer:        IntSlider,
        param.Range:          RangeSlider,
        param.String:         TextInput,
        param.ListSelector:   MultiSelect,
        param.Date:           DatetimeInput,
    }

    def __init__(self, object, **params):
        if isinstance(object, param.parameterized.Parameters):
            object = object.cls if object.self is None else object.self
        if 'name' not in params:
            params['name'] = object.name
        super(Param, self).__init__(object, **params)
        self._widgets = self._get_widgets()
        widgets = [widget for widgets in self._widgets.values() for widget in widgets]
        self._widget_box = WidgetBox(*widgets, height=self.height,
                                     width=self.width, name=self.name)
        kwargs = {'name': self.name}
        if self.subpanel_layout is Tabs:
            kwargs['width'] = self.width
        self._layout = self.subpanel_layout(self._widget_box, **kwargs)
        self._link_subpanels()

    def _link_subpanels(self):
        for pname, widget in self._widgets.items():
            if len(widget) < 2: continue
            selector, toggle = widget

            def toggle_pane(change, parameter=pname):
                "Adds or removes subpanel from layout"
                parameterized = getattr(self.object, parameter)
                existing = [p for p in self._layout.objects
                            if isinstance(p, Param)
                            and p.object is parameterized]
                if existing:
                    old_panel = existing[0]
                    if not change.new:
                        old_panel._cleanup(final=old_panel._temporary)
                        self._layout.pop(old_panel)
                elif change.new:
                    kwargs = {k: v for k, v in self.get_param_values()
                              if k not in ['name', 'object']}
                    pane = Param(parameterized, name=parameterized.name,
                                 _temporary=True, **kwargs)
                    self._layout.append(pane)

            def update_pane(change, parameter=pname):
                "Adds or removes subpanel from layout"
                existing = [p for p in self._layout.objects
                            if isinstance(p, Param)
                            and p.object is change.old]

                toggle.disabled = not is_parameterized(change.new)
                if not existing:
                    return
                elif is_parameterized(change.new):
                    parameterized = change.new
                    kwargs = {k: v for k, v in self.get_param_values()
                              if k not in ['name', 'object']}
                    pane = Param(parameterized, name=parameterized.name,
                                 _temporary=True, **kwargs)
                    self._layout[self._layout.objects.index(existing[0])] = pane
                else:
                    self._layout.pop(existing[0])

            toggle_watcher = toggle.param.watch(toggle_pane, 'active')
            selector_watcher = selector.param.watch(update_panes, 'value')
            self._callbacks['instance'] += [toggle_watcher, selector_watcher]

    @classmethod
    def applies(cls, obj):
        return (is_parameterized(obj) or isinstance(obj, param.parameterized.Parameters))

    def widget_type(cls, pobj):
        ptype = type(pobj)
        for t in classlist(ptype)[::-1]:
            if t in cls._mapping:
                if isinstance(cls._mapping[t], types.FunctionType):
                    return cls._mapping[t](pobj)
                return cls._mapping[t]

    def widget(self, p_name):
        """Get widget for param_name"""
        p_obj = self.object.params(p_name)

        widget_class = self.widget_type(p_obj)
        value = getattr(self.object, p_name)

        kw = dict(value=value, disabled=p_obj.constant)

        if self.label_formatter is not None:
            kw['name'] = self.label_formatter(p_name)
        else:
            kw['name'] = p_name

        if hasattr(p_obj, 'get_range'):
            kw['options'] = p_obj.get_range()

        if hasattr(p_obj, 'get_soft_bounds'):
            bounds = p_obj.get_soft_bounds()
            if bounds[0] is not None:
                kw['start'] = bounds[0]
            if bounds[1] is not None:
                kw['end'] = bounds[1]
            if ('start' not in kw or 'end' not in kw) and not issubclass(widget_class, LiteralInput):
                widget_class = LiteralInput

        kwargs = {k: v for k, v in kw.items() if k in widget_class.params()}
        widget = widget_class(**kwargs)
        watchers = self._callbacks['instance']
        if isinstance(p_obj, param.Action):
            widget.button_type = 'success'
            def action(change):
                value(self.object)
            watchers.append(widget.param.watch(action, 'clicks'))
        elif isinstance(widget, Toggle):
            pass
        else:
            widget.link(self.object, **{'value': p_name})
            def link(change, _updating=[]):
                key = (change.name, change.what)
                if key in _updating:
                    return

                _updating.append(key)
                updates = {}
                if change.what == 'constant':
                    updates['disabled'] = change.new
                elif change.what == 'objects':
                    updates['options'] = p_obj.get_range()
                elif change.what == 'bounds':
                    start, end = p_obj.get_soft_bounds()
                    updates['start'] = start
                    updates['end'] = end
                else:
                    updates['value'] = change.new
                widget.set_param(**updates)
                _updating.pop(_updating.index(key))

            # Set up links to parameterized object
            watchers.append(self.object.param.watch(link, p_name, 'constant'))
            watchers.append(self.object.param.watch(link, p_name))
            if hasattr(p_obj, 'get_range'):
                watchers.append(self.object.param.watch(link, p_name, 'objects'))
            if hasattr(p_obj, 'get_soft_bounds'):
                watchers.append(self.object.param.watch(link, p_name, 'bounds'))

        options = kwargs.get('options', [])
        if isinstance(options, dict):
            options = options.values()
        if is_parameterized(value) or any(is_parameterized(o) for o in options):
            toggle = Toggle(name='...', button_type='primary',
                            disabled=not is_parameterized(value))
            return [widget, toggle]
        else:
            return [widget]

    def _cleanup(self, model=None, final=False):
        self._layout._cleanup(model, final)
        super(Param, self)._cleanup(model, final)

    def _get_widgets(self):
        """Return name,widget boxes for all parameters (i.e., a property sheet)"""
        params = self.object.params().items()
        key_fn = lambda x: x[1].precedence if x[1].precedence is not None else self.default_precedence
        sorted_precedence = sorted(params, key=key_fn)
        filtered = [(k,p) for (k,p) in sorted_precedence
                    if ((p.precedence is None) or (p.precedence >= self.display_threshold))]
        groups = itertools.groupby(filtered, key=key_fn)
        sorted_groups = [sorted(grp) for (k,grp) in groups]
        ordered_params = [el[0] for group in sorted_groups for el in group]

        # Format name specially
        ordered_params.pop(ordered_params.index('name'))
        if self.subpanel_layout is Tabs:
            widgets = []
        else:
            widgets = [('name', [StaticText(value='<b>{0}</b>'.format(self.object.name))])]
        widgets += [(pname, self.widget(pname)) for pname in ordered_params]
        return OrderedDict(widgets)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        return self._layout._get_model(doc, root, parent, comm)

    def _get_root(self, doc, comm=None):
        return self._get_model(doc, comm=comm)



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
                spec = json.load(open(os.path.abspath(fname), 'r'))
            except:
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
               parameterized.set_param(**{name:value})
           except ValueError as e:
               warnobj.warning(str(e))
