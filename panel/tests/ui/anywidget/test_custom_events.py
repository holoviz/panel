"""
Test 6: Custom Events (model.send / msg:custom)

A widget that uses model.send() to send custom messages from JS to Python.
Verifies the messages arrive and Python can respond.

Tests:
    1. JS sends a simple custom message, Python receives it
    2. JS sends a message with payload data
    3. Python sends a response back to JS
    4. Multiple rapid messages are all received
    5. No console errors during messaging
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


class CustomEventWidget(anywidget.AnyWidget):
    """Widget using custom message passing via model.send()."""

    # Track messages received from JS on the Python side
    received_messages = traitlets.List(default_value=[]).tag(sync=True)
    # Python -> JS response channel
    response = traitlets.Unicode("").tag(sync=True)
    # Count of messages sent by JS
    send_count = traitlets.Int(0).tag(sync=True)

    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "custom-event-container";

        let responseDisplay = document.createElement("div");
        responseDisplay.className = "response-display";
        responseDisplay.textContent = "response: (none)";

        let msgLog = document.createElement("div");
        msgLog.className = "msg-log";
        msgLog.textContent = "messages sent: 0";

        // Button: send a simple ping message
        let pingBtn = document.createElement("button");
        pingBtn.className = "ping-btn";
        pingBtn.textContent = "Send Ping";
        pingBtn.addEventListener("click", () => {
            let count = model.get("send_count") + 1;
            model.set("send_count", count);
            model.save_changes();
            model.send({ type: "ping", count: count });
            msgLog.textContent = "messages sent: " + count;
        });

        // Button: send a message with payload
        let payloadBtn = document.createElement("button");
        payloadBtn.className = "payload-btn";
        payloadBtn.textContent = "Send Payload";
        payloadBtn.addEventListener("click", () => {
            let count = model.get("send_count") + 1;
            model.set("send_count", count);
            model.save_changes();
            model.send({
                type: "data",
                count: count,
                payload: { value: 42, name: "test", items: [1, 2, 3] }
            });
            msgLog.textContent = "messages sent: " + count;
        });

        // Button: send multiple messages rapidly
        let rapidBtn = document.createElement("button");
        rapidBtn.className = "rapid-msg-btn";
        rapidBtn.textContent = "Send 5 Messages";
        rapidBtn.addEventListener("click", () => {
            for (let i = 0; i < 5; i++) {
                model.send({ type: "batch", index: i });
            }
        });

        // Listen for responses from Python
        model.on("msg:custom", (msg) => {
            if (msg && msg.type === "pong") {
                responseDisplay.textContent = "response: pong-" + msg.echo;
            } else if (msg && msg.type === "echo") {
                responseDisplay.textContent = "response: echo-" + JSON.stringify(msg.data);
            }
        });

        model.on("change:response", () => {
            // Alternative: response via traitlet
            let r = model.get("response");
            if (r) {
                responseDisplay.textContent = "response: " + r;
            }
        });

        model.on("change:received_messages", () => {
            let msgs = model.get("received_messages") || [];
            msgLog.textContent = "messages received: " + msgs.length;
        });

        container.appendChild(responseDisplay);
        container.appendChild(msgLog);
        container.appendChild(pingBtn);
        container.appendChild(payloadBtn);
        container.appendChild(rapidBtn);
        el.appendChild(container);
    }
    export default { render };
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._custom_messages = []

    def _handle_custom_msg(self, content, buffers):
        """Handle custom messages sent from JS via model.send()."""
        if isinstance(content, dict):
            self._custom_messages.append(content)
            # Update received_messages traitlet so JS can see count
            self.received_messages = list(self._custom_messages)
            # Send a response back
            msg_type = content.get("type")
            if msg_type == "ping":
                self.send({"type": "pong", "echo": content.get("count", 0)})
            elif msg_type == "data":
                self.send({"type": "echo", "data": content.get("payload", {})})


def test_custom_event_ping(page):
    """JS sends a ping message, Python receives it and responds."""
    widget = CustomEventWidget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    container = page.locator("div.custom-event-container")
    expect(container).to_be_visible()

    # Click ping button
    page.locator("button.ping-btn").click()

    # Python should receive the message
    wait_until(lambda: len(widget._custom_messages) >= 1, page, timeout=8000)

    assert len(widget._custom_messages) >= 1
    first_msg = widget._custom_messages[0]
    assert first_msg.get("type") == "ping"
    assert first_msg.get("count") == 1

    assert_no_console_errors(msgs)


def test_custom_event_payload(page):
    """JS sends a message with nested payload, Python receives full payload."""
    widget = CustomEventWidget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Click payload button
    page.locator("button.payload-btn").click()

    wait_until(lambda: len(widget._custom_messages) >= 1, page, timeout=8000)

    msg = widget._custom_messages[0]
    assert msg.get("type") == "data"
    assert msg.get("payload") is not None
    payload = msg["payload"]
    assert payload.get("value") == 42
    assert payload.get("name") == "test"
    assert payload.get("items") == [1, 2, 3]

    assert_no_console_errors(msgs)


def test_custom_event_python_response_to_js(page):
    """Python responds to JS ping via widget.send(), JS receives the response."""
    widget = CustomEventWidget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Click ping - which triggers a Python pong response
    page.locator("button.ping-btn").click()

    # Wait for Python to receive and respond
    wait_until(lambda: len(widget._custom_messages) >= 1, page, timeout=8000)

    # The response display should update with the pong
    response_display = page.locator("div.response-display")
    expect(response_display).to_contain_text("response: pong-1", timeout=8000)

    assert_no_console_errors(msgs)


def test_custom_event_multiple_messages(page):
    """Multiple pings all arrive correctly."""
    widget = CustomEventWidget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    ping_btn = page.locator("button.ping-btn")
    ping_btn.click()
    ping_btn.click()
    ping_btn.click()

    wait_until(lambda: len(widget._custom_messages) >= 3, page, timeout=10000)
    assert len(widget._custom_messages) >= 3

    # Each message should have the correct type
    for msg in widget._custom_messages[:3]:
        assert msg.get("type") == "ping"

    assert_no_console_errors(msgs)


def test_custom_event_traitlet_update_syncs(page):
    """received_messages traitlet syncs back to JS after Python updates."""
    widget = CustomEventWidget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Send a ping (which updates received_messages traitlet in Python)
    page.locator("button.ping-btn").click()

    wait_until(lambda: len(widget.received_messages) >= 1, page, timeout=8000)

    # The msg_log in the browser should update because received_messages traitlet changed
    msg_log = page.locator("div.msg-log")
    expect(msg_log).to_contain_text("messages received: 1", timeout=8000)

    assert_no_console_errors(msgs)
