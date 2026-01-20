"""
Miscellaneous widgets which do not fit into the other main categories.
"""
from __future__ import annotations

from base64 import b64encode
from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

import param

from param.parameterized import eval_function_with_deps, iscoroutinefunction
from pyviz_comms import JupyterComm

from ..io.notebook import push
from ..io.resources import CDN_DIST
from ..io.state import state
from ..models import (
    FileDownload as _BkFileDownload, VideoStream as _BkVideoStream,
)
from ..util import lazy_load
from .base import Widget
from .button import BUTTON_STYLES, BUTTON_TYPES, IconMixin
from .indicators import Progress  # noqa

if TYPE_CHECKING:
    from bokeh.model import Model


class VideoStream(Widget):
    """
    The `VideoStream` displays a video from a local stream (for example from a webcam) and allows
    accessing the streamed video data from Python.

    Reference: https://panel.holoviz.org/reference/widgets/VideoStream.html

    :Example:

    >>> VideoStream(name='Video Stream', timeout=100)
    """

    format = param.Selector(default='png', objects=['png', 'jpeg'],
                                  doc="""
        The file format as which the video is returned.""")

    paused = param.Boolean(default=False, doc="""
        Whether the video is currently paused""")

    timeout = param.Number(default=None, doc="""
        Interval between snapshots in millisecons""")

    value = param.String(default='', doc="""
        A base64 representation of the video stream snapshot.""")

    _widget_type: ClassVar[type[Model]] = _BkVideoStream

    _rename: ClassVar[Mapping[str, str | None]] = {'name': None}

    def snapshot(self):
        """
        Triggers a snapshot of the current VideoStream state to sync
        the widget value.
        """
        for ref, (m, _) in self._models.copy().items():
            m.snapshot = not m.snapshot
            (self, root, doc, comm) = state._views[ref]
            if comm and 'embedded' not in root.tags:
                push(doc, comm)


class FileDownload(IconMixin):
    """
    The `FileDownload` widget allows a user to download a file.

    It works either by sending the file data to the browser on initialization
    (`embed`=True), or when the button is clicked.

    Reference: https://panel.holoviz.org/reference/widgets/FileDownload.html

    :Example:

    >>> FileDownload(file='IntroductionToPanel.ipynb', filename='intro.ipynb')
    """

    auto = param.Boolean(default=True, doc="""
        Whether to download on the initial click or allow for
        right-click save as.""")

    button_type = param.Selector(default='default', objects=BUTTON_TYPES, doc="""
        A button theme; should be one of 'default' (white), 'primary'
        (blue), 'success' (green), 'info' (yellow), 'light' (light),
        or 'danger' (red).""")

    button_style = param.Selector(default='solid', objects=BUTTON_STYLES, doc="""
        A button style to switch between 'solid', 'outline'.""")

    callback = param.Callable(default=None, allow_refs=False, doc="""
        A callable that returns the file path or file-like object.""")

    data = param.String(default=None, doc="""
        The data being transferred.""")

    embed = param.Boolean(default=False, doc="""
        Whether to embed the file on initialization.""")

    file = param.Parameter(default=None, doc="""
        The file, Path, file-like object or file contents to transfer.  If
        the file is not pointing to a file on disk a filename must
        also be provided.""")

    filename = param.String(default=None, doc="""
        A filename which will also be the default name when downloading
        the file.""")

    label = param.String(default="Download file", doc="""
        The label of the download button""")

    description = param.String(default=None, doc="""
        An HTML string describing the function of this component.""")

    _clicks = param.Integer(default=0, doc="Internal counter for button clicks.")

    _transfers = param.Integer(default=0)

    _mime_types = {
        'application': {
            'pdf': 'pdf', 'zip': 'zip'
        },
        'audio': {
            'mp3': 'mp3', 'ogg': 'ogg', 'wav': 'wav', 'webm': 'webm'
        },
        'image': {
            'apng': 'apng', 'bmp': 'bmp', 'gif': 'gif', 'ico': 'x-icon',
            'cur': 'x-icon', 'jpg': 'jpeg', 'jpeg': 'jpeg',  'png': 'png',
            'svg': 'svg+xml', 'tif': 'tiff', 'tiff': 'tiff', 'webp': 'webp'
        },
        'text': {
            'css': 'css', 'csv': 'plain;charset=UTF-8', 'js': 'javascript',
            'html': 'html', 'txt': 'plain;charset=UTF-8'
        },
        'video': {
            'mp4': 'mp4', 'ogg': 'ogg', 'webm': 'webm'
        }
    }

    _rename: ClassVar[Mapping[str, str | None]] = {
        'callback': None, 'button_style': None, 'file': None, '_clicks': 'clicks',
        'value': None
    }

    _stylesheets: ClassVar[list[str]] = [f'{CDN_DIST}css/button.css']

    _widget_type: ClassVar[type[Model]] = _BkFileDownload

    def __init__(self, file=None, **params):
        self._default_label = 'label' not in params
        self._synced = False
        super().__init__(file=file, **params)
        if self.embed:
            self._transfer()
        self._update_label()
        if "filename" not in params:
            self._update_filename()

    def _process_param_change(self, params):
        if 'button_style' in params or 'css_classes' in params:
            params['css_classes'] = [
                params.pop('button_style', self.button_style)
            ] + params.get('css_classes', self.css_classes)
        return super()._process_param_change(params)

    @param.depends('label', watch=True)
    def _update_default(self):
        self._default_label = False

    @property
    def _is_file_path(self)->bool:
        return isinstance(self.file, (str, Path))

    @property
    def _file_path(self)->Path:
        return Path(self.file)

    @param.depends('file', watch=True)
    def _update_filename(self):
        if self._is_file_path:
            self.filename = self._file_path.name

    @param.depends('auto', 'file', 'filename', watch=True)
    def _update_label(self):
        label = 'Download' if self._synced or self.auto else 'Transfer'
        if self._default_label:
            if self.file is None and self.callback is None:
                label = 'No file set'
            else:
                try:
                    filename = self.filename or self._file_path.name
                except TypeError:
                    raise ValueError('Must provide filename if file-like '
                                     'object is provided.') from None
                label = f'{label} {filename}'
            self.label = label
            self._default_label = True

    @param.depends('embed', 'file', 'callback', watch=True)
    def _update_embed(self):
        if self.embed:
            self._transfer()

    def _sync_data(self, fileobj):
        filename = self.filename
        if isinstance(fileobj, (str, Path)):
            fileobj = Path(fileobj)
            if not fileobj.exists():
                raise FileNotFoundError(f'File "{fileobj}" not found.')
            with open(fileobj, 'rb') as f:
                b64 = b64encode(f.read()).decode("utf-8")
            if filename is None:
                filename = fileobj.name
        elif hasattr(fileobj, 'read'):
            if hasattr(fileobj, 'seek'):
                fileobj.seek(0)
            bdata = fileobj.read()
            if not isinstance(bdata, bytes):
                bdata = bdata.encode("utf-8")
            b64 = b64encode(bdata).decode("utf-8")
            if filename is None:
                raise ValueError('Must provide filename if file-like '
                                 'object is provided.')
        else:
            raise ValueError(f'Cannot transfer unknown object of type {type(fileobj).__name__}')

        ext = filename.split('.')[-1]
        stype, mtype = None, None
        for mime_type, subtypes in self._mime_types.items():
            if ext in subtypes:
                mtype = mime_type
                stype = subtypes[ext]
                break
        if stype is None:
            mime = 'application/octet-stream'
        else:
            mime = f'{mtype}/{stype}'

        data = f"data:{mime};base64,{b64}"
        self._synced = True
        self.param.update(data=data, filename=filename)
        self._update_label()
        self._transfers += 1

    async def _async_sync_data(self):
        fileobj = await eval_function_with_deps(self.callback)
        self._sync_data(fileobj)

    @param.depends('_clicks', watch=True)
    def _transfer(self):
        if self.file is None and self.callback is None:
            if self.embed:
                raise ValueError('Must provide a file or a callback '
                                 'if it is to be embedded.')
            return

        if self.callback is None:
            fileobj = self.file
        else:
            if iscoroutinefunction(self.callback):
                state.execute(self._async_sync_data)
                return
            else:
                fileobj = eval_function_with_deps(self.callback)
        self._sync_data(fileobj)



