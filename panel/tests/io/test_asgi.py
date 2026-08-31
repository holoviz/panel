"""
Tests for the framework neutral ASGI application backing the FastAPI and
Django integrations as well as ``panel serve --server asgi``.
"""
import json
import pathlib

from contextlib import contextmanager

import pytest

pytest.importorskip("httpx")

import anyio

from bokeh.server.asgi import _ASGIWebSocketTransport
from starlette.testclient import TestClient

from panel.config import config
from panel.io.application import build_applications
from panel.io.asgi import PanelASGI, build_asgi_app, warm_applications
from panel.io.document import extra_socket_handlers, unlocked
from panel.io.resources import COMPONENT_PATH, DIST_DIR
from panel.io.state import set_curdoc, state
from panel.layout import Column
from panel.pane import Markdown
from panel.tests.util import wait_until
from panel.widgets import IntSlider

ASSETS = pathlib.Path(__file__).parent / 'assets'


class CustomComponent:
    """
    Declares a CSS resource so the component resource endpoint has something
    it is allowed to serve. Deliberately not a Panel component, since a
    component subclass declared in a test module registers itself in the
    global pane and model registries for the rest of the session.
    """

    _css = ['./assets/custom.css']


def markdown_app():
    return Markdown('# Test app')


@pytest.fixture
def asgi_apps():
    """
    Builds PanelASGI applications and cleans up the global state they
    register themselves in.
    """
    apps = []

    def create(panel=None, **kwargs):
        asgi = build_asgi_app(panel or {'/app': markdown_app}, **kwargs)
        apps.append(asgi)
        return asgi

    yield create
    for asgi in apps:
        state._server_config.pop(asgi, None)


@pytest.fixture
def asgi_client(asgi_apps):
    def create(panel=None, **kwargs):
        return TestClient(asgi_apps(panel, **kwargs))
    return create


def test_asgi_serves_document(asgi_client):
    with asgi_client() as client:
        r = client.get('/app')
    assert r.status_code == 200
    assert r.headers['content-type'].startswith('text/html')
    assert r.headers['cache-control'] == 'no-store'
    assert 'Bokeh.safely' in r.text


def test_asgi_document_head_request(asgi_client):
    with asgi_client() as client:
        r = client.head('/app')
    assert r.status_code == 200
    assert r.content == b''


def test_asgi_document_method_not_allowed(asgi_client):
    with asgi_client() as client:
        r = client.post('/app')
    assert r.status_code == 405


def test_asgi_serves_metadata(asgi_client):
    with asgi_client() as client:
        r = client.get('/app/metadata')
    assert r.status_code == 200
    assert 'data' in r.json()


def test_asgi_serves_autoload_js(asgi_client):
    with asgi_client() as client:
        r = client.get('/app/autoload.js?bokeh-autoload-element=1000')
    assert r.status_code == 200
    assert r.headers['content-type'].startswith('application/javascript')
    assert 'bokeh.min.js' in r.text


def test_asgi_autoload_js_requires_element(asgi_client):
    with asgi_client() as client:
        r = client.get('/app/autoload.js')
    assert r.status_code == 400


def test_asgi_get_on_websocket_route(asgi_client):
    with asgi_client() as client:
        r = client.get('/app/ws')
    assert r.status_code == 400
    assert 'WebSocket' in r.text


def test_asgi_unknown_route(asgi_client):
    with asgi_client() as client:
        assert client.get('/nonexistent').status_code == 404
        assert client.get('/app/nonexistent').status_code == 404


def test_asgi_index_page(asgi_client):
    apps = {'/app1': markdown_app, '/app2': markdown_app}
    with asgi_client(apps) as client:
        r = client.get('/')
    assert r.status_code == 200
    assert '/app1' in r.text
    assert '/app2' in r.text


