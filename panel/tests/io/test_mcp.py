import asyncio

import pytest

from bokeh.document.events import MessageSentEvent

import panel as pn

from panel.config import config
from panel.io.mcp import (
    MCP_TEMPLATE, MCPApp, MCPError, _schema_from_signature, init_mcp_doc,
)
from panel.io.state import state
from panel.models.mcp import MCPMessageEvent, MCPReplyEvent
from panel.tests.util import serve_and_request


@pytest.fixture
def mcp_app(document):
    mcp = MCPApp()
    model = mcp.get_root(document)
    sent = []

    def record(event):
        if isinstance(event, MessageSentEvent) and event.msg_type == 'bokeh_event':
            msg = event.msg_data
            sent.append({
                'kind': msg.kind, 'method': msg.method,
                'params': msg.params, 'msg_id': msg.msg_id
            })

    document.on_change(record)
    yield mcp, model, sent
    mcp._cleanup(model)


def message(model, method, params=None, request_id=None):
    return MCPMessageEvent(model, method=method, params=params, request_id=request_id)


def connect(mcp, model, host_context=None, host_capabilities=None, host_info=None):
    model.host_context = host_context or {}
    model.host_capabilities = host_capabilities or {}
    model.host_info = host_info
    mcp._process_events({'connected': True})


def test_mcp_connect_syncs_host_context(mcp_app):
    mcp, model, _ = mcp_app
    connect(
        mcp, model,
        host_context={
            'theme': 'dark', 'displayMode': 'inline', 'locale': 'de-DE',
            'timeZone': 'Europe/Berlin', 'platform': 'web',
            'containerDimensions': {'maxHeight': 600}
        },
        host_capabilities={'openLinks': {}},
        host_info={'name': 'test-host', 'version': '1.0'}
    )
    assert mcp.connected
    assert mcp.theme == 'dark'
    assert mcp.display_mode == 'inline'
    assert mcp.locale == 'de-DE'
    assert mcp.time_zone == 'Europe/Berlin'
    assert mcp.platform == 'web'
    assert mcp.container_dimensions == {'maxHeight': 600}
    assert mcp.host_capabilities == {'openLinks': {}}
    assert mcp.host_info == {'name': 'test-host', 'version': '1.0'}


def test_mcp_tool_input(mcp_app):
    mcp, model, _ = mcp_app
    mcp._process_message(message(model, 'ui/notifications/tool-input', {'arguments': {'x': 1}}))
    assert mcp.tool_input == {'x': 1}


def test_mcp_tool_input_partial(mcp_app):
    mcp, model, _ = mcp_app
    mcp._process_message(message(model, 'ui/notifications/tool-input-partial', {'arguments': {'x': 'a'}}))
    assert mcp.tool_input_partial == {'x': 'a'}
    assert mcp.tool_input is None


def test_mcp_tool_result(mcp_app):
    mcp, model, _ = mcp_app
    result = {'content': [{'type': 'text', 'text': 'Done'}], 'structuredContent': {'a': 1}}
    mcp._process_message(message(model, 'ui/notifications/tool-result', result))
    assert mcp.tool_result == result


def test_mcp_tool_cancelled(mcp_app):
    mcp, model, _ = mcp_app
    mcp._process_message(message(model, 'ui/notifications/tool-cancelled', {'reason': 'User aborted'}))
    assert mcp.tool_cancelled == 'User aborted'


def test_mcp_host_context_changed_merges(mcp_app):
    mcp, model, _ = mcp_app
    connect(mcp, model, host_context={'theme': 'light', 'locale': 'en-US'})
    mcp._process_message(message(model, 'ui/notifications/host-context-changed', {'theme': 'dark'}))
    assert mcp.theme == 'dark'
    assert mcp.locale == 'en-US'
    assert mcp.host_context == {'theme': 'dark', 'locale': 'en-US'}

    mcp._process_message(message(
        model, 'ui/notifications/host-context-changed',
        {'displayMode': 'fullscreen', 'containerDimensions': {'height': 400}}
    ))
    assert mcp.display_mode == 'fullscreen'
    assert mcp.container_dimensions == {'height': 400}
    assert mcp.theme == 'dark'


