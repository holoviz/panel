"""
Transport neutral authentication support.

Panel implements authentication as Tornado ``RequestHandler`` classes,
covering fifteen OAuth providers, PKCE, token refresh, basic auth and PAM.
Rather than reimplementing those flows for ASGI transports this module runs
the very same handlers headlessly, against a Tornado request synthesized
from a framework neutral :class:`~bokeh.server.request.ServerRequest`, and
translates the response they write into an ASGI response.

Tornado therefore remains the only implementation minting and validating
Panel's signed cookies, which is what makes a session established against
the Tornado server usable by an ASGI server and vice versa.
"""
from __future__ import annotations

import asyncio
import logging
import re
import typing as t

from functools import partial
from urllib.parse import urlencode, urljoin

from bokeh.server.auth import AuthPolicy
from bokeh.server.request import Cookie
from tornado.httputil import HTTPHeaders, HTTPServerRequest
from tornado.web import (
    Application as TornadoApplication, HTTPError, RequestHandler,
)

from ..config import config
from .state import state

if t.TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Mapping

    from bokeh.server.auth_provider import AuthProvider
    from bokeh.server.request import ServerRequest

    Event: t.TypeAlias = dict[str, t.Any]
    Receive: t.TypeAlias = Callable[[], Awaitable[Event]]
    Send: t.TypeAlias = Callable[[Event], Awaitable[None]]
    RouteHandler: t.TypeAlias = Callable[
        [ServerRequest, Receive, Send, dict[str, str]], Awaitable[None]
    ]

log = logging.getLogger(__name__)

__all__ = ("PanelAuthPolicy", "configure_auth", "pop_auth_kwargs")

# The authentication related arguments the servers accept, i.e. the
# arguments configure_auth applies.
AUTH_ARGS: tuple[str, ...] = (
    'basic_auth', 'basic_login_template', 'cookie_path', 'cookie_secret',
    'login_endpoint', 'login_template', 'logout_endpoint', 'logout_template',
    'oauth_encryption_key', 'oauth_error_template', 'oauth_extra_params',
    'oauth_guest_endpoints', 'oauth_jwt_user', 'oauth_key', 'oauth_optional',
    'oauth_provider', 'oauth_redirect_uri', 'oauth_refresh_tokens',
    'oauth_secret',
)


class AuthResponse(t.NamedTuple):
    """
    The response a Tornado request handler wrote, in ASGI terms.
    """

    status: int
    headers: list[tuple[bytes, bytes]]
    body: bytes


class _AuthContext:
    """
    Stands in for the ``HTTPConnection`` context Tornado reads the remote
    IP and protocol of a request from.
    """

    def __init__(self, remote_ip: str | None, protocol: str) -> None:
        self.remote_ip = remote_ip
        # The websocket schemes are not meaningful to handlers building
        # redirect and OAuth callback URLs, so report their HTTP equivalent.
        self.protocol = {'ws': 'http', 'wss': 'https'}.get(protocol, protocol)


class _AuthConnection:
    """
    Captures the response a Tornado request handler writes instead of
    sending it to a client.
    """

    def __init__(self, request: ServerRequest) -> None:
        self.context = _AuthContext(request.remote_ip, request.protocol)
        self.status = 200
        self.reason: str | None = None
        self.headers = HTTPHeaders()
        self.chunks: list[bytes] = []

    def set_close_callback(self, callback: t.Callable[[], None] | None) -> None:
        pass

    def write_headers(self, start_line, headers, chunk: bytes | None = None):
        self.status = start_line.code
        self.reason = start_line.reason
        self.headers = headers
        if chunk:
            self.chunks.append(chunk)
        return _resolved()

    def write(self, chunk: bytes):
        self.chunks.append(chunk)
        return _resolved()

    def finish(self) -> None:
        pass


def _resolved() -> asyncio.Future:
    future: asyncio.Future = asyncio.Future()
    future.set_result(None)
    return future


def _is_websocket(request: ServerRequest) -> bool:
    if request.protocol in ('ws', 'wss'):
        return True
    return request.headers.get('Upgrade', '').lower() == 'websocket'


def _fernet(key: bytes):
    try:
        from cryptography.fernet import Fernet
    except ImportError as e:
        raise RuntimeError(
            "Using an OAuth encryption key requires the cryptography "
            "library to be installed."
        ) from e
    return Fernet(key)


async def _read_body(receive: Receive) -> bytes:
    body = b''
    while True:
        event = await receive()
        if event['type'] != 'http.request':
            break
        body += event.get('body') or b''
        if not event.get('more_body'):
            break
    return body


class _AuthProbeHandler(RequestHandler):
    """
    Provides the ``RequestHandler`` API the ``AuthProvider.get_user`` hooks
    rely on, i.e. the signed cookie methods and the request itself, without
    serving a request of its own.
    """

    def get(self) -> None:
        pass


