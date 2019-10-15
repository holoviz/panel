from __future__ import absolute_import, division, unicode_literals

from io import BytesIO
from base64 import b64encode

import numpy as np
from scipy.io import wavfile

from panel.widgets import Audio

def test_audio_array(document, comm):
    data = np.random.randint(-100,100, 100).astype('int16')
    sample_rate = 10
    buffer = BytesIO()
    wavfile.write(buffer, sample_rate, data)
    b64_encoded = b64encode(buffer.getvalue()).decode('utf-8')

    audio = Audio(name='Button', value=data, sample_rate=sample_rate)
    widget = audio.get_root(document, comm=comm)
    widget_value = widget.value

    assert widget_value.split(',')[1] == b64_encoded
    assert widget.value.startswith('data:audio/wav;base64')


def test_audio_url(document, comm):
    audio_url = 'http://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3'
    audio2 = Audio(name='Audio', value=audio_url)
    url_widget = audio2.get_root(document, comm=comm)

    assert audio_url == url_widget.value

