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
from panel.pane.media import TensorLike, _is_1dim_int_or_float_tensor

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
    assert model.value == 'data:audio/wav;base64,UklGRpYDAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YXIDAAAAAAIEAAj3C+EPuxOCFzEbxB45Iosltyi7K5IuOzGyM/U1AjjWOXE7zzzxPdQ+dz/cP/8/4z+GP+k+DT7zPJs7CDo6ODM29jOFMeIuECwRKeklmyIqH5ob7hcqFFIQaQx0CHYEdABz/HT4fPSQ8LTs6+g55aLhKt7U2qPXm9S+0RDPk8xKyjfIXMa7xFbDLcJDwZjALcABwBfAbMACwdbB6sI6xMfFj8ePycbLMc7P0JzTlta52QPdcOD946bnZ+s97yTzGPcV+xf/GQMZBxEL/g7dEqgWXRr3HXMhzSQCKA8r8S2kMCczdjWPN3E5GTuFPLQ9pj5YP8o//T/vP6E/Ez9FPjk97ztpOqg4rjZ9NBgygC+4LMMppCZfI/UfbBzGGAcVMxFODVsJXwVeAVz9XPli9XPxk+3F6Q7mceLx3pPbWdhI1WHSqM8gzcvKq8jDxhXFosNrwnPBucA/wAbADMBTwNrAoMGmwunDaMUixxbJQMugzTPQ9dLl1f/YQNym3yzjzuaL6lzuQPIx9i36Lv4wAjAGKwobDv0RzRWHGSgdqyANJEsnYSpNLQswmTL0NBo3CDm9Ojc8dT10PjU/tj/3P/g/uD85P3k+ez0/PMc6EzkmNwE1qDIbMF4tcypdJyAkvyA8HZ0Z4xUUEjIOQgpIBkcCRf5E+kj2V/Jz7qHq5OZA47rfVNwR2fbVBtNC0K/NTssiyS3HccXxw6zCpsHewFXADcAFwD3AtsBuwWXCmsMMxbnGn8i+yhHNmc9Q0jbVR9iA293eXOL55a/pfe1c8Uv1RPlE/UYBSAVECTcNHRHxFLEYVxzhH0sjkiaxKacscC8JMnA0ojadOF865zsyPUA+Dz+eP+4//T/MP1s/qj66PYw8ITt7OZs3gzU1M7MwAS4gKxQo4CSGIQsechq+FvMSFQ8oCzAHMAMu/yz7L/c781Tvfeu75xLkhOAW3czZqNat09/QQM7Ty5vJmsfRxUPE8cLcwQbBb8AYwAHAK8CVwD7BJ8JOw7LEUsYsyD7KhcwBz67RitSR18HaFt6O4STl1eie7HrwZfRc+Fv8XQBfBF0IUgw7EBQU2ReFGxYfhyLWJf8o/yvSLnYx6TMnNi84/jmTO+w8CD7lPoM/4T//P90/ej/YPvY91jx5O+A5DTgBNsAzSjGiLswrySg=' # noqa

def test_audio_float32(document, comm):
    audio = Audio(object=get_audio_np_float32())
    model = audio.get_root(document, comm=comm)
    assert model.value == 'data:audio/wav;base64,UklGRpYDAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YXIDAAAAAAIEAAj3C+EPuxOCFzEbxB45Iosltyi7K5IuOzGyM/U1AjjWOXE7zzzxPdQ+dz/cP/8/4z+GP+k+DT7zPJs7CDo6ODM29jOFMeIuECwRKeklmyIqH5ob7hcqFFIQaQx0CHYEdABz/HT4fPSQ8LTs6+g55aLhKt7U2qPXm9S+0RDPk8xKyjfIXMa7xFbDLcJDwZjALcABwBfAbMACwdbB6sI6xMfFj8ePycbLMc7P0JzTlta52QPdcOD946bnZ+s97yTzGPcV+xf/GQMZBxEL/g7dEqgWXRr3HXMhzSQCKA8r8S2kMCczdjWPN3E5GTuFPLQ9pj5YP8o//T/vP6E/Ez9FPjk97ztpOqg4rjZ9NBgygC+4LMMppCZfI/UfbBzGGAcVMxFODVsJXwVeAVz9XPli9XPxk+3F6Q7mceLx3pPbWdhI1WHSqM8gzcvKq8jDxhXFosNrwnPBucA/wAbADMBTwNrAoMGmwunDaMUixxbJQMugzTPQ9dLl1f/YQNym3yzjzuaL6lzuQPIx9i36Lv4wAjAGKwobDv0RzRWHGSgdqyANJEsnYSpNLQswmTL0NBo3CDm9Ojc8dT10PjU/tj/3P/g/uD85P3k+ez0/PMc6EzkmNwE1qDIbMF4tcypdJyAkvyA8HZ0Z4xUUEjIOQgpIBkcCRf5E+kj2V/Jz7qHq5OZA47rfVNwR2fbVBtNC0K/NTssiyS3HccXxw6zCpsHewFXADcAFwD3AtsBuwWXCmsMMxbnGn8i+yhHNmc9Q0jbVR9iA293eXOL55a/pfe1c8Uv1RPlE/UYBSAVECTcNHRHxFLEYVxzhH0sjkiaxKacscC8JMnA0ojadOF865zsyPUA+Dz+eP+4//T/MP1s/qj66PYw8ITt7OZs3gzU1M7MwAS4gKxQo4CSGIQsechq+FvMSFQ8oCzAHMAMu/yz7L/c781Tvfeu75xLkhOAW3czZqNat09/QQM7Ty5vJmsfRxUPE8cLcwQbBb8AYwAHAK8CVwD7BJ8JOw7LEUsYsyD7KhcwBz67RitSR18HaFt6O4STl1eie7HrwZfRc+Fv8XQBfBF0IUgw7EBQU2ReFGxYfhyLWJf8o/yvSLnYx6TMnNi84/jmTO+w8CD7lPoM/4T//P90/ej/YPvY91jx5O+A5DTgBNsAzSjGiLswrySg='  # noqa


