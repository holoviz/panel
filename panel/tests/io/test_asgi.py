"""
Tests for the framework neutral ASGI application backing the FastAPI and
Django integrations as well as ``panel serve --server asgi``.
"""
import pathlib

import pytest

pytest.importorskip("httpx")

from starlette.testclient import TestClient

from panel.config import config
from panel.io.application import build_applications
from panel.io.asgi import PanelASGI, build_asgi_app, warm_applications
from panel.io.resources import COMPONENT_PATH, DIST_DIR
from panel.io.state import state
from panel.pane import Markdown

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
    assert r.text == (ASSETS / 'custom.css').read_text()


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


def test_asgi_reuse_sessions(asgi_client):
    docs = []

    def app():
        docs.append(state.curdoc)
        return Markdown('# Reused')

    config.reuse_sessions = True
    try:
        with asgi_client({'/app': app}) as client:
            statuses = [client.get('/app').status_code for _ in range(2)]
    finally:
        config.reuse_sessions = False
        state._sessions.clear()
        state._session_key_funcs.clear()
    assert statuses == [200, 200]
    # The session (and therefore the Document) is created once and handed
    # out to both requests.
    assert len(docs) == 1


def test_asgi_lifespan_starts_and_stops(asgi_apps):
    asgi = asgi_apps()
    assert not asgi._panel_started
    with TestClient(asgi) as client:
        client.get('/app')
        assert asgi._panel_started
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