class JSONEditor(Widget):
    """
    The `JSONEditor` provides a visual editor for JSON-serializable
    datastructures, e.g. Python dictionaries and lists, with functionality for
    different editing modes, inserting objects and validation using JSON
    Schema.

    Reference: https://panel.holoviz.org/reference/widgets/JSONEditor.html

    :Example:

    >>> JSONEditor(value={
    ...     'dict'  : {'key': 'value'},
    ...     'float' : 3.14,
    ...     'int'   : 1,
    ...     'list'  : [1, 2, 3],
    ...     'string': 'A string',
    ... }, mode='code')
    """

    menu = param.Boolean(default=True, doc="""
        Adds main menu bar - Contains format, sort, transform, search
        etc. functionality. true by default. Applicable in all types
        of mode.""")

    mode = param.Selector(default='tree', objects=[
        "tree", "view", "form", "text", "preview"], doc="""
        Sets the editor mode. In 'view' mode, the data and
        datastructure is read-only. In 'form' mode, only the value can
        be changed, the data structure is read-only. Mode 'code'
        requires the Ace editor to be loaded on the page. Mode 'text'
        shows the data as plain text. The 'preview' mode can handle
        large JSON documents up to 500 MiB. It shows a preview of the
        data, and allows to transform, sort, filter, format, or
        compact the data.""")

    search = param.Boolean(default=True, doc="""
        Enables a search box in the upper right corner of the
        JSONEditor. true by default. Only applicable when mode is
        'tree', 'view', or 'form'.""")

    selection = param.List(default=[], doc="""
        Current selection.""")

    schema = param.Dict(default=None, doc="""
        Validate the JSON object against a JSON schema. A JSON schema
        describes the structure that a JSON object must have, like
        required properties or the type that a value must have.

        See http://json-schema.org/ for more information.""")

    templates = param.List(doc="""
        Array of templates that will appear in the context menu, Each
        template is a json object precreated that can be added as a
        object value to any node in your document.""")

    value = param.Parameter(default={}, doc="""
        JSON data to be edited.""")

    _rename: ClassVar[Mapping[str, str | None]] = {
        'name': None, 'value': 'data'
    }

    def _get_model(self, doc, root=None, parent=None, comm=None):
        JSONEditor._widget_type = lazy_load(
            "panel.models.jsoneditor", "JSONEditor", isinstance(comm, JupyterComm)
        )
        model = super()._get_model(doc, root, parent, comm)
        self._register_events('json_edit', model=model, doc=doc, comm=comm)
        return model

    def _process_event(self, event) -> None:
        if event.event_name == 'json_edit':
            self.value  = event.data
