import sys

import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.tests.util import serve_component, wait_until
from panel.widgets import JSONEditor

pytestmark = pytest.mark.ui

def test_json_editor_no_console_errors(page):
    editor = JSONEditor(value={'str': 'string', 'int': 1})

    msgs, _ = serve_component(page, editor)

    expect(page.locator('.jsoneditor')).to_have_count(1)

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []

def test_json_editor_edit(page):
    editor = JSONEditor(value={'str': 'string', 'int': 1})

    msgs, _ = serve_component(page, editor)

    expect(page.locator('.jsoneditor')).to_have_count(1)

    page.locator('.jsoneditor-string').click()
    ctrl_key = 'Meta' if sys.platform == 'darwin' else 'Control'
    page.keyboard.press(f'{ctrl_key}+A')
    page.keyboard.press('Backspace')
    page.keyboard.type('new')
    page.locator('.jsoneditor').click()

    wait_until(lambda: editor.value['str'] == 'new', page)

def test_json_editor_edit_in_text_mode(page):
    editor = JSONEditor(value={'str': 'string', 'int': 1}, mode='text')

    msgs, _ = serve_component(page, editor)

    expect(page.locator('.jsoneditor')).to_have_count(1)

    page.locator('.jsoneditor-text').click()
    ctrl_key = 'Meta' if sys.platform == 'darwin' else 'Control'
    page.keyboard.press(f'{ctrl_key}+A')
    page.keyboard.press('Backspace')
    page.keyboard.type('{"str": "new"}')
    page.locator('.jsoneditor').click()

    wait_until(lambda: editor.value['str'] == 'new', page)
