import io
import sys
import tempfile
import time

import param
import pytest

from panel.io.server import serve
from panel.layout import Column, Tabs
from panel.widgets import FileDownload, TextInput

pytestmark = pytest.mark.ui
not_windows = pytest.mark.skipif(sys.platform=='win32', reason="Does not work on Windows")


@not_windows
def test_file_download_updates_when_navigating_between_dynamic_tabs(page, port):
    text_input = TextInput(value='abc')

    @param.depends(text_input.param.value)
    def create_file(value):
        return io.StringIO(value)

    download = FileDownload(
        callback=create_file, filename='f.txt', embed=False
    )

    tabs = Tabs(
        ("Download", Column(text_input, download)),
        ("Dummy", "dummy tab"),
        dynamic=True
    )

    serve(tabs, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    with page.expect_download() as download_info:
        page.click('.bk-btn > a')

    download = download_info.value
    tmp = tempfile.NamedTemporaryFile(suffix='.txt')
    download.save_as(tmp.name)
    assert tmp.file.read().decode('utf-8') == 'abc'

    page.click('.bk-tab:not(.bk-active)')
    page.click('.bk-tab:not(.bk-active)')

    page.click('.bk-input')

    page.keyboard.type('def')
    page.keyboard.press('Enter')

    with page.expect_download() as download_info:
        page.click('.bk-btn > a')

    download = download_info.value
    tmp = tempfile.NamedTemporaryFile(suffix='.txt')
    download.save_as(tmp.name)
    assert tmp.file.read().decode('utf-8') == 'abcdef'