def test_mcp_on_message_callbacks(mcp_app):
    mcp, model, _ = mcp_app
    specific, wildcard = [], []
    mcp.on_message('ui/notifications/tool-input', specific.append)
    mcp.on_message('*', lambda method, params: wildcard.append((method, params)))
    mcp._process_message(message(model, 'ui/notifications/tool-input', {'arguments': {'x': 1}}))
    mcp._process_message(message(model, 'custom/notification', {'y': 2}))
    assert specific == [{'arguments': {'x': 1}}]
    assert wildcard == [
        ('ui/notifications/tool-input', {'arguments': {'x': 1}}),
        ('custom/notification', {'y': 2}),
    ]


def test_mcp_tool_registration_infers_schema(mcp_app):
    mcp, model, _ = mcp_app

    @mcp.tool
    def highlight(start: str, end: str, count: int, scale: float = 1.0, active: bool = True):
        """Highlight a range."""

    assert model.tools == [{
        'name': 'highlight',
        'description': 'Highlight a range.',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'start': {'type': 'string'},
                'end': {'type': 'string'},
                'count': {'type': 'integer'},
                'scale': {'type': 'number'},
                'active': {'type': 'boolean'},
            },
            'required': ['start', 'end', 'count'],
        }
    }]


def test_mcp_tool_registration_explicit_metadata(mcp_app):
    mcp, model, _ = mcp_app
    schema = {'type': 'object', 'properties': {'q': {'type': 'string'}}}

    @mcp.tool(name='search', description='Search the data', input_schema=schema)
    def _search(q):
        return q

    assert model.tools == [{'name': 'search', 'description': 'Search the data', 'inputSchema': schema}]


def test_mcp_schema_skips_varargs():
    def func(a: list, b: dict, *args, **kwargs):
        pass
    assert _schema_from_signature(func) == {
        'type': 'object',
        'properties': {'a': {'type': 'array'}, 'b': {'type': 'object'}},
        'required': ['a', 'b'],
    }


def test_mcp_tools_list_responds(mcp_app):
    mcp, model, sent = mcp_app

    @mcp.tool
    def ping() -> str:
        """Ping."""
        return 'pong'

    mcp._process_message(message(model, 'tools/list', {}, request_id='tools/list-0'))
    assert sent == [{
        'kind': 'respond', 'method': '', 'msg_id': 'tools/list-0',
        'params': {'tools': [{
            'name': 'ping', 'description': 'Ping.',
            'inputSchema': {'type': 'object', 'properties': {}}
        }]},
    }]


def test_mcp_tool_registration_notifies_when_connected(mcp_app):
    mcp, model, sent = mcp_app
    connect(mcp, model)

    @mcp.tool
    def ping():
        return 'pong'

    assert sent == [{
        'kind': 'notify', 'method': 'notifications/tools/list_changed',
        'params': {}, 'msg_id': None
    }]

    mcp.remove_tool('ping')
    assert model.tools == []
    assert len(sent) == 2


def test_mcp_tool_call_success(mcp_app):
    mcp, model, sent = mcp_app

    @mcp.tool
    def add(a: int, b: int) -> int:
        return a + b

    mcp._process_message(message(
        model, 'tools/call', {'name': 'add', 'arguments': {'a': 1, 'b': 2}}, 'tools/call-0'
    ))
    assert sent == [{
        'kind': 'respond', 'method': '', 'msg_id': 'tools/call-0',
        'params': {'content': [{'type': 'text', 'text': '3'}]}
    }]


def test_mcp_tool_call_passes_through_call_tool_result(mcp_app):
    mcp, model, sent = mcp_app
    result = {'content': [{'type': 'text', 'text': 'ok'}], 'structuredContent': {'ok': True}}

    @mcp.tool
    def structured():
        return result

    mcp._process_message(message(model, 'tools/call', {'name': 'structured'}, 'tools/call-0'))
    assert sent[0]['params'] == result


def test_mcp_tool_call_async(mcp_app):
    mcp, model, sent = mcp_app

    @mcp.tool
    async def slow(text: str) -> str:
        await asyncio.sleep(0)
        return text.upper()

    mcp._process_message(message(
        model, 'tools/call', {'name': 'slow', 'arguments': {'text': 'hi'}}, 'tools/call-0'
    ))
    assert sent[0]['params'] == {'content': [{'type': 'text', 'text': 'HI'}]}


def test_mcp_tool_call_error(mcp_app):
    mcp, model, sent = mcp_app

    @mcp.tool
    def fail():
        raise ValueError('Bad input')

    mcp._process_message(message(model, 'tools/call', {'name': 'fail'}, 'tools/call-0'))
    assert sent[0]['params'] == {
        'content': [{'type': 'text', 'text': 'ValueError: Bad input'}],
        'isError': True
    }


