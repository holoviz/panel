"""
Miscellaneous widgets which do not fit into the other main categories.
"""
import os

from io import BytesIO
from base64 import b64encode
from six import string_types

import param
import numpy as np

from ..io.notebook import push
from ..io.state import state
from ..models import (
    Audio as _BkAudio, VideoStream as _BkVideoStream, FileDownload as _BkFileDownload
)
from .base import Widget
from .indicators import Progress # noqa


class _MediaBase(Widget):

    loop = param.Boolean(default=False, doc="""
        Whether the meida should loop""")

    time = param.Number(default=0, doc="""
        The current timestamp""")

    throttle = param.Integer(default=250, doc="""
        How frequently to sample the current playback time in
        milliseconds""")

    paused = param.Boolean(default=True, doc="""
        Whether the media is currently paused""")

    value = param.String(default='', doc="""
        The media file either local or remote.""")

    volume = param.Number(default=None, bounds=(0, 100), doc="""
        The volume of the media player.""")

    _rename = {'name': None, 'sample_rate': None}

    _default_mime = None

    _media_type = None

    def __init__(self, **params):
        self.param.warning('%s widget is deprecated, use the equivalent '
                           'Pane type instead.' % type(self).__name__)
        super().__init__(**params)

    def _from_numpy(self, data):
        from scipy.io import wavfile
        buffer = BytesIO()
        wavfile.write(buffer, self.sample_rate, data)
        return buffer

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)

        if 'value' in msg:
            value =  msg['value']
            if isinstance(value, np.ndarray):
                fmt = 'wav'
                buffer = self._from_numpy(value)
                data = b64encode(buffer.getvalue())
            elif os.path.isfile(value):
                fmt = value.split('.')[-1]
                with open(value, 'rb') as f:
                    data = f.read()
                data = b64encode(data)
            elif value.lower().startswith('http'):
                return msg
            elif not value:
                data, fmt = b'', self._default_mime
            else:
                raise ValueError('Value should be either path to a sound file or numpy array')
            template = 'data:audio/{mime};base64,{data}'
            msg['value'] = template.format(data=data.decode('utf-8'),
                                           mime=fmt)
        return msg


class Audio(_MediaBase):

    sample_rate = param.Integer(default=44100, doc="""
        The sample_rate of the audio when given a NumPy array.""")

    value = param.ClassSelector(default='', class_=(string_types + (np.ndarray,)), doc="""
        The audio file either local or remote.""")

    _media_type = 'audio'

    _default_mime = 'wav'

    _widget_type = _BkAudio


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
        'default', 'primary', 'success', 'warning', 'danger'])

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
