import sys

import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.tests.util import serve_component, wait_until
from panel.widgets import CodeEditor

pytestmark = pytest.mark.ui


def test_code_editor_on_keyup(page):

    editor = CodeEditor(value="print('Hello World!')", on_keyup=True)
    serve_component(page, editor)
    ace_input = page.locator(".ace_content")
    expect(ace_input).to_have_count(1)
    ace_input.click()

    page.keyboard.press("Enter")
    page.keyboard.type('print("Hello Panel!")')

    expect(page.locator(".ace_content")).to_have_text("print('Hello World!')\nprint(\"Hello Panel!\")", use_inner_text=True)
    wait_until(lambda: editor.value_input == "print('Hello World!')\nprint(\"Hello Panel!\")", page)
    assert editor.value == "print('Hello World!')\nprint(\"Hello Panel!\")"

    # clear the editor
    editor.value = ""
    expect(page.locator(".ace_content")).to_have_text("", use_inner_text=True)
    assert editor.value == ""
    assert editor.value_input == ""

    # enter Hello UI
    ace_input.click()
    page.keyboard.type('print("Hello UI!")')
    expect(page.locator(".ace_content")).to_have_text("print(\"Hello UI!\")", use_inner_text=True)

    wait_until(lambda: editor.value == "print(\"Hello UI!\")", page)


def test_code_editor_not_on_keyup(page):

    editor = CodeEditor(value="print('Hello World!')", on_keyup=False)
    serve_component(page, editor)
    ace_input = page.locator(".ace_content")
    expect(ace_input).to_have_count(1)
    ace_input.click()

    page.keyboard.press("Enter")
    page.keyboard.type('print("Hello Panel!")')

    expect(page.locator(".ace_content")).to_have_text("print('Hello World!')\nprint(\"Hello Panel!\")", use_inner_text=True)
    wait_until(lambda: editor.value_input == "print('Hello World!')\nprint(\"Hello Panel!\")")
    assert editor.value == "print('Hello World!')"

    # page click outside the editor; sync the value
    page.locator("body").click()
    assert editor.value_input == "print('Hello World!')\nprint(\"Hello Panel!\")"
    wait_until(lambda: editor.value == "print('Hello World!')\nprint(\"Hello Panel!\")")

    # clear the editor
    editor.value = ""
    expect(page.locator(".ace_content")).to_have_text("", use_inner_text=True)
    assert editor.value == ""
    assert editor.value_input == ""

    # enter Hello UI
    ace_input.click()
    page.keyboard.type('print("Hello UI!")')
    expect(page.locator(".ace_content")).to_have_text("print(\"Hello UI!\")", use_inner_text=True)
    assert editor.value == ""

    ctrl_key = 'Meta' if sys.platform == 'darwin' else 'Control'
    page.keyboard.down(ctrl_key)
    page.keyboard.press("Enter")
    page.keyboard.up(ctrl_key)

    wait_until(lambda: editor.value == "print(\"Hello UI!\")", page)
