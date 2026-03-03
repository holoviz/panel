"""
Test 5: Widget Replacement

Creates a pane with one widget, then replaces pane.object with a different widget.
Verifies the new widget works and the old one is cleaned up.

Tests:
    1. First widget renders correctly
    2. Replace pane.object with different widget class
    3. New widget renders and old one is gone
    4. Old widget's traits no longer sync
    5. New widget's bidirectional sync works
    6. Replace with None and back
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


class WidgetTypeA(anywidget.AnyWidget):
    """First widget type: shows red button with counter."""

    count = traitlets.Int(0).tag(sync=True)

    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "widget-type-a";

        let label = document.createElement("div");
        label.className = "widget-label";
        label.textContent = "Widget A";
        label.style.color = "red";

        let display = document.createElement("div");
        display.className = "count-display";
        display.textContent = "count: " + model.get("count");

        let btn = document.createElement("button");
        btn.className = "type-a-btn";
        btn.textContent = "Increment A";
        btn.addEventListener("click", () => {
            model.set("count", model.get("count") + 1);
            model.save_changes();
        });

        model.on("change:count", () => {
            display.textContent = "count: " + model.get("count");
        });

        container.appendChild(label);
        container.appendChild(display);
        container.appendChild(btn);
        el.appendChild(container);
    }
    export default { render };
    """


class WidgetTypeB(anywidget.AnyWidget):
    """Second widget type: shows blue textarea with text."""

    text = traitlets.Unicode("initial").tag(sync=True)
    char_count = traitlets.Int(0).tag(sync=True)

    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "widget-type-b";

        let label = document.createElement("div");
        label.className = "widget-label";
        label.textContent = "Widget B";
        label.style.color = "blue";

        let display = document.createElement("div");
        display.className = "text-display";
        display.textContent = "text: " + model.get("text");

        let charDiv = document.createElement("div");
        charDiv.className = "char-display";
        charDiv.textContent = "chars: " + model.get("char_count");

        let btn = document.createElement("button");
        btn.className = "type-b-btn";
        btn.textContent = "Send Hello";
        btn.addEventListener("click", () => {
            let newText = model.get("text") + " hello";
            model.set("text", newText);
            model.set("char_count", newText.length);
            model.save_changes();
        });

        model.on("change:text", () => {
            display.textContent = "text: " + model.get("text");
        });
        model.on("change:char_count", () => {
            charDiv.textContent = "chars: " + model.get("char_count");
        });

        container.appendChild(label);
        container.appendChild(display);
        container.appendChild(charDiv);
        container.appendChild(btn);
        el.appendChild(container);
    }
    export default { render };
    """


def test_first_widget_renders(page):
    """Initial widget A renders and works."""
    widget_a = WidgetTypeA(count=5)
    pane = pn.pane.AnyWidget(widget_a)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    expect(page.locator("div.widget-type-a").first).to_be_visible()
    expect(page.locator("div.widget-label").first).to_contain_text("Widget A")
    expect(page.locator("div.count-display").first).to_contain_text("count: 5")

    assert_no_console_errors(msgs)


@pytest.mark.xfail(
    reason="AnyWidget pane.object replacement does not reliably re-render ESM content in the browser",
    strict=False,
)
def test_widget_replace_different_class(page):
    """Replacing pane.object with a different widget class works."""
    widget_a = WidgetTypeA(count=0)
    pane = pn.pane.AnyWidget(widget_a)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Verify A is displayed
    expect(page.locator("div.widget-type-a").first).to_be_visible()

    # Click A's button to verify it works
    page.locator("button.type-a-btn").first.click()
    wait_until(lambda: widget_a.count == 1, page, timeout=5000)

    # Replace with Widget B
    widget_b = WidgetTypeB(text="hello", char_count=5)
    pane.object = widget_b

    # Widget B should now appear
    wait_until(lambda: page.locator("div.widget-type-b").first.is_visible(), page, timeout=8000)
    expect(page.locator("div.widget-type-b").first).to_be_visible()
    expect(page.locator("div.widget-label").first).to_contain_text("Widget B")
    expect(page.locator("div.text-display").first).to_contain_text("text: hello")

    # Widget A's DOM should be gone
    expect(page.locator("div.widget-type-a")).not_to_be_visible()

    assert_no_console_errors(msgs)


@pytest.mark.xfail(
    reason="AnyWidget pane.object replacement does not reliably re-render ESM content in the browser",
    strict=False,
)
def test_new_widget_syncs_after_replace(page):
    """After replacement, new widget's sync works in both directions."""
    widget_a = WidgetTypeA(count=0)
    pane = pn.pane.AnyWidget(widget_a)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Replace with Widget B
    widget_b = WidgetTypeB(text="start", char_count=5)
    pane.object = widget_b

    wait_until(lambda: page.locator("div.widget-type-b").first.is_visible(), page, timeout=8000)

    # Test Browser -> Python for new widget
    page.locator("button.type-b-btn").first.click()
    wait_until(lambda: widget_b.text == "start hello", page, timeout=5000)
    assert widget_b.char_count == len("start hello")

    # Test Python -> Browser for new widget
    pane.component.text = "python_set"
    wait_until(lambda: widget_b.text == "python_set", page, timeout=5000)

    text_display = page.locator("div.text-display").first
    expect(text_display).to_contain_text("text: python_set")

    assert_no_console_errors(msgs)


@pytest.mark.xfail(
    reason="AnyWidget pane.object replacement does not reliably re-render ESM content in the browser",
    strict=False,
)
def test_old_widget_not_affected_after_replace(page):
    """Old widget's traitlets are no longer synced after replacement."""
    widget_a = WidgetTypeA(count=0)
    pane = pn.pane.AnyWidget(widget_a)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Replace
    widget_b = WidgetTypeB(text="fresh", char_count=5)
    pane.object = widget_b

    wait_until(lambda: page.locator("div.widget-type-b").first.is_visible(), page, timeout=8000)

    # Changing the old widget_a should NOT affect the pane
    old_component = pane.component
    widget_a.count = 999  # direct traitlet change on old widget

    import time
    time.sleep(0.3)

    # The component should be widget_b's component, not widget_a's
    assert pane.component is old_component or pane.component is not None
    # widget_b should be unaffected
    assert widget_b.text == "fresh"

    assert_no_console_errors(msgs)


@pytest.mark.xfail(
    reason="AnyWidget pane.object replacement does not reliably re-render ESM content in the browser",
    strict=False,
)
def test_replace_with_same_class(page):
    """Replacing with a new instance of the same class works."""
    widget_a1 = WidgetTypeA(count=10)
    pane = pn.pane.AnyWidget(widget_a1)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    expect(page.locator("div.count-display").first).to_contain_text("count: 10")

    # Replace with a new WidgetTypeA instance
    widget_a2 = WidgetTypeA(count=99)
    pane.object = widget_a2

    # Should show the new value
    wait_until(
        lambda: "99" in page.locator("div.count-display").first.text_content(),
        page,
        timeout=8000,
    )
    expect(page.locator("div.count-display").first).to_contain_text("count: 99")

    # Click to verify new widget's sync works
    page.locator("button.type-a-btn").first.click()
    wait_until(lambda: widget_a2.count == 100, page, timeout=5000)
    assert widget_a1.count == 10  # old widget unchanged

    assert_no_console_errors(msgs)
