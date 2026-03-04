"""
Test binary data round-trip (bytes trait).

Covers Gap 8 from task-test.md:
End-to-end binary data transfer between Python and JS via base64 encoding.

Tests:
    1. Python sets bytes → JS receives DataView and displays byte values
    2. JS creates DataView → Python receives bytes
    3. Full round-trip: Python → JS → Python
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


class BinaryWidget(anywidget.AnyWidget):
    """Widget for testing binary data (bytes) round-trip."""

    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "binary-widget";

        let displayEl = document.createElement("div");
        displayEl.className = "byte-display";
        displayEl.textContent = "bytes: (none)";

        let statusEl = document.createElement("div");
        statusEl.className = "status";
        statusEl.textContent = "ready";

        // Button to read current binary data from Python and display byte values
        let readBtn = document.createElement("button");
        readBtn.className = "read-btn";
        readBtn.textContent = "Read Bytes";
        readBtn.addEventListener("click", () => {
            let data = model.get("data");
            if (data instanceof DataView) {
                let bytes = [];
                for (let i = 0; i < data.byteLength; i++) {
                    bytes.push(data.getUint8(i));
                }
                displayEl.textContent = "bytes: " + bytes.join(",");
                statusEl.textContent = "type: DataView";
            } else if (data instanceof ArrayBuffer) {
                let view = new DataView(data);
                let bytes = [];
                for (let i = 0; i < view.byteLength; i++) {
                    bytes.push(view.getUint8(i));
                }
                displayEl.textContent = "bytes: " + bytes.join(",");
                statusEl.textContent = "type: ArrayBuffer";
            } else {
                displayEl.textContent = "bytes: unexpected type";
                statusEl.textContent = "type: " + typeof data;
            }
        });

        // Button to send bytes from JS to Python
        let sendBtn = document.createElement("button");
        sendBtn.className = "send-btn";
        sendBtn.textContent = "Send Bytes";
        sendBtn.addEventListener("click", () => {
            let buf = new ArrayBuffer(3);
            let view = new DataView(buf);
            view.setUint8(0, 10);
            view.setUint8(1, 20);
            view.setUint8(2, 30);
            model.set("data", view);
            model.save_changes();
            statusEl.textContent = "sent: 10,20,30";
        });

        // Listen for changes from Python
        model.on("change:data", () => {
            let data = model.get("data");
            if (data instanceof DataView) {
                let bytes = [];
                for (let i = 0; i < data.byteLength; i++) {
                    bytes.push(data.getUint8(i));
                }
                displayEl.textContent = "bytes: " + bytes.join(",");
            }
        });

        container.appendChild(displayEl);
        container.appendChild(statusEl);
        container.appendChild(readBtn);
        container.appendChild(sendBtn);
        el.appendChild(container);
    }
    export default { render };
    """

    data = traitlets.Bytes(b'').tag(sync=True)


def test_bytes_python_to_js(page):
    """Python sets bytes → JS displays byte values via DataView."""
    widget = BinaryWidget(data=b'\x01\x02\x03')
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Click read button to display current bytes
    page.locator("button.read-btn").click()

    display = page.locator("div.byte-display")
    expect(display).to_contain_text("bytes: 1,2,3", timeout=5000)

    assert_no_console_errors(msgs)


def test_bytes_js_to_python(page):
    """JS creates DataView → Python receives bytes."""
    widget = BinaryWidget(data=b'')
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Click send button to send bytes from JS
    page.locator("button.send-btn").click()

    # Wait for Python to receive the bytes
    wait_until(lambda: widget.data == b'\x0a\x14\x1e', page, timeout=8000)

    assert_no_console_errors(msgs)


def test_binary_roundtrip(page):
    """Full round-trip: Python → JS → Python."""
    widget = BinaryWidget(data=b'\x41\x42\x43')
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Verify initial Python → JS
    page.locator("button.read-btn").click()
    display = page.locator("div.byte-display")
    expect(display).to_contain_text("bytes: 65,66,67", timeout=5000)

    # JS → Python
    page.locator("button.send-btn").click()
    wait_until(lambda: widget.data == b'\x0a\x14\x1e', page, timeout=8000)

    # Verify new value in JS
    page.locator("button.read-btn").click()
    expect(display).to_contain_text("bytes: 10,20,30", timeout=5000)

    assert_no_console_errors(msgs)
