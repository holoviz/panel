"""
Resolves the URL a server is reachable on from the outside when it runs
behind a reverse proxy, which request handlers need to build redirects
that lead back through the proxy.
"""
from __future__ import annotations

import logging
import re
import typing as t

from urllib.parse import urlencode

from .state import state

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from tornado.web import RequestHandler

log = logging.getLogger(__name__)

PREFIX_HEADERS = ('X-Forwarded-Prefix', 'X-Script-Name')

HOST_HEADER = 'X-Forwarded-Host'

_HOST_RE = re.compile(r'^(?:[A-Za-z0-9._-]+|\[[0-9A-Fa-f:.]+\])(?::\d{1,5})?$')

# Empty segments are excluded since browsers resolve a leading '//' as a host.
_PATH_RE = re.compile(r"^(?:/[A-Za-z0-9._~!$&'()*+,;=:@%-]+)+$")


def _header(headers: Mapping[str, str], name: str) -> str | None:
    value = headers.get(name) or headers.get(name.lower())
    # Proxies chained in front of each other append to the header
    return value.split(',')[0].strip() if value else None


def normalize_root_path(root_path: str | None) -> str:
    """
    Returns the root path with a leading and without a trailing slash,
    or an empty string if the server is served on the root.
    """
    root_path = (root_path or '').strip('/')
    return f'/{root_path}' if root_path else ''


def forwarded_prefix(headers: Mapping[str, str]) -> str:
    """
    The path prefix a proxy stripped off the request, as declared by the
    ``X-Forwarded-Prefix`` or ``X-Script-Name`` header. Values that are
    not a plain absolute path are ignored.
    """
    for name in PREFIX_HEADERS:
        value = _header(headers, name)
        if not value:
            continue
        prefix = value.rstrip('/')
        if not prefix:
            return ''
        segments = prefix.split('/')
        if _PATH_RE.match(prefix) and '.' not in segments and '..' not in segments:
            return prefix
        log.warning("Ignoring invalid %s header: %r", name, value)
        return ''
    return ''


def forwarded_host(headers: Mapping[str, str]) -> str | None:
    """
    The host the client addressed, as declared by the ``X-Forwarded-Host``
    header, or None if it is missing or not a valid host.
    """
    host = _header(headers, HOST_HEADER)
    if not host:
        return None
    if _HOST_RE.match(host):
        return host
    log.warning("Ignoring invalid %s header: %r", HOST_HEADER, host)
    return None


def uses_xheaders(handler: RequestHandler) -> bool:
    """
    Whether the server was told to trust the headers set by a proxy.
    """
    return bool(getattr(handler.application, 'use_xheaders', False))


def root_path(handler: RequestHandler) -> str:
    """
    The path the proxy serves the server on, without a trailing slash.
    An explicitly configured root path wins over the one a proxy
    declares, which is only trusted if xheaders are enabled.
    """
    root = normalize_root_path(getattr(handler.request, 'root_path', None))
    if not root:
        root = normalize_root_path(state._base_url)
    if not root and uses_xheaders(handler):
        root = forwarded_prefix(handler.request.headers)
    return root


def server_path(handler: RequestHandler) -> str:
    """
    The external path of the server root, i.e. the proxy root path
    followed by the server prefix, without a trailing slash.
    """
    return root_path(handler) + (getattr(handler.application, 'prefix', None) or '')


def external_host(handler: RequestHandler) -> str:
    host = forwarded_host(handler.request.headers) if uses_xheaders(handler) else None
    return host or handler.request.host


def external_url(handler: RequestHandler) -> str:
    """
    The URL the server root is reachable on from the outside, without a
    trailing slash.
    """
    return f'{handler.request.protocol}://{external_host(handler)}{server_path(handler)}'


def external_path(handler: RequestHandler, path: str) -> str:
    """
    Maps a path as the server received it to the path the client
    requested. Requests reaching the server through an ASGI root path
    already include it.
    """
    root = root_path(handler)
    if not root or path == root or path.startswith((f'{root}/', f'{root}?')):
        return path
    return root + path


def relative_url(path: str, target: str) -> str:
    """
    The relative reference which resolves to the ``target`` path from a
    document at ``path``. Unlike an absolute path it stays valid behind
    a proxy which strips a path prefix the server does not know about.
    """
    base = path.split('/')[1:-1]
    segments = target.split('/')[1:]
    common = 0
    for a, b in zip(base, segments[:-1], strict=False):
        if a != b:
            break
        common += 1
    return ('../' * (len(base) - common) or './') + '/'.join(segments[common:])


def login_redirect_url(handler: RequestHandler, login_url: str) -> str:
    """
    The URL to send an unauthenticated request to. If the external root
    path is known the URL is absolute, which is also correct if the
    proxy dropped a trailing slash, otherwise it is relative to the
    request.
    """
    if not login_url.startswith('/') or login_url.startswith('//'):
        return login_url
    target = (getattr(handler.application, 'prefix', None) or '') + login_url
    request = handler.request
    if not root_path(handler):
        return relative_url(request.path, target)
    url = external_path(handler, target)
    if '?' not in url:
        url += '?' + urlencode({'next': external_path(handler, request.uri)})
    return url
