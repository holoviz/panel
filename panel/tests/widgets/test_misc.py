from io import StringIO

import pytest

from panel.widgets import FileDownload, Progress, __file__ as wfile


def test_progress_bounds():
    progress = Progress()
    progress.max = 200
    assert progress.param.value.bounds == (-1, 200)
    progress.value = 120
    assert progress.value == 120
    progress.value = -1
    assert progress.value == -1


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
