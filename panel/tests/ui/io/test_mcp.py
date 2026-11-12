import json
import pathlib

from urllib.parse import quote

import pytest

try:
    from playwright.sync_api import expect

    pytestmark = pytest.mark.ui
except ImportError:
    pytestmark = pytest.mark.skip("playwright not available")

import panel as pn

from panel.io.state import state
from panel.tests.util import serve_and_wait, wait_until

HERE = pathlib.Path(__file__).parent

TOOL_INPUT = {'year': 2024}

TOOL_RESULT = {
    'content': [{'type': 'text', 'text': 'Loaded 2024'}],
    'structuredContent': {'rows': 3},
}


def serve_in_host(page, app, host_context=None, tool_input=TOOL_INPUT, tool_result=TOOL_RESULT):
    sessions = []

    def view():
        sessions.append(state.mcp)
        return app()

    # Serving the host from localhost and the View from 127.0.0.1 makes them
    # cross-origin, as in a real host, while satisfying Chromium's local
    # network access checks.
    port = serve_and_wait(view, static_dirs={'mcp-host': str(HERE)})
    config = {
        'app': f'http://127.0.0.1:{port}/?mcp=1',
        'hostContext': host_context or {},
        'toolInput': tool_input,
        'toolResult': tool_result,
    }
    page.goto(f'http://localhost:{port}/mcp-host/mcp_host.html#{quote(json.dumps(config))}')
    wait_until(lambda: len(sessions) == 1, page)
    mcp = sessions[0]
    assert mcp is not None
    wait_until(lambda: mcp.connected, page)
    return mcp, page.frame_locator('#view')


def host_messages(page, direction='in'):
    return [
        entry['message'] for entry in page.evaluate('() => window.host.messages')
        if entry['direction'] == direction
    ]


def test_mcp_handshake(page):
    mcp, frame = serve_in_host(page, lambda: pn.pane.Markdown('# Hello MCP'))

    expect(frame.locator('h1')).to_contain_text('Hello MCP')
    expect(frame.locator('#pn-mcp-overlay')).to_be_hidden()

    wait_until(lambda: mcp.tool_input == TOOL_INPUT, page)
    wait_until(lambda: mcp.tool_result == TOOL_RESULT, page)
    assert mcp.host_info == {'name': 'panel-test-host', 'version': '1.0.0'}
    assert 'serverTools' in mcp.host_capabilities

    methods = [msg.get('method') for msg in host_messages(page)]
    assert methods[:2] == ['ui/initialize', 'ui/notifications/initialized']
    initialize = host_messages(page)[0]
    assert initialize['params']['clientInfo']['name'] == 'panel'
    assert initialize['params']['appCapabilities']['tools'] == {'listChanged': True}


def test_mcp_host_context_theme(page):
    mcp, frame = serve_in_host(
        page, lambda: pn.pane.Markdown('Themed'),
        host_context={
            'theme': 'dark', 'locale': 'de-DE', 'displayMode': 'inline',
            'styles': {'variables': {'--color-background-primary': 'rgb(1, 2, 3)'}}
        }
    )

    assert mcp.theme == 'dark'
    assert mcp.locale == 'de-DE'
    assert mcp.display_mode == 'inline'
    expect(frame.locator('html')).to_have_attribute('data-mcp-theme', 'dark')
    expect(frame.locator('body')).to_have_css('background-color', 'rgb(1, 2, 3)')


def test_mcp_host_context_changed(page):
    mcp, _ = serve_in_host(page, lambda: pn.pane.Markdown('Theme'), host_context={'theme': 'light'})

    assert mcp.theme == 'light'
    page.evaluate("() => window.host.setHostContext({theme: 'dark', displayMode: 'fullscreen'})")
    wait_until(lambda: mcp.theme == 'dark', page)
    assert mcp.display_mode == 'fullscreen'
    assert mcp.host_context['theme'] == 'dark'


