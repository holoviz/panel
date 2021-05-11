"""
The input widgets generally allow entering arbitrary information into
a text field or similar.
"""
import ast
import json

from base64 import b64decode
from datetime import datetime, date
from six import string_types

import param

from bokeh.models.formatters import TickFormatter
from bokeh.models.widgets import (
    CheckboxGroup as _BkCheckboxGroup, ColorPicker as _BkColorPicker,
    DatePicker as _BkDatePicker, Div as _BkDiv, TextInput as _BkTextInput,
    PasswordInput as _BkPasswordInput, Spinner as _BkSpinner,
    FileInput as _BkFileInput, TextAreaInput as _BkTextAreaInput,
    NumericInput as _BkNumericInput)

from ..config import config
from ..layout import Column
from ..util import param_reprs, as_unicode
from .base import Widget, CompositeWidget
from ..models import DatetimePicker as _bkDatetimePicker


class TextInput(Widget):

    max_length = param.Integer(default=5000, doc="""
      Max count of characters in the input field.""")

    placeholder = param.String(default='', doc="""
      Placeholder for empty input field.""")

    value = param.String(default='', allow_None=True, doc="""
      Initial or entered text value updated when <enter> key is pressed.""")

    value_input = param.String(default='', allow_None=True, doc="""
      Initial or entered text value updated on every key press.""")

    _widget_type = _BkTextInput


class PasswordInput(TextInput):

    _widget_type = _BkPasswordInput


class TextAreaInput(TextInput):

    _widget_type = _BkTextAreaInput


class FileInput(Widget):

    accept = param.String(default=None)

    filename = param.ClassSelector(default=None, class_=(str, list),
                               is_instance=True)

    mime_type = param.ClassSelector(default=None, class_=(str, list),
                               is_instance=True)

    multiple = param.Boolean(default=False)

    value = param.Parameter(default=None)

    _widget_type = _BkFileInput

    _source_transforms = {'value': "'data:' + source.mime_type + ';base64,' + value"}

    _rename = {'name': None, 'filename': None}

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if 'value' in msg:
            msg.pop('value')
        if 'mime_type' in msg:
            msg.pop('mime_type')
        return msg

    def _filter_properties(self, properties):
        properties = super()._filter_properties(properties)
        return properties + ['value', 'mime_type', 'filename']

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'value' in msg:
            if isinstance(msg['value'], string_types):
                msg['value'] = b64decode(msg['value'])
            else:
                msg['value'] = [b64decode(content) for content in msg['value']]
        return msg

    def save(self, filename):
        """
        Saves the uploaded FileInput data to a file or BytesIO object.

        Arguments
        ---------
        filename (str): File path or file-like object
        """
        if isinstance(filename, string_types):
            with open(filename, 'wb') as f:
                f.write(self.value)
        else:
            filename.write(self.value)


class StaticText(Widget):

    style = param.Dict(default=None, doc="""
        Dictionary of CSS property:value pairs to apply to this Div.""")

    value = param.Parameter(default=None)

    _format = '<b>{title}</b>: {value}'

    _rename = {'name': None, 'value': 'text'}

    _target_transforms = {'value': 'target.text.split(": ")[0]+": "+value'}

    _source_transforms = {'value': 'value.split(": ")[1]'}

    _widget_type = _BkDiv

    def _process_param_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'value' in msg:
            text = as_unicode(msg.pop('value'))
            partial = self._format.replace('{value}', '').format(title=self.name)
            if self.name:
                text = self._format.format(title=self.name, value=text.replace(partial, ''))
            msg['text'] = text
        return msg


class DatePicker(Widget):

    value = param.CalendarDate(default=None)

    start = param.CalendarDate(default=None)

    end = param.CalendarDate(default=None)

    disabled_dates = param.List(default=None, class_=(date, str))

    enabled_dates = param.List(default=None, class_=(date, str))

    _source_transforms = {}

    _rename = {'start': 'min_date', 'end': 'max_date', 'name': 'title'}

    _widget_type = _BkDatePicker

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'value' in msg:
            if isinstance(msg['value'], string_types):
                msg['value'] = datetime.date(datetime.strptime(msg['value'], '%Y-%m-%d'))
        return msg


