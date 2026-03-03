"""
Test 2: Complex Nested Data

A widget with a Dict traitlet containing nested dicts and lists.
Verifies deep changes sync both ways.

Tests:
    1. Widget renders with nested initial data
    2. No console errors
    3. Python -> Browser sync for nested dict updates
    4. Browser -> Python sync for nested dict updates
    5. Deep nesting (3 levels) syncs correctly
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


class NestedDataWidget(anywidget.AnyWidget):
    """Widget with nested dict/list traitlets."""

    data = traitlets.Dict(default_value={}).tag(sync=True)
    path_result = traitlets.Unicode("").tag(sync=True)

    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "nested-container";

        let display = document.createElement("pre");
        display.className = "nested-display";
        display.style.whiteSpace = "pre-wrap";
        display.style.fontFamily = "monospace";
        display.style.fontSize = "12px";
        display.style.maxHeight = "200px";
        display.style.overflow = "auto";

        function updateDisplay() {
            let data = model.get("data");
            display.textContent = JSON.stringify(data, null, 2);
        }
        updateDisplay();

        // Button: set a nested value and send back to Python
        let setBtn = document.createElement("button");
        setBtn.className = "set-nested-btn";
        setBtn.textContent = "Set Nested";
        setBtn.addEventListener("click", () => {
            // Set data.level1.level2.level3 = "deep_value"
            let data = model.get("data");
            let updated = JSON.parse(JSON.stringify(data));  // deep clone
            if (!updated.level1) updated.level1 = {};
            if (!updated.level1.level2) updated.level1.level2 = {};
            updated.level1.level2.level3 = "deep_value";
            model.set("data", updated);
            model.save_changes();
        });

        // Button: navigate a path and store result
        let pathBtn = document.createElement("button");
        pathBtn.className = "path-result-btn";
        pathBtn.textContent = "Read Path";
        pathBtn.addEventListener("click", () => {
            let data = model.get("data");
            let result = "";
            try {
                result = String(data.level1.level2.level3);
            } catch (e) {
                result = "NOT_FOUND";
            }
            model.set("path_result", result);
            model.save_changes();
        });

        model.on("change:data", updateDisplay);

        container.appendChild(display);
        container.appendChild(setBtn);
        container.appendChild(pathBtn);
        el.appendChild(container);
    }
    export default { render };
    """


def test_nested_renders_with_initial_data(page):
    """Widget renders and displays nested initial data."""
    initial_data = {
        "users": [
            {"name": "Alice", "age": 30, "tags": ["admin", "user"]},
            {"name": "Bob", "age": 25, "tags": ["user"]},
        ],
        "config": {
            "max_items": 100,
            "features": {"dark_mode": True, "notifications": False},
        },
    }
    widget = NestedDataWidget(data=initial_data)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    container = page.locator("div.nested-container")
    expect(container).to_be_visible()

    # Verify nested data appears in the display
    display = page.locator("pre.nested-display")
    expect(display).to_contain_text("Alice")
    expect(display).to_contain_text("admin")
    expect(display).to_contain_text("dark_mode")

    assert_no_console_errors(msgs)


def test_nested_python_to_browser(page):
    """Updating nested dict from Python updates the browser display."""
    widget = NestedDataWidget(data={"key": "initial"})
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    display = page.locator("pre.nested-display")
    expect(display).to_contain_text("initial")

    # Update with deeply nested data from Python
    new_data = {
        "level1": {
            "level2": {
                "level3": "deep_value",
                "items": [1, 2, 3],
            },
            "sibling": "data",
        },
        "root_key": 42,
    }
    pane.component.data = new_data

    # Browser should show updated nested structure
    expect(display).to_contain_text("deep_value")
    expect(display).to_contain_text("sibling")
    expect(display).to_contain_text("root_key")

    # Python widget should also reflect the change
    assert widget.data["level1"]["level2"]["level3"] == "deep_value"
    assert widget.data["root_key"] == 42

    assert_no_console_errors(msgs)


def test_nested_browser_to_python(page):
    """Setting nested value in browser syncs back to Python."""
    widget = NestedDataWidget(data={})
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Click the "Set Nested" button which sets data.level1.level2.level3
    page.locator("button.set-nested-btn").click()

    # Wait for Python-side update
    wait_until(
        lambda: widget.data.get("level1", {}).get("level2", {}).get("level3") == "deep_value",
        page,
        timeout=8000,
    )

    assert widget.data["level1"]["level2"]["level3"] == "deep_value"
    assert pane.component.data["level1"]["level2"]["level3"] == "deep_value"

    assert_no_console_errors(msgs)


def test_nested_path_read_browser_to_python(page):
    """JS reads a nested path and stores result as a string trait (bidirectional)."""
    initial_data = {
        "level1": {
            "level2": {
                "level3": "expected_result",
            }
        }
    }
    widget = NestedDataWidget(data=initial_data, path_result="")
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Click path read button
    page.locator("button.path-result-btn").click()

    # Wait for path_result to update
    wait_until(lambda: widget.path_result == "expected_result", page, timeout=8000)
    assert pane.component.path_result == "expected_result"

    assert_no_console_errors(msgs)


def test_nested_list_within_dict(page):
    """Lists nested inside dicts sync correctly in both directions."""
    widget = NestedDataWidget(data={"items": []})
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Update from Python: add list items inside dict
    pane.component.data = {
        "items": [
            {"id": 1, "name": "first", "scores": [10, 20, 30]},
            {"id": 2, "name": "second", "scores": [40, 50]},
        ],
        "metadata": {"count": 2, "tags": ["a", "b", "c"]},
    }

    display = page.locator("pre.nested-display")
    expect(display).to_contain_text("first")
    expect(display).to_contain_text("scores")

    # Verify Python widget got updated
    assert widget.data["items"][0]["name"] == "first"
    assert widget.data["items"][1]["scores"] == [40, 50]
    assert widget.data["metadata"]["tags"] == ["a", "b", "c"]

    assert_no_console_errors(msgs)