def test_asgi_index_disabled(asgi_client):
    apps = {'/app1': markdown_app, '/app2': markdown_app}
    with asgi_client(apps, index_enabled=False) as client:
        assert client.get('/').status_code == 404


def test_asgi_single_app_index_redirects(asgi_client):
    with asgi_client() as client:
        r = client.get('/', follow_redirects=False)
    assert r.status_code == 302
    assert r.headers['location'].endswith('/app')


def test_asgi_favicon(asgi_client):
    with asgi_client() as client:
        r = client.get('/favicon.ico')
    assert r.status_code == 200
    assert r.content == (DIST_DIR / 'images' / 'favicon.ico').read_bytes()


def test_asgi_favicon_custom(asgi_client):
    ico_path = DIST_DIR / 'images' / 'icon-32x32.png'
    with asgi_client(ico_path=ico_path) as client:
        r = client.get('/favicon.ico')
    assert r.status_code == 200
    assert r.content == ico_path.read_bytes()


def test_asgi_favicon_disabled(asgi_client):
    with asgi_client(ico_path='none') as client:
        assert client.get('/favicon.ico').status_code == 404


def test_asgi_global_static(asgi_client):
    with asgi_client() as client:
        r = client.get('/static/js/bokeh.min.js')
    assert r.status_code == 200
    assert r.headers['content-type'].startswith('application/javascript')


def test_asgi_component_resource(asgi_client):
    with asgi_client() as client:
        r = client.get(
            f'/{COMPONENT_PATH}panel.tests.io.test_asgi/CustomComponent'
            '/_css/assets/custom.css'
        )
    assert r.status_code == 200
    assert r.text.replace('\r\n', '\n') == (ASSETS / 'custom.css').read_text()


def test_asgi_component_resource_unlisted(asgi_client):
    with asgi_client() as client:
        # Only resources explicitly listed on the component may be served
        r = client.get(
            f'/{COMPONENT_PATH}panel.tests.io.test_asgi/CustomComponent'
            '/_css/assets/secret.css'
        )
    assert r.status_code == 403


def test_asgi_component_resource_not_found(asgi_client):
    with asgi_client() as client:
        assert client.get(f'/{COMPONENT_PATH}not.a.module/Nope/_css/x.css').status_code == 404
        assert client.get(f'/{COMPONENT_PATH}malformed').status_code == 400


def test_asgi_liveness_endpoint(asgi_client):
    with asgi_client(liveness=True) as client:
        r = client.get('/liveness')
    assert r.status_code == 200
    assert r.json() == {'/liveness': True}


def test_asgi_liveness_custom_endpoint(asgi_client):
    with asgi_client(liveness='alive') as client:
        assert client.get('/alive').status_code == 200
        assert client.get('/liveness').status_code == 404


def test_asgi_liveness_checks_application(asgi_client):
    with asgi_client(liveness=True) as client:
        assert client.get('/liveness?endpoint=/app').json() == {'/app': True}
        assert client.get('/liveness?endpoint=/nope').status_code == 400


def test_asgi_no_liveness_endpoint_by_default(asgi_client):
    with asgi_client() as client:
        assert client.get('/liveness').status_code == 404


def test_asgi_session_info(asgi_client):
    try:
        with asgi_client(session_history=5) as client:
            r = client.get('/session_info')
    finally:
        config.session_history = 0
    assert r.status_code == 200
    info = r.json()
    assert info['total'] == 0
    assert info['live'] == 0


def test_asgi_static_dirs(asgi_client, tmp_path):
    (tmp_path / 'file.txt').write_text('static content')
    (tmp_path / 'index.html').write_text('<html>index</html>')
    with asgi_client(static_dirs={'assets': str(tmp_path)}) as client:
        assert client.get('/assets/file.txt').text == 'static content'
        assert client.get('/assets').text == '<html>index</html>'
        assert client.get('/assets/missing.txt').status_code == 404