class _DatetimePickerBase(Widget):

    start = param.CalendarDate(default=None)

    end = param.CalendarDate(default=None)

    disabled_dates = param.List(default=None, class_=(date, str))

    enabled_dates = param.List(default=None, class_=(date, str))

    enable_time = param.Boolean(default=True)

    enable_seconds = param.Boolean(default=True)

    military_time = param.Boolean(default=True)

    _source_transforms = {'value': None, 'start': None, 'end': None, 'mode': None}

    _rename = {'start': 'min_date', 'end': 'max_date', 'name': 'title'}

    _widget_type = _bkDatetimePicker

    __abstract = True

    def __init__(self, **params):
        super().__init__(**params)
        self._update_value_bounds()

    @staticmethod
    def _date_to_datetime(x):
        if isinstance(x, date):
            return datetime(x.year, x.month, x.day)

    @param.depends('start', 'end', watch=True)
    def _update_value_bounds(self):
        self.param.value.bounds = (
            self._date_to_datetime(self.start),
            self._date_to_datetime(self.end),
        )
        self.param.value._validate(self.value)

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = self._serialize_value(msg['value'])
        return msg

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if 'value' in msg:
            msg['value'] = self._deserialize_value(msg['value'])
        return msg


class DatetimePicker(_DatetimePickerBase):

    value = param.Date(default=None)

    mode = param.String('single', constant=True)

    def _serialize_value(self, value):
        if isinstance(value, string_types) and value:
            value = datetime.strptime(value, r'%Y-%m-%d %H:%M:%S')

            # Hour, minute and seconds can be increased after end is reached.
            # This forces the hours, minute and second to be 0.
            end = self._date_to_datetime(self.end)
            if end is not None and value > end:
                value = end

        return value

    def _deserialize_value(self, value):
        if isinstance(value, (datetime, date)):
            value = value.strftime(r'%Y-%m-%d %H:%M:%S')

        return value


class DatetimeRangePicker(_DatetimePickerBase):
    value = param.DateRange(default=None)

    mode = param.String('range', constant=True)

    def _serialize_value(self, value):
        if isinstance(value, string_types) and value:
            value = [
                datetime.strptime(value, r'%Y-%m-%d %H:%M:%S')
                for value in value.split(' to ')
            ]

            # Hour, minute and seconds can be increased after end is reached.
            # This forces the hours, minute and second to be 0.
            end = self._date_to_datetime(self.end)
            if end is not None and value[0] > end:
                value[0] = end
            if end is not None and value[1] > end:
                value[1] = end

            value = tuple(value)

        return value

    def _deserialize_value(self, value):
        if isinstance(value, tuple):
            value = " to ".join(v.strftime(r'%Y-%m-%d %H:%M:%S') for v in value)
        if value is None:
            value = ""

        return value


class ColorPicker(Widget):

    value = param.Color(default=None, doc="""
        The selected color""")

    _widget_type = _BkColorPicker

    _rename = {'value': 'color', 'name': 'title'}


class _NumericInputBase(Widget):

    value = param.Number(default=0, allow_None=True, doc="""
        The initial value of the spinner.""")

    placeholder = param.String(default='0', doc="""
        Placeholder for empty input field.""")

    format = param.ClassSelector(default=None, class_=string_types+(TickFormatter,), doc="""
        Allows defining a custom format string or bokeh TickFormatter.""")

    _rename = {'name': 'title', 'start': 'low', 'end': 'high'}

    _widget_type = _BkNumericInput

    __abstract = True


class _IntInputBase(_NumericInputBase):

    value = param.Integer(default=0, allow_None=True, doc="""
        The initial value of the spinner.""")

    start = param.Integer(default=None, allow_None=True, doc="""
        Optional minimum allowable value.""")

    end = param.Integer(default=None, allow_None=True, doc="""
        Optional maximum allowable value.""")

    mode = param.String(default='int', constant=True, doc="""
        Define the type of number which can be enter in the input""")

    __abstract = True


