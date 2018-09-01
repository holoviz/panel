"""
Provides a set of reactive widgets which provide bi-directional
communication between the rendered dashboard and the Widget parameters.
"""
from __future__ import absolute_import

import ast
from collections import OrderedDict

import param
from bokeh.models import WidgetBox as _BkWidgetBox
from bokeh.models.widgets import (
    TextInput as _BkTextInput, Select as _BkSelect, Slider, CheckboxGroup,
    DateRangeSlider as _BkDateRangeSlider, RangeSlider as _BkRangeSlider,
    DatePicker as _BkDatePicker, MultiSelect as _BkMultiSelect,
    Div as _BkDiv, Button as _BkButton, Toggle as _BkToggle
)

from .layout import WidgetBox # noqa
from .viewable import Reactive
from .util import as_unicode


class Widget(Reactive):
    """
    Widgets allow syncing changes in bokeh widget models with the
    parameters on the Widget instance.
    """

    disabled = param.Boolean(default=False, doc="""
       Whether the widget is disabled.""")

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    __abstract = True

    _widget_type = None

    _rename = {'name': 'title'}

    def __init__(self, **params):
        if 'name' not in params:
            params['name'] = ''
        super(Widget, self).__init__(**params)

    def _init_properties(self):
        properties = {k: v for k, v in self.param.get_param_values()
                      if v is not None}
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
        msg = super(StaticText, self)._process_property_change(msg)
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

    _rename = {'start': 'min_date', 'end': 'max_date'}


class RangeSlider(Widget):

    value = param.NumericTuple(default=(0, 1), length=2)

    start = param.Number(default=0)

    end = param.Number(default=1)

    step = param.Number(default=0.1)

    _widget_type = _BkRangeSlider

    def _process_param_change(self, msg):
        msg = super(RangeSlider, self)._process_param_change(msg)
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
        msg = super(LiteralInput, self)._process_property_change(msg)
        if 'name' in msg:
            msg['name'] = msg.pop('title').replace(self._state, '')
        if 'value' in msg:
            value = msg.pop('value')
            try:
                value = ast.literal_eval(value)
            except:
                self._state = ' (invalid)'
                value = self.value
            else:
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

    def _process_property_change(self, msg):
        msg = super(Checkbox, self)._process_property_change(msg)
        if 'active' in msg:
            msg['value'] = 0 in msg.pop('active')
        return msg

    def _process_param_change(self, msg):
        msg = super(Checkbox, self)._process_param_change(msg)
        if 'value' in msg:
             msg['active'] = [0] if msg.pop('value', None) else []
        if 'title' in msg:
            msg['labels'] = [msg.pop('title')]
        return msg


class Select(Widget):

    options = param.Dict(default={})

    value = param.Parameter(default=None)

    _widget_type = _BkSelect

    def __init__(self, **params):
        options = params.get('options', None)
        if isinstance(options, list):
            params['options'] = OrderedDict([(as_unicode(o), o) for o in options])
        super(Select, self).__init__(**params)

    def _process_param_change(self, msg):
        msg = super(Select, self)._process_param_change(msg)
        mapping = {v: k for k, v in self.options.items()}
        if msg.get('value') is not None:
            msg['value'] = mapping[msg['value']]
        if 'options' in msg:
            msg['options'] = list(msg['options'])
        return msg

    def _process_property_change(self, msg):
        msg = super(Select, self)._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = self.options[msg['value']]
        return msg


class MultiSelect(Select):

    value = param.List(default=[])

    _widget_type = _BkMultiSelect

    def _process_param_change(self, msg):
        msg = super(Select, self)._process_param_change(msg)
        mapping = {v: k for k, v in self.options.items()}
        if 'value' in msg:
            msg['value'] = [mapping[v] for v in msg['value']]
        if 'options' in msg:
            msg['options'] = list(msg['options'])
        return msg

    def _process_property_change(self, msg):
        msg = super(Select, self)._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = [self.options[v] for v in msg['value']]
        return msg


class _ButtonBase(Widget):

    button_type = param.ObjectSelector(default='default', objects=[
        'default', 'primary', 'success', 'info', 'danger'])

    _rename = {'name': 'label'}


class Button(_ButtonBase):

    clicks = param.Integer(default=0)

    _widget_type = _BkButton


class Toggle(_ButtonBase):

    active = param.Boolean(default=False, doc="""
        Whether the button is currently toggled.""")

    _widget_type = _BkToggle
