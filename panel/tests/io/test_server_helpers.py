"""
Tests for the transport neutral helpers in ``panel.io.server`` which the
Tornado handlers and ``panel.io.asgi`` share, so that both transports
behave identically.
"""
import re

from http.cookies import SimpleCookie

import pytest

from bokeh.document import Document

from panel.config import config
from panel.io.server import (
    _sanitize_route_context, authorize_request, compile_route_template,
    index_page_items, index_redirect, is_concrete_route, render_auth_error,
    resolve_session, token_payload_for_request, validate_static_dirs,
)
from panel.io.state import set_curdoc, state

#---------------------------------------------------------------------
# Authorization
#---------------------------------------------------------------------

@pytest.fixture
def authorize_callback():
    def set_callback(callback, doc=None):
        if doc is None:
            config.authorize_callback = callback
        else:
            with set_curdoc(doc):
                config.authorize_callback = callback
    try:
        yield set_callback
    finally:
        config.authorize_callback = None


def test_authorize_request_without_callback():
    assert authorize_request('/app') == (True, None, None)


def test_authorize_request_one_argument(authorize_callback):
    seen = []
    authorize_callback(lambda user_info: seen.append(user_info) or True)
    result = authorize_request('/app')
    assert result == (True, None, None)
    assert seen == [state.user_info]


def test_authorize_request_two_arguments(authorize_callback):
    seen = []
    authorize_callback(lambda user_info, path: seen.append(path) or True)
    assert authorize_request('/app').authorized
    assert seen == ['/app']


def test_authorize_request_denied_reports_path(authorize_callback):
    authorize_callback(lambda user_info, path: False)
    authorized, error, redirect = authorize_request('/app')
    assert authorized is False
    assert redirect is None
    assert "'/app'" in error


def test_authorize_request_redirect(authorize_callback):
    authorize_callback(lambda user_info: '/login')
    # A string return value is a redirect target, not an authorization
    assert authorize_request('/app') == (None, None, '/login')


def test_authorize_request_error_is_not_authorized(authorize_callback):
    def failing(user_info):
        raise ValueError('boom')
    authorize_callback(failing)
    authorized, error, _ = authorize_request('/app')
    assert authorized is False
    assert 'errored' in error


def test_authorize_request_invalid_signature(authorize_callback):
    authorize_callback(lambda user_info, path, extra: True)
    with pytest.raises(RuntimeError, match='must accept either'):
        authorize_request('/app')


def test_authorize_request_skips_global_callback_in_session(authorize_callback):
    calls = []
    authorize_callback(lambda user_info: calls.append(user_info) or False)

    # A globally configured callback already ran for the HTTP request, so
    # it must not run again for the session.
    assert authorize_request('/app', session=True) == (True, None, None)
    assert calls == []
    assert not authorize_request('/app').authorized
    assert len(calls) == 1


def test_authorize_request_applies_session_callback(authorize_callback):
    doc = Document()
    authorize_callback(lambda user_info: False, doc=doc)
    with set_curdoc(doc):
        assert not authorize_request('/app', session=True).authorized
    # The callback is scoped to the session that declared it
    assert authorize_request('/app', session=True) == (True, None, None)


def test_render_auth_error_sanitizes_message():
    page = render_auth_error('<script>alert("xss")</script> denied')
    assert '<script>alert' not in page
    assert 'denied' in page


#---------------------------------------------------------------------
# Token payload
#---------------------------------------------------------------------

class _FilterConfig:
    def __init__(
        self, include_headers=None, exclude_headers=None, include_cookies=None,
        exclude_cookies=None
    ):
        self.include_headers = include_headers
        self.exclude_headers = exclude_headers
        self.include_cookies = include_cookies
        self.exclude_cookies = exclude_cookies


class _Request:
    def __init__(self, headers=None, cookies=None, arguments=None, path='/app'):
        self.headers = headers or {}
        self.cookies = cookies if cookies is not None else {}
        self.arguments = arguments
        self.path = path