class _FloatInputBase(_NumericInputBase):

    value = param.Number(default=0, allow_None=True, doc="""
        The initial value of the spinner.""")

    start = param.Number(default=None, allow_None=True, doc="""
        Optional minimum allowable value.""")

    end = param.Number(default=None, allow_None=True, doc="""
        Optional maximum allowable value.""")

    mode = param.String(default='float', constant=True, doc="""
        Define the type of number which can be enter in the input""")

    __abstract = True


class _SpinnerBase(_NumericInputBase):

    page_step_multiplier = param.Integer(default=10, bounds=(0, None), doc="""
        Defines the multiplication factor applied to step when the page up
        and page down keys are pressed.""")

    wheel_wait = param.Integer(default=100, doc="""
        Defines the debounce time in ms before updating `value_throttled` when
        the mouse wheel is used to change the input.""")

    _widget_type = _BkSpinner

    __abstract = True

    def __init__(self, **params):
        if params.get('value') is None:
            value = params.get('start', self.value)
            if value is not None:
                params['value'] = value
        if 'value' in params and 'value_throttled' in self.param:
            params['value_throttled'] = params['value']
        super().__init__(**params)

    def __repr__(self, depth=0):
        return '{cls}({params})'.format(cls=type(self).__name__,
                                        params=', '.join(param_reprs(self, ['value_throttled'])))

    def _update_model(self, events, msg, root, model, doc, comm):
        if 'value_throttled' in msg:
            del msg['value_throttled']

        return super()._update_model(events, msg, root, model, doc, comm)

    def _process_property_change(self, msg):
        if config.throttled:
            if "value" in msg:
                del msg["value"]
            if "value_throttled" in msg:
                msg["value"] = msg["value_throttled"]
        return super()._process_property_change(msg)


class IntInput(_SpinnerBase, _IntInputBase):

    step = param.Integer(default=1)

    value_throttled = param.Integer(default=None, constant=True)


class FloatInput(_SpinnerBase, _FloatInputBase):

    step = param.Number(default=0.1)

    value_throttled = param.Number(default=None, constant=True)


class NumberInput(_SpinnerBase):

    def __new__(self, **params):
        param_list = ["value", "start", "stop", "step"]
        if all(isinstance(params.get(p, 0), int) for p in param_list):
            return IntInput(**params)
        else:
            return FloatInput(**params)


# Backward compatibility
Spinner = NumberInput


class LiteralInput(Widget):
    """
    LiteralInput allows declaring Python literals using a text
    input widget. Optionally a type may be declared.
    """

    serializer = param.ObjectSelector(default='ast', objects=['ast', 'json'], doc="""
       The serialization (and deserialization) method to use. 'ast'
       uses ast.literal_eval and 'json' uses json.loads and json.dumps.
    """)

    type = param.ClassSelector(default=None, class_=(type, tuple),
                               is_instance=True)

    value = param.Parameter(default=None)

    _rename = {'name': 'title', 'type': None, 'serializer': None}

    _source_transforms = {'value': """JSON.parse(value.replace(/'/g, '"'))"""}

    _target_transforms = {'value': """JSON.stringify(value).replace(/,/g, ", ").replace(/:/g, ": ")"""}

    _widget_type = _BkTextInput

    def __init__(self, **params):
        super().__init__(**params)
        self._state = ''
        self._validate(None)
        self._callbacks.append(self.param.watch(self._validate, 'value'))

    def _validate(self, event):
        if self.type is None: return
        new = self.value
        if not isinstance(new, self.type) and new is not None:
            if event:
                self.value = event.old
            types = repr(self.type) if isinstance(self.type, tuple) else self.type.__name__
            raise ValueError('LiteralInput expected %s type but value %s '
                             'is of type %s.' %
                             (types, new, type(new).__name__))

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        new_state = ''
        if 'value' in msg:
            value = msg.pop('value')
            try:
                if self.serializer == 'json':
                    value = json.loads(value)
                else:
                    value = ast.literal_eval(value)
            except Exception:
                new_state = ' (invalid)'
                value = self.value
            else:
                if self.type and not isinstance(value, self.type):
                    vtypes = self.type if isinstance(self.type, tuple) else (self.type,)
                    typed_value = None
                    for vtype in vtypes:
                        try:
                            typed_value = vtype(value)
                        except Exception:
                            pass
                        else:
                            break
                    if typed_value is None and value is not None:
                        new_state = ' (wrong type)'
                        value = self.value
                    else:
                        value = typed_value
            msg['value'] = value
        msg['name'] = msg.get('title', self.name).replace(self._state, '') + new_state
        self._state = new_state
        self.param.trigger('name')
        return msg

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if 'value' in msg:
            value = msg['value']
            if isinstance(value, string_types):
                value = repr(value)
            elif self.serializer == 'json':
                value = json.dumps(value)
            else:
                value = '' if value is None else as_unicode(value)
            msg['value'] = value
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

    _source_transforms = {'value': None, 'start': None, 'end': None}

    _rename = {'format': None, 'type': None, 'name': 'title',
               'start': None, 'end': None, 'serializer': None}

    def __init__(self, **params):
        super().__init__(**params)
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
            except Exception:
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
        msg = Widget._process_param_change(self, msg)
        if 'value' in msg:
            value = msg['value']
            if value is None:
                value = ''
            else:
                value = datetime.strftime(msg['value'], self.format)
            msg['value'] = value
        msg['title'] = self.name
        return msg


