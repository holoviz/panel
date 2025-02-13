import io
import sys
import tempfile

import param
import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.layout import Column, Tabs
from panel.tests.util import serve_component
from panel.widgets import FileDownload, TextInput

pytestmark = pytest.mark.ui
not_windows = pytest.mark.skipif(sys.platform=='win32', reason="Does not work on Windows")


def test_file_download_label_updates(page):

    download = FileDownload(filename='f.txt', embed=False, callback=lambda: io.StringIO())

    serve_component(page, download)

    expect(page.locator('.bk-btn a')).to_have_text('Download f.txt')

    download.filename = 'g.txt'

    expect(page.locator('.bk-btn a')).to_have_text('Download g.txt')

@not_windows
def test_file_download_updates_when_navigating_between_dynamic_tabs(page):
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

    serve_component(page, tabs)

    with page.expect_download() as download_info:
        page.click('.bk-btn > a')

    download = download_info.value
    tmp = tempfile.NamedTemporaryFile(suffix='.txt')
    download.save_as(tmp.name)
    try:
        assert tmp.file.read().decode('utf-8') == 'abc'
    finally:
        tmp.close()

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
    try:
        assert tmp.file.read().decode('utf-8') == 'abcdef'
    finally:
        tmp.close()
