"""
Test experimental.invoke() RPC mechanism.

Covers Gap 9 from task-test.md:
The anywidget protocol's experimental.invoke() allows JS to call
Python handler functions and receive responses.

Tests:
    1. Basic invoke roundtrip: JS calls → Python responds → JS displays
    2. Invoke with structured data payload
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


class InvokeWidget(anywidget.AnyWidget):
    """Widget testing experimental.invoke() RPC."""

    _esm = """
    function render({ model, el, experimental }) {
        let container = document.createElement("div");
        container.className = "invoke-widget";

        let resultEl = document.createElement("div");
        resultEl.className = "invoke-result";
        resultEl.textContent = "result: (none)";

        let statusEl = document.createElement("div");
        statusEl.className = "invoke-status";
        statusEl.textContent = "ready";

        // Button: invoke a simple command
        let invokeBtn = document.createElement("button");
        invokeBtn.className = "invoke-btn";
        invokeBtn.textContent = "Invoke Echo";
        invokeBtn.addEventListener("click", async () => {
            statusEl.textContent = "invoking...";
            try {
                let [response, buffers] = await experimental.invoke("echo", { message: "hello" });
                resultEl.textContent = "result: " + JSON.stringify(response);
                statusEl.textContent = "success";
            } catch (err) {
                resultEl.textContent = "result: error";
                statusEl.textContent = "error: " + err.message;
            }
        });

        // Button: invoke with structured data
        let structBtn = document.createElement("button");
        structBtn.className = "struct-btn";
        structBtn.textContent = "Invoke Structured";
        structBtn.addEventListener("click", async () => {
            statusEl.textContent = "invoking...";
            try {
                let [response, buffers] = await experimental.invoke("process", {
                    items: [1, 2, 3],
                    config: { scale: 2 }
                });
                resultEl.textContent = "result: " + JSON.stringify(response);
                statusEl.textContent = "success";
            } catch (err) {
                resultEl.textContent = "result: error";
                statusEl.textContent = "error: " + err.message;
            }
        });

        container.appendChild(resultEl);
        container.appendChild(statusEl);
        container.appendChild(invokeBtn);
        container.appendChild(structBtn);
        el.appendChild(container);
    }
    export default { render };
    """

    value = traitlets.Int(0).tag(sync=True)

    def _handle_custom_msg(self, content, buffers):
        """Handle anywidget-command protocol messages."""
        if isinstance(content, dict) and content.get('kind') == 'anywidget-command':
            name = content.get('name')
            msg = content.get('msg')
            msg_id = content.get('id')
            response = None

            if name == 'echo':
                response = {'echo': msg.get('message', ''), 'status': 'ok'}
            elif name == 'process':
                items = msg.get('items', [])
                scale = msg.get('config', {}).get('scale', 1)
                response = {
                    'processed': [x * scale for x in items],
                    'count': len(items),
                }

            if response is not None:
                self.send({
                    'id': msg_id,
                    'kind': 'anywidget-command-response',
                    'response': response,
                })


def test_invoke_basic_roundtrip(page):
    """experimental.invoke() sends command and receives response."""
    widget = InvokeWidget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Click invoke button
    page.locator("button.invoke-btn").click()

    result = page.locator("div.invoke-result")
    expect(result).to_contain_text('"echo":"hello"', timeout=10000)

    status = page.locator("div.invoke-status")
    expect(status).to_contain_text("success")

    assert_no_console_errors(msgs)


def test_invoke_with_structured_data(page):
    """experimental.invoke() works with nested dict/list payloads."""
    widget = InvokeWidget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Click structured invoke button
    page.locator("button.struct-btn").click()

    result = page.locator("div.invoke-result")
    expect(result).to_contain_text('"processed":[2,4,6]', timeout=10000)
    expect(result).to_contain_text('"count":3')

    status = page.locator("div.invoke-status")
    expect(status).to_contain_text("success")

    assert_no_console_errors(msgs)
