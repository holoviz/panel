"""
The input widgets generally allow entering arbitrary information into
a text field or similar.
"""
from __future__ import annotations

import ast
import json

from base64 import b64decode
from datetime import date, datetime
from typing import (
    TYPE_CHECKING, Any, ClassVar, Dict, Mapping, Optional, Type,
)

import numpy as np
import param

from bokeh.models.formatters import TickFormatter
from bokeh.models.widgets import (
    Checkbox as _BkCheckbox, ColorPicker as _BkColorPicker,
    DatePicker as _BkDatePicker, Div as _BkDiv, FileInput as _BkFileInput,
    NumericInput as _BkNumericInput, PasswordInput as _BkPasswordInput,
    Spinner as _BkSpinner, Switch as _BkSwitch,
    TextAreaInput as _BkTextAreaInput, TextInput as _BkTextInput,
)

from ..config import config
from ..layout import Column, Panel
from ..models import DatetimePicker as _bkDatetimePicker
from ..util import param_reprs
from .base import CompositeWidget, Widget

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm

    from ..viewable import Viewable


class TextInput(Widget):
    """
    The `TextInput` widget allows entering any string using a text input box.

    Reference: https://panel.holoviz.org/reference/widgets/TextInput.html

    :Example:

    >>> TextInput(name='Name', placeholder='Enter your name here ...')
    """

    description = param.String(default=None, doc="""
        An HTML string describing the function of this component.""")

    max_length = param.Integer(default=5000, doc="""
        Max count of characters in the input field.""")

    placeholder = param.String(default='', doc="""
        Placeholder for empty input field.""")

    value = param.String(default='', allow_None=True, doc="""
        Initial or entered text value updated when <enter> key is pressed.""")

    value_input = param.String(default='', allow_None=True, doc="""
        Initial or entered text value updated on every key press.""")

    width = param.Integer(default=300, allow_None=True, doc="""
      Width of this component. If sizing_mode is set to stretch
      or scale mode this will merely be used as a suggestion.""")

    _widget_type: ClassVar[Type[Model]] = _BkTextInput

    @classmethod
    def from_param(cls, parameter: param.Parameter, onkeyup=False, **params) -> Viewable:
        """
        Construct a widget from a Parameter and link the two
        bi-directionally.

        Parameters
        ----------
        parameter: param.Parameter
          A parameter to create the widget from.
        onkeyup: boolean
          Whether to trigger events on every key press.
        params: dict
          Keyword arguments to be passed to the widget constructor

        Returns
        -------
        Widget instance linked to the supplied parameter
        """
        params['onkeyup'] = onkeyup
        return super().from_param(parameter, **params)


class PasswordInput(TextInput):
    """
    The `PasswordInput` allows entering any string using an obfuscated text
    input box.

    Reference: https://panel.holoviz.org/reference/widgets/PasswordInput.html

    :Example:

    >>> PasswordInput(
    ...     name='Password', placeholder='Enter your password here...'
    ... )
    """

    _widget_type: ClassVar[Type[Model]] = _BkPasswordInput


class TextAreaInput(TextInput):
    """
    The `TextAreaInput` allows entering any multiline string using a text input
    box.

    Lines are joined with the newline character `\n`.

    Reference: https://panel.holoviz.org/reference/widgets/TextAreaInput.html
    :Example:

    >>> TextAreaInput(
    ...     name='Description', placeholder='Enter your description here...'
    ... )
    """

    _widget_type: ClassVar[Type[Model]] = _BkTextAreaInput


