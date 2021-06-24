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


def test_local_audio(document, comm):
    audio = Audio(str(ASSETS / 'mp3.mp3'))
    model = audio.get_root(document, comm=comm)

    assert model.value == 'data:audio/mp3;base64,/+MYxAAAAANIAAAAAExBTUUzLjk4LjIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' # noqa


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
