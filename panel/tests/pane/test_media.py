import pathlib

from base64 import b64encode
from io import BytesIO

import numpy as np
import pytest

try:
    from scipy.io import wavfile
except Exception:
    wavfile = None

from panel.pane import Audio, Video
from panel.pane.media import TorchLike

ASSETS = pathlib.Path(__file__).parent / 'assets'

scipy_available = pytest.mark.skipif(wavfile is None, reason="requires scipy")



def test_video_url(document, comm):
    url = 'https://file-examples-com.github.io/uploads/2017/04/file_example_MP4_640_3MG.mp4'
    video = Video(url)
    model = video.get_root(document, comm=comm)

    # To check if url is send to the bokeh model
    assert model.value == url


def test_local_video(document, comm):
    video = Video(str(ASSETS / 'mp4.mp4'))
    model = video.get_root(document, comm=comm)

    assert model.value == 'data:video/mp4;base64,AAAAIGZ0eXBpc29tAAACAGlzb21pc28yYXZjMW1wNDEAAAAIZnJlZQAAAAhtZGF0AAAA1m1vb3YAAABsbXZoZAAAAAAAAAAAAAAAAAAAA+gAAAAAAAEAAAEAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAABidWR0YQAAAFptZXRhAAAAAAAAACFoZGxyAAAAAAAAAABtZGlyYXBwbAAAAAAAAAAAAAAAAC1pbHN0AAAAJal0b28AAAAdZGF0YQAAAAEAAAAATGF2ZjU3LjQxLjEwMA==' # noqa


def test_video_autoplay(document, comm):
    video = Video(str(ASSETS / 'mp4.mp4'), autoplay=True)
    model = video.get_root(document, comm=comm)

    assert model.autoplay

def test_video_muted(document, comm):
    video = Video(str(ASSETS / 'mp4.mp4'), muted=True)
    model = video.get_root(document, comm=comm)

    assert model.muted


def test_local_audio(document, comm):
    audio = Audio(str(ASSETS / 'mp3.mp3'))
    model = audio.get_root(document, comm=comm)

    assert model.value == 'data:audio/mp3;base64,/+MYxAAAAANIAAAAAExBTUUzLjk4LjIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' # noqa


@scipy_available
def test_numpy_audio(document, comm):
    sps = 8000 # Samples per second
    duration = 0.01 # Duration in seconds

    modulator_frequency = 2.0
    carrier_frequency = 120.0
    modulation_index = 2.0

    time = np.arange(sps*duration) / sps
    modulator = np.sin(2.0 * np.pi * modulator_frequency * time) * modulation_index
    waveform = np.sin(2. * np.pi * (carrier_frequency * time + modulator))

    waveform_quiet = waveform * 0.3
    waveform_int = np.int16(waveform_quiet * 32767)

    audio = Audio(waveform_int, sample_rate=sps)

    model = audio.get_root(document, comm=comm)

    assert model.value == 'data:audio/wav;base64,UklGRsQAAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YaAAAAAAAF4ErQjgDOgQuBRDGH0bXB7WIOMifCScJT8mYyYHJi0l1yMLIs0fJR0dGr4WFBMqDw4LzQZ1Ahf+vfl59VfxZu2z6UrmN+OD4DjeXNz42g7aotm22UjaWNvi3ODeTOEe5E3nzuqU7pXywvYO+2v/yAMZCFAMXhA1FMoXDxv7HYMgoCJJJHolLyZlJhwmVSURJFciKiCTHZoaSBeqE8oP' # noqa


@scipy_available
def test_audio_array(document, comm):
    data = np.random.randint(-100,100, 100).astype('int16')
    sample_rate = 10
    buffer = BytesIO()
    wavfile.write(buffer, sample_rate, data)
    b64_encoded = b64encode(buffer.getvalue()).decode('utf-8')

    audio = Audio(data, sample_rate=sample_rate)
    model = audio.get_root(document, comm=comm)
    model_value = model.value

    assert model_value.split(',')[1] == b64_encoded
    assert model.value.startswith('data:audio/wav;base64')


def test_audio_url(document, comm):
    audio_url = 'http://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3'
    audio = Audio(audio_url)
    model = audio.get_root(document, comm=comm)

    assert audio_url == model.value

def test_audio_muted(document, comm):
    audio_url = 'http://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3'
    audio = Audio(audio_url, muted=True)
    model = audio.get_root(document, comm=comm)

    assert model.muted

def test_audio_autoplay(document, comm):
    audio_url = 'http://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3'
    audio = Audio(audio_url, autoplay=True)
    model = audio.get_root(document, comm=comm)

    assert model.autoplay

def get_audio_np_float64(duration=0.01):
    sample_rate = Audio.sample_rate
    time_variable = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
    sine_wave_400hz = 0.5 * np.sin(2 * np.pi * 440 * time_variable)
    return sine_wave_400hz

def get_audio_np_float32(duration=0.01):
    return get_audio_np_float64(duration=duration).astype(np.float32)

def test_audio_float64(document, comm):
    audio = Audio(object=get_audio_np_float64())
    model = audio.get_root(document, comm=comm)
    assert model.value == 'data:audio/wav;base64,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' # noqa

def test_audio_float32(document, comm):
    audio = Audio(object=get_audio_np_float32())
    model = audio.get_root(document, comm=comm)
    assert model.value == 'data:audio/wav;base64,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'  # noqa

class TorchMock:
    def __init__(self):
        self._data = np.linspace(0, 2.0, 16000, endpoint=False)

    def numpy(self):
        return self._data

def test_torch_like():
    mock = TorchMock()

    assert not isinstance(None, TorchLike)
    assert isinstance(mock, TorchLike)

if __name__.startswith("bokeh"):
    import panel as pn
    pn.extension()
    pn.Column(
        "## np.float64",
        pn.pane.Audio(get_audio_np_float64(duration=2.0)),
        # "## np.float32",
        # pn.pane.Audio(get_audio_np_float32(duration=2.0)),
    ).servable()