class FileInput(Widget):
    """
    The `FileInput` allows the user to upload one or more files to the server.

    It makes the filename, MIME type and (bytes) content available in Python.

    Please note

    - you can in fact *drag and drop* files onto the `FileInput`.
    - you easily save the files using the `save` method.

    Reference: https://panel.holoviz.org/reference/widgets/FileInput.html

    :Example:

    >>> FileInput(accept='.png,.jpeg', multiple=True)
    """

    accept = param.String(default=None)

    description = param.String(default=None, doc="""
        An HTML string describing the function of this component.""")

    filename = param.ClassSelector(
        default=None, class_=(str, list), is_instance=True)

    mime_type = param.ClassSelector(
        default=None, class_=(str, list), is_instance=True)

    multiple = param.Boolean(default=False)

    value = param.Parameter(default=None)

    _rename: ClassVar[Mapping[str, str | None]] = {
        'filename': None, 'name': None
    }

    _source_transforms: ClassVar[Mapping[str, str | None]] = {
        'value': "'data:' + source.mime_type + ';base64,' + value"
    }

    _widget_type: ClassVar[Type[Model]] = _BkFileInput

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if 'value' in msg:
            msg.pop('value')
        if 'mime_type' in msg:
            msg.pop('mime_type')
        return msg

    @property
    def _linked_properties(self):
        properties = super()._linked_properties
        return properties + ('filename',)

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'value' in msg:
            if isinstance(msg['value'], str):
                msg['value'] = b64decode(msg['value'])
            else:
                msg['value'] = [b64decode(content) for content in msg['value']]
        return msg

    def save(self, filename):
        """
        Saves the uploaded FileInput data object(s) to file(s) or
        BytesIO object(s).

        Arguments
        ---------
        filename (str or list[str]): File path or file-like object
        """
        value = self.value
        if isinstance(filename, list) and not isinstance(value, list):
            raise TypeError(
                "FileInput contains a list of files but only a single "
                "filename was given. Please provide a list of filenames or "
                "file-like objects."
            )
        elif not isinstance(filename, list) and isinstance(value, list):
            raise TypeError(
                "FileInput contains a single files but a list of "
                "filenames was given. Please provide a single filename "
                "or file-like object."
            )
        if not isinstance(value, list):
            value = [self.value]
        if not isinstance(filename, list):
            filename = [filename]

        for val, fn in zip(value, filename):
            if isinstance(fn, str):
                with open(fn, 'wb') as f:
                    f.write(val)
            else:
                fn.write(val)


class StaticText(Widget):
    """
    The `StaticText` widget displays a text value, but does not allow editing
    it.

    Reference: https://panel.holoviz.org/reference/widgets/StaticText.html

    :Example:

    >>> StaticText(name='Model', value='animagen2')
    """

    value = param.Parameter(default=None, doc="""
        The current value""")

    _format: ClassVar[str] = '<b>{title}</b>: {value}'

    _rename: ClassVar[Mapping[str, str | None]] = {'name': None, 'value': 'text'}

    _target_transforms: ClassVar[Mapping[str, str | None]] = {
        'value': 'target.text.split(": ")[0]+": "+value'
    }

    _source_transforms: ClassVar[Mapping[str, str | None]] = {
        'value': 'value.split(": ")[1]'
    }

    _widget_type: ClassVar[Type[Model]] = _BkDiv

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if 'text' in msg:
            text = str(msg.pop('text'))
            partial = self._format.replace('{value}', '').format(title=self.name)
            if self.name:
                text = self._format.format(title=self.name, value=text.replace(partial, ''))
            msg['text'] = text
        return msg


class DatePicker(Widget):
    """
    The `DatePicker` allows selecting selecting a `date` value using a text box
    and a date-picking utility.

    Reference: https://panel.holoviz.org/reference/widgets/DatePicker.html

    :Example:

    >>> DatePicker(
    ...     value=date(2025,1,1),
    ...     start=date(2025,1,1), end=date(2025,12,31),
    ...     name='Date'
    ... )
    """

    value = param.CalendarDate(default=None, doc="""
        The current value""")

    start = param.CalendarDate(default=None, doc="""
        Inclusive lower bound of the allowed date selection""")

    end = param.CalendarDate(default=None, doc="""
        Inclusive upper bound of the allowed date selection""")

    disabled_dates = param.List(default=None, item_type=(date, str))

    enabled_dates = param.List(default=None, item_type=(date, str))

    width = param.Integer(default=300, allow_None=True, doc="""
      Width of this component. If sizing_mode is set to stretch
      or scale mode this will merely be used as a suggestion.""")

    description = param.String(default=None, doc="""
        An HTML string describing the function of this component.""")

    _source_transforms: ClassVar[Mapping[str, str | None]] = {}

    _rename: ClassVar[Mapping[str, str | None]] = {
        'start': 'min_date', 'end': 'max_date'
    }

    _widget_type: ClassVar[Type[Model]] = _BkDatePicker

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        for p in ('start', 'end', 'value'):
            if p not in msg:
                continue
            value = msg[p]
            if isinstance(value, str):
                msg[p] = datetime.date(datetime.strptime(value, '%Y-%m-%d'))
        return msg


