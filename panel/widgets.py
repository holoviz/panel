"""
Provides a set of reactive widgets which provide bi-directional
communication between the rendered dashboard and the Widget parameters.
"""
from __future__ import absolute_import

import ast
from collections import OrderedDict
from datetime import datetime

import param
import numpy as np
from bokeh.models import WidgetBox as _BkWidgetBox
from bokeh.models.widgets import (
    TextInput as _BkTextInput, Select as _BkSelect, Slider as _BkSlider,
    CheckboxGroup as _BkCheckboxGroup, DateRangeSlider as _BkDateRangeSlider,
    RangeSlider as _BkRangeSlider, DatePicker as _BkDatePicker,
    MultiSelect as _BkMultiSelect, Div as _BkDiv,Button as _BkButton,
    Toggle as _BkToggle, AutocompleteInput as _BkAutocompleteInput,
    CheckboxButtonGroup as _BkCheckboxButtonGroup
)

from .layout import WidgetBox # noqa
from .models.widgets import Player as _BkPlayer
from .viewable import Reactive
from .util import as_unicode, push, value_as_datetime, hashable


class Widget(Reactive):
    """
    Widgets allow syncing changes in bokeh widget models with the
    parameters on the Widget instance.
    """

    disabled = param.Boolean(default=False, doc="""
       Whether the widget is disabled.""")

    name = param.String(default='')

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
        self._models[root.ref['id']] = model
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
            text = as_unicode(msg.pop('value'))
            if self.name:
                text = self._format.format(title=self.name, value=text)
            msg['text'] = text
        return msg


class AutocompleteInput(Widget):

    options = param.List(default=[])

    placeholder = param.String(default='')

    value = param.Parameter(default=None)

    _widget_type = _BkAutocompleteInput

    _rename = {'name': 'title', 'options': 'completions'}


class FloatSlider(Widget):

    start = param.Number(default=0.0)

    end = param.Number(default=1.0)

    value = param.Number(default=0.0)

    step = param.Number(default=0.1)

    _widget_type = _BkSlider


class IntSlider(Widget):

    value = param.Integer(default=0)

    start = param.Integer(default=0)

    end = param.Integer(default=1)

    step = param.Integer(default=1)

    _widget_type = _BkSlider


class DatePicker(Widget):

    value = param.Date(default=None)

    start = param.Date(default=None)

    end = param.Date(default=None)

    _widget_type = _BkDatePicker

    _rename = {'start': 'min_date', 'end': 'max_date', 'name': 'title'}

    def _process_property_change(self, msg):
        msg = super(DatePicker, self)._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = datetime.strptime(msg['value'][4:], '%b %d %Y')
        return msg


class RangeSlider(Widget):

    value = param.NumericTuple(default=(0, 1), length=2)

    start = param.Number(default=0)

    end = param.Number(default=1)

    step = param.Number(default=0.1)

    _widget_type = _BkRangeSlider

    def __init__(self, **params):
        super(RangeSlider, self).__init__(**params)
        values = [self.value[0], self.value[1], self.start, self.end]
        if (all(v is None or isinstance(v, int) for v in values) and
            'step' not in params):
            self.step = 1

    def _process_property_change(self, msg):
        msg = super(RangeSlider, self)._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = tuple(msg['value'])
        return msg


class IntRangeSlider(Widget):

    start = param.Integer(default=0)

    end = param.Integer(default=1)

    step = param.Integer(default=1)


class DateRangeSlider(Widget):

    value = param.Tuple(default=None, length=2)

    start = param.Date(default=None)

    end = param.Date(default=None)

    step = param.Number(default=1)

    _widget_type = _BkDateRangeSlider

    def _process_property_change(self, msg):
        msg = super(DateRangeSlider, self)._process_property_change(msg)
        if 'value' in msg:
            v1, v2 = msg['value']
            msg['value'] = (value_as_datetime(v1), value_as_datetime(v2))
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
        self._validate(None)
        self.param.watch(self._validate, 'value')

    def _validate(self, event):
        if self.type is None: return
        new = self.value
        if not isinstance(new, self.type):
            if event:
                self.value = event.old
            raise ValueError('LiteralInput expected %s type but value %s '
                             'is of type %s.' %
                             (self.type.__name__, new, type(new).__name__))

    def _process_property_change(self, msg):
        msg = super(LiteralInput, self)._process_property_change(msg)
        new_state = ''
        if 'value' in msg:
            value = msg.pop('value')
            try:
                value = ast.literal_eval(value)
            except:
                new_state = ' (invalid)'
                value = self.value
            else:
                if self.type and not isinstance(value, self.type):
                    new_state = ' (wrong type)'
                    value = self.value
            msg['value'] = value
        msg['name'] = msg.get('title', self.name).replace(self._state, '') + new_state
        self._state = new_state
        return msg

    def _process_param_change(self, msg):
        msg.pop('type', None)
        if 'value' in msg:
            msg['value'] = '' if msg['value'] is None else as_unicode(msg['value'])
        msg['title'] = self.name
        return msg


