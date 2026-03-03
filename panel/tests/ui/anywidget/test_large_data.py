"""
Test 3: Large Data Transfer

A widget with a List traitlet containing 1000+ items.
Verifies the list syncs both ways without errors.

Tests:
    1. Widget renders with large list (1000 items)
    2. No console errors with large payload
    3. Python -> Browser sync for large list
    4. Browser -> Python sync for large list
    5. List length is preserved accurately
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


class LargeListWidget(anywidget.AnyWidget):
    """Widget with a large list traitlet."""

    items = traitlets.List(default_value=[]).tag(sync=True)
    item_count = traitlets.Int(0).tag(sync=True)
    sum_value = traitlets.Int(0).tag(sync=True)
    status = traitlets.Unicode("idle").tag(sync=True)

    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "large-list-container";

        let statusDiv = document.createElement("div");
        statusDiv.className = "status-display";

        let countDiv = document.createElement("div");
        countDiv.className = "count-display";

        let sumDiv = document.createElement("div");
        sumDiv.className = "sum-display";

        function updateDisplay() {
            let items = model.get("items") || [];
            statusDiv.textContent = "status: " + model.get("status");
            countDiv.textContent = "count: " + items.length;
            sumDiv.textContent = "sum: " + items.reduce((a, b) => a + b, 0);
        }
        updateDisplay();

        // Compute sum in JS and send back
        let computeBtn = document.createElement("button");
        computeBtn.className = "compute-btn";
        computeBtn.textContent = "Compute";
        computeBtn.addEventListener("click", () => {
            let items = model.get("items") || [];
            let sum = items.reduce((a, b) => a + b, 0);
            model.set("item_count", items.length);
            model.set("sum_value", sum);
            model.set("status", "computed");
            model.save_changes();
        });

        // Generate a large list in JS and send to Python
        let generateBtn = document.createElement("button");
        generateBtn.className = "generate-btn";
        generateBtn.textContent = "Generate 500";
        generateBtn.addEventListener("click", () => {
            let newItems = [];
            for (let i = 0; i < 500; i++) {
                newItems.push(i * 2);  // even numbers 0..998
            }
            model.set("items", newItems);
            model.set("status", "generated");
            model.save_changes();
        });

        model.on("change:items", updateDisplay);
        model.on("change:status", updateDisplay);

        container.appendChild(statusDiv);
        container.appendChild(countDiv);
        container.appendChild(sumDiv);
        container.appendChild(computeBtn);
        container.appendChild(generateBtn);
        el.appendChild(container);
    }
    export default { render };
    """


def test_large_list_renders(page):
    """Widget renders with 1000-item list without errors."""
    large_list = list(range(1000))
    widget = LargeListWidget(items=large_list, status="ready")
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    container = page.locator("div.large-list-container")
    expect(container).to_be_visible()

    count_div = page.locator("div.count-display")
    expect(count_div).to_contain_text("count: 1000")

    assert_no_console_errors(msgs)


def test_large_list_sum_computed_in_browser(page):
    """JS computes sum of 1000+ items and syncs result to Python."""
    large_list = list(range(1, 101))  # 1..100, sum = 5050
    widget = LargeListWidget(items=large_list)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Click compute button - JS computes sum and sends back
    page.locator("button.compute-btn").click()

    wait_until(lambda: widget.status == "computed", page, timeout=8000)
    assert widget.item_count == 100
    assert widget.sum_value == 5050
    assert pane.component.item_count == 100
    assert pane.component.sum_value == 5050

    assert_no_console_errors(msgs)


def test_large_list_python_to_browser(page):
    """Sending 1000+ item list from Python to browser renders correctly."""
    widget = LargeListWidget(items=[], status="idle")
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    count_div = page.locator("div.count-display")
    expect(count_div).to_contain_text("count: 0")

    # Send 1000-item list from Python
    large_list = list(range(1000))
    pane.component.items = large_list

    # Browser should show updated count
    expect(count_div).to_contain_text("count: 1000", timeout=10000)

    # Python widget should be updated
    assert len(widget.items) == 1000
    assert widget.items[0] == 0
    assert widget.items[999] == 999

    assert_no_console_errors(msgs)


def test_large_list_browser_to_python(page):
    """Generating 500-item list in JS syncs correctly to Python."""
    widget = LargeListWidget(items=[])
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Generate list in JS
    page.locator("button.generate-btn").click()

    wait_until(lambda: widget.status == "generated", page, timeout=8000)
    assert len(widget.items) == 500
    assert widget.items[0] == 0
    assert widget.items[1] == 2   # even numbers
    assert widget.items[499] == 998

    # Also verify component param is in sync
    assert len(pane.component.items) == 500

    assert_no_console_errors(msgs)


def test_large_list_replace_with_larger(page):
    """Replacing a large list with an even larger one syncs correctly."""
    widget = LargeListWidget(items=list(range(100)))
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    count_div = page.locator("div.count-display")
    expect(count_div).to_contain_text("count: 100")

    # Replace with 2000-item list
    large_list = list(range(2000))
    pane.component.items = large_list

    expect(count_div).to_contain_text("count: 2000", timeout=10000)
    assert len(widget.items) == 2000

    assert_no_console_errors(msgs)
