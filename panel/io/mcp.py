"""
Implements the MCP Apps (SEP-1865) View side of the protocol, allowing a Panel
app embedded in an MCP host to receive tool input and results, expose tools back
to the host, and update the model's context.
"""
from __future__ import annotations

import asyncio
import inspect
import pathlib
import typing as t
import uuid

from functools import partial
from urllib.parse import urlencode, urlsplit

import param

from bokeh.core.templates import FILE

from ..config import config
from ..models.mcp import (
    MCPApp as _BkMCPApp, MCPMessageEvent, MCPReplyEvent, MCPSendEvent,
)
from ..reactive import Syncable
from ..util import edit_readonly
from ..util.warnings import warn
from .document import create_doc_if_none_exists, with_lock
from .resources import BASE_TEMPLATE, _env
from .state import set_curdoc, state

if t.TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm

__all__ = ('MCPApp', 'MCPError')

DisplayMode = t.Literal['inline', 'fullscreen', 'pip']

_BRIDGE_PATH = pathlib.Path(__file__).parent.parent / '_templates' / 'mcp_bridge.js'

MCP_BRIDGE_JS = _BRIDGE_PATH.read_text(encoding='utf-8')

MCP_TEMPLATE = _env.get_template('mcp_app.html')

# Seconds the template waits for the app to render before showing the error
# state with an open-in-browser link.
MCP_RENDER_TIMEOUT = 15

# Timeout for host round-trips. Hosts may gate requests on user consent, so this
# is generous; without it a lost reply would leak the future forever.
DEFAULT_TIMEOUT = 60