def test_token_payload_excludes_headers_and_cookies():
    request = _Request(
        headers={'Cookie': 'user=alice; session=xyz', 'X-Custom': '1', 'X-Secret': '2'},
        cookies=SimpleCookie('user=alice; session=xyz'),
        arguments={'theme': [b'dark']}
    )
    payload = token_payload_for_request(
        _FilterConfig(exclude_headers=['X-Secret'], exclude_cookies=['session']), request
    )
    # The Cookie header is dropped since the cookies are carried separately
    assert payload['headers'] == {'X-Custom': '1'}
    assert payload['cookies'] == {'user': 'alice'}
    assert payload['arguments'] == {'theme': [b'dark']}


def test_token_payload_includes_headers_and_cookies():
    request = _Request(
        headers={'Cookie': 'user=alice', 'X-Custom': '1', 'X-Secret': '2'},
        cookies=SimpleCookie('user=alice; session=xyz'),
    )
    payload = token_payload_for_request(
        _FilterConfig(include_headers=['X-Secret', 'Cookie'], include_cookies=['session']),
        request
    )
    # An explicitly included Cookie header is retained
    assert payload['headers'] == {'Cookie': 'user=alice', 'X-Secret': '2'}
    assert payload['cookies'] == {'session': 'xyz'}
    assert payload['arguments'] == {}


#---------------------------------------------------------------------
# Session resolution
#---------------------------------------------------------------------

class _Session:
    def __init__(self):
        self.document = Document()
        self.expiration_blocked = False

    def block_expiration(self):
        self.expiration_blocked = True


@pytest.fixture
def sessions():
    created = []

    async def create():
        created.append(_Session())
        return created[-1]

    try:
        yield created, create
    finally:
        config.reuse_sessions = False
        config.session_key_func = None
        state._sessions.clear()
        state._session_key_funcs.clear()


@pytest.mark.asyncio
async def test_resolve_session_creates_a_session_per_request(sessions):
    created, create = sessions
    request = _Request(arguments={})

    first = await resolve_session(request, create)
    second = await resolve_session(request, create)

    assert first is created[0]
    assert second is created[1]
    assert not first.expiration_blocked
    assert not state._sessions


@pytest.mark.asyncio
async def test_resolve_session_reuses_session(sessions):
    created, create = sessions
    config.reuse_sessions = True
    request = _Request(arguments={})

    first = await resolve_session(request, create)
    second = await resolve_session(request, create)

    assert len(created) == 1
    assert second is first
    # A reused session must not expire while it is being handed out
    assert first.expiration_blocked
    assert state._session_key_funcs['/app'](request) == ('/app', 'default')


@pytest.mark.asyncio
async def test_resolve_session_reuse_is_keyed_by_theme(sessions):
    created, create = sessions
    config.reuse_sessions = True

    default = await resolve_session(_Request(arguments={}), create)
    dark = await resolve_session(_Request(arguments={'theme': [b'dark']}), create)

    assert len(created) == 2
    assert dark is not default


@pytest.mark.asyncio
async def test_resolve_session_reuse_honors_session_key_func(sessions):
    created, create = sessions
    config.reuse_sessions = True
    config.session_key_func = lambda request: request.arguments.get('user')

    first = await resolve_session(_Request(arguments={'user': 'alice'}), create)
    second = await resolve_session(_Request(arguments={'user': 'alice'}), create)
    other = await resolve_session(_Request(arguments={'user': 'bob'}), create)

    assert second is first
    assert other is not first
    assert len(created) == 2


@pytest.mark.asyncio
async def test_resolve_session_path_overrides_request_path(sessions):
    created, create = sessions
    config.reuse_sessions = True

    # Wildcard routes are keyed by the application path, not the request
    # path, so that every request resolves to the same key.
    await resolve_session(_Request(arguments={}, path='/user/alice'), create, path='/user/{name}')
    assert list(state._session_key_funcs) == ['/user/{name}']


#---------------------------------------------------------------------
# Routing
#---------------------------------------------------------------------

