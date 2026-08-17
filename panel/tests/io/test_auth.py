"""
Tests for authentication on ASGI transports, i.e. Panel's Tornado auth
handlers run headlessly by panel.io.auth.PanelAuthPolicy.
"""
import datetime as dt

from urllib.parse import parse_qs, urlparse

import pytest

pytest.importorskip("httpx")

import requests

from starlette.testclient import TestClient
from tornado.web import create_signed_value, decode_signed_value

from panel.auth import AUTH_PROVIDERS, OAuthLoginHandler, OAuthProvider
from panel.config import config
from panel.io.asgi import build_asgi_app
from panel.io.state import state
from panel.pane import Markdown
from panel.tests.util import serve_and_wait

COOKIE_SECRET = 'cookie-secret'
PASSWORD = 'secret-password'

# The config values configure_auth applies, all of which are global and
# therefore have to be restored between tests.
AUTH_CONFIG = (
    '_basic_auth', '_cookie_path', '_cookie_secret', '_oauth_encryption_key',
    '_oauth_expiry', '_oauth_extra_params', '_oauth_guest_endpoints',
    '_oauth_jwt_user', '_oauth_key', '_oauth_optional', '_oauth_provider',
    '_oauth_redirect_uri', '_oauth_refresh_tokens', '_oauth_secret',
)


@pytest.fixture(autouse=True)
def auth_config_cleanup():
    values = {name: getattr(config, name) for name in AUTH_CONFIG}
    try:
        yield
    finally:
        config.param.update(**values)
        state.encryption = None


@pytest.fixture
def auth_apps():
    apps = []

    def create(panel=None, **kwargs):
        kwargs.setdefault('cookie_secret', COOKIE_SECRET)
        asgi = build_asgi_app(panel or {'/app': lambda: Markdown('# Test app')}, **kwargs)
        apps.append(asgi)
        return asgi

    yield create
    for asgi in apps:
        state._server_config.pop(asgi, None)


@pytest.fixture
def basic_auth_client(auth_apps):
    def create(panel=None, **kwargs):
        kwargs.setdefault('basic_auth', PASSWORD)
        return TestClient(auth_apps(panel, **kwargs))
    return create


def login(client, username='user', password=PASSWORD, endpoint='/login', next=None):
    if next is not None:
        # The destination is recorded in a cookie by the login page, which is
        # what the form submission redirects to.
        client.get(f'{endpoint}?next={next}', follow_redirects=False)
    return client.post(
        endpoint, data={'username': username, 'password': password},
        follow_redirects=False
    )


#---------------------------------------------------------------------
# Basic auth
#---------------------------------------------------------------------

def test_no_auth_does_not_serve_login(auth_apps):
    with TestClient(auth_apps()) as client:
        assert client.get('/app').status_code == 200
        assert client.get('/login').status_code == 404


def test_unauthenticated_document_redirects_to_login(basic_auth_client):
    with basic_auth_client() as client:
        r = client.get('/app', follow_redirects=False)
    assert r.status_code == 302
    assert r.headers['location'] == '/login?next=%2Fapp'


def test_unauthenticated_endpoints_redirect_to_login(basic_auth_client, tmp_path):
    (tmp_path / 'file.txt').write_text('static content')
    with basic_auth_client(static_dirs={'assets': str(tmp_path)}) as client:
        for path in ('/', '/app/metadata', '/app/autoload.js', '/assets/file.txt'):
            r = client.get(path, follow_redirects=False)
            assert r.status_code == 302, path
            assert r.headers['location'].startswith('/login?next='), path


def test_unauthenticated_document_under_prefix_redirects_below_prefix(basic_auth_client):
    with basic_auth_client(prefix='/prefix') as client:
        r = client.get('/prefix/app', follow_redirects=False)
    assert r.status_code == 302
    assert r.headers['location'] == '/prefix/login?next=%2Fprefix%2Fapp'