class _DatetimePickerBase(Widget):

    disabled_dates = param.List(default=None, item_type=(date, str), doc="""
      Dates to make unavailable for selection.""")

    enabled_dates = param.List(default=None, item_type=(date, str), doc="""
      Dates to make available for selection.""")

    enable_time = param.Boolean(default=True, doc="""
      Enable editing of the time in the widget.""")

    enable_seconds = param.Boolean(default=True, doc="""
      Enable editing of the seconds in the widget.""")

    end = param.Date(default=None, doc="""
      Inclusive upper bound of the allowed date selection.""")

    military_time = param.Boolean(default=True, doc="""
      Whether to display time in 24 hour format.""")

    start = param.Date(default=None, doc="""
      Inclusive lower bound of the allowed date selection.""")

    width = param.Integer(default=300, allow_None=True, doc="""
      Width of this component. If sizing_mode is set to stretch
      or scale mode this will merely be used as a suggestion.""")

    description = param.String(default=None, doc="""
        An HTML string describing the function of this component.""")

    _source_transforms: ClassVar[Mapping[str, str | None]] = {
        'value': None, 'start': None, 'end': None, 'mode': None
    }

    _rename: ClassVar[Mapping[str, str | None]] = {
        'start': 'min_date', 'end': 'max_date'
    }

    _widget_type: ClassVar[Type[Model]] = _bkDatetimePicker

    __abstract = True

    def __init__(self, **params):
        super().__init__(**params)
        self._update_value_bounds()

    @staticmethod
    def _convert_to_datetime(v):
        if isinstance(v, datetime):
            return v
        elif isinstance(v, date):
            return datetime(v.year, v.month, v.day)

    @param.depends('start', 'end', watch=True)
    def _update_value_bounds(self):
        self.param.value.bounds = (
            self._convert_to_datetime(self.start),
            self._convert_to_datetime(self.end)
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
        if 'min_date' in msg:
            msg['min_date'] = self._convert_to_datetime(msg['min_date'])
        if 'max_date' in msg:
            msg['max_date'] = self._convert_to_datetime(msg['max_date'])
        return msg


class DatetimePicker(_DatetimePickerBase):
    """
    The `DatetimePicker` allows selecting selecting a `datetime` value using a
    textbox and a datetime-picking utility.

    Reference: https://panel.holoviz.org/reference/widgets/DatetimePicker.html

    :Example:

    >>> DatetimePicker(
    ...    value=datetime(2025,1,1,22,0),
    ...    start=date(2025,1,1), end=date(2025,12,31),
    ...    military_time=True, name='Date and time'
    ... )
    """


    value = param.Date(default=None)

    mode = param.String('single', constant=True)

    def _serialize_value(self, value):
        if isinstance(value, str) and value:
            value = datetime.strptime(value, r'%Y-%m-%d %H:%M:%S')

        return value

    def _deserialize_value(self, value):
        if isinstance(value, (datetime, date)):
            value = value.strftime(r'%Y-%m-%d %H:%M:%S')

        return value


class DatetimeRangePicker(_DatetimePickerBase):
    """
    The `DatetimeRangePicker` allows selecting selecting a `datetime` range
    using a text box and a datetime-range-picking utility.

    Reference: https://panel.holoviz.org/reference/widgets/DatetimeRangePicker.html

    :Example:

    >>> DatetimeRangePicker(
    ...    value=(datetime(2025,1,1,22,0), datetime(2025,1,2,22,0)),
    ...    start=date(2025,1,1), end=date(2025,12,31),
    ...    military_time=True, name='Datetime Range'
    ... )
    """

    value = param.DateRange(default=None, doc="""
        The current value""")

    mode = param.String('range', constant=True)

    def _serialize_value(self, value):
        if isinstance(value, str) and value:
            value = [
                datetime.strptime(value, r'%Y-%m-%d %H:%M:%S')
                for value in value.split(' to ')
            ]


            value = tuple(value)

        return value

    def _deserialize_value(self, value):
        if isinstance(value, tuple):
            value = " to ".join(v.strftime(r'%Y-%m-%d %H:%M:%S') for v in value)
        if value is None:
            value = ""

        return value


class ColorPicker(Widget):
    """
    The `ColorPicker` widget allows selecting a hexadecimal RGB color value
    using the browser’s color-picking widget.

    Reference: https://panel.holoviz.org/reference/widgets/ColorPicker.html

    :Example:

    >>> ColorPicker(name='Color', value='#99ef78')
    """

    description = param.String(default=None, doc="""
        An HTML string describing the function of this component.""")

    value = param.Color(default=None, doc="""
        The selected color""")

    width = param.Integer(default=52, allow_None=True, doc="""
      Width of this component. If sizing_mode is set to stretch
      or scale mode this will merely be used as a suggestion.""")

    _widget_type: ClassVar[Type[Model]] = _BkColorPicker

    _rename: ClassVar[Mapping[str, str | None]] = {'value': 'color'}


class _NumericInputBase(Widget):

    description = param.String(default=None, doc="""
        An HTML string describing the function of this component.""")

    value = param.Number(default=0, allow_None=True, doc="""
        The current value of the spinner.""")

    placeholder = param.String(default='0', doc="""
        Placeholder for empty input field.""")

    format = param.ClassSelector(default=None, class_=(str, TickFormatter,), doc="""
        Allows defining a custom format string or bokeh TickFormatter.""")

    start = param.Parameter(default=None, allow_None=True, doc="""
        Optional minimum allowable value.""")

    end = param.Parameter(default=None, allow_None=True, doc="""
        Optional maximum allowable value.""")

    _rename: ClassVar[Mapping[str, str | None]] = {'start': 'low', 'end': 'high'}

    _widget_type: ClassVar[Type[Model]] = _BkNumericInput

    __abstract = True


class _IntInputBase(_NumericInputBase):

    value = param.Integer(default=0, allow_None=True, doc="""
        The current value of the spinner.""")

    start = param.Integer(default=None, allow_None=True, doc="""
        Optional minimum allowable value.""")

    end = param.Integer(default=None, allow_None=True, doc="""
        Optional maximum allowable value.""")

    mode = param.String(default='int', constant=True, doc="""
        Define the type of number which can be enter in the input""")

    __abstract = True


class _FloatInputBase(_NumericInputBase):

    value = param.Number(default=0, allow_None=True, doc="""
        The current value of the spinner.""")

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

    width = param.Integer(default=300, allow_None=True, doc="""
      Width of this component. If sizing_mode is set to stretch
      or scale mode this will merely be used as a suggestion.""")

    _widget_type: ClassVar[Type[Model]] = _BkSpinner

    __abstract = True

    def __init__(self, **params):
        if 'value' not in params:
            value = params.get('start', self.value)
            if value is not None:
                params['value'] = value
        if 'value' in params and 'value_throttled' in self.param:
            params['value_throttled'] = params['value']
        super().__init__(**params)

    def __repr__(self, depth=0):
        return '{cls}({params})'.format(cls=type(self).__name__,
                                        params=', '.join(param_reprs(self, ['value_throttled'])))

    def _update_model(
        self, events: Dict[str, param.parameterized.Event], msg: Dict[str, Any],
        root: Model, model: Model, doc: Document, comm: Optional[Comm]
    ) -> None:
        if 'value_throttled' in msg:
            del msg['value_throttled']

        return super()._update_model(events, msg, root, model, doc, comm)

    def _process_param_change(self, msg):
        # Workaround for -inf serialization errors
        if 'value' in msg and msg['value'] == float('-inf'):
            msg['value'] = None
            msg['value_throttled'] = None
        return super()._process_param_change(msg)

    def _process_property_change(self, msg):
        if config.throttled:
            if "value" in msg:
                del msg["value"]
            if "value_throttled" in msg:
                msg["value"] = msg["value_throttled"]
        return super()._process_property_change(msg)


class IntInput(_SpinnerBase, _IntInputBase):
    """
    The `IntInput` allows selecting an integer value using a spinbox.

    It behaves like a slider except that lower and upper bounds are optional
    and a specific value can be entered. The value can be changed using the
    keyboard (up, down, page up, page down), mouse wheel and arrow buttons.

    Reference: https://panel.holoviz.org/reference/widgets/IntInput.html

    :Example:

    >>> IntInput(name='Value', value=100, start=0, end=1000, step=10)
    """

    step = param.Integer(default=1, doc="""
        The step size.""")

    value_throttled = param.Integer(default=None, constant=True, doc="""
        The current value. Updates only on `<enter>` or when the widget looses focus.""")


class FloatInput(_SpinnerBase, _FloatInputBase):
    """
    The `FloatInput` allows selecting a floating point value using a spinbox.

    It behaves like a slider except that the lower and upper bounds are
    optional and a specific value can be entered. The value can be changed
    using the keyboard (up, down, page up, page down), mouse wheel and arrow
    buttons.

    Reference: https://panel.holoviz.org/reference/widgets/FloatInput.html

    :Example:

    >>> FloatInput(name='Value', value=5., step=1e-1, start=0, end=10)
    """

    placeholder = param.String(default='', doc="""
        Placeholder when the value is empty.""")

    step = param.Number(default=0.1, doc="""
        The step size.""")

    value_throttled = param.Number(default=None, constant=True, doc="""
        The current value. Updates only on `<enter>` or when the widget looses focus.""")

    def _process_param_change(self, msg):
        if msg.get('value', False) is None:
            msg['value'] = float('NaN')
        if msg.get('value_throttled', False) is None:
            msg['value_throttled'] = float('NaN')
        return super()._process_param_change(msg)

    def _process_property_change(self, msg):
        if msg.get('value', False) and np.isnan(msg['value']):
            msg['value'] = None
        if msg.get('value_throttled', False) and np.isnan(msg['value_throttled']):
            msg['value_throttled'] = None
        return super()._process_property_change(msg)


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
    The `LiteralInput` allows declaring Python literals using a text
    input widget.

    A *literal* is some specific primitive value of type `str`
    , `int`, `float`, `bool` etc or a `dict`, `list`, `tuple`, `set` etc of
    primitive values.

    Optionally the literal `type` may be declared.

    Reference: https://panel.holoviz.org/reference/widgets/LiteralInput.html

    :Example:

    >>> LiteralInput(name='Dictionary', value={'key': [1, 2, 3]}, type=dict)
    """

    description = param.String(default=None, doc="""
        An HTML string describing the function of this component.""")

    placeholder = param.String(default='', doc="""
      Placeholder for empty input field.""")

    serializer = param.ObjectSelector(default='ast', objects=['ast', 'json'], doc="""
       The serialization (and deserialization) method to use. 'ast'
       uses ast.literal_eval and 'json' uses json.loads and json.dumps.
    """)

    type = param.ClassSelector(default=None, class_=(type, tuple),
                               is_instance=True)

    value = param.Parameter(default=None)

    width = param.Integer(default=300, allow_None=True, doc="""
      Width of this component. If sizing_mode is set to stretch
      or scale mode this will merely be used as a suggestion.""")

    _rename: ClassVar[Mapping[str, str | None]] = {
        'type': None, 'serializer': None
    }

    _source_transforms: ClassVar[Mapping[str, str | None]] = {
        'serializer': None,
        'value': """JSON.parse(value.replace(/'/g, '"'))"""
    }

    _target_transforms: ClassVar[Mapping[str, str | None]] = {
        'value': """JSON.stringify(value).replace(/,/g, ",").replace(/:/g, ": ")"""
    }

    _widget_type: ClassVar[Type[Model]] = _BkTextInput

    def __init__(self, **params):
        super().__init__(**params)
        self._state = ''
        self._validate(None)
        self._internal_callbacks.append(self.param.watch(self._validate, 'value'))

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
                if value == '':
                    value = ''
                elif self.serializer == 'json':
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
                    if typed_value is None and value == '':
                        value = None
                    elif typed_value is None and value is not None:
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
            if isinstance(value, str):
                value = repr(value)
            elif self.serializer == 'json':
                value = json.dumps(value)
            else:
                value = '' if value is None else str(value)
            msg['value'] = value
        msg['title'] = self.name
        return msg


class ArrayInput(LiteralInput):
    """
    The `ArrayInput` allows rendering and editing NumPy arrays in a text
    input widget.

    Arrays larger than the `max_array_size` will be summarized and editing
    will be disabled.

    Reference: https://panel.holoviz.org/reference/widgets/ArrayInput.html

    :Example:

    >>> To be determined ...
    """

    max_array_size = param.Number(default=1000, doc="""
        Arrays larger than this limit will be allowed in Python but
        will not be serialized into JavaScript. Although such large
        arrays will thus not be editable in the widget, such a
        restriction helps avoid overwhelming the browser and lets
        other widgets remain usable.""")

    _rename: ClassVar[Mapping[str, str | None]] = {
        'max_array_size': None
    }

    _source_transforms: ClassVar[Mapping[str, str | None]] = {
        'serializer': None, 'type': None, 'value': None
    }

    def __init__(self, **params):
        super().__init__(**params)
        self._auto_disabled = False

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'value' in msg and isinstance(msg['value'], list):
            msg['value'] = np.asarray(msg['value'])
        return msg

    def _process_param_change(self, msg):
        if msg.get('disabled', False):
            self._auto_disabled = False
        value = msg.get('value')
        if value is None:
            return super()._process_param_change(msg)
        if value.size <= self.max_array_size:
            msg['value'] = value.tolist()
            # If array is no longer larger than max_array_size
            # unset disabled
            if self.disabled and self._auto_disabled:
                self.disabled = False
                msg['disabled'] = False
                self._auto_disabled = False
        else:
            msg['value'] = np.array2string(
                msg['value'], separator=',',
                threshold=self.max_array_size
            )
            if not self.disabled:
                self.param.warning(
                    f"Number of array elements ({value.size}) exceeds "
                    f"`max_array_size` ({self.max_array_size}), editing "
                    "will be disabled."
                )
                self.disabled = True
                msg['disabled'] = True
                self._auto_disabled = True
        return super()._process_param_change(msg)


class DatetimeInput(LiteralInput):
    """
    The `DatetimeInput` allows specifying Python `datetime` like values using
    a text input widget.

    An optional `type` may be declared.

    Reference: https://panel.holoviz.org/reference/widgets/DatetimeInput.html

    :Example:

    >>> DatetimeInput(name='Datetime', value=datetime(2019, 2, 8))
    """

    value = param.Date(default=None, doc="""
        The current value""")

    start = param.Date(default=None, doc="""
        Inclusive lower bound of the allowed date selection""")

    end = param.Date(default=None, doc="""
        Inclusive upper bound of the allowed date selection""")

    format = param.String(default='%Y-%m-%d %H:%M:%S', doc="""
        Datetime format used for parsing and formatting the datetime.""")

    type = datetime

    _source_transforms: ClassVar[Mapping[str, str | None]] = {
        'value': None, 'start': None, 'end': None
    }

    _rename: ClassVar[Mapping[str, str | None]] = {
        'format': None, 'type': None, 'start': None, 'end': None,
        'serializer': None
    }

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
    """
    The `DatetimeRangeInput` widget allows selecting a `datetime` range using
    two `DatetimeInput` widgets, which return a `tuple` range.

    Reference: https://panel.holoviz.org/reference/widgets/DatetimeRangeInput.html

    :Example:

    >>> DatetimeRangeInput(
    ...     name='Datetime Range',
    ...     value=(datetime(2017, 1, 1), datetime(2018, 1, 10)),
    ...     start=datetime(2017, 1, 1), end=datetime(2019, 1, 1),
    ... )
    """

    value = param.Tuple(default=(None, None), length=2, doc="""
        The current value""")

    start = param.Date(default=None, doc="""
        Inclusive lower bound of the allowed date selection""")

    end = param.Date(default=None, doc="""
        Inclusive upper bound of the allowed date selection""")

    format = param.String(default='%Y-%m-%d %H:%M:%S', doc="""
        Datetime format used for parsing and formatting the datetime.""")

    _composite_type: ClassVar[Type[Panel]] = Column

    def __init__(self, **params):
        self._text = StaticText(margin=(5, 0, 0, 0), styles={'white-space': 'nowrap'})
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
            params = {k: v for k, v in self.param.values().items() if k in filters}
            start_params = dict(params, value=self.value[0])
            end_params = dict(params, value=self.value[1])
            self._start.param.update(**start_params)
            self._end.param.update(**end_params)
        finally:
            self._updating = False


class _BooleanWidget(Widget):

    value = param.Boolean(default=False, doc="""
        The current value""")

    _supports_embed: ClassVar[bool] = True

    _rename: ClassVar[Mapping[str, str | None]] = {'value': 'active', 'name': 'label'}

    __abstract = True

    def _get_embed_state(self, root, values=None, max_opts=3):
        return (self, self._models[root.ref['id']][0], [False, True],
                lambda x: x.active, 'active', "cb_obj.active")


class Checkbox(_BooleanWidget):
    """
    The `Checkbox` allows toggling a single condition between `True`/`False`
    states by ticking a checkbox.

    This widget is interchangeable with the `Toggle` widget.

    Reference: https://panel.holoviz.org/reference/widgets/Checkbox.html

    :Example:

    >>> Checkbox(name='Works with the tools you know and love', value=True)
    """

    _widget_type: ClassVar[Type[Model]] = _BkCheckbox


class Switch(_BooleanWidget):
    """
    The `Switch` allows toggling a single condition between `True`/`False`
    states by ticking a checkbox.

    This widget is interchangeable with the `Toggle` widget.

    Reference: https://panel.holoviz.org/reference/widgets/Switch.html

    :Example:

    >>> Switch(name='Works with the tools you know and love', value=True)
    """

    _rename: ClassVar[Mapping[str, str | None]] = {
        'name': None, 'value': 'active'
    }

    _widget_type: ClassVar[Type[Model]] = _BkSwitch
