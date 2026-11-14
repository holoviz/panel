from types import SimpleNamespace

import pytest

from tornado.httputil import HTTPHeaders
from tornado.web import HTTPError

from panel.auth import OAuthLoginHandler, _default_next_url, _validate_next_url
from panel.config import config
from panel.io.proxy import (
    external_path, external_url, forwarded_host, forwarded_prefix,
    login_redirect_url, relative_url, root_path,
)
from panel.io.state import state
from panel.util import edit_readonly


def make_handler(
    uri='/app', headers=None, use_xheaders=False, prefix='', request_root=None,
    host='internal:5006', protocol='http'
):
    request = SimpleNamespace(
        uri=uri, path=uri.split('?')[0], host=host, protocol=protocol,
        headers=HTTPHeaders(headers or {}),
    )
    if request_root is not None:
        request.root_path = request_root
    application = SimpleNamespace(prefix=prefix, use_xheaders=use_xheaders)
    return SimpleNamespace(request=request, application=application)


@pytest.fixture
def set_root_path():
    def set_base_url(value):
        with edit_readonly(state):
            state.base_url = value
    yield set_base_url
    set_base_url('/')


PROXY_HEADERS = {
    'X-Forwarded-Prefix': '/proxy', 'X-Forwarded-Host': 'example.org',
}


@pytest.mark.parametrize('value, expected', [
    ('/proxy', '/proxy'),
    ('/proxy/', '/proxy'),
    ('/a/b-c/d_e', '/a/b-c/d_e'),
    ('/outer, /inner', '/outer'),
    ('/', ''),
    ('', ''),
    ('proxy', ''),
    ('//evil.org', ''),
    ('/a//b', ''),
    ('/\\evil.org', ''),
    ('https://evil.org/a', ''),
    ('/a/../b', ''),
    ('/a?next=b', ''),
    ('/a#b', ''),
    ('/a b', ''),
    ('/a\r\nSet-Cookie: x', ''),
])
def test_forwarded_prefix(value, expected):
    assert forwarded_prefix({'X-Forwarded-Prefix': value}) == expected


def test_forwarded_prefix_from_script_name():
    assert forwarded_prefix({'X-Script-Name': '/proxy'}) == '/proxy'
    assert forwarded_prefix({'x-forwarded-prefix': '/a', 'X-Script-Name': '/b'}) == '/a'


@pytest.mark.parametrize('value, expected', [
    ('example.org', 'example.org'),
    ('example.org:8443', 'example.org:8443'),
    ('[::1]:8080', '[::1]:8080'),
    ('outer.org, inner.org', 'outer.org'),
    ('', None),
    ('evil.org/path', None),
    ('user@evil.org', None),
    ('evil.org\r\nX: y', None),
    ('evil .org', None),
])
def test_forwarded_host(value, expected):
    assert forwarded_host({'X-Forwarded-Host': value}) == expected


@pytest.mark.parametrize('path, target, expected', [
    ('/', '/login', './login'),
    ('/app', '/login', './login'),
    ('/app/', '/login', '../login'),
    ('/nested/app', '/login', '../login'),
    ('/prefix', '/prefix/login', './prefix/login'),
    ('/prefix/', '/prefix/login', './login'),
    ('/prefix/app', '/prefix/login', './login'),
    ('/prefix/nested/app', '/prefix/login', '../login'),
])
def test_relative_url(path, target, expected):
    assert relative_url(path, target) == expected


def test_proxy_headers_are_ignored_without_xheaders():
    handler = make_handler(headers=PROXY_HEADERS)
    assert root_path(handler) == ''
    assert external_url(handler) == 'http://internal:5006'
    assert login_redirect_url(handler, '/login') == './login'


def test_proxy_headers_are_trusted_with_xheaders():
    handler = make_handler(headers=PROXY_HEADERS, use_xheaders=True, protocol='https')
    assert root_path(handler) == '/proxy'
    assert external_url(handler) == 'https://example.org/proxy'
    assert login_redirect_url(handler, '/login') == '/proxy/login?next=%2Fproxy%2Fapp'


