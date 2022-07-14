"""
Contains Media panes including renderers for Audio and Video content.
"""
from __future__ import annotations

import os

from base64 import b64encode
from io import BytesIO
from typing import (
    TYPE_CHECKING, Any, ClassVar, List, Mapping, Optional,
)

import numpy as np
import param

from ..models import Audio as _BkAudio, Video as _BkVideo
from ..util import isfile, isurl
from .base import PaneBase

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


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

    autoplay = param.Boolean(default=False, doc="""
        When True, it specifies that the output will play automatically.
        In Chromium browsers this requires the user to click play once.""")

    muted = param.Boolean(default=False, doc="""
        When True, it specifies that the output should be muted.""")

    _default_mime: ClassVar[str]

    _formats: ClassVar[List[str]]

    _media_type: ClassVar[str]

    _rename: ClassVar[Mapping[str, str | None]] = {
        'name': None, 'sample_rate': None, 'object': 'value'}

    _rerender_params: ClassVar[List[str]] = []

    _updates: ClassVar[bool] = True

    __abstract = True

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        if isinstance(obj, str):
            if isfile(obj) and any(obj.endswith('.'+fmt) for fmt in cls._formats):
                return True
            if isurl(obj, cls._formats):
                return True
        if hasattr(obj, 'read'):  # Check for file like object
            return True
        return False

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
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
    """
    The `Audio` pane displays an audio player given a local or remote audio
    file or numpy array.

    The pane also allows access and control over the player state including
    toggling of playing/paused and loop state, the current time, and the
    volume.

    The audio player supports ogg, mp3, and wav files as well as numpy arrays.

    Reference: https://panel.holoviz.org/reference/panes/Audio.html

    :Example:

    >>> Audio('http://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3', name='Audio')
    """

    object = param.ClassSelector(default='', class_=(str, np.ndarray,),
                                 allow_None=True, doc="""
        The audio file either local or remote.""")

    sample_rate = param.Integer(default=44100, doc="""
        The sample_rate of the audio when given a NumPy array.""")

    _bokeh_model = _BkAudio

    _default_mime = 'wav'

    _formats = ['mp3', 'wav', 'ogg']

    _media_type = 'audio'

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        return (super().applies(obj) or
                (isinstance(obj, np.ndarray) and obj.ndim==1 and obj.dtype in [np.int16, np.uint16]))


class Video(_MediaBase):
    """
    The `Video` Pane displays a video player given a local or remote video
    file.

    The widget also allows access and control over the player state including
    toggling of playing/paused and loop state, the current time, and the
    volume.

    Depending on the browser the video player supports mp4, webm, and ogg
    containers and a variety of codecs.

    Reference: https://panel.holoviz.org/reference/panes/Video.html

    :Example:

    >>> Video(
    ...     'https://file-examples-com.github.io/uploads/2017/04/file_example_MP4_640_3MG.mp4',
    ...     width=640, height=360, loop=True
    ... )
    """

    _bokeh_model = _BkVideo

    _default_mime = 'mp4'

    _formats = ['mp4', 'webm', 'ogg']

    _media_type = 'video'
