"""
The input widgets generally allow entering arbitrary information into
a text field or similar.
"""
from __future__ import annotations

import ast
import json

from base64 import b64decode
from collections.abc import Iterable, Mapping
from datetime import date, datetime, time as dt_time
from typing import (
    TYPE_CHECKING, Any, ClassVar, Type,
)

import numpy as np
import param

from bokeh.models.formatters import TickFormatter
from bokeh.models.widgets import (
    Checkbox as _BkCheckbox, ColorPicker as _BkColorPicker,
    DatePicker as _BkDatePicker, DateRangePicker as _BkDateRangePicker,
    Div as _BkDiv, FileInput as _BkFileInput, NumericInput as _BkNumericInput,
    PasswordInput as _BkPasswordInput, Spinner as _BkSpinner,
    Switch as _BkSwitch,
)
from bokeh.models.widgets.inputs import ClearInput
from pyviz_comms import JupyterComm

from ..config import config
from ..layout import Column, Panel
from ..models import (
    DatetimePicker as _bkDatetimePicker, TextAreaInput as _bkTextAreaInput,
    TextInput as _BkTextInput, TimePicker as _BkTimePicker,
)
from ..util import (
    escape, lazy_load, param_reprs, try_datetime64_to_datetime,
)
from .base import CompositeWidget, Widget

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm

    from ..models.file_dropper import DeleteEvent, UploadEvent
    from ..viewable import Viewable


class _TextInputBase(Widget):

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


class TextInput(_TextInputBase):

    """
    The `TextInput` widget allows entering any string using a text input box.

    Reference: https://panel.holoviz.org/reference/widgets/TextInput.html

    :Example:

    >>> TextInput(name='Name', placeholder='Enter your name here ...')
    """

    enter_pressed = param.Event(doc="""
        Event when the enter key has been pressed.""")

    _widget_type: ClassVar[type[Model]] = _BkTextInput

    _rename = {'enter_pressed': None}

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        model = super()._get_model(doc, root, parent, comm)
        self._register_events('enter-pressed', model=model, doc=doc, comm=comm)
        return model

    def _process_event(self, event) -> None:
        if event.event_name == 'enter-pressed':
            self.value = event.value_input
            self.value_input = event.value_input
            self.enter_pressed = True


class PasswordInput(_TextInputBase):
    """
    The `PasswordInput` allows entering any string using an obfuscated text
    input box.

    Reference: https://panel.holoviz.org/reference/widgets/PasswordInput.html

    :Example:

    >>> PasswordInput(
    ...     name='Password', placeholder='Enter your password here...'
    ... )
    """

    _widget_type: ClassVar[type[Model]] = _BkPasswordInput