def test_mcp_update_model_context_from_callback(page):
    def app():
        async def update(event):
            await state.mcp.update_model_context(
                content=[{'type': 'text', 'text': 'Viewing 2024'}],
                structured_content={'year': 2024}
            )
            button.label = 'Updated'
        button = pn.widgets.Button(label='Update')
        button.on_click(update)
        return button

    _, frame = serve_in_host(page, app)

    frame.locator('button').click()
    wait_until(lambda: page.evaluate('() => window.modelContext') == {
        'content': [{'type': 'text', 'text': 'Viewing 2024'}],
        'structuredContent': {'year': 2024}
    }, page)
    expect(frame.locator('button')).to_have_text('Updated')


def test_mcp_call_server_tool(page):
    results = []

    def app():
        async def call(event):
            results.append(await state.mcp.call_tool('fetch', {'id': 1}))
        button = pn.widgets.Button(label='Fetch')
        button.on_click(call)
        return button

    _, frame = serve_in_host(page, app)

    frame.locator('button').click()
    wait_until(lambda: results == [{'content': [{'type': 'text', 'text': 'server ran fetch'}]}], page)
    assert page.evaluate('() => window.serverToolCalls') == [{'name': 'fetch', 'arguments': {'id': 1}}]


def test_mcp_host_calls_view_tool(page):
    def app():
        md = pn.pane.Markdown('Initial')

        @state.mcp.tool
        def set_text(text: str) -> str:
            """Replace the displayed text."""
            md.object = text
            return f'Showing {text}'

        return md

    _, frame = serve_in_host(page, app)

    tools = page.evaluate('() => window.host.listTools()')
    assert tools == {'tools': [{
        'name': 'set_text',
        'description': 'Replace the displayed text.',
        'inputSchema': {
            'type': 'object', 'properties': {'text': {'type': 'string'}}, 'required': ['text']
        }
    }]}

    result = page.evaluate("() => window.host.callTool('set_text', {text: 'From the agent'})")
    assert result == {'content': [{'type': 'text', 'text': 'Showing From the agent'}]}
    expect(frame.locator('.markdown')).to_have_text('From the agent')


def test_mcp_host_calls_failing_view_tool(page):
    def app():
        @state.mcp.tool
        def fail():
            raise ValueError('Nope')
        return pn.pane.Markdown('Failing')

    serve_in_host(page, app)

    result = page.evaluate("() => window.host.callTool('fail', {})")
    assert result == {'content': [{'type': 'text', 'text': 'ValueError: Nope'}], 'isError': True}


def test_mcp_teardown(page):
    reasons = []

    def app():
        state.mcp.on_teardown(reasons.append)
        return pn.pane.Markdown('Teardown')

    serve_in_host(page, app)

    assert page.evaluate("() => window.host.teardown('closed')") == {}
    assert reasons == ['closed']


def test_mcp_size_changed(page):
    serve_in_host(page, lambda: pn.Column(*(pn.pane.Markdown(f'Row {i}') for i in range(10))))

    def size_changed():
        msgs = [msg for msg in host_messages(page) if msg.get('method') == 'ui/notifications/size-changed']
        return msgs and msgs[-1]['params']['height'] > 100

    wait_until(size_changed, page)
    height = host_messages(page)[-1]['params']['height']
    wait_until(lambda: page.evaluate("() => document.getElementById('view').style.height") == f'{height}px', page)


def test_mcp_view_opened_top_level(page):
    sessions = []

    def app():
        sessions.append(state.mcp)
        return pn.pane.Markdown('# Standalone')

    port = serve_and_wait(app)
    page.goto(f'http://127.0.0.1:{port}/?mcp=1')

    expect(page.locator('h1')).to_contain_text('Standalone')
    expect(page.locator('#pn-mcp-overlay')).to_be_hidden()
    assert page.evaluate('() => window.__panelMCP__') is None
    assert len(sessions) == 1
    assert sessions[0] is not None
    assert not sessions[0].connected