def test_invalid_proxy_headers_fall_back_to_request():
    headers = {'X-Forwarded-Prefix': '//evil.org', 'X-Forwarded-Host': 'evil.org/a'}
    handler = make_handler(headers=headers, use_xheaders=True)
    assert external_url(handler) == 'http://internal:5006'
    assert login_redirect_url(handler, '/login') == './login'


def test_configured_root_path_wins_over_proxy_headers(set_root_path):
    set_root_path('/configured/')
    handler = make_handler(headers=PROXY_HEADERS, use_xheaders=True)
    assert root_path(handler) == '/configured'
    assert external_url(handler) == 'http://example.org/configured'


def test_root_path_and_prefix_are_combined(set_root_path):
    set_root_path('/proxy/')
    handler = make_handler(uri='/prefix/app?a=1', prefix='/prefix')
    assert external_url(handler) == 'http://internal:5006/proxy/prefix'
    assert login_redirect_url(handler, '/login') == (
        '/proxy/prefix/login?next=%2Fproxy%2Fprefix%2Fapp%3Fa%3D1'
    )
    assert _default_next_url(handler) == '/proxy/prefix/'


def test_login_redirect_url_with_prefix_only():
    assert login_redirect_url(make_handler('/prefix', prefix='/prefix'), '/login') == './prefix/login'
    assert login_redirect_url(make_handler('/prefix/a/b', prefix='/prefix'), '/login') == '../login'


def test_login_redirect_url_keeps_external_login_url():
    handler = make_handler(headers=PROXY_HEADERS, use_xheaders=True)
    assert login_redirect_url(handler, 'https://sso.example.org/login') == 'https://sso.example.org/login'


def test_asgi_root_path_is_not_applied_twice():
    handler = make_handler('/proxy/app', request_root='/proxy')
    assert external_path(handler, '/proxy/app') == '/proxy/app'
    assert external_path(handler, '/proxy?code=1') == '/proxy?code=1'
    assert external_path(handler, '/proxyapp') == '/proxy/proxyapp'
    assert login_redirect_url(handler, '/login') == '/proxy/login?next=%2Fproxy%2Fapp'


@pytest.mark.parametrize('next_url', [
    'https://evil.org', '//evil.org', '///evil.org', '/\\evil.org', ' //evil.org',
])
def test_validate_next_url_rejects_other_origins(next_url):
    handler = make_handler(headers=PROXY_HEADERS, use_xheaders=True)
    with pytest.raises(HTTPError):
        _validate_next_url(next_url, handler)


def test_validate_next_url_applies_root_path(set_root_path):
    handler = make_handler(headers=PROXY_HEADERS, use_xheaders=True)
    assert _validate_next_url('/app', handler) == '/proxy/app'
    assert _validate_next_url('/proxy/app', handler) == '/proxy/app'
    assert _validate_next_url('/app', make_handler(headers=PROXY_HEADERS)) == '/app'
    set_root_path('/proxy/')
    assert _validate_next_url('/app') == '/proxy/app'
    assert _validate_next_url('/proxy') == '/proxy'


def _login_handler(**kwargs):
    handler = make_handler(**kwargs)
    return SimpleNamespace(
        request=handler.request, application=handler.application,
        redirect_uri=lambda: OAuthLoginHandler._redirect_uri.fget(handler)
    )


@pytest.mark.parametrize('kwargs, expected', [
    ({}, 'http://internal:5006'),
    ({'prefix': '/prefix'}, 'http://internal:5006/prefix'),
    ({'headers': PROXY_HEADERS}, 'http://internal:5006'),
    ({'headers': PROXY_HEADERS, 'use_xheaders': True}, 'http://example.org/proxy'),
    (
        {'headers': PROXY_HEADERS, 'use_xheaders': True, 'prefix': '/prefix', 'protocol': 'https'},
        'https://example.org/proxy/prefix'
    ),
    ({'request_root': '/proxy'}, 'http://internal:5006/proxy'),
])
def test_oauth_redirect_uri(kwargs, expected):
    assert _login_handler(**kwargs).redirect_uri() == expected


def test_oauth_redirect_uri_override():
    with config.set(oauth_redirect_uri='https://example.org/custom/login'):
        handler = _login_handler(headers=PROXY_HEADERS, use_xheaders=True)
        assert handler.redirect_uri() == 'https://example.org/custom/login'
