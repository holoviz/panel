"""
Test 4: Multiple Widgets on Same Page

Creates a page with 3+ different AnyWidget panes.
Verifies they don't interfere with each other.

FINDING: When two same-class AnyWidget instances are placed in a Column, each gets
its own Bokeh model with correct values. The component's param values are independent.
Playwright can see elements in shadow DOMs, but when multiple shadow roots exist
for the same widget class, we need nth() selectors or use the Python-side state.

Tests:
    1. All widgets render independently
    2. No console errors
    3. Clicking one widget doesn't affect others (Python-side verification)
    4. Python updates target the correct widget
    5. Different widget types coexist cleanly
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


class CounterWidgetA(anywidget.AnyWidget):
    """Counter widget type A (distinct class for isolation)."""

    value = traitlets.Int(0).tag(sync=True)

    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "widget-a-container";

        let display = document.createElement("div");
        display.className = "widget-a-display";
        display.textContent = "A: " + model.get("value");

        let btn = document.createElement("button");
        btn.className = "widget-a-btn";
        btn.textContent = "Inc A";
        btn.addEventListener("click", () => {
            model.set("value", model.get("value") + 1);
            model.save_changes();
        });

        model.on("change:value", () => {
            display.textContent = "A: " + model.get("value");
        });

        container.appendChild(display);
        container.appendChild(btn);
        el.appendChild(container);
    }
    export default { render };
    """


class CounterWidgetB(anywidget.AnyWidget):
    """Counter widget type B (distinct class for isolation)."""

    value = traitlets.Int(0).tag(sync=True)

    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "widget-b-container";

        let display = document.createElement("div");
        display.className = "widget-b-display";
        display.textContent = "B: " + model.get("value");

        let btn = document.createElement("button");
        btn.className = "widget-b-btn";
        btn.textContent = "Inc B";
        btn.addEventListener("click", () => {
            model.set("value", model.get("value") + 1);
            model.save_changes();
        });

        model.on("change:value", () => {
            display.textContent = "B: " + model.get("value");
        });

        container.appendChild(display);
        container.appendChild(btn);
        el.appendChild(container);
    }
    export default { render };
    """


class CounterWidgetC(anywidget.AnyWidget):
    """Counter widget type C (distinct class for isolation)."""

    value = traitlets.Int(0).tag(sync=True)
    label = traitlets.Unicode("C").tag(sync=True)

    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "widget-c-container";

        let display = document.createElement("div");
        display.className = "widget-c-display";
        display.textContent = model.get("label") + ": " + model.get("value");

        let btn = document.createElement("button");
        btn.className = "widget-c-btn";
        btn.textContent = "Inc C";
        btn.addEventListener("click", () => {
            model.set("value", model.get("value") + 1);
            model.save_changes();
        });

        model.on("change:value", () => {
            display.textContent = model.get("label") + ": " + model.get("value");
        });
        model.on("change:label", () => {
            display.textContent = model.get("label") + ": " + model.get("value");
        });

        container.appendChild(display);
        container.appendChild(btn);
        el.appendChild(container);
    }
    export default { render };
    """


def test_multi_widget_all_render(page):
    """Three widgets of different classes all render on the same page."""
    widget_a = CounterWidgetA(value=10)
    widget_b = CounterWidgetB(value=20)
    widget_c = CounterWidgetC(value=30, label="C")

    pane_a = pn.pane.AnyWidget(widget_a)
    pane_b = pn.pane.AnyWidget(widget_b)
    pane_c = pn.pane.AnyWidget(widget_c)

    layout = pn.Column(pane_a, pane_b, pane_c)

    msgs, _ = serve_component(page, layout)
    wait_for_anywidget(page)

    # All three should be visible (each has a unique class per widget type)
    expect(page.locator("div.widget-a-container")).to_be_visible()
    expect(page.locator("div.widget-b-container")).to_be_visible()
    expect(page.locator("div.widget-c-container")).to_be_visible()

    # Initial values
    expect(page.locator("div.widget-a-display")).to_contain_text("A: 10")
    expect(page.locator("div.widget-b-display")).to_contain_text("B: 20")
    expect(page.locator("div.widget-c-display")).to_contain_text("C: 30")

    assert_no_console_errors(msgs)