class DatetimeInput(LiteralInput):
    """
    DatetimeInput allows declaring Python literals using a text
    input widget. Optionally a type may be declared.
    """

    format = param.String(default='%Y-%m-%d %H:%M:%S', doc="""
        Datetime format used for parsing and formatting the datetime.""")

    value = param.Date(default=None)

    start = param.Date(default=None)

    end = param.Date(default=None)

    type = datetime

    def __init__(self, **params):
        super(DatetimeInput, self).__init__(**params)
        self.param.watch(self._validate, 'value')
        self._validate(None)

    def _validate(self, event):
        new = self.value
        if new is not None and ((self.start is not None and self.start > new) or
                                (self.end is not None and self.end < new)):
            value = datetime.strftime(new, self.format)
            start = datetime.strftime(self.start, self.format)
            end = datetime.strftime(self.end, self.format)
            if event:
                self.value = event.old
            raise ValueError('DatetimeInput value must be between {start} and {end}, '
                             'supplied value is {value}'.format(start=start, end=end,
                                                                value=value))

    def _process_property_change(self, msg):
        msg = Widget._process_property_change(self, msg)
        new_state = ''
        if 'value' in msg:
            value = msg.pop('value')
            try:
                value = datetime.strptime(value, self.format)
            except:
                new_state = ' (invalid)'
                value = self.value
            else:
                if value is not None and ((self.start is not None and self.start > value) or
                                          (self.end is not None and self.end < value)):
                    new_state = ' (out of bounds)'
                    value = self.value
            msg['value'] = value
        msg['name'] = msg.get('title', self.name).replace(self._state, '') + new_state
        self._state = new_state
        return msg

    def _process_param_change(self, msg):
        msg = {k: v for k, v in msg.items() if k not in ('type', 'format', 'start', 'end')}
        if 'value' in msg:
            value = msg['value']
            if value is None:
                value = ''
            else:
                value = datetime.strftime(msg['value'], self.format)
            msg['value'] = value
        msg['title'] = self.name
        return msg


class Checkbox(Widget):

    value = param.Boolean(default=False)

    _widget_type = _BkCheckboxGroup

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
        options = list(self.options.values())
        if self.value is None and None not in options:
            self.value = options[0]

    def _process_param_change(self, msg):
        msg = super(Select, self)._process_param_change(msg)
        mapping = {hashable(v): k for k, v in self.options.items()}
        if msg.get('value') is not None:
            msg['value'] = mapping[hashable(msg['value'])]
        if 'options' in msg:
            msg['options'] = list(msg['options'])
        return msg

    def _process_property_change(self, msg):
        msg = super(Select, self)._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = self.options[msg['value']]
        msg.pop('options', None)
        return msg


class RadioButtons(Select):

    value = param.List(default=[])

    _widget_type = _BkCheckboxGroup

    def _process_param_change(self, msg):
        msg = super(Select, self)._process_param_change(msg)
        mapping = OrderedDict([(hashable(v), k) for k, v in self.options.items()])
        if msg.get('value') is not None:
            msg['active'] = [list(mapping).index(v) for v in msg.pop('value')]
        if 'options' in msg:
            msg['labels'] = list(msg.pop('options'))
        msg.pop('title', None)
        return msg

    def _process_property_change(self, msg):
        msg = super(Select, self)._process_property_change(msg)
        if msg.get('active', []):
            msg['value'] = [list(self.options.values())[a] for a in msg.pop('active')]
        return msg


class ToggleButtons(RadioButtons):

    _widget_type = _BkCheckboxButtonGroup


