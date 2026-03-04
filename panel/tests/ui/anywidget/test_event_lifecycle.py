"""
Test event lifecycle: on/off callbacks, generic change events.

Covers protocol gaps 4, 6, 7 from task-test.md:
- Gap 4: model.off() removes callback
- Gap 6: Generic "change" event fires on any property change
- Gap 7: model.on("change:x", cb) receives the new value as argument

Tests:
    1. model.off() removes a specific callback
    2. Generic "change" fires on any property change
    3. Change callback receives the new value as argument
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


class OffCallbackWidget(anywidget.AnyWidget):
    """Widget that tests model.off() for removing callbacks."""

    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "off-test";

        let fireCountEl = document.createElement("div");
        fireCountEl.className = "fire-count";
        fireCountEl.textContent = "fires: 0";

        let statusEl = document.createElement("div");
        statusEl.className = "status";
        statusEl.textContent = "listening";

        container.appendChild(fireCountEl);
        container.appendChild(statusEl);
        el.appendChild(container);

        let fireCount = 0;
        let cb = () => {
            fireCount++;
            fireCountEl.textContent = "fires: " + fireCount;
        };

        model.on("change:value", cb);

        // After first fire, unregister callback
        let unregBtn = document.createElement("button");
        unregBtn.className = "unreg-btn";
        unregBtn.textContent = "Unregister";
        unregBtn.addEventListener("click", () => {
            model.off("change:value", cb);
            statusEl.textContent = "unregistered";
        });
        container.appendChild(unregBtn);
    }
    export default { render };
    """

    value = traitlets.Int(0).tag(sync=True)


def test_model_off_removes_callback(page):
    """model.off("change:x", cb) removes the callback so it no longer fires."""
    widget = OffCallbackWidget(value=0)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # First change — callback should fire
    pane.component.value = 1
    fire_count = page.locator("div.fire-count")
    expect(fire_count).to_contain_text("fires: 1", timeout=5000)

    # Unregister callback
    page.locator("button.unreg-btn").click()
    status = page.locator("div.status")
    expect(status).to_contain_text("unregistered")

    # Second change — callback should NOT fire
    pane.component.value = 2

    # Give it time to potentially fire
    page.wait_for_timeout(500)
    expect(fire_count).to_contain_text("fires: 1")

    assert_no_console_errors(msgs)


class GenericChangeWidget(anywidget.AnyWidget):
    """Widget that tests generic "change" event (fires on any property)."""

    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "generic-change";

        let countEl = document.createElement("div");
        countEl.className = "change-count";
        countEl.textContent = "changes: 0";

        container.appendChild(countEl);
        el.appendChild(container);

        let changeCount = 0;
        model.on("change", () => {
            changeCount++;
            countEl.textContent = "changes: " + changeCount;
        });
    }
    export default { render };
    """

    value = traitlets.Int(0).tag(sync=True)
    label = traitlets.Unicode("").tag(sync=True)


def test_generic_change_fires_on_any_property(page):
    """model.on("change", cb) fires when any trait changes."""
    widget = GenericChangeWidget(value=0, label="")
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    count_el = page.locator("div.change-count")

    # Change first trait
    pane.component.value = 42
    expect(count_el).to_contain_text("changes: 1", timeout=5000)

    # Change second trait
    pane.component.label = "hello"
    expect(count_el).to_contain_text("changes: 2", timeout=5000)

    assert_no_console_errors(msgs)


class ChangeValueWidget(anywidget.AnyWidget):
    """Widget that tests change callback receives the new value."""

    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "change-value";

        let receivedEl = document.createElement("div");
        receivedEl.className = "received-value";
        receivedEl.textContent = "received: (none)";

        container.appendChild(receivedEl);
        el.appendChild(container);

        model.on("change:value", (newVal) => {
            receivedEl.textContent = "received: " + newVal;
        });
    }
    export default { render };
    """

    value = traitlets.Int(0).tag(sync=True)


def test_change_callback_receives_new_value(page):
    """model.on("change:x", cb) passes the new value to the callback."""
    widget = ChangeValueWidget(value=0)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    pane.component.value = 99

    received = page.locator("div.received-value")
    expect(received).to_contain_text("received: 99", timeout=5000)

    assert_no_console_errors(msgs)