def test_mcp_tool_call_unknown_tool(mcp_app):
    mcp, model, sent = mcp_app
    mcp._process_message(message(model, 'tools/call', {'name': 'missing'}, 'tools/call-0'))
    assert sent[0]['params'] == {
        'content': [{'type': 'text', 'text': 'Unknown tool: missing'}],
        'isError': True
    }


def test_mcp_teardown_callbacks(mcp_app):
    mcp, model, sent = mcp_app
    reasons = []

    def failing(reason):
        raise RuntimeError('Should not prevent other callbacks')

    async def flush(reason):
        await asyncio.sleep(0)
        reasons.append(reason)

    mcp.on_teardown(reasons.append)
    mcp.on_teardown(failing)
    mcp.on_teardown(flush)
    mcp._process_message(message(model, 'ui/resource-teardown', {'reason': 'closed'}, 'teardown-0'))
    assert reasons == ['closed', 'closed']
    assert sent == [{'kind': 'respond', 'method': '', 'params': {}, 'msg_id': 'teardown-0'}]


def test_mcp_log_notifies(mcp_app):
    mcp, _, sent = mcp_app
    mcp.log('info', {'a': 1}, logger='app')
    assert sent == [{
        'kind': 'notify', 'method': 'notifications/message',
        'params': {'level': 'info', 'data': {'a': 1}, 'logger': 'app'},
        'msg_id': None
    }]


async def _await_request(mcp, model, sent, coro, result=None, error=None):
    task = asyncio.ensure_future(coro)
    for _ in range(10):
        await asyncio.sleep(0)
        if sent:
            break
    request = sent[-1]
    mcp._process_reply_event(MCPReplyEvent(model, msg_id=request['msg_id'], result=result, error=error))
    return request, await task


async def test_mcp_call_tool_resolves(mcp_app):
    mcp, model, sent = mcp_app
    result = {'content': [{'type': 'text', 'text': 'ok'}]}
    request, value = await _await_request(
        mcp, model, sent, mcp.call_tool('fetch', {'id': 1}), result=result
    )
    assert request['kind'] == 'request'
    assert request['method'] == 'tools/call'
    assert request['params'] == {'name': 'fetch', 'arguments': {'id': 1}}
    assert value == result
    assert mcp._replies == {}


async def test_mcp_update_model_context_request(mcp_app):
    mcp, model, sent = mcp_app
    request, _ = await _await_request(
        mcp, model, sent, mcp.update_model_context(
            content=[{'type': 'text', 'text': 'Viewing 2024'}],
            structured_content={'year': 2024}
        ), result={}
    )
    assert request['method'] == 'ui/update-model-context'
    assert request['params'] == {
        'content': [{'type': 'text', 'text': 'Viewing 2024'}],
        'structuredContent': {'year': 2024}
    }


async def test_mcp_send_message_request(mcp_app):
    mcp, model, sent = mcp_app
    request, _ = await _await_request(mcp, model, sent, mcp.send_message('Hello'), result={})
    assert request['method'] == 'ui/message'
    assert request['params'] == {'role': 'user', 'content': {'type': 'text', 'text': 'Hello'}}


async def test_mcp_request_display_mode_returns_applied_mode(mcp_app):
    mcp, model, sent = mcp_app
    connect(mcp, model, host_context={'availableDisplayModes': ['inline', 'fullscreen']})
    _, mode = await _await_request(
        mcp, model, sent, mcp.request_display_mode('fullscreen'), result={'mode': 'inline'}
    )
    assert mode == 'inline'


async def test_mcp_request_display_mode_unavailable(mcp_app):
    mcp, model, _ = mcp_app
    connect(mcp, model, host_context={'availableDisplayModes': ['inline']})
    with pytest.raises(ValueError):
        await mcp.request_display_mode('pip')


async def test_mcp_request_error_raises_mcp_error(mcp_app):
    mcp, model, sent = mcp_app
    with pytest.raises(MCPError, match='Denied by user'):
        await _await_request(
            mcp, model, sent, mcp.open_link('https://holoviz.org'),
            error={'code': -32000, 'message': 'Denied by user'}
        )
    assert mcp._replies == {}


async def test_mcp_request_timeout(mcp_app):
    mcp, _, _ = mcp_app
    with pytest.raises(asyncio.TimeoutError):
        await mcp.read_resource('ui://app', timeout=0.01)
    assert mcp._replies == {}