class MultiSelect(Select):

    size = param.Integer(default=4, doc="""
        The number of items displayed at once (i.e. determines the
        widget height).""")

    value = param.List(default=[])

    _widget_type = _BkMultiSelect

    def _process_param_change(self, msg):
        msg = super(Select, self)._process_param_change(msg)
        mapping = {hashable(v): k for k, v in self.options.items()}
        if 'value' in msg:
            msg['value'] = [hashable(mapping[v]) for v in msg['value']]
        if 'options' in msg:
            msg['options'] = list(msg['options'])
        return msg

    def _process_property_change(self, msg):
        msg = super(Select, self)._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = [self.options[v] for v in msg['value']]
        msg.pop('options', None)
        return msg


class DiscreteSlider(Widget):

    options = param.ClassSelector(default=[], class_=(dict, list))

    value = param.Parameter()

    formatter = param.String(default='%.3g')

    def __init__(self, **params):
        super(DiscreteSlider, self).__init__(**params)
        if 'formatter' not in params and all(isinstance(v, (int, np.int_)) for v in self.values):
            self.formatter = '%d'
        if self.value is None and None not in self.values:
            self.value = self.values[0]
        elif self.value not in self.values:
            raise ValueError('Value %s not a valid option, '
                             'ensure that the supplied value '
                             'is one of the declared options.'
                             % self.value)

    @property
    def labels(self):
        title = '<b>%s</b>: ' % (self.name if self.name else '')
        if isinstance(self.options, dict):
            return [title + o for o in self.options]
        else:
            return [title + (self.formatter % o) for o in self.options]

    @property
    def values(self):
        return list(self.options.values()) if isinstance(self.options, dict) else self.options

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = _BkWidgetBox()
        parent = parent or model
        root = root or parent
        msg = self._init_properties()
        div = _BkDiv(text=msg['text'])
        slider = _BkSlider(start=msg['start'], end=msg['end'], value=msg['value'],
                           title=None, step=1, show_value=False, tooltips=None)

        # Link parameters and bokeh model
        self._link_params(model, slider, div, ['value', 'options'], doc, root, comm)
        self._link_props(slider, ['value'], doc, root, comm)

        model.children = [div, slider]
        self._models[root.ref['id']] = model
        
        return model

    def _link_params(self, model, slider, div, params, doc, root, comm=None):
        def param_change(*events):
            combined_msg = {}
            for event in events:
                msg = self._process_param_change({event.name: event.new})
                msg = {k: v for k, v in msg.items() if k not in self._active}
                if msg:
                    combined_msg.update(msg)

            if not combined_msg:
                return

            def update_model():
                slider.update(**{k: v for k, v in combined_msg.items()
                                 if k in slider.properties()})
                div.update(**{k: v for k, v in combined_msg.items()
                              if k in div.properties()})

            if comm:
                update_model()
                push(doc, comm)
            else:
                doc.add_next_tick_callback(update_model)

        ref = root.ref['id']
        for p in params:
            self._callbacks[ref].append(self.param.watch(param_change, p))

    def _process_param_change(self, msg):
        title = '<b>%s</b>: ' % (self.name if self.name else '')
        if 'name' in msg:
            msg['text'] = title + self.formatter % self.value
        if 'options' in msg:
            msg['start'] = 0
            msg['end'] = len(msg['options']) - 1
            options = msg['options']
            if isinstance(options, dict):
                msg['labels'] = list(options)
                options = list(options.values())
            else:
                msg['labels'] = [title + (self.formatter % o) for o in options]
            if self.value not in options:
                self.value = options[0]
        if 'value' in msg:
            value = msg['value']
            if value not in self.values:
                self.value = self.values[0]
                msg.pop('value')
                return msg
            label = self.labels[self.values.index(value)]
            msg['value'] = self.values.index(value)
            msg['text'] = label
        return msg

    def _process_property_change(self, msg):
        if 'value' in msg:
            msg['value'] = self.values[msg['value']]
        return msg


class Player(Widget):
    """
    The Player provides controls to play and skip through a number of
    frames defined by the length. The speed at which the widget plays
    is defined by the interval.
    """

    interval = param.Integer(default=500, doc="Interval between updates")

    length = param.Integer(default=10, doc="Number of frames")

    loop_policy = param.ObjectSelector(default='once',
                                       objects=['once', 'loop', 'reflect'], doc="""
       Policy used when player hits last frame""")

    value = param.Integer(default=0, doc="Current player value")

    height = param.Integer(default=250, readonly=True)

    _widget_type = _BkPlayer

    _rename = {'name': None}