def test_asgi_prefix(asgi_client):
    with asgi_client(prefix='/prefix') as client:
        assert client.get('/prefix/app').status_code == 200
        assert client.get('/app').status_code == 404
        assert client.get('/prefix/liveness').status_code == 404


def test_asgi_prefix_root_redirects_to_single_app(asgi_client):
    with asgi_client(prefix='/prefix') as client:
        r = client.get('/prefix/', follow_redirects=False)
    assert r.status_code == 302
    assert r.headers['location'] == '/prefix/app'


def test_asgi_prefixed_root_app_redirects_to_trailing_slash(asgi_client):
    with asgi_client({'/': markdown_app}, prefix='/prefix') as client:
        r = client.get('/prefix', follow_redirects=False)
        assert r.status_code == 302
        assert r.headers['location'] == '/prefix/'
        assert client.get('/prefix/').status_code == 200


def test_asgi_prefix_resources_are_relative(asgi_client):
    # Resources are resolved relative to the document URL so that both the
    # prefix and any proxy root path are applied by the browser.
    with asgi_client(prefix='/prefix') as client:
        r = client.get('/prefix/app')
        assert 'src="static/js/bokeh.min.js"' in r.text
        assert client.get('/prefix/static/js/bokeh.min.js').status_code == 200


def test_asgi_root_path(asgi_apps):
    with TestClient(asgi_apps(), root_path='/mounted') as client:
        r = client.get('/mounted/app')
        assert r.status_code == 200
        assert 'src="static/js/bokeh.min.js"' in r.text
        assert client.get('/mounted/static/js/bokeh.min.js').status_code == 200


def test_asgi_wildcard_route_params(asgi_client):
    params = []

    def app():
        params.append(dict(state.route_params))
        return Markdown('# Wildcard')

    with asgi_client({'/user/{name}': app}) as client:
        assert client.get('/user/alice').status_code == 200
        assert client.get('/user/alice/extra').status_code == 404
    assert params == [{'name': 'alice'}]


def test_asgi_handles_scope(asgi_apps):
    asgi = asgi_apps(prefix='/prefix')

    def scope(path, type='http'):
        return {'type': type, 'path': path, 'root_path': '', 'method': 'GET'}

    assert asgi.handles(scope('/prefix/app'))
    assert asgi.handles(scope('/prefix/app/ws', type='websocket'))
    assert asgi.handles(scope('/prefix/favicon.ico'))
    assert asgi.handles(scope('/prefix/static/js/bokeh.min.js'))
    assert asgi.handles(scope('/prefix/'))
    assert not asgi.handles(scope('/app'))
    assert not asgi.handles(scope('/prefix/other'))
    assert not asgi.handles({'type': 'lifespan'})


@pytest.fixture
def reuse_sessions():
    def enable(value=True):
        config.reuse_sessions = value
    try:
        yield enable
    finally:
        config.reuse_sessions = False
        state._sessions.clear()
        state._session_key_funcs.clear()


def test_asgi_reuse_sessions(asgi_client, reuse_sessions):
    docs = []

    def app():
        docs.append(state.curdoc)
        return Markdown('# Reused')

    reuse_sessions()
    with asgi_client({'/app': app}) as client:
        statuses = [client.get('/app').status_code for _ in range(2)]
    assert statuses == [200, 200]
    # The session (and therefore the Document) is created once and handed
    # out to both requests.
    assert len(docs) == 1


def test_asgi_reuse_sessions_regenerates_token(asgi_client, reuse_sessions):
    """
    A reused session hands the same Document to multiple requests, so each
    request must be given its own session id, otherwise the second browser
    would attach to the websocket of the first.
    """
    from bokeh.util.token import get_session_id, get_token_payload

    reuse_sessions()
    with asgi_client() as client:
        first, second = _token(client), _token(client)

    assert get_session_id(first) != get_session_id(second)
    # The payload of the reused session is carried over to the new token
    assert get_token_payload(first) == get_token_payload(second)


