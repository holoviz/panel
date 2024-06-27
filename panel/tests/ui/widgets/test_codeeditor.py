import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.tests.util import serve_component, wait_until
from panel.widgets import CodeEditor

pytestmark = pytest.mark.ui


def test_code_editor(page):

    editor = CodeEditor(value="print('Hello World!')")
    serve_component(page, editor)
    ace_input = page.locator(".ace_content")
    expect(ace_input).to_have_count(1)
    ace_input.click()

    page.keyboard.press("Enter")
    page.keyboard.type('print("Hello Panel!")')
    expect(page.locator(".ace_content")).to_have_text("print('Hello World!')\nprint(\"Hello Panel!\")")
    wait_until(lambda: editor.value_input == "print('Hello World!')\nprint(\"Hello Panel!\")")
    assert editor.value == "print('Hello World!')"

    # page click outside the editor
    page.locator("body").click()
    assert editor.value_input == "print('Hello World!')\nprint(\"Hello Panel!\")"
    wait_until(lambda: editor.value == "print('Hello World!')\nprint(\"Hello Panel!\")")
