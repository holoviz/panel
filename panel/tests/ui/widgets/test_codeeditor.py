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


def _find_ace_editor_js():
    """Return JS snippet that locates the Ace editor through shadow DOM."""
    return """
        function findAceEditor(root) {
            const elements = root.querySelectorAll('*');
            for (const el of elements) {
                if (el.shadowRoot) {
                    const ed = el.shadowRoot.querySelector('.ace_editor');
                    if (ed && ed.env && ed.env.editor) return ed.env.editor;
                    const nested = findAceEditor(el.shadowRoot);
                    if (nested) return nested;
                }
            }
            return null;
        }
    """


def _get_ace_annotations(page):
    """Get annotations from the Ace editor session via JS evaluation."""
    return page.evaluate(f"""() => {{
        {_find_ace_editor_js()}
        const editor = findAceEditor(document);
        if (!editor) return [];
        return editor.session.getAnnotations();
    }}""")


def _get_ace_use_worker(page):
    """Get whether the Ace session worker is enabled."""
    return page.evaluate(f"""() => {{
        {_find_ace_editor_js()}
        const editor = findAceEditor(document);
        if (!editor) return null;
        return editor.session.getOption('useWorker');
    }}""")


def _assert_annotations_stable(page, expected_count, checks=5, interval=200):
    """Assert annotations stay at expected_count over multiple checkpoints.

    More robust than a single hardcoded sleep — verifies persistence across
    multiple intervals, catching any delayed worker overwrites.
    """
    for _ in range(checks):
        page.wait_for_timeout(interval)
        assert len(_get_ace_annotations(page)) == expected_count


def test_code_editor_annotations(page):
    """Test that user-set annotations are not overwritten by Ace's worker."""
    code = "test:\n- {a: 1, b: 2}\n- {c: 3, d: 4}\n"
    editor = CodeEditor(value=code, language="yaml", annotations=[])

    serve_component(page, editor)
    ace_input = page.locator(".ace_content")
    expect(ace_input).to_have_count(1)

    # Worker should be enabled initially (no user annotations)
    wait_until(lambda: _get_ace_use_worker(page) is True, page)

    # Set user annotations
    editor.annotations = [
        {"row": 1, "column": 0, "text": "a warning", "type": "warning"},
        {"row": 2, "column": 0, "text": "an error", "type": "error"},
    ]

    # Wait for annotations to sync and worker to be disabled
    wait_until(lambda: len(_get_ace_annotations(page)) == 2, page)
    wait_until(lambda: _get_ace_use_worker(page) is False, page)

    # Verify annotations persist across multiple checkpoints
    # (worker would overwrite within ~200ms if still active)
    _assert_annotations_stable(page, expected_count=2)
    annotations = _get_ace_annotations(page)
    assert annotations[0]["type"] == "warning"
    assert annotations[1]["type"] == "error"

    # Clear annotations — worker should re-enable
    editor.annotations = []
    wait_until(lambda: len(_get_ace_annotations(page)) == 0, page)
    wait_until(lambda: _get_ace_use_worker(page) is True, page)


def test_code_editor_annotations_constructor(page):
    """Test that annotations provided at construction time are applied."""
    code = "test:\n- {a: 1}\n"
    annotations = [{"row": 1, "column": 0, "text": "note", "type": "info"}]
    editor = CodeEditor(value=code, language="yaml", annotations=annotations)

    serve_component(page, editor)
    expect(page.locator(".ace_content")).to_have_count(1)

    # Worker should be disabled (user annotations set at construction)
    wait_until(lambda: _get_ace_use_worker(page) is False, page)

    # Annotations set at construction should survive across checkpoints
    _assert_annotations_stable(page, expected_count=1)
    result = _get_ace_annotations(page)
    assert result[0]["type"] == "info"
    assert result[0]["text"] == "note"