def test_asgi_reuse_sessions_warm(asgi_apps, reuse_sessions):
    """
    In 'warm' mode the session the regenerated token refers to is created
    ahead of the websocket connection rather than on connect.
    """
    reuse_sessions('warm')
    asgi = asgi_apps()
    with TestClient(asgi) as client:
        _token(client)
        assert len(asgi.core.get_sessions('/app')) == 1
        token = _token(client)
        # Warming is scheduled on the event loop, so let it run
        wait_until(lambda: len(asgi.core.get_sessions('/app')) == 2)
        session_ids = [session.id for session in asgi.core.get_sessions('/app')]

    from bokeh.util.token import get_session_id
    assert get_session_id(token) in session_ids


def test_asgi_session_error_is_reported(asgi_client):
    with asgi_client() as client:
        r = client.get('/app?bokeh-session-id=abc&bokeh-token=xyz')
    assert r.status_code == 403
    assert 'Both token and session ID were provided' in r.text


def test_asgi_autoload_session_error_is_reported(asgi_client):
    with asgi_client() as client:
        r = client.get(
            '/app/autoload.js?bokeh-autoload-element=1000&bokeh-session-id=abc'
            '&bokeh-token=xyz'
        )
    assert r.status_code == 403
    assert 'Both token and session ID were provided' in r.text


def test_asgi_lifespan_starts_and_stops(asgi_apps):
    asgi = asgi_apps()
    assert not asgi._panel_started
    with TestClient(asgi) as client:
        client.get('/app')
        assert asgi._panel_started
    assert not asgi._panel_started


@pytest.mark.asyncio
async def test_asgi_lifespan_reports_startup_failure(asgi_apps, monkeypatch):
    """
    An ASGI server relies on the startup failure event to abort the boot,
    so a failing application must not report a successful startup.
    """
    asgi = asgi_apps()
    events, sent = [{'type': 'lifespan.startup'}], []

    async def receive():
        return events.pop(0)

    async def send(message):
        sent.append(message)

    async def failing_start():
        raise RuntimeError('boom')

    monkeypatch.setattr(asgi.core, 'start', failing_start)
    await asgi({'type': 'lifespan'}, receive, send)

    assert sent == [{'type': 'lifespan.startup.failed', 'message': 'boom'}]
    assert not asgi._panel_started


def test_asgi_registers_server_config(asgi_apps):
    assert asgi_apps() in state._server_config


def test_asgi_warm_applications():
    apps = build_applications({'/app': markdown_app})
    warm_applications(apps)


def test_asgi_build_websocket_origins(asgi_apps):
    asgi = asgi_apps(websocket_origin='example.com')
    assert isinstance(asgi, PanelASGI)
    assert 'example.com' in asgi.core.websocket_origins


#---------------------------------------------------------------------
# Websockets
#---------------------------------------------------------------------

# The event BokehJS sends once it has built the document, which is what
# makes a session connected and runs the onload callbacks.
DOCUMENT_READY = [{
    'kind': 'MessageSent',
    'msg_type': 'bokeh_event',
    'msg_data': {
        'type': 'event',
        'name': 'document_ready',
        'values': {'type': 'map', 'entries': []}
    }
}]


def _token(client, path='/app'):
    """
    Extracts the session token embedded in the rendered document.
    """
    r = client.get(path)
    assert r.status_code == 200
    return r.text.split('"token":')[1].split('"')[1]


def _receive_frame(ws, binary=False, timeout=10):
    """
    Receives a single websocket frame.

    ``WebSocketTestSession.receive_text`` blocks indefinitely if the server
    never writes, so the read is bounded by awaiting the session's message
    stream directly, turning a lost message into a failure rather than a
    hanging test.
    """
    async def receive():
        with anyio.fail_after(timeout):
            return await ws._send_rx.receive()

    message = ws.portal.call(receive)
    ws._raise_on_close(message)
    return message['bytes'] if binary else message['text']