class MCPApp(Syncable):
    """
    Exposes the MCP Apps protocol to a Panel application running as a View
    inside an MCP host.

    Available as ``pn.state.mcp`` when the session was requested as an MCP
    App View, i.e. served with ``panel serve --mcp`` or requested with the
    ``?mcp=1`` query parameter, and ``None`` otherwise. When such a View is
    opened outside an MCP host, e.g. directly in a browser tab, the app still
    renders but ``connected`` stays False and requests to the host time out.
    """

    connected = param.Boolean(default=False, readonly=True, doc="""
        Whether the MCP handshake with the host completed.""")

    tool_input = param.Dict(default=None, allow_None=True, readonly=True, doc="""
        Arguments of the tool call that instantiated this View.""")

    tool_input_partial = param.Dict(default=None, allow_None=True, readonly=True, doc="""
        Best-effort partial arguments streamed while the agent is still
        generating the tool call. Never rely on these for critical operations.""")

    tool_result = param.Dict(default=None, allow_None=True, readonly=True, doc="""
        The full CallToolResult of the tool call that instantiated this View.""")

    tool_cancelled = param.String(default=None, allow_None=True, readonly=True, doc="""
        Reason the tool call was cancelled, if it was.""")

    theme: t.Literal['light', 'dark'] | None = param.Selector(
        default=None, allow_None=True, objects=['light', 'dark'],
        readonly=True, doc="""
        The host's current color theme preference.""")  # type: ignore[assignment, ty:invalid-assignment]

    display_mode: DisplayMode | None = param.Selector(
        default=None, allow_None=True, objects=['inline', 'fullscreen', 'pip'],
        readonly=True, doc="""
        How the View is currently displayed.""")  # type: ignore[assignment, ty:invalid-assignment]

    host_context = param.Dict(default={}, readonly=True, doc="""
        The full HostContext most recently reported by the host.""")

    host_capabilities = param.Dict(default={}, readonly=True, doc="""
        Capabilities advertised by the host.""")

    host_info = param.Dict(default=None, allow_None=True, readonly=True, doc="""
        Name and version of the host application.""")

    locale = param.String(default=None, allow_None=True, readonly=True, doc="""
        The user's language/region preference as a BCP 47 tag.""")

    time_zone = param.String(default=None, allow_None=True, readonly=True, doc="""
        The user's IANA timezone.""")

    platform: t.Literal['web', 'desktop', 'mobile'] | None = param.Selector(
        default=None, allow_None=True, objects=['web', 'desktop', 'mobile'],
        readonly=True, doc="""
        The host's platform type.""")  # type: ignore[assignment, ty:invalid-assignment]

    container_dimensions = param.Dict(default=None, allow_None=True, readonly=True, doc="""
        Dimensions of the container holding this View.""")

    _rename: t.ClassVar[Mapping[str, str | None]] = {
        'name': None, 'tool_input': None, 'tool_input_partial': None,
        'tool_result': None, 'tool_cancelled': None, 'theme': None,
        'display_mode': None, 'locale': None, 'time_zone': None,
        'platform': None, 'container_dimensions': None, 'host_context': None,
        'host_capabilities': None, 'host_info': None,
    }

    def __init__(self, **params):
        super().__init__(**params)
        self._replies: dict[str, asyncio.Future] = {}
        self._tools: dict[str, dict[str, t.Any]] = {}
        self._tool_callbacks: dict[str, Callable] = {}
        self._teardown_callbacks: list[Callable] = []
        self._message_callbacks: dict[str, list[Callable]] = {}

    # ------------------------------------------------------------------
    # Model wiring
    # ------------------------------------------------------------------

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        model = _BkMCPApp()
        root = root or model
        self._models[root.ref['id']] = (model, parent)
        self._link_props(model, ['connected'], doc, root, comm)
        model.on_event(MCPMessageEvent, self._process_message)  # type: ignore[arg-type]
        model.on_event(MCPReplyEvent, self._process_reply_event)  # type: ignore[arg-type]
        return model

    def get_root(
        self, doc: Document | None = None, comm: Comm | None = None,
        preprocess: bool = True
    ) -> Model:
        doc = create_doc_if_none_exists(doc)
        root = self._get_model(doc, comm=comm)
        ref = root.ref['id']
        state._views[ref] = (self, root, doc, comm)
        self._documents[doc] = root
        return root

    def _cleanup(self, root: Model | None = None) -> None:
        super()._cleanup(root)
        if root is not None:
            state._views.pop(root.ref['id'], None)

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'connected' in msg:
            # Host context lands on the model at the same time as `connected`,
            # so read it off the model rather than waiting for a second sync.
            for model, _ in self._models.values():
                self._sync_host_context(model.host_context or {})
                with edit_readonly(self):
                    self.host_capabilities = dict(model.host_capabilities or {})
                    self.host_info = dict(model.host_info) if model.host_info else None
                break
        return msg

    def _sync_host_context(self, context: dict[str, t.Any]) -> None:
        merged = dict(self.host_context or {})
        merged.update(context)
        params: dict[str, t.Any] = {'host_context': merged}
        if 'theme' in context:
            params['theme'] = context['theme']
        if 'displayMode' in context:
            params['display_mode'] = context['displayMode']
        if 'locale' in context:
            params['locale'] = context['locale']
        if 'timeZone' in context:
            params['time_zone'] = context['timeZone']
        if 'platform' in context:
            params['platform'] = context['platform']
        if 'containerDimensions' in context:
            params['container_dimensions'] = context['containerDimensions']
        with edit_readonly(self):
            self.param.update(**params)

    def _process_message(self, event: MCPMessageEvent) -> None:
        method, params = event.method, event.params or {}

        if method == 'ui/notifications/tool-input':
            with edit_readonly(self):
                self.tool_input = params.get('arguments', {})
        elif method == 'ui/notifications/tool-input-partial':
            with edit_readonly(self):
                self.tool_input_partial = params.get('arguments', {})
        elif method == 'ui/notifications/tool-result':
            with edit_readonly(self):
                self.tool_result = dict(params)
        elif method == 'ui/notifications/tool-cancelled':
            with edit_readonly(self):
                self.tool_cancelled = params.get('reason', '')
        elif method == 'ui/notifications/host-context-changed':
            self._sync_host_context(dict(params))
        elif method == 'ui/resource-teardown':
            self._handle_teardown(params, event.request_id)
            return
        elif method == 'tools/list':
            self._respond(event.request_id, {'tools': list(self._tools.values())})
            return
        elif method == 'tools/call':
            self._handle_tool_call(params, event.request_id)
            return

        for cb in self._message_callbacks.get(method, []):
            state.execute(partial(cb, params))
        for cb in self._message_callbacks.get('*', []):
            state.execute(partial(cb, method, params))

    # ------------------------------------------------------------------
    # Outbound
    # ------------------------------------------------------------------

    def _send(self, kind, method, params=None, msg_id=None) -> None:
        self._send_event(
            MCPSendEvent, kind=kind, method=method, params=params, msg_id=msg_id
        )

    def _notify(self, method: str, params: dict[str, t.Any] | None = None) -> None:
        self._send('notify', method, params or {})

    def _respond(self, request_id, result) -> None:
        if request_id is None:
            return
        self._send('respond', '', result or {}, msg_id=request_id)

    async def _request(
        self, method: str, params: dict[str, t.Any] | None = None,
        timeout: float = DEFAULT_TIMEOUT
    ) -> t.Any:
        msg_id = uuid.uuid4().hex
        future: asyncio.Future = asyncio.get_running_loop().create_future()
        self._replies[msg_id] = future
        self._send('request', method, params or {}, msg_id=msg_id)
        try:
            return await asyncio.wait_for(future, timeout)
        finally:
            self._replies.pop(msg_id, None)

    def _process_reply_event(self, event: MCPReplyEvent) -> None:
        self._process_reply(event.msg_id, event.result, event.error)

    def _process_reply(self, msg_id, result, error) -> None:
        future = self._replies.get(msg_id)
        if future is None or future.done():
            return
        if error is not None:
            message = error.get('message', str(error)) if isinstance(error, dict) else str(error)
            future.set_exception(MCPError(message))
        else:
            future.set_result(result)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def call_tool(
        self, name: str, arguments: dict[str, t.Any] | None = None,
        timeout: float = DEFAULT_TIMEOUT
    ) -> dict[str, t.Any]:
        """
        Calls a tool on the MCP server via the host.

        Parameters
        ----------
        name: str
            Name of the tool to call.
        arguments: dict
            Arguments to invoke the tool with.
        timeout: float
            Seconds to wait for the host to reply.

        Returns
        -------
        The CallToolResult returned by the server.
        """
        return await self._request(
            'tools/call', {'name': name, 'arguments': arguments or {}}, timeout
        )

    async def read_resource(self, uri: str, timeout: float = DEFAULT_TIMEOUT) -> dict[str, t.Any]:
        """
        Reads a resource from the MCP server via the host.
        """
        return await self._request('resources/read', {'uri': uri}, timeout)

    async def request_display_mode(
        self, mode: DisplayMode, timeout: float = DEFAULT_TIMEOUT
    ) -> str:
        """
        Requests a change of display mode.

        The host may decline, so the mode it actually applied is returned.
        """
        available = (self.host_context or {}).get('availableDisplayModes')
        if available and mode not in available:
            raise ValueError(
                f'Host does not support the {mode!r} display mode, '
                f'available modes: {available}.'
            )
        result = await self._request('ui/request-display-mode', {'mode': mode}, timeout)
        return (result or {}).get('mode', mode)

    async def open_link(self, url: str, timeout: float = DEFAULT_TIMEOUT) -> bool:
        """
        Asks the host to open a URL in the user's browser.

        Hosts usually ask the user to confirm first.

        Returns
        -------
        Whether the link was opened, i.e. False if the user declined.
        """
        result = await self._request('ui/open-link', {'url': url}, timeout)
        return not (result or {}).get('isError', False)

    async def send_message(self, text: str, timeout: float = DEFAULT_TIMEOUT) -> None:
        """
        Proposes a user message to the host's chat interface.

        Hosts differ in what they do with it: some send it, others ask the
        user to confirm and only pre-fill the chat input (e.g. Claude), so
        the user always stays in control of what is sent.
        """
        await self._request(
            'ui/message',
            {'role': 'user', 'content': [{'type': 'text', 'text': text}]},
            timeout
        )

    async def update_model_context(
        self, content: list[dict[str, t.Any]] | None = None,
        structured_content: dict[str, t.Any] | None = None,
        timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        """
        Tells the model what the user is currently looking at.

        Each call overwrites the context set by the previous one. Hosts differ
        in how the model receives it: some add it to future turns, others
        (e.g. Claude) store it and let the model read it on demand, so keep it
        a compact, self-contained summary.

        Parameters
        ----------
        content: list
            ContentBlocks describing the current view.
        structured_content: dict
            Structured representation of the current view.
        """
        params: dict[str, t.Any] = {}
        if content is not None:
            params['content'] = content
        if structured_content is not None:
            supported = (self.host_capabilities or {}).get('updateModelContext')
            if supported is not None and 'structuredContent' not in supported:
                self.param.warning(
                    'The host does not advertise structured content support '
                    'for update_model_context, so it may be dropped; include '
                    'the information in the text content as well.'
                )
            params['structuredContent'] = structured_content
        await self._request('ui/update-model-context', params, timeout)

    def log(self, level: str, data: t.Any, logger: str | None = None) -> None:
        """
        Sends a log message to the host.

        Parameters
        ----------
        level: str
            One of debug, info, notice, warning, error, critical, alert or
            emergency.
        data: any
            JSON-serializable payload to log.
        logger: str
            Optional name of the logger issuing the message.
        """
        params: dict[str, t.Any] = {'level': level, 'data': data}
        if logger is not None:
            params['logger'] = logger
        self._notify('notifications/message', params)

    def tool(
        self, func: Callable | None = None, /, *,
        name: str | None = None,
        description: str | None = None,
        input_schema: dict[str, t.Any] | None = None,
    ) -> Callable:
        """
        Registers a tool the host (and therefore the agent) can call on this
        running app, letting it drive the live view.

        Parameters
        ----------
        name: str
            Tool name; defaults to the function name.
        description: str
            Tool description; defaults to the function docstring.
        input_schema: dict
            JSON Schema for the arguments. Inferred from type hints when
            omitted.

        Examples
        --------
        >>> @pn.state.mcp.tool(description="Highlight a date range")
        ... def highlight(start: str, end: str) -> str:
        ...     plot.x_range = (start, end)
        ...     return f"Highlighted {start} to {end}"
        """
        def decorator(f: Callable) -> Callable:
            tool_name = name or f.__name__
            schema = input_schema or _schema_from_signature(f)
            self._tools[tool_name] = {
                'name': tool_name,
                'description': description or (inspect.getdoc(f) or ''),
                'inputSchema': schema,
            }
            self._tool_callbacks[tool_name] = f
            self._sync_tools()
            return f

        if func is not None:
            return decorator(func)
        return decorator

    def remove_tool(self, name: str) -> None:
        """
        Unregisters a previously registered tool.
        """
        self._tools.pop(name, None)
        self._tool_callbacks.pop(name, None)
        self._sync_tools()

    def _sync_tools(self) -> None:
        tools = list(self._tools.values())
        for model, _ in self._models.values():
            model.tools = tools
        if self.connected:
            self._notify('notifications/tools/list_changed', {})

    def _handle_tool_call(self, params: dict[str, t.Any], request_id) -> None:
        name = params.get('name', '')
        arguments = params.get('arguments') or {}
        callback = self._tool_callbacks.get(name)
        if callback is None:
            self._respond(request_id, {
                'content': [{'type': 'text', 'text': f'Unknown tool: {name}'}],
                'isError': True,
            })
            return

        # Locked so that _respond may dispatch the reply event directly.
        @with_lock
        async def run():
            try:
                result = callback(**arguments)
                if inspect.isawaitable(result):
                    result = await result
            except Exception as e:
                self._respond(request_id, {
                    'content': [{'type': 'text', 'text': f'{type(e).__name__}: {e}'}],
                    'isError': True,
                })
                return
            if isinstance(result, dict) and 'content' in result:
                payload = result
            else:
                payload = {'content': [{'type': 'text', 'text': '' if result is None else str(result)}]}
            self._respond(request_id, payload)

        state.execute(run)

    def on_teardown(self, callback: Callable) -> None:
        """
        Registers a callback invoked before the host tears down this View.

        The host waits for the callbacks to complete, so this is the place to
        flush unsaved state.
        """
        self._teardown_callbacks.append(callback)

    def _handle_teardown(self, params: dict[str, t.Any], request_id) -> None:
        @with_lock
        async def run():
            for cb in self._teardown_callbacks:
                try:
                    result = cb(params.get('reason', ''))
                    if inspect.isawaitable(result):
                        await result
                except Exception:
                    pass
            self._respond(request_id, {})
        state.execute(run)

    def on_message(self, method: str, callback: Callable) -> None:
        """
        Registers a callback for a raw inbound JSON-RPC method.

        Use ``'*'`` to receive every message, in which case the callback is
        passed both the method and the params.
        """
        self._message_callbacks.setdefault(method, []).append(callback)


class MCPError(Exception):
    """
    Raised when the host returns a JSON-RPC error.
    """


_JSON_TYPES: dict[t.Any, str] = {
    str: 'string', int: 'integer', float: 'number', bool: 'boolean',
    list: 'array', dict: 'object',
}


def _schema_from_signature(func: Callable) -> dict[str, t.Any]:
    """
    Derives a JSON Schema from a callable's type hints.
    """
    try:
        hints = t.get_type_hints(func)
    except Exception:
        hints = {}
    signature = inspect.signature(func)
    properties: dict[str, t.Any] = {}
    required: list[str] = []
    for pname, parameter in signature.parameters.items():
        if parameter.kind in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD):
            continue
        annotation = hints.get(pname)
        properties[pname] = {'type': _JSON_TYPES.get(annotation, 'string')}
        if parameter.default is parameter.empty:
            required.append(pname)
    schema: dict[str, t.Any] = {'type': 'object', 'properties': properties}
    if required:
        schema['required'] = required
    return schema


