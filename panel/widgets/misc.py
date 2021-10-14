"""
Miscellaneous widgets which do not fit into the other main categories.
"""
import os

from base64 import b64encode

import param

from ..io.notebook import push
from ..io.state import state
from ..models import (
    VideoStream as _BkVideoStream, FileDownload as _BkFileDownload
)
from .base import Widget
from .indicators import Progress # noqa


class VideoStream(Widget):

    format = param.ObjectSelector(default='png', objects=['png', 'jpeg'],
                                  doc="""
        The file format as which the video is returned.""")

    paused = param.Boolean(default=False, doc="""
        Whether the video is currently paused""")

    timeout = param.Number(default=None, doc="""
        Interval between snapshots in millisecons""")

    value = param.String(default='', doc="""
        A base64 representation of the video stream snapshot.""")

    _widget_type = _BkVideoStream

    _rename = {'name': None}

    def snapshot(self):
        """
        Triggers a snapshot of the current VideoStream state to sync
        the widget value.
        """
        for ref, (m, _) in self._models.items():
            m.snapshot = not m.snapshot
            (self, root, doc, comm) = state._views[ref]
            if comm and 'embedded' not in root.tags:
                push(doc, comm)


class FileDownload(Widget):

    auto = param.Boolean(default=True, doc="""
        Whether to download on the initial click or allow for
        right-click save as.""")

    button_type = param.ObjectSelector(default='default', objects=[
        'default', 'primary', 'success', 'warning', 'danger', 'light'])

    callback = param.Callable(default=None, doc="""
        A callable that returns the file path or file-like object.""")

    data = param.String(default=None, doc="""
        The data being transferred.""")

    embed = param.Boolean(default=False, doc="""
        Whether to embed the file on initialization.""")

    file = param.Parameter(default=None, doc="""
        The file, file-like object or file contents to transfer.  If
        the file is not pointing to a file on disk a filename must
        also be provided.""")

    filename = param.String(default=None, doc="""
        A filename which will also be the default name when downloading
        the file.""")

    label = param.String(default="Download file", doc="""
        The label of the download button""")

    _clicks = param.Integer(default=0)

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

    _widget_type = _BkFileDownload

    _rename = {
        'callback': None, 'embed': None, 'file': None,
        '_clicks': 'clicks', 'name': 'title'
    }

    def __init__(self, file=None, **params):
        self._default_label = 'label' not in params
        self._synced = False
        super().__init__(file=file, **params)
        if self.embed:
            self._transfer()
        self._update_label()

    @param.depends('label', watch=True)
    def _update_default(self):
        self._default_label = False

    @param.depends('file', watch=True)
    def _update_filename(self):
        if isinstance(self.file, str):
            self.filename = os.path.basename(self.file)

    @param.depends('auto', 'file', 'filename', watch=True)
    def _update_label(self):
        label = 'Download' if self._synced or self.auto else 'Transfer'
        if self._default_label:
            if self.file is None and self.callback is None:
                label = 'No file set'
            else:
                try:
                    filename = self.filename or os.path.basename(self.file)
                except TypeError:
                    raise ValueError('Must provide filename if file-like '
                                     'object is provided.')
                label = '%s %s' % (label, filename)
            self.label = label
            self._default_label = True

    @param.depends('embed', 'file', 'callback', watch=True)
    def _update_embed(self):
        if self.embed:
            self._transfer()

    @param.depends('_clicks', watch=True)
    def _transfer(self):
        if self.file is None and self.callback is None:
            if self.embed:
                raise ValueError('Must provide a file or a callback '
                                 'if it is to be embedded.')
            return

        from ..param import ParamFunction
        if self.callback is None:
            fileobj = self.file
        else:
            fileobj = ParamFunction.eval(self.callback)
        filename = self.filename
        if isinstance(fileobj, str):
            if not os.path.isfile(fileobj):
                raise FileNotFoundError('File "%s" not found.' % fileobj)
            with open(fileobj, 'rb') as f:
                b64 = b64encode(f.read()).decode("utf-8")
            if filename is None:
                filename = os.path.basename(fileobj)
        elif hasattr(fileobj, 'read'):
            bdata = fileobj.read()
            if not isinstance(bdata, bytes):
                bdata = bdata.encode("utf-8")
            b64 = b64encode(bdata).decode("utf-8")
            if filename is None:
                raise ValueError('Must provide filename if file-like '
                                 'object is provided.')
        else:
            raise ValueError('Cannot transfer unknown object of type %s' %
                             type(fileobj).__name__)

        ext = filename.split('.')[-1]
        for mtype, subtypes in self._mime_types.items():
            stype = None
            if ext in subtypes:
                stype = subtypes[ext]
                break
        if stype is None:
            mime = 'application/octet-stream'
        else:
            mime = '{type}/{subtype}'.format(type=mtype, subtype=stype)

        data = "data:{mime};base64,{b64}".format(mime=mime, b64=b64)
        self._synced = True

        self.param.set_param(data=data, filename=filename)
        self._update_label()
        self._transfers += 1
