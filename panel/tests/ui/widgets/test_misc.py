import io
import re
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

    # A late re-render from the server replaces the input while typing
    page.click('.bk-tab:not(.bk-active)')
    expect(page.locator('.bk-input')).to_have_count(0)
    page.click('.bk-tab:not(.bk-active)')
    expect(page.locator('.bk-input')).to_have_count(1)

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


@not_windows
def test_file_download_auto_false_serves_fresh_data_on_each_click(page):
    text_input = TextInput(value='abc')

    @param.depends(text_input.param.value)
    def create_file(value):
        return io.StringIO(value)

    download = FileDownload(callback=create_file, filename='f.txt', auto=False)

    serve_component(page, Column(text_input, download))

    link = page.locator('.bk-btn > a')
    expect(link).to_have_text('Transfer f.txt')

    # The first click only prepares the file and turns the button into a link
    link.click()
    expect(link).to_have_text('Download f.txt')
    expect(link).to_have_attribute('href', re.compile('^blob:'))

    for expected in ('abc', 'def'):
        text_input.value = expected
        with page.expect_download() as download_info:
            link.click()
        tmp = tempfile.NamedTemporaryFile(suffix='.txt')
        download_info.value.save_as(tmp.name)
        try:
            assert tmp.file.read().decode('utf-8') == expected
        finally:
            tmp.close()
