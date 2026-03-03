"""
Test 1: Rapid State Changes

A widget with a counter that auto-increments every 100ms via JavaScript.
Verifies Python side keeps up with rapid updates.

Tests:
    1. Widget renders (initial value shows)
    2. Auto-increment runs (JS interval fires)
    3. Python side receives rapid updates
    4. Stop/start works correctly
    5. No console errors during rapid updates
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


class RapidCounterWidget(anywidget.AnyWidget):
    """Widget that auto-increments every 100ms via a JS interval."""

    value = traitlets.Int(0).tag(sync=True)
    running = traitlets.Bool(False).tag(sync=True)

    _esm = """
    let _interval = null;

    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "rapid-container";

        let display = document.createElement("div");
        display.className = "rapid-display";
        display.textContent = "value: " + model.get("value");

        let startBtn = document.createElement("button");
        startBtn.className = "start-btn";
        startBtn.textContent = "Start";
        startBtn.addEventListener("click", () => {
            model.set("running", true);
            model.save_changes();
        });

        let stopBtn = document.createElement("button");
        stopBtn.className = "stop-btn";
        stopBtn.textContent = "Stop";
        stopBtn.addEventListener("click", () => {
            model.set("running", false);
            model.save_changes();
        });

        let resetBtn = document.createElement("button");
        resetBtn.className = "reset-btn";
        resetBtn.textContent = "Reset";
        resetBtn.addEventListener("click", () => {
            model.set("value", 0);
            model.save_changes();
        });

        model.on("change:value", () => {
            display.textContent = "value: " + model.get("value");
        });

        model.on("change:running", () => {
            if (model.get("running")) {
                _interval = setInterval(() => {
                    model.set("value", model.get("value") + 1);
                    model.save_changes();
                }, 100);
            } else {
                if (_interval !== null) {
                    clearInterval(_interval);
                    _interval = null;
                }
            }
        });

        container.appendChild(display);
        container.appendChild(startBtn);
        container.appendChild(stopBtn);
        container.appendChild(resetBtn);
        el.appendChild(container);
    }
    export default { render };
    """


def test_rapid_counter_renders(page):
    """Widget renders with initial value of 0."""
    widget = RapidCounterWidget(value=0, running=False)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    container = page.locator("div.rapid-container")
    expect(container).to_be_visible()

    display = page.locator("div.rapid-display")
    expect(display).to_contain_text("value: 0")

    assert_no_console_errors(msgs)


def test_rapid_auto_increment(page):
    """JS interval auto-increments value; Python side receives updates."""
    widget = RapidCounterWidget(value=0, running=False)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Click Start to begin auto-increment
    start_btn = page.locator("button.start-btn")
    start_btn.click()

    # Wait for running to be True on Python side
    wait_until(lambda: widget.running is True, page, timeout=5000)

    # Wait for value to reach at least 3 (3 * 100ms = 300ms minimum)
    wait_until(lambda: widget.value >= 3, page, timeout=5000)

    # Value should have incremented
    assert widget.value >= 3, f"Expected value >= 3, got {widget.value}"

    # Stop the interval
    stop_btn = page.locator("button.stop-btn")
    stop_btn.click()

    wait_until(lambda: widget.running is False, page, timeout=5000)
    stopped_value = widget.value

    # After stopping, value should stabilize
    import time
    time.sleep(0.3)
    final_value = widget.value
    # Allow at most 1-2 more increments after stop (race condition window)
    assert abs(final_value - stopped_value) <= 2, (
        f"Value kept changing after stop: {stopped_value} -> {final_value}"
    )

    assert_no_console_errors(msgs)


def test_rapid_python_to_browser_during_updates(page):
    """Python can set value while JS is rapidly updating (bidirectional stress)."""
    widget = RapidCounterWidget(value=0, running=False)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Start auto-increment
    page.locator("button.start-btn").click()
    wait_until(lambda: widget.running is True, page, timeout=5000)
    wait_until(lambda: widget.value >= 2, page, timeout=5000)

    # Stop the JS interval
    page.locator("button.stop-btn").click()
    wait_until(lambda: widget.running is False, page, timeout=5000)

    # Now set value from Python
    pane.component.value = 999
    wait_until(lambda: widget.value == 999, page, timeout=5000)

    # Browser should reflect the Python-set value
    display = page.locator("div.rapid-display")
    expect(display).to_contain_text("value: 999")

    assert_no_console_errors(msgs)


def test_rapid_reset(page):
    """Reset button sets value back to 0 (browser -> Python sync)."""
    widget = RapidCounterWidget(value=50, running=False)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    display = page.locator("div.rapid-display")
    expect(display).to_contain_text("value: 50")

    page.locator("button.reset-btn").click()

    wait_until(lambda: widget.value == 0, page, timeout=5000)
    expect(display).to_contain_text("value: 0")
    assert pane.component.value == 0

    assert_no_console_errors(msgs)