class DatetimeRangeInput(CompositeWidget):

    value = param.Tuple(default=(None, None), length=2)

    start = param.Date(default=None)

    end = param.Date(default=None)

    format = param.String(default='%Y-%m-%d %H:%M:%S', doc="""
        Datetime format used for parsing and formatting the datetime.""")

    _composite_type = Column

    def __init__(self, **params):
        self._text = StaticText(margin=(5, 0, 0, 0), style={'white-space': 'nowrap'})
        self._start = DatetimeInput(sizing_mode='stretch_width', margin=(5, 0, 0, 0))
        self._end = DatetimeInput(sizing_mode='stretch_width', margin=(5, 0, 0, 0))
        if 'value' not in params:
            params['value'] = (params['start'], params['end'])
        super().__init__(**params)
        self._msg = ''
        self._composite.extend([self._text, self._start, self._end])
        self._updating = False
        self.param.watch(self._update_widgets, [p for p in self.param if p != 'name'])
        self._update_widgets()
        self._update_label()

    @param.depends('name', '_start.name', '_end.name', watch=True)
    def _update_label(self):
        self._text.value = f'{self.name}{self._start.name}{self._end.name}{self._msg}'

    @param.depends('_start.value', '_end.value', watch=True)
    def _update(self):
        if self._updating:
            return
        if (self._start.value is not None and
            self._end.value is not None and
            self._start.value > self._end.value):
            self._msg = ' (start of range must be <= end)'
            self._update_label()
            return
        elif self._msg:
            self._msg = ''
            self._update_label()
        try:
            self._updating = True
            self.value = (self._start.value, self._end.value)
        finally:
            self._updating = False

    def _update_widgets(self, *events):
        filters = [event.name for event in events] if events else list(self.param)
        if 'name' in filters:
            filters.remove('name')
        if self._updating:
            return
        try:
            self._updating = True
            params = {k: v for k, v in self.param.get_param_values() if k in filters}
            start_params = dict(params, value=self.value[0])
            end_params = dict(params, value=self.value[1])
            self._start.param.set_param(**start_params)
            self._end.param.set_param(**end_params)
        finally:
            self._updating = False


class Checkbox(Widget):

    value = param.Boolean(default=False)

    _supports_embed = True

    _rename = {'value': 'active', 'name': 'labels'}

    _source_transforms = {'value': "value.indexOf(0) >= 0", 'name': "value[0]"}

    _target_transforms = {'value': "value ? [0] : []", 'name': "[value]"}

    _widget_type = _BkCheckboxGroup

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = 0 in msg.pop('value')
        if 'name' in msg:
            msg['name'] = [msg['name']]
        return msg

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if 'active' in msg:
            msg['active'] = [0] if msg.pop('active', None) else []
        if 'labels' in msg:
            msg['labels'] = [msg.pop('labels')]
        return msg

    def _get_embed_state(self, root, values=None, max_opts=3):
        return (self, self._models[root.ref['id']][0], [False, True],
                lambda x: str(0 in x.active).lower(), 'active',
                "String(cb_obj.active.indexOf(0) >= 0)")
