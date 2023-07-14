"""
Contains Media panes including renderers for Audio and Video content.
"""
from __future__ import annotations

import os

from base64 import b64encode
from io import BytesIO
from typing import (
    Any, ClassVar, Dict, List, Mapping,
)

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
    pass

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

    _formats: ClassVar[List[str]]

    _media_type: ClassVar[str]

    _rename: ClassVar[Mapping[str, str | None]] = {
        'sample_rate': None, 'object': 'value'
    }

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

    def _to_np_int16(self, data: np.ndarray):
        dtype = data.dtype

        if dtype in (np.float32, np.float64):
            data = (data * 32768.0).astype(np.int16)

        return data

    def _to_buffer(self, data: np.ndarray|TensorLike):
        if isinstance(data, TensorLike):
            data = data.numpy()
        data = self._to_np_int16(data)

        from scipy.io import wavfile
        buffer = BytesIO()
        wavfile.write(buffer, self.sample_rate, data)
        return buffer

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'js_property_callbacks' in msg:
            del msg['js_property_callbacks']
        return msg

    def _transform_object(self, obj: Any) -> Dict[str, Any]:
        fmt = self._default_mime
        if obj is None:
            data = b''
        elif isinstance(obj, (np.ndarray, TensorLike)):
            fmt = 'wav'
            buffer = self._to_buffer(obj)
            data = b64encode(buffer.getvalue())
        elif os.path.isfile(obj):
            fmt = obj.split('.')[-1]
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

    object = param.ClassSelector(default='', class_=(str, np.ndarray, TensorLike),
                                 allow_None=True, doc="""
        The audio file either local or remote, a 1-dim NumPy ndarray or a 1-dim Torch Tensor.""")

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
    volume = param.Integer(default=100, bounds=(0, 100), doc="""
        The volume of the media player.""")

    _bokeh_model = _BkVideo

    _default_mime = 'mp4'

    _formats = ['mp4', 'webm', 'ogg']

    _media_type = 'video'