class TextAreaInput(_TextInputBase):
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

    auto_grow = param.Boolean(default=False, doc="""
        Whether the text area should automatically grow vertically to
        accommodate the current text.""")

    cols = param.Integer(default=20, doc="""
        Number of columns in the text input field.""")

    max_rows = param.Integer(default=None, doc="""
        When combined with auto_grow this determines the maximum number
        of rows the input area can grow.""")

    rows = param.Integer(default=2, doc="""
        Number of rows in the text input field.""")

    resizable = param.Selector(
        objects=["both", "width", "height", False], doc="""
        Whether the layout is interactively resizable,
        and if so in which dimensions: `width`, `height`, or `both`.
        Can only be set during initialization.""")

    _widget_type: ClassVar[type[Model]] = _bkTextAreaInput


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

    accept = param.String(default=None, doc="""
        A comma separated string of all extension types that should
        be supported.""")

    description = param.String(default=None, doc="""
        An HTML string describing the function of this component
        rendered as a tooltip icon.""")

    directory = param.Boolean(default=False, doc="""
        Whether to allow selection of directories instead of files.
        The filename will be relative paths to the uploaded directory.

        .. note::
            When a directory is uploaded it will give add a confirmation pop up.
            The confirmation pop up cannot be disabled, as this is a security feature
            in the browser.

        .. note::
            The `accept` parameter only works with file extension.
            When using `accept` with `directory`, the number of files
            reported will be the total amount of files, not the filtered.""")

    filename = param.ClassSelector(
        default=None, class_=(str, list), is_instance=True, doc="""
        Name of the uploaded file(s).""")

    mime_type = param.ClassSelector(
        default=None, class_=(str, list), is_instance=True, doc="""
        Mimetype of the uploaded file(s).""")

    multiple = param.Boolean(default=False, doc="""
        Whether to allow uploading multiple files. If enabled value
        parameter will return a list.""")

    value = param.Parameter(default=None, doc="""
        The uploaded file(s) stored as a single bytes object if
        multiple is False or a list of bytes otherwise.""")

    _rename: ClassVar[Mapping[str, str | None]] = {
        'filename': None
    }

    _source_transforms: ClassVar[Mapping[str, str | None]] = {
        'value': "'data:' + source.mime_type + ';base64,' + value"
    }

    _widget_type: ClassVar[type[Model]] = _BkFileInput

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if 'value' in msg:
            msg.pop('value')
        if 'mime_type' in msg:
            msg.pop('mime_type')
        return msg

    @property
    def _linked_properties(self) -> tuple[str, ...]:
        properties = super()._linked_properties
        return properties + ('filename',)

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'value' in msg:
            if isinstance(msg['value'], str):
                msg['value'] = b64decode(msg['value']) if msg['value'] else None
            else:
                msg['value'] = [b64decode(content) for content in msg['value']]
        if 'filename' in msg and len(msg['filename']) == 0:
            msg['filename'] = None
        if 'mime_type' in msg and len(msg['mime_type']) == 0:
            msg['mime_type'] = None
        return msg

    def save(self, filename):
        """
        Saves the uploaded FileInput data object(s) to file(s) or
        BytesIO object(s).

        Parameters
        ----------
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

    def clear(self):
        """
        Clear the file(s) in the FileInput widget
        """
        self._send_event(ClearInput)


class FileDropper(Widget):
    """
    The `FileDropper` allows the user to upload one or more files to the server.

    It is similar to the `FileInput` widget but additionally adds support
    for chunked uploads, making it possible to upload large files. The
    UI also supports previews for image files. Unlike `FileInput` the
    uploaded files are stored as dictionary of bytes object indexed
    by the filename.

    Reference: https://panel.holoviz.org/reference/widgets/FileDropper.html

    :Example:

    >>> FileDropper(accepted_filetypes=['image/*'], multiple=True)
    """

    accepted_filetypes = param.List(default=[], doc="""
        List of accepted file types. Can be mime types, file extensions
        or wild cards.For instance ['image/*'] will accept all images.
        ['.png', 'image/jpeg'] will only accepts PNGs and JPEGs.""")

    chunk_size = param.Integer(default=10_000_000, doc="""
        Size in bytes per chunk transferred across the WebSocket.""")

    layout = param.Selector(
        default=None, objects=["circle", "compact", "integrated"], doc="""
        Compact mode will remove padding, integrated mode is used to render
        FilePond as part of a bigger element. Circle mode adjusts the item
        position offsets so buttons and progress indicators don't fall outside
        of the circular shape.""")

    max_file_size = param.String(default=None, doc="""
        Maximum size of a file as a string with units given in KB or MB,
        e.g. 5MB or 750KB.""")

    max_files = param.Integer(default=None, doc="""
        Maximum number of files that can be uploaded if multiple=True.""")

    max_total_file_size = param.String(default=None, doc="""
        Maximum size of all uploaded files, as a string with units given
        in KB or MB, e.g. 5MB or 750KB.""")

    mime_type = param.Dict(default={}, doc="""
        A dictionary containing the mimetypes for each of the uploaded
        files indexed by their filename.""")

    multiple = param.Boolean(default=False, doc="""
        Whether to allow uploading multiple files.""")

    previews = param.ListSelector(default=["image", "pdf"],
        objects=["image", "pdf"], doc="""
        List of previews to enable in the FileDropper.
        The following previews are available:
        - image: Adds support for image previews.
        - pdf: Adds support for PDF previews.""")

    value = param.Dict(default={}, doc="""
        A dictionary containing the uploaded file(s) as bytes or string
        objects indexed by the filename. Files that have a text/* mimetype
        will automatically be decoded as utf-8.""")

    width = param.Integer(default=300, allow_None=True, doc="""
      Width of this component. If sizing_mode is set to stretch
      or scale mode this will merely be used as a suggestion.""")

    _rename = {'value': None}

    def __init__(self, **params):
        super().__init__(**params)
        self._file_buffer = {}

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        FileDropper._widget_type = lazy_load(
            'panel.models.file_dropper', 'FileDropper', isinstance(comm, JupyterComm), root,
            ext='filedropper'
        )
        model = super()._get_model(doc, root, parent, comm)
        self._register_events('delete_event', 'upload_event', model=model, doc=doc, comm=comm)
        return model

    def _process_event(self, event: DeleteEvent | UploadEvent):
        data = event.data
        name = data['name']
        if event.event_name == 'delete_event':
            if name in self.mime_type:
                del self.mime_type[name]
            if name in self.value:
                del self.value[name]
            self.param.trigger('mime_type', 'value')
            return

        if data['chunk'] == 1:
            self._file_buffer[name] = []
        self._file_buffer[name].append(data['data'])
        if data['chunk'] != data['total_chunks']:
            return

        buffers = self._file_buffer.pop(name)
        file_buffer: bytes | str = b''.join(buffers)
        if data['type'].startswith('text/') and isinstance(file_buffer, bytes):
            try:
                file_buffer = file_buffer.decode('utf-8')
            except UnicodeDecodeError:
                pass
        self.value[name] = file_buffer
        self.mime_type[name] = data['type']
        self.param.trigger('mime_type', 'value')


class StaticText(Widget):
    """
    The `StaticText` widget displays a text value, but does not allow editing
    it.

    Reference: https://panel.holoviz.org/reference/widgets/StaticText.html

    :Example:

    >>> StaticText(name='Model', value='animagen2')
    """

    value = param.Parameter(default=None, doc="""
        The current value to be displayed.""")

    _format: ClassVar[str] = '<b>{title}</b>: {value}'

    _rename: ClassVar[Mapping[str, str | None]] = {'name': None, 'value': 'text'}

    _target_transforms: ClassVar[Mapping[str, str | None]] = {
        'value': 'target.text.split(": ")[0]+": "+value'
    }

    _source_transforms: ClassVar[Mapping[str, str | None]] = {
        'value': 'value.split(": ")[1]'
    }

    _widget_type: ClassVar[type[Model]] = _BkDiv

    @property
    def _linked_properties(self) -> tuple[str, ...]:
        return ()

    def _init_params(self) -> dict[str, Any]:
        return {
            k: v for k, v in self.param.values().items()
            if k in self._synced_params and (v is not None or k == 'value')
        }

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if 'text' in msg:
            text = msg.pop('text')
            if not isinstance(text, str):
                text = escape("" if text is None else str(text))
            partial = self._format.replace('{value}', '').format(title=self.name)
            if self.name:
                text = self._format.format(title=self.name, value=text.replace(partial, ''))
            msg['text'] = text
        return msg


class DatePicker(Widget):
    """
    The `DatePicker` allows selecting a `date` value using a text box
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

    disabled_dates = param.List(default=None, item_type=(date, str), doc="""
        Dates to make unavailable for selection; others will be available.""")

    enabled_dates = param.List(default=None, item_type=(date, str), doc="""
        Dates to make available for selection; others will be unavailable.""")

    width = param.Integer(default=300, allow_None=True, doc="""
      Width of this component. If sizing_mode is set to stretch
      or scale mode this will merely be used as a suggestion.""")

    description = param.String(default=None, doc="""
        An HTML string describing the function of this component.""")

    _source_transforms: ClassVar[Mapping[str, str | None]] = {}

    _rename: ClassVar[Mapping[str, str | None]] = {
        'start': 'min_date', 'end': 'max_date'
    }

    _widget_type: ClassVar[type[Model]] = _BkDatePicker

    def __init__(self, **params):
        # Since options is the standard for other widgets,
        # it makes sense to also support options here, converting
        # it to enabled_dates
        if 'options' in params:
            options = list(params.pop('options'))
            params['enabled_dates'] = options
        if 'value' in params:
            value = try_datetime64_to_datetime(params['value'])
            if hasattr(value, "date"):
                value = value.date()
            params["value"] = value
        super().__init__(**params)

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        for p in ('start', 'end', 'value'):
            if p not in msg:
                continue
            value = msg[p]
            if isinstance(value, str):
                msg[p] = datetime.date(datetime.strptime(value, '%Y-%m-%d'))
        return msg


class DateRangePicker(Widget):
    """
    The `DateRangePicker` allows selecting a `date` range using a text box
    and a date-picking utility.

    Reference: https://panel.holoviz.org/reference/widgets/DateRangePicker.html

    :Example:

    >>> DateRangePicker(
    ...     value=(date(2025,1,1), date(2025,1,5)),
    ...     start=date(2025,1,1), end=date(2025,12,31),
    ...     name='Date range'
    ... )
    """

    value = param.DateRange(default=None, doc="""
        The current value""")

    start = param.CalendarDate(default=None, doc="""
        Inclusive lower bound of the allowed date selection""")

    end = param.CalendarDate(default=None, doc="""
        Inclusive upper bound of the allowed date selection""")

    disabled_dates = param.List(default=None, item_type=(date, str), doc="""
        Dates to make unavailable for selection; others will be available.""")

    enabled_dates = param.List(default=None, item_type=(date, str), doc="""
        Dates to make available for selection; others will be unavailable.""")

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

    _widget_type: ClassVar[type[Model]] = _BkDateRangePicker

    def __init__(self, **params):
        super().__init__(**params)
        self._update_value_bounds()

    @param.depends('start', 'end', watch=True)
    def _update_value_bounds(self):
        self.param.value.bounds = (self.start, self.end)
        self.param.value._validate(self.value)

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        for p in ('start', 'end', 'value'):
            if p not in msg:
                continue
            value = msg[p]
            if isinstance(value, tuple):
                msg[p] = tuple(self._convert_string_to_date(v) for v in value)
        return msg

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if 'value' in msg and msg['value'] is not None:
            msg['value'] = tuple(
                v if v is None else self._convert_date_to_string(v)
                for v in msg['value']
            )
        if 'min_date' in msg:
            msg['min_date'] = self._convert_date_to_string(msg['min_date'])
        if 'max_date' in msg:
            msg['max_date'] = self._convert_date_to_string(msg['max_date'])
        return msg

    @staticmethod
    def _convert_string_to_date(v):
        return datetime.strptime(v, '%Y-%m-%d').date()

    @staticmethod
    def _convert_date_to_string(v):
        return v.strftime('%Y-%m-%d')


class _DatetimePickerBase(Widget):

    allow_input = param.Boolean(default=False, doc="""
      Enable manual date input in the widget.""")

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

    as_numpy_datetime64 = param.Boolean(default=None, doc="""
        Whether to return values as numpy.datetime64. If left unset,
        will be True if value is a numpy.datetime64, else False.""")

    _source_transforms: ClassVar[Mapping[str, str | None]] = {
        'value': None, 'start': None, 'end': None, 'mode': None
    }

    _rename: ClassVar[Mapping[str, str | None]] = {
        'start': 'min_date', 'end': 'max_date', 'as_numpy_datetime64': None,
    }

    _widget_type: ClassVar[type[Model]] = _bkDatetimePicker

    __abstract = True

    def __init__(self, **params):
        # Since options is the standard for other widgets,
        # it makes sense to also support options here, converting
        # it to enabled_dates
        if 'options' in params:
            options = list(params.pop('options'))
            params['enabled_dates'] = options
        if params.get('as_numpy_datetime64', None) is None:
            params['as_numpy_datetime64'] = isinstance(
                params.get("value"), np.datetime64)
        super().__init__(**params)
        self._update_value_bounds()

    def _convert_to_datetime(self, v):
        if v is None:
            return

        if isinstance(v, Iterable) and not isinstance(v, str):
            container_type = type(v)
            return container_type(
                self._convert_to_datetime(vv)
                for vv in v
            )

        v = try_datetime64_to_datetime(v)
        if isinstance(v, datetime):
            return v
        elif isinstance(v, date):
            return datetime(v.year, v.month, v.day)
        elif isinstance(v, str):
            return datetime.strptime(v, r'%Y-%m-%d %H:%M:%S')
        else:
            raise ValueError(f"Could not convert {v} to datetime")

    @param.depends('start', 'end', watch=True)
    def _update_value_bounds(self):
        self.param.value.bounds = (
            self._convert_to_datetime(self.start),
            self._convert_to_datetime(self.end)
        )
        self.param.value._validate(
            self._convert_to_datetime(self.value)
        )

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = self._serialize_value(msg['value'])
        return msg

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if 'value' in msg:
            msg['value'] = self._deserialize_value(self._convert_to_datetime(msg['value']))
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

    mode = param.String('single', constant=True, doc="""
        The mode of the datetime picker, which is always 'single' for this widget.""")

    def _serialize_value(self, value):
        if isinstance(value, str) and value:
            if self.as_numpy_datetime64:
                value = np.datetime64(value)
            else:
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

    mode = param.String('range', constant=True, doc="""
        The mode of the datetime picker, which is always 'range' for this widget.""")

    def _serialize_value(self, value):
        if isinstance(value, str) and value:
            value = [
                np.datetime64(value)
                if self.as_numpy_datetime64
                else datetime.strptime(value, r'%Y-%m-%d %H:%M:%S')
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


class _TimeCommon(Widget):

    hour_increment = param.Integer(default=1, bounds=(1, None), doc="""
    Defines the granularity of hour value increments in the UI.
    """)

    minute_increment = param.Integer(default=1, bounds=(1, None), doc="""
    Defines the granularity of minute value increments in the UI.
    """)

    second_increment = param.Integer(default=1, bounds=(1, None), doc="""
    Defines the granularity of second value increments in the UI.
    """)

    seconds = param.Boolean(default=False, doc="""
    Allows to select seconds. By default only hours and minutes are
    selectable, and AM/PM depending on the `clock` option.
    """)

    clock = param.Selector(default='12h', objects=['12h', '24h'], doc="""
        Whether to use 12 hour or 24 hour clock.""")

    __abstract = True


class TimePicker(_TimeCommon):
    """
    The `TimePicker` allows selecting a `time` value using a text box
    and a time-picking utility.

    Reference: https://panel.holoviz.org/reference/widgets/TimePicker.html

    :Example:

    >>> TimePicker(
    ...     value="12:59:31", start="09:00:00", end="18:00:00", name="Time"
    ... )
    """

    value = param.ClassSelector(default=None, class_=(dt_time, str), doc="""
        The current value""")

    start = param.ClassSelector(default=None, class_=(dt_time, str), doc="""
        Inclusive lower bound of the allowed time selection""")

    end = param.ClassSelector(default=None, class_=(dt_time, str), doc="""
        Inclusive upper bound of the allowed time selection""")

    format = param.String(default='H:i', doc="""
        Formatting specification for the display of the picked date.

        +---+------------------------------------+------------+
        | H | Hours (24 hours)                   | 00 to 23   |
        | h | Hours                              | 1 to 12    |
        | G | Hours, 2 digits with leading zeros | 1 to 12    |
        | i | Minutes                            | 00 to 59   |
        | S | Seconds, 2 digits                  | 00 to 59   |
        | s | Seconds                            | 0, 1 to 59 |
        | K | AM/PM                              | AM or PM   |
        +---+------------------------------------+------------+

        See also https://flatpickr.js.org/formatting/#date-formatting-tokens.
    """)

    _rename: ClassVar[Mapping[str, str | None]] = {
        'start': 'min_time', 'end': 'max_time', 'format': 'time_format'
    }

    _widget_type: ClassVar[type[Model]] = _BkTimePicker


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

    _widget_type: ClassVar[type[Model]] = _BkColorPicker

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

    _widget_type: ClassVar[type[Model]] = _BkNumericInput

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

    _rename: ClassVar[Mapping[str, str | None]] = {'value_throttled': None}

    _widget_type: ClassVar[type[Model]] = _BkSpinner

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

    @property
    def _linked_properties(self) -> tuple[str, ...]:
        return super()._linked_properties + ('value_throttled',)

    def _update_model(
        self, events: dict[str, param.parameterized.Event], msg: dict[str, Any],
        root: Model, model: Model, doc: Document, comm: Comm | None
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

    def _process_events(self, events: dict[str, Any]) -> None:
        if config.throttled:
            events.pop("value", None)
        super()._process_events(events)


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

    _rename: ClassVar[Mapping[str, str | None]] = {'start': 'low', 'end': 'high'}


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

    _rename: ClassVar[Mapping[str, str | None]] = {'start': 'low', 'end': 'high'}

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

    serializer = param.Selector(default='ast', objects=['ast', 'json'], doc="""
       The serialization (and deserialization) method to use. 'ast'
       uses ast.literal_eval and 'json' uses json.loads and json.dumps.
    """)

    type = param.ClassSelector(default=None, class_=(type, tuple),
                               is_instance=True, doc="""
        A Python literal type (e.g. list, dict, set, int, float, bool, str).""")

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

    _widget_type: ClassVar[Type[Model]] = _BkTextInput  # noqa

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
            raise ValueError(f'{self.__class__.__name__} expected {types} type, but value \'{new}\' '
                             f'is of type {type(new).__name__}.')

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
            raise ValueError(f'DatetimeInput value must be between {start} and {end}, '
                             f'supplied value is {value}')

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

    _composite_type: ClassVar[type[Panel]] = Column

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

    _supports_embed: bool = True

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

    _widget_type: ClassVar[type[Model]] = _BkCheckbox


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
        'value': 'active'
    }

    _widget_type: ClassVar[type[Model]] = _BkSwitch
