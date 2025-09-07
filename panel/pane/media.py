"""
Contains Media panes including renderers for Audio and Video content.
"""
from __future__ import annotations

import os
import pathlib

from base64 import b64encode
from collections.abc import Mapping
from io import BytesIO
from typing import Any, ClassVar

import numpy as np
import param

from ..models import Audio as _BkAudio, Video as _BkVideo
from ..util import isfile, isurl
from .base import ModelPane


class TensorLikeMeta(type):
    """See https://blog.finxter.com/python-__instancecheck__-magic-method/"""
    def __instancecheck__(self, instance):
        numpy_attr = getattr(instance, "numpy", "")
        dim_attr = getattr(instance, "dim", "")
        return (
            bool(numpy_attr) and
            callable(numpy_attr) and
            callable(dim_attr) and
            hasattr(instance, "dtype")
        )

# When support for Python 3.7 is dropped, Torchlike should be implemented as a typing.Protocol
# That would provide type checking and intellisense in editors
class TensorLike(metaclass=TensorLikeMeta):
    """A class similar to torch.Tensor. We don't want to make PyTorch a dependency of this project
    """

class _MediaBase(ModelPane):

    loop = param.Boolean(default=False, doc="""
        Whether the media should loop""")

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

    _formats: ClassVar[list[str]]

    _media_type: ClassVar[str]

    _rename: ClassVar[Mapping[str, str | None]] = {
        'sample_rate': None, 'object': 'value'
    }

    _rerender_params: ClassVar[list[str]] = []

    _updates: ClassVar[bool] = True

    __abstract = True

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        if isinstance(obj, (pathlib.Path, str)):
            path = str(obj)
            if isfile(path) and any(path.endswith('.'+fmt) for fmt in cls._formats):
                return True
            if isurl(path, cls._formats):
                return True
        if hasattr(obj, 'read') or isinstance(obj, bytes):  # Check for file like object (or bytes)
            return True
        return False

    def _to_np_int16(self, data: np.ndarray) -> np.ndarray:
        dtype = data.dtype

        if dtype in (np.float32, np.float64):
            data = (data * 32768.0).astype(np.int16)

        return data

    def _to_buffer(self, data: np.ndarray | TensorLike):
        if isinstance(data, np.ndarray):
            values = data
        elif isinstance(data, TensorLike):
            values = data.numpy()
        data = self._to_np_int16(values)

        from scipy.io import wavfile
        buffer = BytesIO()
        wavfile.write(buffer, self.sample_rate, data)
        return buffer

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'js_property_callbacks' in msg:
            del msg['js_property_callbacks']
        return msg

    @classmethod
    def _detect_format(cls, data: bytes):
        return cls._default_mime

    def _transform_object(self, obj: Any) -> dict[str, Any]:
        fmt = self._default_mime
        if obj is None:
            data = b''
        elif isinstance(obj, bytes):
            fmt = self._detect_format(obj)
            data = b64encode(obj)
        elif isinstance(obj, (np.ndarray, TensorLike)):
            fmt = 'wav'
            buffer = self._to_buffer(obj)
            data = b64encode(buffer.getvalue())
        elif isinstance(obj, BytesIO):
            bffr = obj.read()
            fmt = self._detect_format(bffr)
            data = b64encode(bffr)
        elif os.path.isfile(obj):
            fmt = str(obj).split('.')[-1]
            with open(obj, 'rb') as f:
                data = f.read()
            data = b64encode(data)
        elif obj.lower().startswith('http'):
            return dict(object=obj)
        elif not obj or obj == f'data:{self._media_type}/{fmt};base64,':
            data = b''
        else:
            raise ValueError(f'Object should be either path to a {self._media_type} file or numpy array.')
        b64 = f"data:{self._media_type}/{fmt};base64,{data.decode('utf-8')}"
        return dict(object=b64)

_VALID_TORCH_DTYPES_FOR_AUDIO = [
    "torch.short", "torch.int16",
    "torch.half", "torch.float16",
    "torch.float", "torch.float32",
    "torch.double", "torch.float64",
]

_VALID_NUMPY_DTYPES_FOR_AUDIO = [np.int16, np.uint16, np.float32, np.float64]

