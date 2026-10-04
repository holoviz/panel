"""
Tests for the admin panel and its access control.
"""
import subprocess
import sys
import time

import pandas as pd
import pytest

from bokeh.document import Document

from panel.config import config
from panel.io.admin import (
    _filter_logs, _ui, admin_template, log_component, log_terminal,
)
from panel.io.admin_auth import (
    ADMIN_COOKIE, admin_cookie, admin_document_url, check_admin_access,
    create_admin_token, relative_endpoint, validate_admin_password,
    validate_admin_token,
)
from panel.io.state import set_curdoc, state
from panel.tests.util import serve_and_wait

# The admin panel renders panel.ui components, whose registration cannot be
# undone, so these tests have to run after the classic suite.
pytestmark = pytest.mark.usefixtures('panel_ui')

PASSWORD = 'admin-secret'

ADMIN_CONFIG = ('_admin', '_admin_password', '_admin_users', '_cookie_secret', '_page_config', 'admin_plugins')


@pytest.fixture(autouse=True)
def admin_config_cleanup():
    values = {name: getattr(config, name) for name in ADMIN_CONFIG}
    try:
        yield
    finally:
        config.param.update(**values)
        # The admin panel records the full session history.
        state.session_info = {'total': 0, 'live': 0, 'sessions': {}}


@pytest.fixture
def admin_password():
    config.admin_password = PASSWORD
    return PASSWORD


def _log(session, message, level='INFO', app='panel.io.server'):
    log_terminal.write(f'2026-10-03 14:38:04,803 {level}: {app} - Session {session} {message}\n')


#---------------------------------------------------------------------
# Admin panel
#---------------------------------------------------------------------

def test_ui_import_preserves_global_design():
    # Run in a fresh interpreter, the test session may have imported
    # panel.ui already.
    script = (
        "import panel as pn\n"
        "from panel.io.admin import _ui\n"
        "ui = _ui()\n"
        "assert pn.config.design is None, pn.config.design\n"
        "import panel.ui\n"
        "assert pn.config.design is panel.ui.MaterialUIDesign, pn.config.design\n"
        "assert panel.ui.Button is ui.Button\n"
    )
    subprocess.run([sys.executable, '-c', script], check=True, timeout=120)


def test_filter_logs():
    df = pd.DataFrame([
        ['2026-10-03', 'INFO', 'panel.io.server', 1, 'rendered'],
        ['2026-10-03', 'DEBUG', 'panel.state', 2, 'logged "[x]"'],
    ], columns=['datetime', 'level', 'app', 'session', 'message'])
    assert len(_filter_logs(df, [], '', [], '')) == 2
    assert _filter_logs(df, ['DEBUG'], '', [], '')['session'].tolist() == [2]
    assert _filter_logs(df, [], 'IO.SERVER', [], '')['session'].tolist() == [1]
    assert _filter_logs(df, [], '', [2], '')['session'].tolist() == [2]
    # Patterns are literal, an incomplete regex must not raise
    assert _filter_logs(df, [], '', [], '"[x')['session'].tolist() == [2]


def test_log_component_filters_and_streams_records():
    component = log_component()
    filters, table = component.objects
    level, _, session, _ = (grid.objects[0] for grid in filters.objects[0].objects)

    level.value = ['WARNING']
    assert table.value.empty or set(table.value['level']) == {'WARNING'}

    _log(9001, 'rendered', level='WARNING')
    _log(9001, 'created', level='INFO')
    assert table.value['message'].tolist()[-1:] == ['rendered']
    assert 9001 in session.options

    level.value = []
    assert {'rendered', 'created'} <= set(table.value['message'])


def test_log_components_do_not_share_filters():
    first, second = log_component(), log_component()
    first_level = first.objects[0].objects[0].objects[0].objects[0]
    second_level = second.objects[0].objects[0].objects[0].objects[0]
    first_level.value = ['ERROR']
    assert second_level.value == []


def test_admin_template_navigation():
    config.admin_plugins = [('Plugin', lambda: _ui().Markdown('Plugin content'))]
    doc = Document()
    with set_curdoc(doc):
        page = admin_template(doc)
    assert isinstance(page, _ui().Page)
    menu = page.sidebar[0]
    labels = [item['label'] for item in menu.items]
    assert labels == ['Overview', 'Timeline', 'User Profiling', 'Logs', 'Plugin']

    main = page.main[0]
    assert main[0][0].object == 'Overview'
    with set_curdoc(doc):
        menu.active = (4,)
    assert main[0][0].object == 'Plugin'
    assert main[0][1].object == 'Plugin content'
    with set_curdoc(doc):
        menu.active = (0,)
    assert main[0][0].object == 'Overview'


