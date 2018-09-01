"""
Defines the ParamPanel which converts Parameterized classes into a
set of widgets.
"""
from __future__ import absolute_import

import os
import json
import itertools

import param
from param.parameterized import classlist
from bokeh.models import Div

from .panels import PanelBase, Panel
from .layout import WidgetBox
from .util import default_label_formatter
from .widgets import (
    LiteralInput, Select, Checkbox, FloatSlider, IntSlider, RangeSlider,
    MultiSelect, DatePicker, StaticText, Button
)


class ParamPanel(PanelBase):
    """
    ParamPanel renders a Parameterized class to a set of widgets which
    are linke to the parameter values on the class.
    """

    show_labels = param.Boolean(default=True)

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

    precedence = 1

    _mapping = {
        param.Action:        Button,
        param.Parameter:     LiteralInput,
        param.Dict:          LiteralInput,
        param.Selector:      Select,
        param.Boolean:       Checkbox,
        param.Number:        FloatSlider,
        param.Integer:       IntSlider,
        param.Range:         RangeSlider,
        param.ListSelector:  MultiSelect,
        param.Date:          DatePicker,
    }

    @classmethod
    def applies(cls, obj):
        return isinstance(obj, param.Parameterized)

    def widget_type(cls, pobj):
        for t in classlist(type(pobj))[::-1]:
            if t in cls._mapping:
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

        if hasattr(p_obj, 'get_range') and not isinstance(kw['value'], dict):
            kw['options'] = p_obj.get_range()

        if hasattr(p_obj, 'get_soft_bounds'):
            bounds = p_obj.get_soft_bounds()
            if None not in bounds:
                kw['start'], kw['end'] = bounds
            else:
                widget_class = StaticText

        kwargs = {k: v for k, v in kw.items() if k in widget_class.params()}
        widget = widget_class(**kwargs)
        if isinstance(p_obj, param.Action):
            def action(change):
                value(self.object)
            widget.param.watch(action, 'clicks')
        else:
            widget.link(self.object, **{'value': p_name})
            def link(change, _updating=[]):
                if change.attribute not in _updating:
                    _updating.append(change.attribute)
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
                    _updating.pop(_updating.index(change.attribute))
            self.object.param.watch(link, p_name, 'constant')
            self.object.param.watch(link, p_name)
            if hasattr(p_obj, 'get_range'):
                self.object.param.watch(link, p_name, 'objects')
            if hasattr(p_obj, 'get_soft_bounds'):
                self.object.param.watch(link, p_name, 'bounds')
        return widget

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
        widgets = [Panel(Div(text='<b>{0}</b>'.format(self.object.name)))]
        widgets += [self.widget(pname) for pname in ordered_params]
        return widgets

    def _get_model(self, doc, root=None, parent=None, comm=None):
        panels = self._get_widgets()
        return WidgetBox(*panels)._get_model(doc, root, parent, comm)

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