def test_unauthenticated_document_under_root_path_redirects_below_root_path(auth_apps):
    asgi = auth_apps(basic_auth=PASSWORD)
    with TestClient(asgi, root_path='/mounted') as client:
        r = client.get('/mounted/app', follow_redirects=False)
    assert r.status_code == 302
    assert r.headers['location'] == '/mounted/login?next=%2Fmounted%2Fapp'


def test_basic_auth_login_page(basic_auth_client):
    with basic_auth_client() as client:
        r = client.get('/login?next=%2Fapp')
    assert r.status_code == 200
    assert r.headers['content-type'].startswith('text/html')
    assert 'name="username"' in r.text
    # The login page records where to return to after authenticating
    assert client.cookies['next_url'].strip('"') == '/app'


def test_basic_auth_login_and_logout(basic_auth_client):
    with basic_auth_client() as client:
        r = login(client, next='%2Fapp')
        assert r.status_code == 302
        assert r.headers['location'] == '/app'
        assert 'user' in r.cookies

        assert client.get('/app').status_code == 200

        r = client.get('/logout', follow_redirects=False)
        assert r.status_code == 200
        assert 'user=""' in ''.join(r.headers.get_list('set-cookie'))

        r = client.get('/app', follow_redirects=False)
        assert r.status_code == 302


def test_basic_auth_invalid_credentials(basic_auth_client):
    with basic_auth_client() as client:
        r = login(client, password='wrong')
        assert r.status_code == 302
        assert 'error=Invalid' in r.headers['location']
        assert 'user' not in r.cookies


def test_basic_auth_custom_endpoints(basic_auth_client):
    with basic_auth_client(login_endpoint='/signin', logout_endpoint='/signout') as client:
        r = client.get('/app', follow_redirects=False)
        assert r.headers['location'] == '/signin?next=%2Fapp'
        assert client.get('/signin').status_code == 200
        assert client.get('/login').status_code == 404
        assert login(client, endpoint='/signin').status_code == 302
        assert client.get('/app').status_code == 200
        assert client.get('/signout').status_code == 200


def test_auth_routes_are_handled(auth_apps):
    asgi = auth_apps(basic_auth=PASSWORD, prefix='/prefix')

    def scope(path):
        return {'type': 'http', 'path': path, 'root_path': '', 'method': 'GET'}

    assert asgi.handles(scope('/prefix/login'))
    assert asgi.handles(scope('/prefix/logout'))
    assert not asgi.handles(scope('/login'))


def test_authenticated_user_is_available_on_state(basic_auth_client):
    users = []

    def app():
        users.append(state.user)
        return Markdown('# Test app')

    with basic_auth_client({'/app': app}) as client:
        login(client, username='alice')
        assert client.get('/app').status_code == 200
    assert users == ['alice']


#---------------------------------------------------------------------
# FastAPI
#---------------------------------------------------------------------

def test_fastapi_serves_auth_endpoints():
    fastapi = pytest.importorskip('fastapi')

    from panel.io.fastapi import add_applications

    app = fastapi.FastAPI()

    @app.get('/api')
    def api():
        return {'ok': True}

    panel_app = add_applications(
        {'/app': lambda: Markdown('# Test app')}, app=app,
        basic_auth=PASSWORD, cookie_secret=COOKIE_SECRET
    )
    try:
        with TestClient(app) as client:
            # Routes declared on the FastAPI app are never authenticated
            assert client.get('/api').status_code == 200
            r = client.get('/app', follow_redirects=False)
            assert r.status_code == 302
            assert r.headers['location'] == '/login?next=%2Fapp'
            login(client, next='%2Fapp')
            assert client.get('/app').status_code == 200
    finally:
        state._server_config.pop(panel_app.asgi, None)


#---------------------------------------------------------------------
# Websockets
#---------------------------------------------------------------------

def _token(client, path='/app'):
    """
    Extracts the session token the document page embeds.
    """
    from bokeh.util.token import get_session_id

    r = client.get(path)
    assert r.status_code == 200
    token = r.text.split('"token":')[1].split('"')[1]
    get_session_id(token)
    return token


