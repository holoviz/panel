"""
Playwright test for the counter anywidget example.

This is the REFERENCE TEST — other anywidget test files should follow this pattern.

Tests:
    1. Widget renders (button appears with initial value)
    2. No unexpected console errors
    3. Browser -> Python sync (click button, value increments in Python)
    4. Python -> Browser sync (change value in Python, button label updates)
"""
import anywidget
import pytest
import traitlets

import panel as pn

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.tests.util import serve_component, wait_until

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui


# --- Widget definition (same as research/anywidget/examples/counter.py) ---

class CounterWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) {
        let btn = document.createElement("button");
        btn.className = "counter-btn";
        btn.innerHTML = `count is ${model.get("value")}`;
        btn.addEventListener("click", () => {
            model.set("value", model.get("value") + 1);
            model.save_changes();
        });
        model.on("change:value", () => {
            btn.innerHTML = `count is ${model.get("value")}`;
        });
        el.appendChild(btn);
    }
    export default { render };
    """
    value = traitlets.Int(0).tag(sync=True)


def test_counter_renders(page):
    """Widget renders and shows the initial value."""
    widget = CounterWidget(value=5)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    btn = page.locator("button.counter-btn")
    expect(btn).to_be_visible()
    expect(btn).to_contain_text("count is 5")

    assert_no_console_errors(msgs)


def test_counter_click_increments(page):
    """Clicking the button increments the value (browser -> Python sync)."""
    widget = CounterWidget(value=0)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    btn = page.locator("button.counter-btn")
    btn.click()

    # Wait for Python-side value to update
    wait_until(lambda: widget.value == 1, page)
    assert pane.component.value == 1

    btn.click()
    btn.click()

    wait_until(lambda: widget.value == 3, page)
    expect(btn).to_contain_text("count is 3")

    assert_no_console_errors(msgs)


def test_counter_python_to_browser(page):
    """Changing value from Python updates the button label (Python -> browser)."""
    widget = CounterWidget(value=0)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    btn = page.locator("button.counter-btn")
    expect(btn).to_contain_text("count is 0")

    # Change from Python side via the component
    pane.component.value = 42

    expect(btn).to_contain_text("count is 42")
    assert widget.value == 42

    assert_no_console_errors(msgs)