def test_compile_route_template_literal():
    assert compile_route_template('/') == ('/', ())
    pattern, params = compile_route_template('/app')
    assert params == ()
    assert re.fullmatch(pattern, '/app')


def test_compile_route_template_parameters():
    pattern, params = compile_route_template('/user/{name}/detail')
    assert params == ('name',)
    match = re.fullmatch(pattern, '/user/alice/detail')
    assert match.groupdict() == {'name': 'alice'}
    # The literal segments are escaped, so only the declared route matches
    assert re.fullmatch(pattern, '/user/alice/other') is None
    assert re.fullmatch(pattern, '/user/alice/extra/detail') is None


def test_compile_route_template_converters():
    pattern, params = compile_route_template('/files/{path:path}')
    assert params == ('path',)
    assert re.fullmatch(pattern, '/files/nested/file.txt')

    pattern, _ = compile_route_template('/item/{id:int}')
    assert re.fullmatch(pattern, '/item/12')
    assert re.fullmatch(pattern, '/item/abc') is None


def test_compile_route_template_invalid():
    with pytest.raises(ValueError, match='Invalid path template segment'):
        compile_route_template('/user/{name')
    with pytest.raises(ValueError, match='Invalid path template segment'):
        compile_route_template('/user/{name:bogus}')


def test_is_concrete_route():
    assert is_concrete_route('/app')
    assert not is_concrete_route('/user/{name}')
    assert not is_concrete_route(r'/user/(?P<name>\w+)')


def test_index_redirect():
    assert index_redirect(['/app'], True) == './app'
    assert index_redirect({'/app': None}, True) == './app'
    assert index_redirect(['/app'], False) is None
    assert index_redirect(['/app1', '/app2'], True) is None
    # A single wildcard route has no concrete URL to redirect to
    assert index_redirect(['/user/{name}'], True) is None


def test_index_page_items_default_template():
    assert index_page_items(['/b', '/a'], '') == ['/a', '/b']


def test_index_page_items_custom_template():
    items = index_page_items(['/b', '/a'], '', index='index.html')
    assert items == [('/a', 'a'), ('/b', 'b')]


def test_index_page_items_applies_prefix():
    # Without a trailing slash on the URI the links have to carry the prefix
    assert index_page_items(['/app'], '/prefix', index='index.html', uri='/prefix') == [
        ('/prefix/app', 'app')
    ]
    assert index_page_items(['/app'], '/prefix', index='index.html', uri='/prefix/') == [
        ('/app', 'app')
    ]


def test_index_page_items_applies_index_titles():
    config.index_titles = {'/a': 'Zulu', '/b': 'Alpha'}
    try:
        items = index_page_items(['/a', '/b'], '', index='index.html')
    finally:
        config.index_titles = {}
    # Sorted by title rather than slug
    assert items == [('/b', 'Alpha'), ('/a', 'Zulu')]


def test_sanitize_route_context_truncates():
    params, app_path = _sanitize_route_context(
        {'name': 'a' * 2000, 'k' * 200: 'v'}, '/app'
    )
    assert len(params['name']) == 1024
    assert len(list(params)[1]) == 128
    assert app_path == '/app'


def test_sanitize_route_context_caps_parameters():
    params, app_path = _sanitize_route_context({str(i): i for i in range(64)}, None)
    assert len(params) == 32
    assert params['0'] == '0'
    assert app_path is None


#---------------------------------------------------------------------
# Static directories
#---------------------------------------------------------------------

def test_validate_static_dirs(tmp_path):
    static = validate_static_dirs({'assets': str(tmp_path)})
    assert static == {'/assets': str(tmp_path)}


def test_validate_static_dirs_reserved_slug(tmp_path):
    with pytest.raises(ValueError, match='reserved for internal use'):
        validate_static_dirs({'static': str(tmp_path)})


def test_validate_static_dirs_missing_path(tmp_path):
    with pytest.raises(ValueError, match='non-existent path'):
        validate_static_dirs({'assets': str(tmp_path / 'nope')})