class TensorMock:
    def __init__(self, duration=2.0):
        self._data = get_audio_np_float32(duration=duration)

    def numpy(self):
        return self._data

    def dim(self):
        return self._data.ndim

    @property
    def dtype(self):
        return "torch.float32"

def test_torch_like():
    mock = TensorMock()

    assert not isinstance(None, TensorLike)
    assert isinstance(mock, TensorLike)

def get_audio_tensor_float32(duration=2.0):
    return TensorMock(duration=duration)

def test_audio_tensor_float32(document, comm):
    obj = get_audio_tensor_float32(duration=0.01)
    assert _is_1dim_int_or_float_tensor(obj)
    audio = Audio(object=obj)
    model = audio.get_root(document, comm=comm)
    assert model.value == 'data:audio/wav;base64,UklGRpYDAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YXIDAAAAAAIEAAj3C+EPuxOCFzEbxB45Iosltyi7K5IuOzGyM/U1AjjWOXE7zzzxPdQ+dz/cP/8/4z+GP+k+DT7zPJs7CDo6ODM29jOFMeIuECwRKeklmyIqH5ob7hcqFFIQaQx0CHYEdABz/HT4fPSQ8LTs6+g55aLhKt7U2qPXm9S+0RDPk8xKyjfIXMa7xFbDLcJDwZjALcABwBfAbMACwdbB6sI6xMfFj8ePycbLMc7P0JzTlta52QPdcOD946bnZ+s97yTzGPcV+xf/GQMZBxEL/g7dEqgWXRr3HXMhzSQCKA8r8S2kMCczdjWPN3E5GTuFPLQ9pj5YP8o//T/vP6E/Ez9FPjk97ztpOqg4rjZ9NBgygC+4LMMppCZfI/UfbBzGGAcVMxFODVsJXwVeAVz9XPli9XPxk+3F6Q7mceLx3pPbWdhI1WHSqM8gzcvKq8jDxhXFosNrwnPBucA/wAbADMBTwNrAoMGmwunDaMUixxbJQMugzTPQ9dLl1f/YQNym3yzjzuaL6lzuQPIx9i36Lv4wAjAGKwobDv0RzRWHGSgdqyANJEsnYSpNLQswmTL0NBo3CDm9Ojc8dT10PjU/tj/3P/g/uD85P3k+ez0/PMc6EzkmNwE1qDIbMF4tcypdJyAkvyA8HZ0Z4xUUEjIOQgpIBkcCRf5E+kj2V/Jz7qHq5OZA47rfVNwR2fbVBtNC0K/NTssiyS3HccXxw6zCpsHewFXADcAFwD3AtsBuwWXCmsMMxbnGn8i+yhHNmc9Q0jbVR9iA293eXOL55a/pfe1c8Uv1RPlE/UYBSAVECTcNHRHxFLEYVxzhH0sjkiaxKacscC8JMnA0ojadOF865zsyPUA+Dz+eP+4//T/MP1s/qj66PYw8ITt7OZs3gzU1M7MwAS4gKxQo4CSGIQsechq+FvMSFQ8oCzAHMAMu/yz7L/c781Tvfeu75xLkhOAW3czZqNat09/QQM7Ty5vJmsfRxUPE8cLcwQbBb8AYwAHAK8CVwD7BJ8JOw7LEUsYsyD7KhcwBz67RitSR18HaFt6O4STl1eie7HrwZfRc+Fv8XQBfBF0IUgw7EBQU2ReFGxYfhyLWJf8o/yvSLnYx6TMnNi84/jmTO+w8CD7lPoM/4T//P90/ej/YPvY91jx5O+A5DTgBNsAzSjGiLswrySg='  # noqa