class PanelAuthPolicy(AuthPolicy):
    """
    An :class:`~bokeh.server.auth.AuthPolicy` which authenticates requests
    with a Panel ``AuthProvider`` and serves its login and logout endpoints.

    Parameters
    ----------
    provider: AuthProvider
        The provider whose handlers implement the authentication flow.
    server_config: dict
        Per-server configuration, e.g. the ``basic_auth`` credentials, which
        the handlers look up on ``state._server_config``.
    prefix: str
        The URL prefix the server, and therefore the login and logout
        endpoints, are served under.
    """

    def __init__(
        self,
        provider: AuthProvider,
        server_config: dict[str, t.Any] | None = None,
        prefix: str = '',
    ) -> None:
        self.provider = provider
        self.prefix = f'/{prefix.strip("/")}' if prefix.strip('/') else ''
        self.application = TornadoApplication(
            [],
            cookie_secret=config.cookie_secret or '',
            login_url=provider.login_url,
            xsrf_cookies=False,
        )
        self.application.auth_provider = provider  # type: ignore[attr-defined]
        if server_config is not None:
            state._server_config[self.application] = server_config
        super().__init__(
            self._authenticate, login_url=self._login_url, logout_url=provider.logout_url
        )

    @property
    def routes(self) -> list[tuple[str, RouteHandler]]:
        """
        The routes the provider's login and logout endpoints are served on,
        as ``(pattern, handler)`` pairs.
        """
        return [
            (rf'{re.escape(url.rstrip("/"))}/?$', partial(self._serve, handler))
            for url, handler in self.provider.endpoints
        ]

    #-----------------------------------------------------------------
    # Private API
    #-----------------------------------------------------------------

    def _handler(
        self, handler_cls: type[RequestHandler], request: ServerRequest, body: bytes = b''
    ) -> RequestHandler:
        headers = HTTPHeaders()
        for name, value in request.headers.items():
            headers.add(name, value)
        tornado_request = HTTPServerRequest(
            method=request.method,
            uri=request.uri,
            headers=headers,
            body=body,
            host=request.host or '127.0.0.1',
            connection=t.cast('t.Any', _AuthConnection(request)),
        )
        if body:
            tornado_request._parse_body()
        handler = handler_cls(self.application, tornado_request)
        # Handlers distinguish websocket connections, which cannot be
        # redirected and must not write cookies, by their class. Declare the
        # request type explicitly since there is only one handler here.
        handler._is_websocket = _is_websocket(request)  # type: ignore[attr-defined]
        return handler

    def _propagate(self, handler: RequestHandler, request: ServerRequest) -> None:
        """
        Copies the cookies a handler set onto the request being served, so
        that refreshed tokens reach both the client and the session.
        """
        headers = getattr(request, 'response_headers', None)
        for morsel in getattr(handler, '_new_cookie', {}).values():
            if headers is not None:
                headers.append((b'set-cookie', morsel.OutputString(None).encode()))
        for name, morsel in handler.request.cookies.items():
            # Guest access is signalled by injecting a cookie into the
            # request, which the session then reports as pn.state.user.
            if name not in request.cookies:
                request.cookies[name] = Cookie(morsel.value)

    async def _authenticate(self, request: ServerRequest) -> t.Any | None:
        provider = self.provider
        get_user_async = provider.get_user_async
        get_user = provider.get_user
        if get_user_async is None and get_user is None:
            return "default_user"
        handler = t.cast('t.Any', self._handler(_AuthProbeHandler, request))
        user = None
        try:
            if get_user_async is not None:
                user = await get_user_async(handler)
            elif get_user is not None:
                user = get_user(handler)
        except HTTPError as e:
            log.debug("Authentication failed with %s, requesting login.", e)
            return None
        self._propagate(handler, request)
        return user

    def _login_url(self, request: ServerRequest) -> str | None:
        get_login_url = self.provider.get_login_url
        url = get_login_url(t.cast('t.Any', request)) if get_login_url else self.provider.login_url
        if url is None:
            return None
        # Apply the server prefix and any proxy root path to the endpoint, as
        # Panel's Tornado handlers do by resolving it relative to the
        # document URL.
        if url.startswith('/'):
            url = f'{request.root_path.rstrip("/")}{self.prefix}{url}'
        if '?' not in url:
            url = f'{url}?{urlencode({"next": request.uri})}'
        return urljoin(request.uri, url)

    async def _serve(
        self,
        handler_cls: type[RequestHandler],
        request: ServerRequest,
        receive: Receive,
        send: Send,
        params: dict[str, str],
    ) -> None:
        body = b''
        if request.method.upper() in ('POST', 'PUT', 'PATCH'):
            body = await _read_body(receive)
        response = await self.run(handler_cls, request, body=body)
        await send({
            'type': 'http.response.start',
            'status': response.status,
            'headers': response.headers,
        })
        await send({'type': 'http.response.body', 'body': response.body})

    #-----------------------------------------------------------------
    # Public API
    #-----------------------------------------------------------------

    async def authenticate(self, request: ServerRequest) -> t.Any | None:
        # Overridden to run the handlers on the event loop. AuthPolicy
        # offloads the authenticator to a thread, but token refresh issues
        # HTTP requests through tornado.httpclient, which requires a loop.
        return await self._authenticate(request)

    async def run(
        self, handler_cls: type[RequestHandler], request: ServerRequest, body: bytes = b''
    ) -> AuthResponse:
        """
        Executes a Tornado request handler headlessly and returns the
        response it wrote.

        Parameters
        ----------
        handler_cls: type[RequestHandler]
            The handler class to execute.
        request: ServerRequest
            The request to serve.
        body: bytes
            The request body, e.g. a submitted login form.
        """
        handler = self._handler(handler_cls, request, body=body)
        await handler._execute([])
        connection = t.cast('_AuthConnection', handler.request.connection)
        headers = [
            (name.lower().encode('latin-1'), value.encode('latin-1'))
            for name, value in connection.headers.get_all()
        ]
        return AuthResponse(connection.status, headers, b''.join(connection.chunks))


