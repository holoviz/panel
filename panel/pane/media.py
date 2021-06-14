"""
Contains Media panes including renderers for Audio and Video content.
"""
import os

from base64 import b64encode
from io import BytesIO
from six import string_types

import numpy as np
import param

from ..models import Audio as _BkAudio, Video as _BkVideo
from ..util import isfile, isurl
from .base import PaneBase


class _MediaBase(PaneBase):

    loop = param.Boolean(default=False, doc="""
        Whether the meida should loop""")

    time = param.Number(default=0, doc="""
        The current timestamp""")

    throttle = param.Integer(default=250, doc="""
        How frequently to sample the current playback time in milliseconds""")

    paused = param.Boolean(default=True, doc="""
        Whether the media is currently paused""")

    object = param.String(default='', allow_None=True, doc="""
        The media file either local or remote.""")

    volume = param.Number(default=None, bounds=(0, 100), doc="""
        The volume of the media player.""")

    _default_mime = None

    _formats = []

    _media_type = None

    _rename = {'name': None, 'sample_rate': None, 'object': 'value'}

    _rerender_params = []

    _updates = True

    __abstract = True

    @classmethod
    def applies(cls, obj):
        if isinstance(obj, string_types):
            if isfile(obj) and any(obj.endswith('.'+fmt) for fmt in cls._formats):
                return True
            if isurl(obj, cls._formats):
                return True
        if hasattr(obj, 'read'):  # Check for file like object
            return True
        return False

    def _get_model(self, doc, root=None, parent=None, comm=None):
        props = self._process_param_change(self._init_params())
        model = self._bokeh_model(**props)
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        self._link_props(model, list(model.properties()), doc, root, comm)
        return model

    def _from_numpy(self, data):
        from scipy.io import wavfile
        buffer = BytesIO()
        wavfile.write(buffer, self.sample_rate, data)
        return buffer

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'js_property_callbacks' in msg:
            del msg['js_property_callbacks']
        return msg

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if 'value' in msg:
            value = msg['value']
            fmt = self._default_mime
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
            elif not value or value == f'data:{self._media_type}/{fmt};base64,':
                data = b''
            else:
                raise ValueError(f'Object should be either path to a {self._media_type} file or numpy array.')
            msg['value'] = f"data:{self._media_type}/{fmt};base64,{data.decode('utf-8')}"
        return msg


class Audio(_MediaBase):

    object = param.ClassSelector(default='', class_=(string_types + (np.ndarray,)),
                                 allow_None=True, doc="""
        The audio file either local or remote.""")

    sample_rate = param.Integer(default=44100, doc="""
        The sample_rate of the audio when given a NumPy array.""")

    _bokeh_model = _BkAudio

    _default_mime = 'wav'

    _formats = ['mp3', 'wav', 'ogg']

    _media_type = 'audio'

    @classmethod
    def applies(cls, obj):
        return (super().applies(obj) or 
                (isinstance(obj, np.ndarray) and obj.ndim==1 and obj.dtype in [np.int16, np.uint16]))


class Video(_MediaBase):

    _bokeh_model = _BkVideo

    _default_mime = 'mp4'

    _formats = ['mp4', 'webm', 'ogg']

    _media_type = 'video'

