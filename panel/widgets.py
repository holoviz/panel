"""
Provides a set of reactive widgets which provide bi-directional
communication between the rendered dashboard and the Widget parameters.
"""
from __future__ import absolute_import

import ast

import param
from bokeh.models import WidgetBox as _BkWidgetBox
from bokeh.models.widgets import (
    TextInput as _BkTextInput, Select as _BkSelect, Slider, CheckboxGroup,
    DateRangeSlider as _BkDateRangeSlider, RangeSlider as _BkRangeSlider,
    DatePicker as _BkDatePicker, MultiSelect as _BkMultiSelect, Div as _BkDiv
)

from .layout import WidgetBox # noqa
from .viewable import Reactive
from .util import as_unicode



class Widget(Reactive):
    """
    Widgets allow syncing changes in bokeh widget models with the
    parameters on the Widget instance.
    """

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    __abstract = True

    _widget_type = None


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

    def _get_model(self, doc, root=None, parent=None, comm=None):
        in_box = isinstance(parent, _BkWidgetBox)
        if not in_box:
            parent = _BkWidgetBox()
        root = parent if root is None else root

        model = self._widget_type(**self._init_properties())

        # Link parameters and bokeh model
        params = [p for p in self.params()]
        properties = list(self._process_param_change(dict(self.get_param_values())))
        self._link_params(model, params, doc, root, comm)
        self._link_props(model, properties, doc, root, comm)

        if not in_box:
            parent.children = [model]
            return parent
        return model



class TextInput(Widget):

    value = param.String(default='')

    placeholder = param.String(default='')

    _widget_type = _BkTextInput


class StaticText(Widget):

    value = param.Parameter(default=None)

    _widget_type = _BkDiv

    _format = '<b>{title}</b>: {value}'

    def _process_param_change(self, msg):
        msg.pop('name', None)
        msg.pop('title', None)
        if 'value' in msg:
            value = msg.pop('value')
            text = self._format.format(title=self.name, value=as_unicode(value))
            msg['text'] = text
        return msg


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

    _widget_type = _BkDatePicker

    _renames = {'start': 'min_date', 'end': 'max_date'}


class RangeSlider(Widget):

    value = param.NumericTuple(default=(0, 1), length=2)

    start = param.Number(default=0)

    end = param.Number(default=1)

    step = param.Number(default=0.1)

    _widget_type = _BkRangeSlider

    def _process_param_change(self, msg):
        if 'value' in msg:
            msg['value'] = tuple(msg['value'])
        return msg


class DateRangeSlider(Widget):

    value = param.Tuple(default=None, length=2)

    start = param.Date(default=None)

    end = param.Date(default=None)

    step = param.Number(default=1)

    _widget_type = _BkDateRangeSlider


class LiteralInput(Widget):
    """
    LiteralInput allows declaring Python literals using a text
    input widget. Optionally a type may be declared.
    """

    type = param.ClassSelector(default=None, class_=type,
                               is_instance=True)

    value = param.Parameter(default=None)

    _widget_type = _BkTextInput

    def __init__(self, **params):
        super(LiteralInput, self).__init__(**params)
        self._state = ''

    def _process_property_change(self, msg):
        if 'title' in msg:
            msg['name'] = msg.pop('title').replace(self._state, '')
        if 'value' in msg:
            value = msg.pop('value')
            try:
                value = ast.literal_eval(value)
            except:
                self._state = ' (invalid)'
                value = self.value

            if self.type and not isinstance(value, self.type):
                self._state = ' (wrong type)'
                value = self.value
            else:
                self._state = ''
            msg['value'] = value
        return msg

    def _process_param_change(self, msg):
        msg.pop('type', None)
        if 'value' in msg:
            msg['value'] = '' if msg['value'] is None else as_unicode(msg['value'])
        msg['title'] = self.name + self._state
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

    _widget_type = _BkSelect

    def _process_property_change(self, msg):
        mapping = {as_unicode(o): o for o in self.options}
        if 'value' in msg:
            msg['value'] = mapping[msg['value']]
        return msg

    def _process_param_change(self, msg):
        mapping = {o: as_unicode(o) for o in self.options}
        if msg.get('value') is not None:
            msg['value'] = mapping[msg['value']]
        if 'options' in msg:
            msg['options'] = [mapping[o] for o in msg['options']]
        return msg


class MultiSelect(Select):

    options = param.List(default=[])

    value = param.List(default=[])

    _widget_type = _BkMultiSelect

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