def pop_auth_kwargs(kwargs: dict[str, t.Any]) -> dict[str, t.Any]:
    """
    Extracts the authentication related arguments from a set of server
    keyword arguments, so they can be applied with ``configure_auth``.
    """
    return {arg: kwargs.pop(arg) for arg in AUTH_ARGS if arg in kwargs}


def configure_auth(
    basic_auth: str | None = None,
    oauth_provider: str | None = None,
    oauth_key: str | None = None,
    oauth_secret: str | None = None,
    oauth_redirect_uri: str | None = None,
    oauth_extra_params: Mapping[str, str] = {},
    oauth_error_template: str | None = None,
    cookie_path: str = "/",
    cookie_secret: str | None = None,
    oauth_encryption_key: str | None = None,
    oauth_jwt_user: str | None = None,
    oauth_refresh_tokens: bool | None = None,
    oauth_guest_endpoints: list[str] | None = None,
    oauth_optional: bool | None = None,
    login_endpoint: str | None = None,
    logout_endpoint: str | None = None,
    login_template: str | None = None,
    logout_template: str | None = None,
    basic_login_template: str | None = None,
) -> tuple[AuthProvider | None, dict[str, t.Any]]:
    """
    Applies authentication configuration and builds the ``AuthProvider``
    serving it, if any. Shared by all transports.

    Returns
    -------
    The AuthProvider, if authentication was requested, and the per-server
    configuration the provider's handlers need.
    """
    login_template = basic_login_template or login_template
    server_config: dict[str, t.Any] = {}
    provider = None
    if basic_auth or oauth_provider:
        from ..auth import BasicAuthProvider, OAuthProvider
        provider_type: type[AuthProvider]
        if basic_auth:
            server_config['basic_auth'] = basic_auth
            provider_type = BasicAuthProvider
        else:
            config.oauth_provider = oauth_provider  # type: ignore
            provider_type = OAuthProvider
        provider = provider_type(
            login_endpoint=login_endpoint,
            logout_endpoint=logout_endpoint,
            login_template=login_template,
            logout_template=logout_template,
            error_template=oauth_error_template,
            guest_endpoints=oauth_guest_endpoints,
        )
    if oauth_key:
        config.oauth_key = oauth_key # type: ignore
    if oauth_secret:
        config.oauth_secret = oauth_secret # type: ignore
    if oauth_extra_params:
        config.oauth_extra_params = oauth_extra_params # type: ignore
    if cookie_path:
        config.cookie_path = cookie_path # type: ignore
    if cookie_secret:
        config.cookie_secret = cookie_secret # type: ignore
    if oauth_encryption_key:
        key = oauth_encryption_key
        if isinstance(key, str):
            key = key.encode('ascii')
        config.oauth_encryption_key = key # type: ignore
        state.encryption = _fernet(key)
    if oauth_redirect_uri:
        config.oauth_redirect_uri = oauth_redirect_uri # type: ignore
    if oauth_refresh_tokens is not None:
        config.oauth_refresh_tokens = oauth_refresh_tokens  # type: ignore
    if oauth_optional is not None:
        config.oauth_optional = oauth_optional  # type: ignore
    if oauth_guest_endpoints is not None:
        config.oauth_guest_endpoints = oauth_guest_endpoints  # type: ignore
    if oauth_jwt_user is not None:
        config.oauth_jwt_user = oauth_jwt_user  # type: ignore
    return provider, server_config