def test_admin_template_applies_page_config():
    config.page_config = {'title': 'Acme', 'theme_config': {'palette': {'primary': {'main': '#ff0000'}}}}
    doc = Document()
    with set_curdoc(doc):
        page = admin_template(doc)
    assert page.title == 'Acme Admin'
    assert page.theme_config == {'palette': {'primary': {'main': '#ff0000'}}}
    assert page.header == []


def test_admin_template_logout_button(admin_password):
    doc = Document()
    with set_curdoc(doc):
        page = admin_template(doc)
    assert page.header[-1].icon == 'logout'


#---------------------------------------------------------------------
# Admin access
#---------------------------------------------------------------------

def test_admin_token_roundtrip(admin_password):
    assert validate_admin_token(create_admin_token())
    assert not validate_admin_token(None)
    assert not validate_admin_token('garbage')
    assert not validate_admin_token(create_admin_token(now=time.time() - 2 * 86400))


def test_admin_token_invalidated_by_password_change(admin_password):
    token = create_admin_token()
    config.admin_password = 'other'
    assert not validate_admin_token(token)


def test_admin_token_invalidated_by_cookie_secret_change(admin_password):
    config.cookie_secret = 'first'
    token = create_admin_token()
    config.cookie_secret = 'second'
    assert not validate_admin_token(token)


def test_validate_admin_password(admin_password):
    assert validate_admin_password(PASSWORD)
    assert not validate_admin_password('wrong')
    config.admin_password = None
    assert not validate_admin_password('')


def test_check_admin_access_unprotected():
    assert check_admin_access(None, None).allowed


def test_check_admin_access_password(admin_password):
    access = check_admin_access(None, None)
    assert not access.allowed and access.login
    assert check_admin_access(None, create_admin_token()).allowed


def test_check_admin_access_users():
    config.admin_users = ['alice']
    assert check_admin_access('alice', None).allowed
    access = check_admin_access('bob', None)
    assert not access.allowed and not access.login
    assert "'bob'" in access.error


def test_check_admin_access_users_and_password(admin_password):
    config.admin_users = ['alice']
    assert not check_admin_access('bob', create_admin_token()).allowed
    assert check_admin_access('alice', None).login
    assert check_admin_access('alice', create_admin_token()).allowed


def test_admin_users_env_var(monkeypatch):
    monkeypatch.setenv('PANEL_ADMIN_USERS', 'alice, bob,')
    assert config.admin_users == ['alice', 'bob']


@pytest.mark.parametrize(('path', 'expected'), [
    ('/admin', 'admin/login'),
    ('/admin/', 'login'),
    ('/prefix/admin', 'admin/login'),
])
def test_relative_endpoint(path, expected):
    assert relative_endpoint(path, 'login') == expected


@pytest.mark.parametrize(('path', 'expected'), [
    ('/admin/login', '../admin'),
    ('/prefix/admin/login', '../admin'),
])
def test_admin_document_url(path, expected):
    assert admin_document_url(path) == expected


def test_admin_cookie():
    cookie = admin_cookie('token', secure=True)
    assert cookie.startswith(f'{ADMIN_COOKIE}=token')
    assert 'HttpOnly' in cookie and 'Secure' in cookie and 'SameSite=Lax' in cookie
    assert 'Path' not in cookie
    assert 'Max-Age=0' in admin_cookie(None)


#---------------------------------------------------------------------
# ASGI
#---------------------------------------------------------------------

@pytest.fixture
def admin_client():
    pytest.importorskip('httpx')
    from starlette.testclient import TestClient

    from panel.io.asgi import build_asgi_app
    from panel.pane import Markdown

    apps = []

    def create(**kwargs):
        asgi = build_asgi_app({'/app': lambda: Markdown('# App')}, admin=True, **kwargs)
        apps.append(asgi)
        return TestClient(asgi)

    yield create
    for asgi in apps:
        state._server_config.pop(asgi, None)


def _token(client, path):
    r = client.get(path)
    assert r.status_code == 200
    return r.text.split('"token":')[1].split('"')[1]