def _receive(ws):
    """
    Reassembles one Bokeh protocol message from its wire fragments.
    """
    header = json.loads(_receive_frame(ws))
    _receive_frame(ws)  # metadata
    content = json.loads(_receive_frame(ws))
    for _ in range(header.get('num_buffers', 0)):
        _receive_frame(ws)
        _receive_frame(ws, binary=True)
    return header['msgtype'], content


def _receive_patch(ws, tries=3):
    """
    Returns the events of the next PATCH-DOC, skipping the protocol
    replies, whose ordering relative to a patch is not guaranteed.
    """
    for _ in range(tries):
        msgtype, content = _receive(ws)
        if msgtype == 'PATCH-DOC':
            return content['events']
    raise AssertionError('Expected a PATCH-DOC message')


def _send_patch(ws, events):
    ws.send_text(json.dumps({'msgid': '1', 'msgtype': 'PATCH-DOC'}))
    ws.send_text('{}')
    ws.send_text(json.dumps({'events': events}))


@contextmanager
def _connect(client, path='/app'):
    """
    Connects a websocket to a new session and reports the document as
    ready, leaving the session in the state a live browser session is in.
    """
    subprotocols = ['bokeh', _token(client, path)]
    with client.websocket_connect(f'{path}/ws', subprotocols=subprotocols) as ws:
        assert _receive(ws)[0] == 'ACK'
        _send_patch(ws, DOCUMENT_READY)
        assert _receive(ws)[0] == 'OK'
        yield ws


def test_asgi_websocket_acks(asgi_client):
    with asgi_client() as client:
        token = _token(client)
        with client.websocket_connect('/app/ws', subprotocols=['bokeh', token]) as ws:
            assert _receive(ws)[0] == 'ACK'


def test_asgi_websocket_requires_subprotocol(asgi_client):
    from starlette.websockets import WebSocketDisconnect

    with asgi_client() as client:
        with pytest.raises(WebSocketDisconnect) as excinfo:
            with client.websocket_connect('/app/ws'):
                pass
    assert excinfo.value.code == 1002


def test_asgi_websocket_rejects_invalid_token(asgi_client):
    from starlette.websockets import WebSocketDisconnect

    with asgi_client() as client:
        with pytest.raises(WebSocketDisconnect) as excinfo:
            with client.websocket_connect('/app/ws', subprotocols=['bokeh', 'not-a-token']):
                pass
    assert excinfo.value.code == 1008


def test_asgi_websocket_rejects_disallowed_origin(asgi_client):
    from starlette.websockets import WebSocketDisconnect

    with asgi_client() as client:
        token = _token(client)
        with pytest.raises(WebSocketDisconnect) as excinfo:
            with client.websocket_connect(
                '/app/ws', subprotocols=['bokeh', token],
                headers={'origin': 'http://evil.example.com'}
            ):
                pass
    assert excinfo.value.code == 1008


def test_asgi_websocket_allows_configured_origin(asgi_client):
    with asgi_client(websocket_origin='evil.example.com') as client:
        token = _token(client)
        with client.websocket_connect(
            '/app/ws', subprotocols=['bokeh', token],
            headers={'origin': 'http://evil.example.com'}
        ) as ws:
            assert _receive(ws)[0] == 'ACK'


def test_asgi_websocket_document_ready_connects_session(asgi_client):
    docs, loaded = [], []

    def app():
        docs.append(state.curdoc)
        state.onload(lambda: loaded.append(state.curdoc))
        return Markdown('# Test app')

    with asgi_client({'/app': app}) as client:
        with _connect(client):
            doc = docs[0]
            assert loaded == [doc]
            assert state._connected[doc]
            assert state._loaded[doc]


