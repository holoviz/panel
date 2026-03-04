"""
Test reference stability for model.get() return values.

Covers protocol gaps 1 and 2 from task-test.md:
- Gap 1: _decode_binary preserves reference identity for non-binary data
- Gap 2: _cached_ws_values returns same reference on repeated calls

Tests:
    1. model.get() returns stable reference for unchanged values
    2. model.get() returns new reference after Python-side change
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


class ReferenceStabilityWidget(anywidget.AnyWidget):
    """Widget that polls model.get() and detects reference instability."""

    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "ref-stability";

        let statusEl = document.createElement("div");
        statusEl.className = "stability-status";
        statusEl.textContent = "checking...";

        let countEl = document.createElement("div");
        countEl.className = "instability-count";
        countEl.textContent = "instability: 0";

        container.appendChild(statusEl);
        container.appendChild(countEl);
        el.appendChild(container);

        // Poll model.get("data") and compare references
        let lastRef = model.get("data");
        let instabilityCount = 0;
        let checkCount = 0;

        let interval = setInterval(() => {
            let currentRef = model.get("data");
            checkCount++;
            if (currentRef !== lastRef) {
                instabilityCount++;
                lastRef = currentRef;
            }
            countEl.textContent = "instability: " + instabilityCount;
            statusEl.textContent = "checks: " + checkCount;

            if (checkCount >= 20) {
                clearInterval(interval);
                // Report final result
                model.set("instability_count", instabilityCount);
                model.save_changes();
                statusEl.textContent = "done: " + checkCount + " checks";
            }
        }, 50);
    }
    export default { render };
    """

    data = traitlets.List(default_value=[1, 2, 3]).tag(sync=True)
    instability_count = traitlets.Int(0).tag(sync=True)


def test_get_returns_stable_reference(page):
    """model.get() returns the same JS reference on repeated calls
    when the underlying value hasn't changed (React #185 fix)."""
    widget = ReferenceStabilityWidget(data=[1, 2, 3])
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    status = page.locator("div.stability-status")
    expect(status).to_contain_text("done:", timeout=10000)

    count_el = page.locator("div.instability-count")
    expect(count_el).to_contain_text("instability: 0")

    wait_until(lambda: widget.instability_count == 0, page, timeout=5000)

    assert_no_console_errors(msgs)


class ReferenceChangeWidget(anywidget.AnyWidget):
    """Widget that detects when model.get() returns a new reference after change."""

    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "ref-change";

        let statusEl = document.createElement("div");
        statusEl.className = "change-status";
        statusEl.textContent = "waiting";

        let changeCountEl = document.createElement("div");
        changeCountEl.className = "change-count";
        changeCountEl.textContent = "changes: 0";

        container.appendChild(statusEl);
        container.appendChild(changeCountEl);
        el.appendChild(container);

        let lastRef = model.get("items");
        let changeCount = 0;

        model.on("change:items", () => {
            let newRef = model.get("items");
            if (newRef !== lastRef) {
                changeCount++;
                lastRef = newRef;
            }
            changeCountEl.textContent = "changes: " + changeCount;
            statusEl.textContent = "value: " + JSON.stringify(newRef);
        });
    }
    export default { render };
    """

    items = traitlets.List(default_value=[1, 2, 3]).tag(sync=True)


def test_get_returns_new_reference_after_change(page):
    """model.get() returns a new reference after Python-side value change."""
    widget = ReferenceChangeWidget(items=[1, 2, 3])
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Change from Python
    pane.component.items = [4, 5, 6]

    change_count = page.locator("div.change-count")
    expect(change_count).to_contain_text("changes: 1", timeout=8000)

    status = page.locator("div.change-status")
    expect(status).to_contain_text("[4,5,6]")

    assert_no_console_errors(msgs)