def _fallback_url(request) -> str | None:
    """
    Absolute URL of the app rendered as a regular page, offered by the MCP
    template when the View cannot reach the server.
    """
    try:
        path = urlsplit(request.uri).path
        url = f'{request.protocol}://{request.host}{path}'
    except (AttributeError, TypeError):
        return None
    query = [
        (key, value.decode('utf-8') if isinstance(value, bytes) else value)
        for key, values in request.arguments.items() if key != 'mcp'
        for value in values
    ]
    if config.mcp:
        query.append(('mcp', '0'))
    return f'{url}?{urlencode(query)}' if query else url


def init_mcp_doc(doc: Document) -> MCPApp | None:
    """
    Renders a session Document as an MCP App View if one was requested,
    adding the MCPApp root and switching the page to the MCP template.
    """
    with set_curdoc(doc):
        mcp = state.mcp
        if mcp is None:
            return None
        if not any(doc.template is tmpl for tmpl in (FILE, BASE_TEMPLATE, MCP_TEMPLATE)):
            warn(
                'Rendering a custom template, e.g. one of pn.template, as an '
                'MCP App View is not supported. The app is served as a regular '
                'page and pn.state.mcp will never connect.', UserWarning
            )
            return mcp
        if doc not in mcp._documents:
            model = mcp.get_root(doc)
            model.name = 'mcp'
            doc.add_root(model)
        request = doc.session_context.request if doc.session_context else None
        doc.template = MCP_TEMPLATE
        doc.template_variables.update(
            mcp_bridge_js=MCP_BRIDGE_JS,
            mcp_app_url=None if request is None else _fallback_url(request),
            mcp_timeout=MCP_RENDER_TIMEOUT * 1000,
        )
    return mcp