def test_asgi_websocket_writes_server_side_changes(asgi_client, monkeypatch):
    """
    Changes made on the server outside a locked callback are written to the
    socket by Panel itself, i.e. via the dispatcher registered for the ASGI
    transport, batched into a single message.
    """
    objs = {}

    def app():
        one, two = Markdown('one'), Markdown('two')
        objs.update(doc=state.curdoc, one=one, two=two)
        return Column(one, two)

    dispatched = []
    dispatch_asgi = extra_socket_handlers[_ASGIWebSocketTransport]
    monkeypatch.setitem(
        extra_socket_handlers, _ASGIWebSocketTransport,
        lambda conn, **kwargs: dispatched.append(conn) or dispatch_asgi(conn, **kwargs)
    )

    async def push():
        with set_curdoc(objs['doc']):
            with unlocked():
                objs['one'].object = 'first'
                objs['two'].object = 'second'

    with asgi_client({'/app': app}) as client:
        with _connect(client) as ws:
            client.portal.call(push)
            events = _receive_patch(ws)

    assert len(dispatched) == 1
    assert [event['kind'] for event in events] == ['ModelChanged', 'ModelChanged']
    assert 'first' in events[0]['new']
    assert 'second' in events[1]['new']


def test_asgi_websocket_applies_client_events(asgi_client):
    objs, values = {}, []

    def app():
        slider = IntSlider(value=1)
        text = Markdown('1')

        def sync(event):
            values.append(event.new)
            text.object = str(event.new)

        slider.param.watch(sync, 'value')
        objs.update(slider=slider, text=text)
        return Column(slider, text)

    with asgi_client({'/app': app}) as client:
        with _connect(client) as ws:
            model_id = list(objs['slider']._models.values())[0][0].id
            _send_patch(ws, [{
                'kind': 'ModelChanged', 'model': {'id': model_id},
                'attr': 'value', 'new': 7
            }])
            events = _receive_patch(ws)

    # The client event was applied to the parameter and the resulting
    # server side change was written back to the client
    assert values == [7]
    assert objs['slider'].value == 7
    assert '7' in events[0]['new']


#---------------------------------------------------------------------
# Authorization
#---------------------------------------------------------------------

@pytest.fixture
def authorize_callback():
    def set_callback(callback):
        config.authorize_callback = callback
    try:
        yield set_callback
    finally:
        config.authorize_callback = None


def test_asgi_authorize_callback_denies_document(asgi_client, authorize_callback):
    paths = []
    authorize_callback(lambda user_info, path: paths.append(path) or False)
    with asgi_client() as client:
        r = client.get('/app')
    assert r.status_code == 403
    assert r.headers['content-type'].startswith('text/html')
    assert 'Authorization Error' in r.text
    assert paths == ['/app']


def test_asgi_authorize_callback_grants_document(asgi_client, authorize_callback):
    authorize_callback(lambda user_info, path: True)
    with asgi_client() as client:
        assert client.get('/app').status_code == 200


def test_asgi_authorize_callback_redirects(asgi_client, authorize_callback):
    authorize_callback(lambda user_info: '/denied')
    with asgi_client() as client:
        r = client.get('/app', follow_redirects=False)
    assert r.status_code == 302
    assert r.headers['location'] == '/denied'


def test_asgi_authorize_callback_errors_are_not_authorized(asgi_client, authorize_callback):
    def failing(user_info):
        raise ValueError('boom')

    authorize_callback(failing)
    with asgi_client() as client:
        r = client.get('/app')
    assert r.status_code == 403
    # The exception is not leaked to the user
    assert 'boom' not in r.text


def test_asgi_authorize_callback_declared_in_session(asgi_client):
    """
    A callback declared by the application itself is scoped to the session,
    so it is only applied on the second, session level authorization check.
    """
    def app():
        config.authorize_callback = lambda user_info: False
        return Markdown('# Test app')

    with asgi_client({'/app': app}) as client:
        r = client.get('/app')
    assert r.status_code == 403
    assert 'Authorization Error' in r.text