async def test_mcp_reply_for_unknown_request_ignored(mcp_app):
    mcp, model, _ = mcp_app
    mcp._process_reply_event(MCPReplyEvent(model, msg_id='missing', result={}))


def test_state_mcp_none_outside_session():
    assert state.mcp is None


def test_state_mcp_none_without_flag(server_document):
    server_document.session_context.request.arguments = {}
    assert state.mcp is None


@pytest.mark.parametrize('value', [b'1', b'true', b''])
def test_state_mcp_from_query_parameter(server_document, value):
    server_document.session_context.request.arguments = {'mcp': [value]}
    mcp = state.mcp
    assert isinstance(mcp, MCPApp)
    assert state.mcp is mcp


@pytest.mark.parametrize('value', [b'0', b'false'])
def test_state_mcp_query_parameter_overrides_config(server_document, value):
    server_document.session_context.request.arguments = {'mcp': [value]}
    with config.set(mcp=True):
        assert state.mcp is None


def test_state_mcp_from_config(server_document):
    server_document.session_context.request.arguments = {}
    with config.set(mcp=True):
        assert isinstance(state.mcp, MCPApp)


def test_init_mcp_doc(server_document):
    request = server_document.session_context.request
    request.arguments = {'mcp': [b'1'], 'year': [b'2024']}
    request.protocol = 'http'
    request.host = 'localhost:5006'
    request.uri = '/app?mcp=1&year=2024'
    pn.panel('Hello').server_doc(server_document)
    mcp = init_mcp_doc(server_document)
    assert mcp is state.mcp
    roots = {root.name: root for root in server_document.roots}
    assert 'mcp' in roots
    assert server_document.template is MCP_TEMPLATE
    assert server_document.template_variables['mcp_app_url'] == 'http://localhost:5006/app?year=2024'
    assert server_document.template_variables['mcp_timeout'] == 15000
    assert 'window.__panelMCP__' in server_document.template_variables['mcp_bridge_js']

    init_mcp_doc(server_document)
    assert [root.name for root in server_document.roots].count('mcp') == 1


def test_init_mcp_doc_fallback_url_disables_mcp(server_document):
    request = server_document.session_context.request
    request.arguments = {}
    request.protocol = 'https'
    request.host = 'example.com'
    request.uri = '/app'
    with config.set(mcp=True):
        init_mcp_doc(server_document)
        assert server_document.template_variables['mcp_app_url'] == 'https://example.com/app?mcp=0'


def test_init_mcp_doc_without_flag(server_document):
    server_document.session_context.request.arguments = {}
    pn.panel('Hello').server_doc(server_document)
    assert init_mcp_doc(server_document) is None
    assert 'mcp' not in [root.name for root in server_document.roots]


def test_init_mcp_doc_custom_template_warns(server_document):
    server_document.session_context.request.arguments = {'mcp': [b'1']}
    pn.template.BootstrapTemplate(main=['Hello']).server_doc(server_document)
    template = server_document.template
    with pytest.warns(UserWarning, match='not supported'):
        mcp = init_mcp_doc(server_document)
    assert isinstance(mcp, MCPApp)
    assert server_document.template is template
    assert 'mcp' not in [root.name for root in server_document.roots]


def test_mcp_destroyed_with_session(server_document):
    server_document.session_context._document = server_document
    server_document.session_context.request.arguments = {'mcp': [b'1']}
    mcp = init_mcp_doc(server_document)
    assert server_document in state._mcp_apps
    state._destroy_session(server_document.session_context)
    assert server_document not in state._mcp_apps
    assert mcp._documents == {}


def test_serve_mcp_query_parameter(server_implementation):
    def app():
        assert state.mcp is not None
        return pn.panel('Hello')

    html = serve_and_request(app, suffix='/?mcp=1').text
    assert 'window.__panelMCP__' in html
    assert 'pn-mcp-overlay' in html


def test_serve_without_mcp_query_parameter():
    def app():
        assert state.mcp is None
        return pn.panel('Hello')

    html = serve_and_request(app).text
    assert 'window.__panelMCP__' not in html
    assert 'pn-mcp-overlay' not in html


def test_serve_mcp_config(server_implementation):
    with config.set(mcp=True):
        html = serve_and_request(pn.panel('Hello')).text
    assert 'window.__panelMCP__' in html
    assert '?mcp=0' in html
