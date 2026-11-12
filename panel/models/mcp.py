"""
Defines a Bokeh MCPApp model bridging the MCP Apps (SEP-1865) postMessage
protocol into the Panel session.
"""
from bokeh.core.properties import (
    Any, Bool, Dict, List, Nullable, String,
)
from bokeh.events import ModelEvent
from bokeh.models import Model


class MCPMessageEvent(ModelEvent):
    """
    Carries an inbound JSON-RPC notification or request from the host.
    """

    event_name = 'mcp_message'

    def __init__(self, model, method=None, params=None, request_id=None):
        self.method = method
        self.params = params
        self.request_id = request_id
        super().__init__(model=model)

    def event_values(self):
        return dict(
            super().event_values(), method=self.method, params=self.params,
            request_id=self.request_id
        )


class MCPSendEvent(ModelEvent):
    """
    Carries an outbound JSON-RPC request, notification or response from Python.

    ``msg_id`` correlates the eventual result back to the awaiting coroutine;
    it is unrelated to the JSON-RPC id, which the frontend allocates.
    """

    event_name = 'mcp_send'

    def __init__(self, model, kind=None, method=None, params=None, msg_id=None):
        self.kind = kind
        self.method = method
        self.params = params
        self.msg_id = msg_id
        super().__init__(model=model)

    def event_values(self):
        return dict(
            super().event_values(), kind=self.kind, method=self.method,
            params=self.params, msg_id=self.msg_id
        )


class MCPReplyEvent(ModelEvent):
    """
    Carries the result or error of an outbound request back to Python.
    """

    event_name = 'mcp_reply'

    def __init__(self, model, msg_id=None, result=None, error=None):
        self.msg_id = msg_id
        self.result = result
        self.error = error
        super().__init__(model=model)

    def event_values(self):
        return dict(
            super().event_values(), msg_id=self.msg_id, result=self.result,
            error=self.error
        )


class MCPApp(Model):
    """
    Exposes the host side of the MCP Apps protocol to Python.
    """

    connected = Bool(False)

    # Free-form nested JSON from the host (theme, styles.variables, container
    # dimensions, locale, ...), so Any rather than a stricter mapping.
    host_context = Dict(String, Any, default={})

    host_capabilities = Dict(String, Any, default={})

    host_info = Nullable(Dict(String, Any), default=None)

    protocol_version = Nullable(String(), default=None)

    # Tool declarations served to the host via `tools/list`.
    tools = List(Dict(String, Any), default=[])
