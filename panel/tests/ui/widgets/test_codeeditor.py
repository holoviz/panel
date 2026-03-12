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


def test_code_editor_value_update_no_selection(page):
    """Test that updating editor value programmatically doesn't select all text."""
    editor = CodeEditor(value="foo", on_keyup=True)
    serve_component(page, editor)
    ace_input = page.locator(".ace_content")
    expect(ace_input).to_have_count(1)

    # Click in the editor and position cursor after 'f' (position 1)
    ace_input.click()
    page.keyboard.press('End')  # Go to end
    page.keyboard.press('ArrowLeft')  # Move left twice to be after 'f'
    page.keyboard.press('ArrowLeft')

    # Type 'X' to verify cursor position (should result in "fXoo")
    page.keyboard.type('X')
    wait_until(lambda: editor.value == "fXoo", page)

    # Update the value programmatically (simulating periodic callback)
    # This should preserve cursor position at index 2 (after "fX")
    editor.value = "fXoo bar"
    wait_until(lambda: editor.value == "fXoo bar", page)
    expect(page.locator(".ace_content")).to_have_text("fXoo bar", use_inner_text=True)

    # Type some more text - cursor should still be at position 2
    # If cursor position was preserved, typing 'Y' should give "fXYoo bar"
    # If cursor moved to end, typing 'Y' would give "fXoo barY"
    page.keyboard.type('Y')

    # Check that cursor was preserved (Y inserted at original position)
    wait_until(lambda: editor.value == "fXYoo bar", page)


def test_code_editor_value_update_cursor_to_end_when_invalid(page):
    """Test that cursor moves to end when its position becomes invalid after update."""
    editor = CodeEditor(value="line1\nline2\nline3\nline4", on_keyup=True)
    serve_component(page, editor)
    ace_input = page.locator(".ace_content")
    expect(ace_input).to_have_count(1)

    # Click in the editor and position cursor on line 3
    ace_input.click()
    page.keyboard.press('End')  # Go to end of document
    page.keyboard.press('ArrowUp')  # Move up to line 3
    page.keyboard.press('Home')  # Go to start of line 3

    # Type 'X' to verify cursor position (should be at start of line 3)
    page.keyboard.type('X')
    wait_until(lambda: "Xline3" in editor.value, page)

    # Update the value programmatically to something with fewer lines
    # The cursor was on line 3 (row 2), but now there's only 1 line
    editor.value = "short"
    wait_until(lambda: editor.value == "short", page)
    expect(page.locator(".ace_content")).to_have_text("short", use_inner_text=True)

    # Type some text - cursor should now be at the end since old position is invalid
    # Typing 'Y' should give "shortY"
    page.keyboard.type('Y')

    # Check that cursor moved to end (Y appended at end)
    wait_until(lambda: editor.value == "shortY", page)


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