def test_unauthenticated_websocket_is_rejected(basic_auth_client):
    from starlette.websockets import WebSocketDisconnect

    with basic_auth_client() as client:
        login(client)
        token = _token(client)
        client.cookies.clear()
        with pytest.raises(WebSocketDisconnect) as excinfo:
            with client.websocket_connect('/app/ws', subprotocols=['bokeh', token]):
                pass
    # A websocket upgrade cannot be redirected to a login page
    assert excinfo.value.code == 1008


def test_authenticated_websocket_connects(basic_auth_client):
    with basic_auth_client() as client:
        login(client)
        token = _token(client)
        with client.websocket_connect('/app/ws', subprotocols=['bokeh', token]) as ws:
            assert 'ACK' in ws.receive_text()


#---------------------------------------------------------------------
# Cookie interoperability
#---------------------------------------------------------------------

def test_asgi_cookie_is_a_tornado_signed_value(basic_auth_client):
    with basic_auth_client() as client:
        login(client, username='alice')
        cookie = client.cookies['user']
    user = decode_signed_value(COOKIE_SECRET, 'user', cookie.strip('"'))
    assert user == b'alice'


def test_asgi_accepts_tornado_signed_cookie(basic_auth_client):
    cookie = create_signed_value(COOKIE_SECRET, 'user', 'alice').decode()
    with basic_auth_client() as client:
        client.cookies.set('user', cookie)
        assert client.get('/app').status_code == 200


def test_tornado_and_asgi_sessions_interoperate(basic_auth_client, port):
    """
    A user authenticated against the Tornado server must be accepted by an
    ASGI server sharing the cookie secret, and vice versa.
    """
    serve_and_wait(
        {'/app': Markdown('# Test app')}, port=port, basic_auth=PASSWORD,
        cookie_secret=COOKIE_SECRET
    )
    tornado_session = requests.Session()
    r = tornado_session.post(
        f'http://localhost:{port}/login',
        data={'username': 'alice', 'password': PASSWORD}
    )
    assert r.status_code == 200
    assert 'user' in tornado_session.cookies

    with basic_auth_client() as client:
        client.cookies.set('user', tornado_session.cookies['user'])
        assert client.get('/app').status_code == 200
        client.cookies.clear()
        login(client, username='alice')
        asgi_cookie = client.cookies['user']

    r = requests.get(
        f'http://localhost:{port}/app', cookies={'user': asgi_cookie},
        allow_redirects=False
    )
    assert r.status_code == 200


#---------------------------------------------------------------------
# Guest access
#---------------------------------------------------------------------

def test_guest_endpoints_allow_unauthenticated_access(basic_auth_client):
    users = []

    def app():
        users.append(state.user)
        return Markdown('# Test app')

    apps = {'/app': app, '/private': lambda: Markdown('# Private')}
    with basic_auth_client(apps, oauth_guest_endpoints=['/app']) as client:
        r = client.get('/app')
        assert r.status_code == 200
        assert 'is_guest=1' in ''.join(r.headers.get_list('set-cookie'))
        assert client.get('/private', follow_redirects=False).status_code == 302
    assert users == ['guest']


def test_oauth_optional_allows_unauthenticated_access(basic_auth_client):
    with basic_auth_client(oauth_optional=True) as client:
        assert client.get('/app').status_code == 200


#---------------------------------------------------------------------
# OAuth
#---------------------------------------------------------------------

OAUTH_USER = 'alice@example.com'