def test_code_editor_annotations_persist_on_language_change(page):
    """Test that annotations persist when the language/mode is changed."""
    code = "x = 1\ny = 2\n"
    editor = CodeEditor(value=code, language="python", annotations=[])

    serve_component(page, editor)
    expect(page.locator(".ace_content")).to_have_count(1)

    # Set user annotations
    editor.annotations = [
        {"row": 0, "column": 0, "text": "check this", "type": "warning"},
    ]
    wait_until(lambda: len(_get_ace_annotations(page)) == 1, page)

    # Change the language — triggers setMode() which spawns a new worker
    editor.language = "yaml"

    # Annotations should survive the language change and worker respawn
    _assert_annotations_stable(page, expected_count=1)
    annotations = _get_ace_annotations(page)
    assert annotations[0]["type"] == "warning"
    assert annotations[0]["text"] == "check this"
    # Worker should still be disabled after language change
    assert _get_ace_use_worker(page) is False


def test_code_editor_annotations_replacement(page):
    """Test that replacing annotations (set A -> set B) works correctly."""
    code = "line1\nline2\nline3\n"
    editor = CodeEditor(value=code, language="text", annotations=[])

    serve_component(page, editor)
    expect(page.locator(".ace_content")).to_have_count(1)

    # Set initial annotations (set A)
    editor.annotations = [
        {"row": 0, "column": 0, "text": "first warning", "type": "warning"},
    ]
    wait_until(lambda: len(_get_ace_annotations(page)) == 1, page)
    assert _get_ace_annotations(page)[0]["text"] == "first warning"

    # Replace with different annotations (set B)
    editor.annotations = [
        {"row": 1, "column": 0, "text": "error here", "type": "error"},
        {"row": 2, "column": 0, "text": "also here", "type": "error"},
    ]
    wait_until(lambda: len(_get_ace_annotations(page)) == 2, page)
    annotations = _get_ace_annotations(page)
    assert annotations[0]["text"] == "error here"
    assert annotations[1]["text"] == "also here"


def test_code_editor_annotations_persist_on_value_change(page):
    """Test that annotations persist when the editor value is changed."""
    code = "x = 1\n"
    editor = CodeEditor(value=code, language="python", annotations=[])

    serve_component(page, editor)
    expect(page.locator(".ace_content")).to_have_count(1)

    # Set user annotations
    editor.annotations = [
        {"row": 0, "column": 0, "text": "flagged", "type": "error"},
    ]
    wait_until(lambda: len(_get_ace_annotations(page)) == 1, page)

    # Change the code programmatically
    editor.value = "y = 2\nz = 3\n"
    wait_until(lambda: "y = 2" in page.locator(".ace_content").inner_text(), page)

    # Annotations should still be present after value change
    _assert_annotations_stable(page, expected_count=1)
    assert _get_ace_annotations(page)[0]["text"] == "flagged"


def test_code_editor_worker_resumes_after_clear(page):
    """Test that Ace's syntax worker resumes producing annotations after clear.

    Full lifecycle: worker active -> user annotations (worker off) ->
    clear (worker back on) -> worker produces its own annotations.
    Uses intentionally invalid JavaScript to trigger Ace's JS worker.
    """
    # Invalid JS that Ace's worker will flag with syntax errors
    invalid_js = "function foo( {\n  return\n}\n"
    editor = CodeEditor(value=invalid_js, language="javascript", annotations=[])

    serve_component(page, editor)
    expect(page.locator(".ace_content")).to_have_count(1)

    # Step 1: Worker should be active and produce annotations on invalid JS
    wait_until(lambda: len(_get_ace_annotations(page)) > 0, page)
    worker_annotations = _get_ace_annotations(page)
    assert any(a["type"] == "error" for a in worker_annotations)

    # Step 2: Set user annotations — worker should be disabled
    editor.annotations = [
        {"row": 0, "column": 0, "text": "user note", "type": "info"},
    ]
    wait_until(lambda: _get_ace_use_worker(page) is False, page)
    wait_until(lambda: len(_get_ace_annotations(page)) == 1, page)
    assert _get_ace_annotations(page)[0]["text"] == "user note"

    # Step 3: Clear user annotations — worker should re-enable and
    # produce its own annotations on the still-invalid JS code
    editor.annotations = []
    wait_until(lambda: _get_ace_use_worker(page) is True, page)
    wait_until(lambda: len(_get_ace_annotations(page)) > 0, page)
    resumed_annotations = _get_ace_annotations(page)
    assert any(a["type"] == "error" for a in resumed_annotations)
    # Verify these are worker-produced, not our cleared user annotations
    assert all(a["text"] != "user note" for a in resumed_annotations)
