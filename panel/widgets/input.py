"""
The input widgets generally allow entering arbitrary information into
a text field or similar.
"""
from __future__ import absolute_import, division, unicode_literals

import ast
import json

from base64 import b64decode
from datetime import datetime, date
from six import string_types

import param

from bokeh.models.widgets import (
    CheckboxGroup as _BkCheckboxGroup, ColorPicker as _BkColorPicker,
    DatePicker as _BkDatePicker, Div as _BkDiv, TextInput as _BkTextInput,
    PasswordInput as _BkPasswordInput, Spinner as _BkSpinner,
    FileInput as _BkFileInput, TextAreaInput as _BkTextAreaInput)

from ..util import as_unicode
from .base import Widget


class TextInput(Widget):

    value = param.String(default='', allow_None=True)

    placeholder = param.String(default='')

    _widget_type = _BkTextInput


class PasswordInput(Widget):

    value = param.String(default='', allow_None=True)

    placeholder = param.String(default='')

    _widget_type = _BkPasswordInput


class TextAreaInput(Widget):

    value = param.String(default='', allow_None=True)

    placeholder = param.String(default='')

    max_length = param.Integer(default=5000)

    _widget_type = _BkTextAreaInput


class FileInput(Widget):

    accept = param.String(default=None)

    filename = param.String(default=None)

    mime_type = param.String(default=None)

    value = param.Parameter(default=None)

    _widget_type = _BkFileInput

    _source_transforms = {'value': "'data:' + source.mime_type + ';base64,' + value"}

    _rename = {'name': None, 'filename': None}

    def _process_param_change(self, msg):
        msg = super(FileInput, self)._process_param_change(msg)
        if 'value' in msg:
            msg.pop('value')
        if 'mime_type' in msg:
            msg.pop('mime_type')
        return msg

    def _filter_properties(self, properties):
        properties = super(FileInput, self)._filter_properties(properties)
        return properties + ['value', 'mime_type', 'filename']

    def _process_property_change(self, msg):
        msg = super(FileInput, self)._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = b64decode(msg['value'])
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
        msg = super(StaticText, self)._process_property_change(msg)
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
        msg = super(DatePicker, self)._process_property_change(msg)
        if 'value' in msg:
            if isinstance(msg['value'], string_types):
                msg['value'] = datetime.date(datetime.strptime(msg['value'], '%Y-%m-%d'))
        return msg


class ColorPicker(Widget):

    value = param.Color(default=None, doc="""
        The selected color""")

    _widget_type = _BkColorPicker

    _rename = {'value': 'color', 'name': 'title'}


class Spinner(Widget):

    start = param.Number(default=None, doc="""
        Optional minimum allowable value.""")

    end = param.Number(default=None, doc="""
        Optional maximum allowable value.""")

    value = param.Number(default=0, doc="""
        The initial value of the spinner.""")

    step = param.Number(default=1, doc="""
        The step added or subtracted to the current value.""")

    _widget_type = _BkSpinner

    _rename = {'name': 'title', 'start': 'low', 'end': 'high'}

    def __init__(self, **params):
        if params.get('value') is None:
            value = params.get('start', self.value)
            if value is not None:
                params['value'] = value
        super(Spinner, self).__init__(**params)


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
        super(LiteralInput, self).__init__(**params)
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
        msg = super(LiteralInput, self)._process_property_change(msg)
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
        msg = super(LiteralInput, self)._process_param_change(msg)
        if 'value' in msg:
            value = '' if msg['value'] is None else msg['value']
            if isinstance(value, string_types):
                value = repr(value)
            elif self.serializer == 'json':
                value = json.dumps(value, sort_keys=True)
            else:
                value = as_unicode(value)
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


class Checkbox(Widget):

    value = param.Boolean(default=False)

    _supports_embed = True

    _rename = {'value': 'active', 'name': 'labels'}

    _source_transforms = {'value': "value.indexOf(0) >= 0", 'name': "value[0]"}

    _target_transforms = {'value': "value ? [0] : []", 'name': "[value]"}

    _widget_type = _BkCheckboxGroup

    def _process_property_change(self, msg):
        msg = super(Checkbox, self)._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = 0 in msg.pop('value')
        if 'name' in msg:
            msg['name'] = [msg['name']]
        return msg

    def _process_param_change(self, msg):
        msg = super(Checkbox, self)._process_param_change(msg)
        if 'active' in msg:
            msg['active'] = [0] if msg.pop('active', None) else []
        if 'labels' in msg:
            msg['labels'] = [msg.pop('labels')]
        return msg

    def _get_embed_state(self, root, values=None, max_opts=3):
        return (self, self._models[root.ref['id']][0], [False, True],
                lambda x: str(0 in x.active).lower(), 'active',
                "String(cb_obj.active.indexOf(0) >= 0)")