class StubLoginHandler(OAuthLoginHandler):
    """
    Stands in for a real OAuth provider, replacing only the token endpoint
    request so that the authorization redirect, the state and PKCE cookies
    and the callback handling are all exercised as they are in production.
    """

    _OAUTH_AUTHORIZE_URL = 'https://auth.example.com/authorize'
    _OAUTH_ACCESS_TOKEN_URL = 'https://auth.example.com/token'
    _OAUTH_LOGOUT_URL = ''
    _USER_KEY = 'email'

    async def _fetch_access_token(
        self, client_id, redirect_uri=None, client_secret=None, code=None,
        refresh_token=None, username=None, password=None, user=None
    ):
        if refresh_token:
            return user, 'refreshed-access-token', 'refreshed-refresh-token', 3600
        user = OAuthLoginHandler.set_auth_cookies(
            self, {'email': OAUTH_USER}, 'access-token', 'refresh-token', 3600
        )
        return user, 'access-token', 'refresh-token', 3600


@pytest.fixture
def oauth_client(auth_apps):
    AUTH_PROVIDERS['stub'] = StubLoginHandler
    provider_param = config.param.objects(False)['_oauth_provider']
    provider_param.objects = list(AUTH_PROVIDERS)

    def create(panel=None, **kwargs):
        kwargs.setdefault('oauth_provider', 'stub')
        kwargs.setdefault('oauth_key', 'client-id')
        kwargs.setdefault('oauth_secret', 'client-secret')
        return TestClient(auth_apps(panel, **kwargs))

    try:
        yield create
    finally:
        del AUTH_PROVIDERS['stub']
        provider_param.objects = list(AUTH_PROVIDERS)
        state._oauth_user_overrides.clear()


def oauth_login(client, next='%2Fapp'):
    """
    Runs the authorization code flow against the stub provider and returns
    the response to the callback request.
    """
    r = client.get(f'/login?next={next}', follow_redirects=False)
    assert r.status_code == 302
    location = urlparse(r.headers['location'])
    assert f'{location.scheme}://{location.netloc}{location.path}' == (
        StubLoginHandler._OAUTH_AUTHORIZE_URL
    )
    params = parse_qs(location.query)
    assert params['client_id'] == ['client-id']
    return client.get(
        f'/login?code=authorization-code&state={params["state"][0]}',
        follow_redirects=False
    )


def test_oauth_provider_is_configured(oauth_client):
    with oauth_client() as client:
        assert isinstance(client.app._auth_policy.provider, OAuthProvider)
        assert config.oauth_provider == 'stub'
        assert client.get('/app', follow_redirects=False).headers['location'] == (
            '/login?next=%2Fapp'
        )


def test_oauth_code_flow(oauth_client):
    users = []

    def app():
        users.append(state.user)
        return Markdown('# Test app')

    with oauth_client({'/app': app}) as client:
        r = oauth_login(client)
        assert r.status_code == 302
        assert r.headers['location'] == '/app'
        assert 'user' in r.cookies
        assert 'access_token' in r.cookies
        assert client.get('/app').status_code == 200
    assert users == [OAUTH_USER]
    assert decode_signed_value(
        COOKIE_SECRET, 'user', client.cookies['user'].strip('"')
    ) == OAUTH_USER.encode()


def test_oauth_refreshes_expired_access_token(oauth_client):
    with oauth_client(oauth_refresh_tokens=True) as client:
        oauth_login(client)
        expired = dt.datetime.now(dt.timezone.utc).timestamp() - 10
        client.cookies.set(
            'oauth_expiry',
            create_signed_value(COOKIE_SECRET, 'oauth_expiry', str(expired)).decode()
        )
        assert client.get('/app').status_code == 200
        access_token = client.cookies['access_token']
    assert decode_signed_value(
        COOKIE_SECRET, 'access_token', access_token.strip('"')
    ) == b'refreshed-access-token'


def test_oauth_state_mismatch_is_rejected(oauth_client):
    with oauth_client() as client:
        client.get('/login', follow_redirects=False)
        r = client.get('/login?code=code&state=tampered', follow_redirects=False)
    assert r.status_code == 401
    assert 'user' not in r.cookies


def test_oauth_error_is_reported(oauth_client):
    with oauth_client() as client:
        r = client.get(
            '/login?error=access_denied&error_description=Nope',
            follow_redirects=False
        )
    assert r.status_code == 401
    assert 'Nope' in r.text
