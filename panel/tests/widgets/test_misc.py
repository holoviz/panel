from io import BytesIO, StringIO
from base64 import b64encode

import numpy as np
import pytest

try:
    from scipy.io import wavfile
except Exception:
    wavfile = None

from panel.widgets import __file__ as wfile, Audio, FileDownload, Progress

scipy_available = pytest.mark.skipif(wavfile is None, reason="requires scipy")


@scipy_available
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


def test_progress_bounds():
    progress = Progress()
    progress.max = 200
    assert progress.param.value.bounds == (0, 200)
    progress.value = 120
    assert progress.value == 120


def test_file_download_label():
    file_download = FileDownload()

    assert file_download.label == 'No file set'

    file_download = FileDownload(StringIO("data"), filename="abc.py")

    assert file_download.label == "Download abc.py"

    file_download = FileDownload(__file__)

    assert file_download.label == 'Download test_misc.py'

    file_download.auto = False

    assert file_download.label == 'Transfer test_misc.py'

    file_download.embed = True

    assert file_download.label == 'Download test_misc.py'

    file_download.filename = 'abc.py'

    assert file_download.label == 'Download abc.py'


def test_file_download_filename(tmpdir):
    file_download = FileDownload()

    filepath = tmpdir.join("foo.txt")
    filepath.write("content")
    file_download.file = str(filepath)

    assert file_download.filename == "foo.txt"

    file_download._clicks += 1
    file_download.file = __file__

    assert file_download.filename == "test_misc.py"

    file_download.file = StringIO("data")
    assert file_download.filename == "test_misc.py"


def test_file_download_file():
    with pytest.raises(ValueError):
        FileDownload(StringIO("data"))

    with pytest.raises(ValueError):
        FileDownload(embed=True)
    
    with pytest.raises(FileNotFoundError):
        FileDownload("nofile", embed=True)

    with pytest.raises(ValueError):
        FileDownload(666, embed=True)
    
    file_download = FileDownload("nofile")
    with pytest.raises(FileNotFoundError):
        file_download._clicks += 1


def test_file_download_callback():
    file_download = FileDownload(callback=lambda: StringIO("data"), file="abc")

    with pytest.raises(ValueError):
        file_download._clicks += 1
    
    file_download = FileDownload(callback=lambda: StringIO("data"), filename="abc.py")
    
    assert file_download.data is None

    file_download._clicks += 1
    assert file_download.data is not None

    file_download.data = None

    def cb():
        file_download.filename = "cba.py"
        return StringIO("data")

    file_download.callback = cb
    file_download._clicks += 1

    assert file_download.data is not None
    assert file_download.filename == "cba.py"
    assert file_download.label == "Download cba.py"


def test_file_download_transfers():
    file_download = FileDownload(__file__, embed=True)
    assert file_download._transfers == 1

    file_download = FileDownload(__file__)
    assert file_download._transfers == 0
    file_download._clicks += 1
    assert file_download._transfers == 1


def test_file_download_data():
    file_download = FileDownload(__file__, embed=True)

    tfile_data = file_download.data
    assert tfile_data is not None

    file_download.file = wfile
    assert tfile_data != file_download.data

    file_download.data = None
    file_download.embed = False
    file_download.embed = True
    assert file_download.data is not None

    file_download.data = None
    file_download._clicks += 1
    assert file_download.data is not None
