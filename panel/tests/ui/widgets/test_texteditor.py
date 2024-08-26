import sys

import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel import depends
from panel.layout import Column
from panel.pane import HTML
from panel.tests.util import serve_component, wait_until
from panel.widgets import RadioButtonGroup, TextEditor

pytestmark = pytest.mark.ui


def test_texteditor_renders(page):
    widget = TextEditor()

    serve_component(page, widget)

    expect(page.locator('.ql-container')).to_be_visible()


def test_texteditor_toolbar_by_default(page):
    widget = TextEditor()

    serve_component(page, widget)

    shadowdivs = page.locator('.bk-panel-models-quill-QuillInput > div')
    expect(shadowdivs).to_have_count(2)
    expect(page.locator('.ql-toolbar')).to_be_visible()

def test_texteditor_no_toolbar(page):
    widget = TextEditor(toolbar=False)

    serve_component(page, widget)

    shadowdivs = page.locator('.bk-panel-models-quill-QuillInput > div')
    expect(shadowdivs).to_have_count(1)
    expect(page.locator('.ql-container')).to_be_visible()


def test_texteditor_init_with_value(page):
    widget = TextEditor(value='test')

    serve_component(page, widget)

    expect(page.locator('.ql-container')).to_have_text('test')


def test_texteditor_enter_value(page):
    widget = TextEditor()

    serve_component(page, widget)

    editor = page.locator('.ql-editor')
    editor.fill('test')

    expect(page.locator('.ql-container')).to_have_text('test')
    wait_until(lambda: widget.value == '<p>test</p>', page)


def test_texteditor_regression_copy_paste(page):
    # https://github.com/holoviz/panel/issues/5545
    widget = TextEditor()
    html = HTML('test')

    serve_component(page, Column(html, widget))

    page.get_by_text('test').select_text()

    ctrl_key = 'Meta' if sys.platform == 'darwin' else 'Control'
    page.get_by_text('test').press(f'{ctrl_key}+KeyC')

    page.locator('.ql-editor').press(f'{ctrl_key}+KeyV')

    expect(page.locator('.ql-container')).to_have_text('test')
    wait_until(lambda: widget.value == '<p>test</p>', page)


def test_texteditor_regression_preserve_formatting_on_view_change(page):
    # https://github.com/holoviz/panel/pull/5511#issuecomment-1719706966
    expected = '<ul><li>aaa</li><li>bbb</li><li>ccc</li></ul>'
    widget = TextEditor(value=expected)
    contents = [widget, HTML('<h1>Bob</h1>')]
    contents = [Column(c) for c in contents]
    w_radio = RadioButtonGroup(options=[0, 1])

    placeholder = Column(contents[0])

    @depends(w_radio, watch=True)
    def update_view(i):
        placeholder[:] = [contents[i]]

    app = Column(w_radio, placeholder)

    serve_component(page, app)

    expect(page.locator('.ql-container')).to_be_visible()
    wait_until(lambda: widget.value == expected, page)

    html = page.locator('.ql-editor').inner_html()
    assert html == expected

    page.locator('button', has_text='1').click()
    wait_until(lambda: w_radio.value == 1, page)
    page.wait_for_timeout(200)
    page.locator('button', has_text='0').click()
    wait_until(lambda: w_radio.value == 0, page)

    html = page.locator('.ql-editor').inner_html()
    assert html == expected
    wait_until(lambda: widget.value == expected, page)


def test_texteditor_regression_click_toolbar_cursor_stays_in_place(page):
    # https://github.com/holoviz/panel/pull/5511#issuecomment-1719706966
    widget = TextEditor()

    serve_component(page, widget)

    editor = page.locator('.ql-editor')
    editor.press('A')
    editor.press('Enter')
    page.locator('.ql-bold').click()
    editor.press('B')
    wait_until(lambda: widget.value == '<p>A</p><p><strong>B</strong></p>', page)