def _is_1dim_int_or_float_tensor(obj: Any)->bool:
    return (
        isinstance(obj, TensorLike) and
        obj.dim()==1 and
        str(obj.dtype) in _VALID_TORCH_DTYPES_FOR_AUDIO
    )

def _is_1dim_int_or_float_ndarray(obj: Any)->bool:
    return (
        isinstance(obj, np.ndarray) and
        obj.ndim==1 and
        obj.dtype in _VALID_NUMPY_DTYPES_FOR_AUDIO
    )

def _detect_audio_format(data: bytes) -> str | None:
    """
    Detect the audio format of a byte stream.

    Parameters
    ----------
    data: bytes
       The audio data as bytes.

    Returns
    -------
    "mp3", "wav", "ogg", or None if unknown.
    """
    # MP3: ID3 tag or MPEG frame sync (0xFFEx or 0xFFFx)
    if data.startswith(b"ID3") or (len(data) > 2 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0):
        return "mp3"
    elif data.startswith(b"RIFF") and data[8:12] == b"WAVE":
        return "wav"
    elif data.startswith(b"OggS"):
        return "ogg"
    else:
        return None

class Audio(_MediaBase):
    """
    The `Audio` pane displays an audio player given a local or remote audio
    file, a NumPy Array or Torch Tensor.

    The pane also allows access and control over the player state including
    toggling of playing/paused and loop state, the current time, and the
    volume.

    The audio player supports ogg, mp3, and wav files

    If SciPy is installed, 1-dim Numpy Arrays and 1-dim
    Torch Tensors are also supported. The dtype must be one of the following

    - numpy: np.int16, np.uint16, np.float32, np.float64
    - torch: torch.short, torch.int16, torch.half, torch.float16, torch.float, torch.float32,
    torch.double, torch.float64

    The array or Tensor input will be downsampled to 16bit and converted to a wav file by SciPy.

    Reference: https://panel.holoviz.org/reference/panes/Audio.html

    :Example:

    >>> Audio('http://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3', name='Audio')
    """

    object = param.ClassSelector(default='', class_=(str, bytes, pathlib.Path, BytesIO, np.ndarray, TensorLike),
                                 allow_None=True, doc="""
        The audio file either local or remote, a 1-dim NumPy ndarray or a 1-dim Torch Tensor
        or a bytes or BytesIO object.""")

    sample_rate = param.Integer(default=44100, doc="""
        The sample_rate of the audio when given a NumPy array or Torch tensor.""")

    _bokeh_model = _BkAudio

    _default_mime = 'wav'

    _formats = ['mp3', 'wav', 'ogg']

    _media_type = 'audio'

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        return (super().applies(obj)
            or _is_1dim_int_or_float_ndarray(obj)
            or _is_1dim_int_or_float_tensor(obj)
        )

    @classmethod
    def _detect_format(cls, data: bytes):
        return _detect_audio_format(data) or cls._default_mime


def _detect_video_format(data: bytes) -> str | None:
    """
    Detects whether the given bytes represent an MP4, WebM, or OGG container.

    Parameters
    ----------
    data: bytes
       The audio data as bytes.

    Returns
    -------
    "mp4", "webm", "ogg", or None if unknown.
    """
    # OGG: starts with "OggS"
    if data.startswith(b'OggS'):
        return 'ogg'
    # MP4: contains "ftyp" at byte offset 4
    elif len(data) > 12 and data[4:8] == b'ftyp':
        return 'mp4'  # Fallback — most 'ftyp' indicate MP4
    # WebM: EBML signature — starts with 0x1A45DFA3
    elif data.startswith(b'\x1A\x45\xDF\xA3'):
        return 'webm'
    return None


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

    object = param.ClassSelector(default='', class_=(str, pathlib.Path, BytesIO, bytes), allow_None=True, doc="""
        The video file either local or remote as a string or URL or as a bytes or BytesIO object.""")

    volume = param.Integer(default=100, bounds=(0, 100), doc="""
        The volume of the media player.""")

    _bokeh_model = _BkVideo

    _default_mime = 'mp4'

    _formats = ['mp4', 'webm', 'ogg']

    _media_type = 'video'

    @classmethod
    def _detect_format(cls, data: bytes):
        return _detect_video_format(data) or cls._default_mime