def test_asgi_admin_unprotected(admin_client):
    with admin_client() as client:
        assert client.get('/admin').status_code == 200
        assert client.get('/admin/login').status_code == 404


def test_asgi_admin_password_login(admin_client, admin_password):
    with admin_client() as client:
        r = client.get('/admin', follow_redirects=False)
        assert r.status_code == 302
        assert r.headers['location'] == 'admin/login'
        assert client.get('/app').status_code == 200

        r = client.get('/admin/login')
        assert r.status_code == 200
        assert 'name="password"' in r.text

        r = client.post('/admin/login', data={'password': 'wrong'}, follow_redirects=False)
        assert r.status_code == 401
        assert 'Invalid password' in r.text

        r = client.post('/admin/login', data={'password': PASSWORD}, follow_redirects=False)
        assert r.status_code == 302
        assert r.headers['location'] == '../admin'
        assert client.get('/admin').status_code == 200

        r = client.get('/admin/logout', follow_redirects=False)
        assert r.status_code == 302
        assert client.get('/admin', follow_redirects=False).status_code == 302


def test_asgi_admin_autoload_requires_password(admin_client, admin_password):
    with admin_client() as client:
        r = client.get('/admin/autoload.js?bokeh-autoload-element=el')
        assert r.status_code == 403


def test_asgi_admin_websocket_requires_password(admin_client, admin_password):
    from starlette.websockets import WebSocketDisconnect

    with admin_client() as client:
        client.post('/admin/login', data={'password': PASSWORD}, follow_redirects=False)
        token = _token(client, '/admin')
        with client.websocket_connect('/admin/ws', subprotocols=['bokeh', token]) as ws:
            assert 'ACK' in ws.receive_text()
        client.cookies.clear()
        with pytest.raises(WebSocketDisconnect) as excinfo:
            with client.websocket_connect('/admin/ws', subprotocols=['bokeh', token]):
                pass
    assert excinfo.value.code == 1008


def test_asgi_admin_users(admin_client):
    config.admin_users = ['alice']
    with admin_client(basic_auth={'alice': 'pw', 'bob': 'pw'}, cookie_secret='secret') as client:
        client.post('/login', data={'username': 'bob', 'password': 'pw'}, follow_redirects=False)
        assert client.get('/app').status_code == 200
        r = client.get('/admin')
        assert r.status_code == 403
        assert 'not authorized to access the admin panel' in r.text

        client.cookies.clear()
        client.post('/login', data={'username': 'alice', 'password': 'pw'}, follow_redirects=False)
        assert client.get('/admin').status_code == 200


#---------------------------------------------------------------------
# Tornado
#---------------------------------------------------------------------

def test_tornado_admin_password_login(admin_password):
    import requests

    from panel.pane import Markdown

    port = serve_and_wait({'app': Markdown('# App')}, admin=True)
    base = f'http://127.0.0.1:{port}'
    session = requests.Session()

    r = session.get(f'{base}/admin', allow_redirects=False, timeout=30)
    assert r.status_code == 302
    assert r.headers['location'] == 'admin/login'
    assert session.get(f'{base}/app', timeout=30).status_code == 200

    r = session.get(
        f'{base}/admin/ws', timeout=30, headers={
            'Connection': 'Upgrade', 'Upgrade': 'websocket', 'Sec-WebSocket-Version': '13',
            'Sec-WebSocket-Key': 'dGhlIHNhbXBsZSBub25jZQ==',
        }
    )
    assert r.status_code == 403
    r = session.get(f'{base}/admin/autoload.js?bokeh-autoload-element=el', timeout=30)
    assert r.status_code == 403

    r = session.post(f'{base}/admin/login', data={'password': 'wrong'}, timeout=30)
    assert r.status_code == 401

    r = session.post(
        f'{base}/admin/login', data={'password': PASSWORD}, allow_redirects=False, timeout=30
    )
    assert r.status_code == 302
    assert r.headers['location'] == '../admin'
    assert ADMIN_COOKIE in session.cookies
    r = session.get(f'{base}/admin', allow_redirects=False, timeout=30)
    assert r.status_code == 200

    session.get(f'{base}/admin/logout', timeout=30)
    r = session.get(f'{base}/admin', allow_redirects=False, timeout=30)
    assert r.status_code == 302
