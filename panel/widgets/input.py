"""
The input widgets generally allow entering arbitrary information into
a text field or similar.
"""
from __future__ import absolute_import, division, unicode_literals

import ast

from base64 import b64decode, b64encode
from datetime import datetime
from six import string_types

import param

from bokeh.models.widgets import (
    CheckboxGroup as _BkCheckboxGroup, ColorPicker as _BkColorPicker,
    DatePicker as _BkDatePicker, Div as _BkDiv, TextInput as _BkTextInput,
    Spinner as _BkSpinner)

from ..models import FileInput as _BkFileInput
from ..util import as_unicode
from .base import Widget


class TextInput(Widget):

    value = param.String(default='', allow_None=True)

    placeholder = param.String(default='')

    _widget_type = _BkTextInput


class FileInput(Widget):

    mime_type = param.String(default=None)

    value = param.Parameter(default=None)

    _widget_type = _BkFileInput

    _rename = {'name': None, 'mime_type': None}

    def _process_param_change(self, msg):
        msg = super(FileInput, self)._process_param_change(msg)
        if 'value' in msg:
            if self.mime_type:
                template = 'data:{mime};base64,{data}'
                data = b64encode(msg['value'])
                msg['value'] = template.format(data=data.decode('utf-8'),
                                               mime=self.mime_type)
            else:
                msg['value'] = ''
        return msg

    def _process_property_change(self, msg):
        msg = super(FileInput, self)._process_property_change(msg)
        if 'value' in msg:
            header, content = msg['value'].split(",", 1)
            msg['mime_type'] = header.split(':')[1].split(';')[0]
            msg['value'] = b64decode(content)
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

    _widget_type = _BkDiv

    _format = '<b>{title}</b>: {value}'

    _rename = {'name': 'title', 'value': 'text'}

    def _process_param_change(self, msg):
        msg = super(StaticText, self)._process_property_change(msg)
        msg.pop('title', None)
        if 'value' in msg:
            text = as_unicode(msg.pop('value'))
            if self.name:
                text = self._format.format(title=self.name, value=text)
            msg['text'] = text
        return msg


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


class ColorPicker(Widget):

    value = param.Color(default=None, doc="""
        The selected color""")

    _widget_type = _BkColorPicker

    _rename = {'value': 'color', 'name': 'title'}


class Spinner(Widget):

    start = param.Number(default=None, doc="""
        Optional minimum allowable value""")

    end = param.Number(default=None, doc="""
        Optional maximum allowable value""")

    value = param.Number(default=0, doc="""
        The initial value of the spinner""")

    step = param.Number(default=1, doc="""
        The step added or subtracted to the current value""")

    _widget_type = _BkSpinner

    _rename = {'name': 'title', 'start': 'low', 'end': 'high'}


class LiteralInput(Widget):
    """
    LiteralInput allows declaring Python literals using a text
    input widget. Optionally a type may be declared.
    """

    type = param.ClassSelector(default=None, class_=(type, tuple),
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
        self.param.trigger('name')
        return msg

    def _process_param_change(self, msg):
        msg = super(LiteralInput, self)._process_param_change(msg)
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

    _supports_embed = True

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

    def _get_embed_state(self, root, max_opts=3):
        return (self, self._models[root.ref['id']][0], [False, True],
                lambda x: 0 in x.active, 'active', 'cb_obj.active.indexOf(0) >= 0')