def test_multi_widget_isolation_click(page):
    """Clicking widget A increments only A, not B or C."""
    widget_a = CounterWidgetA(value=0)
    widget_b = CounterWidgetB(value=0)
    widget_c = CounterWidgetC(value=0, label="C")

    pane_a = pn.pane.AnyWidget(widget_a)
    pane_b = pn.pane.AnyWidget(widget_b)
    pane_c = pn.pane.AnyWidget(widget_c)

    layout = pn.Column(pane_a, pane_b, pane_c)

    msgs, _ = serve_component(page, layout)
    wait_for_anywidget(page)

    # Click widget A's button 3 times
    btn_a = page.locator("button.widget-a-btn")
    btn_a.click()
    btn_a.click()
    btn_a.click()

    wait_until(lambda: widget_a.value == 3, page, timeout=5000)

    # Only A should have changed
    assert widget_a.value == 3
    assert widget_b.value == 0  # B unchanged
    assert widget_c.value == 0  # C unchanged

    # Click widget B's button twice
    btn_b = page.locator("button.widget-b-btn")
    btn_b.click()
    btn_b.click()

    wait_until(lambda: widget_b.value == 2, page, timeout=5000)

    # A still at 3, C still at 0
    assert widget_a.value == 3
    assert widget_b.value == 2
    assert widget_c.value == 0

    # Verify browser displays
    expect(page.locator("div.widget-a-display")).to_contain_text("A: 3")
    expect(page.locator("div.widget-b-display")).to_contain_text("B: 2")
    expect(page.locator("div.widget-c-display")).to_contain_text("C: 0")

    assert_no_console_errors(msgs)


def test_multi_widget_python_targets_correct(page):
    """Python updates target specific widgets without cross-contamination."""
    widget_a = CounterWidgetA(value=0)
    widget_b = CounterWidgetB(value=0)
    widget_c = CounterWidgetC(value=0, label="C")

    pane_a = pn.pane.AnyWidget(widget_a)
    pane_b = pn.pane.AnyWidget(widget_b)
    pane_c = pn.pane.AnyWidget(widget_c)

    layout = pn.Column(pane_a, pane_b, pane_c)

    msgs, _ = serve_component(page, layout)
    wait_for_anywidget(page)

    # Update only B from Python
    pane_b.component.value = 100

    wait_until(lambda: widget_b.value == 100, page, timeout=5000)

    # A and C should stay at 0
    assert widget_a.value == 0
    assert widget_b.value == 100
    assert widget_c.value == 0

    # Verify browser
    expect(page.locator("div.widget-b-display")).to_contain_text("B: 100")
    expect(page.locator("div.widget-a-display")).to_contain_text("A: 0")
    expect(page.locator("div.widget-c-display")).to_contain_text("C: 0")

    assert_no_console_errors(msgs)


def test_multi_widget_four_widgets_no_interference(page):
    """Four widgets of mixed types coexist without interference."""
    widget_a = CounterWidgetA(value=1)
    widget_b = CounterWidgetB(value=2)
    widget_c = CounterWidgetC(value=3, label="C")
    # Use CounterWidgetA again to test same-class-different-instance behavior
    widget_a2 = CounterWidgetA(value=4)

    pane_a = pn.pane.AnyWidget(widget_a)
    pane_b = pn.pane.AnyWidget(widget_b)
    pane_c = pn.pane.AnyWidget(widget_c)
    pane_a2 = pn.pane.AnyWidget(widget_a2)

    layout = pn.Column(pane_a, pane_b, pane_c, pane_a2)

    msgs, _ = serve_component(page, layout)
    wait_for_anywidget(page)

    # At least three distinct widget types are visible
    expect(page.locator("div.widget-a-container").first).to_be_visible()
    expect(page.locator("div.widget-b-container")).to_be_visible()
    expect(page.locator("div.widget-c-container")).to_be_visible()

    # Update all from Python - each should only affect its own widget
    pane_a.component.value = 10
    pane_b.component.value = 20
    pane_c.component.value = 30

    wait_until(lambda: widget_a.value == 10 and widget_b.value == 20 and widget_c.value == 30, page, timeout=8000)

    # widget_a2 should be unaffected
    assert widget_a2.value == 4

    assert_no_console_errors(msgs)


def test_multi_widget_same_class_independence(page):
    """Two instances of the SAME AnyWidget class have independent state."""
    # Both use CounterWidgetA - important test for cache behavior
    widget1 = CounterWidgetA(value=100)
    widget2 = CounterWidgetA(value=200)

    pane1 = pn.pane.AnyWidget(widget1)
    pane2 = pn.pane.AnyWidget(widget2)

    # Verify components are distinct objects
    assert pane1.component is not pane2.component
    assert pane1.component.value == 100
    assert pane2.component.value == 200

    # Update one, verify the other is untouched
    pane1.component.value = 999
    assert widget1.value == 999
    assert widget2.value == 200  # unchanged

    pane2.component.value = 888
    assert widget1.value == 999  # unchanged
    assert widget2.value == 888
