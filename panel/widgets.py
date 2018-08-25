import ast
import functools

import param
from bokeh.models import WidgetBox
from bokeh.models.widgets import (
    Button, TextInput as BkTextInput, Div, Slider, CheckboxGroup,
    DateRangeSlider as BkDateRangeSlider, RangeSlider as BkRangeSlider,
    DatePicker as BkDatePicker, MultiSelect as BkMultiSelect, Select as BkSelect
)
from .viewable import Reactive, Viewable
from .util import push, as_unicode, named_objs

from functools import partial

import param

from bokeh.document import Document
from bokeh.io import curdoc, show
from bokeh.models import LayoutDOM, CustomJS
from pyviz_comms import JS_CALLBACK, JupyterCommManager

from .util import render_mimebundle, add_to_doc, get_method_owner, push, Div



class Widget(Reactive):
    """
    Widgets allow syncing changes in bokeh widget models with the
    parameters on the Widget instance.
    """

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    __abstract = True

    _widget_type = None

    # Mapping from parameter name to bokeh model property name
    _renames = {}

    def __init__(self, **params):
        if 'name' not in params:
            params['name'] = ''
        super(Widget, self).__init__(**params)
        self._active = False
        self._events = {}

    def _init_properties(self):
        properties = {k: v for k, v in self.param.get_param_values()
                      if v is not None}
        properties['title'] = self.name
        return self._process_param_change(properties)

    def _process_property_change(self, msg):
        """
        Transform bokeh model property changes into parameter updates.
        """
        inverted = {v: k for k, v in self._renames}
        return {inverted.get(k, k): v for k, v in msg.items()}

    def _process_param_change(self, msg):
        """
        Transform parameter changes into bokeh model property updates.
        """
        return {self._renames.get(k, k): v for k, v in msg.items()}

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = self._widget_type(**self._init_properties())
        params = [p for p in self.params() if p != 'name']
        plot_id = root.ref['id']
        properties = list(self._process_param_change(dict(self.get_param_values())))
        self._link_params(model, properties, doc, plot_id, comm)
        self._link_props(model, params, doc, plot_id, comm)
        return model

    def _get_root(self, doc, comm=None):
        root = WidgetBox()
        model = self._get_model(doc, root, root, comm)
        root.children = [model]
        return root



class TextInput(Widget):

    value = param.String(default='')

    _widget_type = BkTextInput


class FloatSlider(Widget):

    start = param.Number(default=0.0)

    end = param.Number(default=1.0)

    value = param.Number(default=0.0)

    step = param.Number(default=0.1)

    _widget_type = Slider


class IntSlider(Widget):

    value = param.Integer(default=0)

    start = param.Integer(default=0)

    end = param.Integer(default=1)

    _widget_type = Slider

    def _init_properties(self):
        properties = super(IntSlider, self)._init_properties()
        properties['step'] = 1
        return properties


class DatePicker(Widget):

    value = param.Date(default=None)

    start = param.Date(default=None)

    end = param.Date(default=None)

    _widget_type = BkDatePicker

    _renames = {'start': 'min_date', 'end': 'max_date'}


class RangeSlider(Widget):

    value = param.NumericTuple(default=(0, 1), length=2)

    start = param.Number(default=0)

    end = param.Number(default=1)

    step = param.Number(default=0.1)

    _widget_type = BkRangeSlider

    def _process_param_change(self, msg):
        if 'value' in msg:
            msg['value'] = tuple(msg['value'])
        return msg


class DateWidget(Widget):

    value = param.Date(default=None)

    start = param.Date(default=None)

    end = param.Date(default=None)

    _widget_type = BkDatePicker

    _renames = {'start': 'min_date', 'end': 'max_date'}


class DateRangeSlider(Widget):

    value = param.Tuple(default=None, length=2)

    start = param.Date(default=None)

    end = param.Date(default=None)

    step = param.Number(default=1)

    _widget_type = BkDateRangeSlider


class DatePicker(Widget):

    value = param.Date(default=None)

    start = param.Date(default=None)

    end = param.Date(default=None)

    _widget_type = BkDatePicker

    _renames = {'start': 'min_date', 'end': 'max_date'}


class LiteralInput(Widget):

    value = param.Parameter(default=None)

    _widget_type = BkTextInput

    def _process_property_change(self, msg):
        if 'value' in msg:
            msg['value'] = ast.literal_eval(msg['value'])
        return msg

    def _process_param_change(self, msg):
        if 'value' in msg:
            msg['value'] = as_unicode(msg['value'])
        return msg


class Checkbox(Widget):

    value = param.Boolean(default=False)

    _widget_type = CheckboxGroup

    def _init_properties(self):
        properties = super(Checkbox, self)._init_properties()
        properties = self._process_param_change(properties)
        properties['labels'] = [properties.pop('name')]
        return properties

    def _process_property_change(self, msg):
        if 'active' in msg:
            msg['value'] = 0 in msg.pop('active')
        return msg

    def _process_param_change(self, msg):
        if 'value' in msg:
             msg['active'] = [0] if msg.pop('value', None) else []
        if 'title' in msg:
            msg['labels'] = [msg.pop('title')]
        return msg


class Select(Widget):

    options = param.List(default=[])

    value = param.Parameter(default=None)

    _widget_type = BkSelect

    def _process_property_change(self, msg):
        mapping = {as_unicode(o): o for o in self.options}
        if 'value' in msg:
            msg['value'] = mapping[msg['value']]
        return msg

    def _process_param_change(self, msg):
        mapping = {o: as_unicode(o) for o in self.options}
        if msg.get('value', None) is not None:
            msg['value'] = mapping[msg['value']]
        if 'options' in msg:
            msg['options'] = [mapping[o] for o in msg['options']]
        return msg


class MultiSelect(Select):

    options = param.List(default=[])

    value = param.List(default=[])

    _widget_type = BkMultiSelect

    def _process_param_change(self, msg):
        mapping = {o: as_unicode(o) for o in self.options}
        if 'value' in msg:
            msg['value'] = [mapping[v] for v in msg['value']]
        if 'options' in msg:
            msg['options'] = [mapping[o] for o in msg['options']]
        return msg

    def _process_property_change(self, msg):
        mapping = {as_unicode(o): o for o in self.options}
        if 'value' in msg:
            msg['value'] = [mapping[v] for v in msg['value']]
        return msg
