"""The Microphone widget controls the Media Stream Recording API of the browser.

It wraps the [Media Stream Recording API](https://developer.mozilla.org/en-US/docs/Web/API/MediaStream_Recording_API/Using_the_MediaStream_Recording_API).
"""

import tempfile

from os import PathLike
from pathlib import Path

import numpy as np
import param

from ..custom import JSComponent
from .button import BUTTON_TYPES


class Microphone(JSComponent):
    # Alternatively AudioRecorder. Or MediaRecorder if should support both video and audio.
    """The Microphone widget can be used to record audio and create speech to "other media" applications.

    recorder = Microphone(format="mp3")
    pn.Column("Click the button below to start recording", recorder)
    """

    value = param.Bytes(doc="""The value recorded in the format given by the format parameter""")
    # Maybe I will have to transfer as data url instead of bytes.

    format = param.Selector(default="webm", objects=["wav", "webm", "mp3"], doc="""The format of the value""")
    # webm by default because that is the default in the Mediau Stream Recording API

    # Alternatively: state = param.Selector(default="not-recoding", objects=["not-recording", "recording"])

    # The below parameters are aligned with SpeechToText
    state = param.Selector(default="started", objects=["paused", "started", "stopped"])

    continuous = param.Boolean(default=False, doc="""If True incremental values are streamed during the recording.
        If False a single value is transferred when the recording ends.""")
    # Alternatively: streaming = param.Boolean(default=False)

    button_hide = param.Boolean(default=False, label="Hide the Button", doc="""
        If True no button is shown. If False a toggle Start/ Stop button is shown.""")

    button_type = param.ObjectSelector(default="light", objects=BUTTON_TYPES+['light', 'dark'], doc="""
        The button styling.""")

    button_not_started = param.String(label="Button Text when not started", doc="""
        The text to show on the button when the Media
        service is NOT started.  If '' a *muted microphone* icon is
        shown.""")

    button_started = param.String(label="Button Text when started", doc="""
        The text to show on the button when the Media
        service is started. If '' a *microphone* icon is
        shown.""")

    options = param.Dict(doc="""Wavesurfer Options""")
    # We should figure out if we want to use Wavesurfer: https://wavesurfer.xyz/docs/

    @staticmethod
    def _to_data_url(self, value: bytes)->str:
        raise NotImplementedError()

    @param.depends("value")
    def value_as_data_url(self):
        return self._to_data_url(self.value)

    @staticmethod
    def _to_numpy(self, value: bytes)->tuple[int, np.ndarray]:
        """Returns the sample rate and numpy array"""
        raise NotImplementedError()

    # I want to make it easy for users to bind to the numpy array but not spend resources on
    # calculating it if not needed.
    @param.depends("value")
    def value_as_numpy(self)->tuple[int, np.ndarray]:
        """Returns the value as a tuple of sample rate and numpy array"""
        return self._to_numpy(self.value)

    @param.depends("value")
    def value_as_file(self)->Path:
        # This is currently the best way to bind to the Audio player!
        if not self.value:
            return None
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{self.format}") as temp_file:
                temp_file.write(self.value)
                temp_file_name = temp_file.name
            return temp_file_name

    def save(self, path: PathLike):
        raise NotImplementedError()
