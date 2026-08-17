"""
A framework neutral ASGI implementation for serving Panel applications.

``PanelASGI`` extends Bokeh's :class:`~bokeh.server.asgi.BokehASGI` with the
routing, session and rendering behavior Panel's Tornado server provides,
i.e. wildcard routes, a custom index page, ``--static-dirs`` mounts,
component resources, liveness endpoints and session reuse. It is the shared
core behind :mod:`panel.io.fastapi`, :mod:`panel.io.django` and
``panel serve --server asgi``.
"""
from __future__ import annotations

import asyncio
import json
import logging
import pathlib
import re
import typing as t

from functools import partial
from urllib.parse import urljoin, urlparse

from bokeh.server.asgi import BokehASGI, _ASGIWebSocketTransport
from bokeh.server.core import SessionError
from bokeh.util.token import (
    generate_jwt_token, generate_session_id, get_token_payload,
)
from tornado.web import HTTPError

from ..config import config
from .application import build_applications
from .auth import PanelAuthPolicy, configure_auth, pop_auth_kwargs
from .document import _cleanup_doc, extra_socket_handlers
from .logging import LOG_SESSION_CREATED
from .reload import record_modules
from .resources import COMPONENT_PATH, DIST_DIR, Resources
from .server import (
    INDEX_HTML, _sanitize_route_context, authorize_request, autoload_js_script,
    compile_route_template, index_redirect, render_auth_error,
    render_index_page, resolve_component_resource, resolve_session,
    server_html_page_for_session, token_payload_for_request,
    validate_static_dirs,
)
from .session import generate_session
from .state import set_curdoc, state

if t.TYPE_CHECKING:
    import os

    from collections.abc import (
        Awaitable, Callable, Mapping, Sequence,
    )

    from bokeh.application.application import Application as BkApplication
    from bokeh.core.types import ID
    from bokeh.document.events import DocumentPatchedEvent
    from bokeh.protocol.message import Message
    from bokeh.server.auth import AuthPolicy
    from bokeh.server.auth_provider import AuthProvider
    from bokeh.server.contexts import ApplicationContext
    from bokeh.server.request import ServerRequest

    from .application import TViewableFuncOrPath
    from .location import Location

    Scope: t.TypeAlias = dict[str, t.Any]
    Event: t.TypeAlias = dict[str, t.Any]
    Receive: t.TypeAlias = Callable[[], Awaitable[Event]]
    Send: t.TypeAlias = Callable[[Event], Awaitable[None]]
    Headers: t.TypeAlias = list[tuple[bytes, bytes]]

    # A Panel owned route handler. Receives the parsed request, the ASGI
    # receive and send callables and the named groups captured by the route.
    RouteHandler: t.TypeAlias = Callable[
        [ServerRequest, Receive, Send, dict[str, str]], Awaitable[None]
    ]

logger = logging.getLogger(__name__)

__all__ = ("PanelASGI", "build_asgi_app", "dispatch_asgi")

# Application sub-routes, in the order Tornado registers them so that
# ambiguous wildcard routes (e.g. /files/{path:path}) resolve identically
# on both transports.
_APP_SUFFIXES: tuple[str, ...] = (
    r'(?P<__suffix__>/ws)',
    r'(?P<__suffix__>/metadata)',
    r'(?P<__suffix__>/autoload\.js)',
    r'(?P<__suffix__>/?)',
    r'(?P<__suffix__>/static/.*)',
)


def dispatch_asgi(
    conn, events: list[DocumentPatchedEvent] | None = None, msg: Message | None = None
):
    """
    Dispatches a message or set of events to an ASGI websocket transport.
    """
    if msg is None:
        msg = conn.protocol.create("PATCH-DOC", events)
    return [conn._socket.send_message(msg)]

extra_socket_handlers[_ASGIWebSocketTransport] = dispatch_asgi


class PanelASGI(BokehASGI):
    """
    An ASGI3 application serving one or more Panel applications.

    Parameters
    ----------
    applications: Mapping[str, Application] | Application | callable | path
        The application(s) to serve, either already built Bokeh/Panel
        Application objects or anything ``BokehServerCore`` accepts.
    prefix: str
        URL prefix all routes are served under.
    index: str | None
        Path to a template rendered on the root URL when it is not itself
        an application. Defaults to Panel's own index page.
    index_enabled: bool
        Whether to render an index page on the root URL at all.
    ico_path: str | os.PathLike | None
        Path to the favicon served on ``/favicon.ico``. The string ``'none'``
        disables the endpoint.
    static_dirs: Mapping[str, str] | None
        Mapping from URL slug to a local directory to serve.
    liveness: bool | str
        Whether to serve a liveness endpoint and, if a string is given, the
        endpoint to serve it on.
    mem_log_frequency_milliseconds: int
        How often to log memory usage, 0 to disable. Requires psutil.
    session_history: int | None
        If set, enables session history tracking and serves it on
        ``/session_info``.
    extra_routes: Sequence[tuple[str, RouteHandler]] | None
        Additional routes as ``(pattern, handler)`` pairs. Patterns are
        regular expressions matched against the prefix-relative path.
    auth_provider: AuthProvider | None
        Provider implementing authentication, i.e. the login and logout
        endpoints and the user lookup. Ignored if an ``auth_policy`` is
        given.
    auth_policy: AuthPolicy | None
        Policy used to authenticate HTTP and websocket requests.
    server_config: dict[str, Any] | None
        Per-server configuration, e.g. the ``basic_auth`` credentials,
        looked up by the authentication handlers.
    """

    def __init__(
        self,
        applications: t.Any,
        *,
        prefix: str = '',
        index: str | None = INDEX_HTML,
        index_enabled: bool = True,
        ico_path: str | os.PathLike | None = None,
        static_dirs: Mapping[str, str] | None = None,
        liveness: bool | str = False,
        mem_log_frequency_milliseconds: int = 0,
        session_history: int | None = None,
        extra_routes: Sequence[tuple[str, RouteHandler]] | None = None,
        auth_provider: AuthProvider | None = None,
        auth_policy: AuthPolicy | None = None,
        server_config: dict[str, t.Any] | None = None,
        **kwargs
    ) -> None:
        if auth_policy is None and auth_provider is not None:
            auth_policy = PanelAuthPolicy(auth_provider, server_config, prefix=prefix)
        super().__init__(applications, prefix=prefix, auth_policy=auth_policy, **kwargs)
        if isinstance(auth_policy, PanelAuthPolicy):
            # Ensure the login redirects apply the normalized prefix
            auth_policy.prefix = self._core.prefix
        self._index = index
        self._index_enabled = index_enabled
        self._icon = self._load_icon(ico_path)
        self._static_dirs = validate_static_dirs(static_dirs or {})
        self._app_routes = self._compile_app_routes()
        self._extra_routes: list[tuple[re.Pattern[str], RouteHandler]] = []
        self._panel_started = False
        self._autoreload_stop_event: asyncio.Event | None = None
        self._autoreload_task: asyncio.Task | None = None
        self._mem_log_frequency = mem_log_frequency_milliseconds
        self._mem_log_task: asyncio.Task | None = None
        if session_history is not None:
            config.session_history = session_history
        if config.session_history != 0:
            self._add_route(r'/session_info/?$', self._session_info)
        if liveness:
            endpoint = liveness if isinstance(liveness, str) else '/liveness'
            if not endpoint.startswith('/'):
                endpoint = f'/{endpoint}'
            self._add_route(rf'{re.escape(endpoint)}/?$', self._liveness)
        self._add_route(rf'/{COMPONENT_PATH}(?P<path>.*)$', self._component_resource)
        for slug, path in self._static_dirs.items():
            self._add_route(
                rf'{re.escape(slug)}(?:/(?P<path>.*))?$', partial(self._static_dir, path)
            )
        for pattern, handler in (extra_routes or ()):
            self._add_route(pattern, handler)
        if isinstance(auth_policy, PanelAuthPolicy):
            for pattern, handler in auth_policy.routes:
                self._add_route(pattern, handler)
        state._server_config[self] = server_config or {}

    #-----------------------------------------------------------------
    # Setup
    #-----------------------------------------------------------------

    @staticmethod
    def _load_icon(ico_path: str | os.PathLike | None) -> bytes | None:
        if ico_path is None:
            ico_path = DIST_DIR / 'images' / 'favicon.ico'
        elif ico_path == 'none':
            return None
        with open(ico_path, 'rb') as f:
            return f.read()

    def _compile_app_routes(self) -> list[tuple[re.Pattern[str], str]]:
        """
        Compile the served application paths, which may contain
        ``{param}`` templates, into anchored regular expressions for each
        application sub-route.
        """
        routes = []
        for app_path in self._core.applications:
            pattern, _ = compile_route_template(app_path)
            base = '' if app_path == '/' else pattern
            for suffix in _APP_SUFFIXES:
                routes.append((re.compile(f'^{base}{suffix}$'), app_path))
        return routes

    def _add_route(self, pattern: str, handler: RouteHandler) -> None:
        self._extra_routes.append((re.compile(pattern), handler))

    #-----------------------------------------------------------------
    # Lifecycle
    #-----------------------------------------------------------------

    def _owns_admin_context(self) -> bool:
        """
        Whether the admin application is served as one of our own
        applications, in which case ``BokehServerCore`` runs its lifecycle.
        """
        return state._admin_context in self._core.applications.values()

    async def _ensure_started(self) -> None:
        await super()._ensure_started()
        if self._panel_started:
            return
        self._panel_started = True
        loop = asyncio.get_running_loop()
        # Route Bokeh's asyncio.to_thread offloading through Panel's bounded
        # thread pool so --num-threads bounds it. BokehServerCore does not
        # pass an executor to the ApplicationContext, unlike BokehTornado.
        state._install_thread_pool(loop)
        if state._admin_context and not self._owns_admin_context():
            # The admin context was created outside the server, e.g. by
            # pn.serve(admin=True), so its lifecycle is ours to run.
            # BokehServerCore.start already ran the hook for a context it
            # holds itself.
            state._admin_context._loop = loop
            loop.call_soon(state._admin_context.run_load_hook)
        if state._setup_module and state._setup_file_callback:
            loop.call_soon(state._setup_file_callback)
        if config.autoreload:
            from .reload import setup_autoreload_watcher
            self._autoreload_stop_event = stop_event = asyncio.Event()
            self._autoreload_task = loop.create_task(setup_autoreload_watcher(stop_event))
        if self._mem_log_frequency > 0:
            self._start_mem_log(loop)

    def _start_mem_log(self, loop: asyncio.AbstractEventLoop) -> None:
        """
        Periodically logs memory usage, replicating the periodic callback
        BokehTornado sets up. The logging itself is reused from Bokeh so the
        output is identical, it does not depend on any Tornado state.
        """
        from bokeh.server.tornado import BokehTornado, psutil
        if psutil is None:
            logger.warning(
                "Memory logging requested, but is disabled. Optional dependency "
                "'psutil' is missing. Try 'pip install psutil' or 'conda install psutil'"
            )
            return
        interval = self._mem_log_frequency / 1000
        logger.info("Log memory usage every %d milliseconds", self._mem_log_frequency)

        async def log_mem() -> None:
            while True:
                await asyncio.sleep(interval)
                BokehTornado._log_mem(self)  # type: ignore[arg-type]

        self._mem_log_task = loop.create_task(log_mem())

    async def _panel_stop(self) -> None:
        if self._mem_log_task is not None:
            self._mem_log_task.cancel()
            self._mem_log_task = None
        if self._autoreload_stop_event is not None:
            for event in state._watch_events:
                event.set()
            state._watch_events.clear()
            self._autoreload_stop_event.set()
            if self._autoreload_task is not None:
                await self._autoreload_task
            self._autoreload_stop_event = None
            self._autoreload_task = None
        if state._admin_context and not self._owns_admin_context():
            state._admin_context.run_unload_hook()
        self._panel_started = False

    async def _lifespan(self, receive: Receive, send: Send) -> None:
        while True:
            event = await receive()
            if event['type'] == 'lifespan.startup':
                try:
                    await self._ensure_started()
                except Exception as error:
                    await send({'type': 'lifespan.startup.failed', 'message': str(error)})
                    return
                await send({'type': 'lifespan.startup.complete'})
            elif event['type'] == 'lifespan.shutdown':
                await self._panel_stop()
                await self._core.stop()
                self._start_lock = None
                await send({'type': 'lifespan.shutdown.complete'})
                return

    #-----------------------------------------------------------------
    # Routing
    #-----------------------------------------------------------------

    def handles(self, scope: Scope) -> bool:
        """
        Whether this application owns the given ASGI scope. Allows composing
        ``PanelASGI`` with another ASGI application, e.g. Django or FastAPI.
        """
        if scope['type'] not in ('http', 'websocket'):
            return False
        route = self._route_path(scope)
        if not route:
            return False
        if route == '/favicon.ico' or route.startswith('/static/'):
            return True
        if self._resolve_route(route) is not None:
            return True
        if any(pattern.match(route) for pattern, _ in self._extra_routes):
            return True
        return bool(self._index_enabled and route == '/')

    def _resolve_route(
        self, route: str
    ) -> tuple[ApplicationContext, str, dict[str, str]] | None:
        for pattern, app_path in self._app_routes:
            if (match := pattern.match(route)) is None:
                continue
            groups = match.groupdict()
            suffix = groups.pop('__suffix__')
            params = {k: v for k, v in groups.items() if v is not None}
            return self._core.applications[app_path], suffix, params
        return None

    def _resolve_application(self, route: str) -> tuple[ApplicationContext, str] | None:
        resolved = self._resolve_route(route)
        if resolved is None:
            return None
        context, suffix, _ = resolved
        return context, suffix

    def _request(self, scope: Scope) -> ServerRequest:
        request = super()._request(scope)
        params: dict[str, str] = {}
        app_path: str | None = None
        if route := self._route_path(scope):
            if (resolved := self._resolve_route(route)) is not None:
                _, suffix, params = resolved
                app_path = (route[:len(route)-len(suffix)] if suffix else route) or '/'
        # ServerRequest is a plain dataclass, so the route context can be
        # attached to it directly for RequestProxy and Application to pick up.
        request.route_params, request.app_path = _sanitize_route_context(params, app_path)  # type: ignore[attr-defined]
        request.response_headers = []  # type: ignore[attr-defined]
        return request

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] == 'http':
            await self._ensure_started()
            await self._http(scope, send, receive)
        else:
            await super().__call__(scope, receive, send)

    async def _http(self, scope: Scope, send: Send, receive: Receive | None = None) -> None:
        request = self._request(scope)
        route = self._route_path(scope)
        if not route:
            await self._not_found(request, send)
            return

        if route == '/favicon.ico':
            await self._favicon(request, send)
            return
        if route.startswith('/static/'):
            await self._global_static(route, request, send)
            return

        if (resolved := self._resolve_route(route)) is not None:
            context, suffix, _ = resolved
            if suffix in ('', '/'):
                await self._document(context, request, send)
            elif suffix == '/metadata':
                await self._metadata(context, request, send)
            elif suffix == '/autoload.js':
                await self._autoload(context, request, send)
            elif suffix.startswith('/static/'):
                await self._application_static(context, suffix, request, send)
            elif suffix == '/ws':
                # Match Tornado's response to a plain GET on the websocket URL.
                await self._respond(
                    request, send, 400, b'Can "Upgrade" only to "WebSocket".', 'text/plain'
                )
            else:
                await self._not_found(request, send)
            return

        for pattern, handler in self._extra_routes:
            if (match := pattern.match(route)) is not None:
                await handler(request, t.cast('Receive', receive), send, match.groupdict())
                return

        if route == '/' and self._index_enabled:
            await self._root(request, send)
            return
        await self._not_found(request, send)

    #-----------------------------------------------------------------
    # Responses
    #-----------------------------------------------------------------

    async def _respond(
        self,
        request: ServerRequest,
        send: Send,
        status: int,
        body: bytes,
        content_type: str,
        *,
        head: bool = False,
        extra_headers: Headers | None = None,
    ) -> None:
        """
        Send a response, merging in any headers accumulated on the request,
        e.g. refreshed authentication cookies.
        """
        headers: Headers = list(getattr(request, 'response_headers', None) or ())
        headers += list(extra_headers or ())
        await self._response(send, status, body, content_type, head=head, extra_headers=headers)

    async def _redirect(self, request: ServerRequest, send: Send, location: str) -> None:
        await self._respond(
            request, send, 302, b'', 'text/plain',
            head=request.method.upper() == 'HEAD',
            extra_headers=[(b'location', location.encode())]
        )

    async def _check_method(
        self, request: ServerRequest, send: Send, allowed: tuple[str, ...] = ('GET', 'HEAD')
    ) -> bool:
        if request.method.upper() not in allowed:
            await self._method_not_allowed(send, allowed)
            return False
        return True

    #-----------------------------------------------------------------
    # Panel routes
    #-----------------------------------------------------------------

    async def _favicon(self, request: ServerRequest, send: Send) -> None:
        if not await self._check_method(request, send):
            return
        head = request.method.upper() == 'HEAD'
        if self._icon is None:
            await self._respond(request, send, 404, b'Not found', 'text/plain', head=head)
            return
        await self._respond(request, send, 200, self._icon, 'image/x-icon', head=head)

    async def _liveness(
        self, request: ServerRequest, receive: Receive, send: Send, params: dict[str, str]
    ) -> None:
        if not await self._check_method(request, send):
            return
        head = request.method.upper() == 'HEAD'
        endpoint = self._argument(request, 'endpoint')
        if endpoint is None:
            body = json.dumps({request.path: True}).encode()
            await self._respond(request, send, 200, body, 'application/json', head=head)
            return
        context = self._core.applications.get(endpoint)
        if context is None:
            body = f'Endpoint {endpoint!r} does not exist.'.encode()
            await self._respond(request, send, 400, body, 'text/plain', head=head)
            return
        try:
            doc = context.application.create_document()
            _cleanup_doc(doc)
        except Exception as e:
            body = (
                f'Endpoint {endpoint!r} could not be served. '
                f'Application raised error: {e}'
            ).encode()
            await self._respond(request, send, 500, body, 'text/plain', head=head)
            return
        body = json.dumps({endpoint: True}).encode()
        await self._respond(request, send, 200, body, 'application/json', head=head)

    async def _session_info(
        self, request: ServerRequest, receive: Receive, send: Send, params: dict[str, str]
    ) -> None:
        if not await self._check_method(request, send):
            return
        head = request.method.upper() == 'HEAD'
        body = json.dumps(state.session_info).encode()
        await self._respond(request, send, 200, body, 'application/json', head=head)

    async def _component_resource(
        self, request: ServerRequest, receive: Receive, send: Send, params: dict[str, str]
    ) -> None:
        if not await self._check_method(request, send):
            return
        head = request.method.upper() == 'HEAD'
        try:
            resolved = resolve_component_resource(params.get('path', ''))
        except HTTPError as e:
            reason = e.log_message or e.reason or 'Error'
            await self._respond(request, send, e.status_code, reason.encode(), 'text/plain', head=head)
            return
        path = pathlib.Path(resolved)
        await self._serve_static(send, path.parent, path.name, head=head)

    async def _static_dir(
        self, root: str, request: ServerRequest, receive: Receive, send: Send,
        params: dict[str, str]
    ) -> None:
        if not await self._check_method(request, send):
            return
        head = request.method.upper() == 'HEAD'
        if not await self._authenticate_http(request, send, head=head):
            return
        relative = params.get('path') or ''
        if not relative or relative.endswith('/'):
            relative += 'index.html'
        elif (pathlib.Path(root) / relative).is_dir():
            relative = f'{relative}/index.html'
        await self._serve_static(send, root, relative, head=head)

    #-----------------------------------------------------------------
    # Application handlers
    #-----------------------------------------------------------------

    def _authorize(
        self, request: ServerRequest, session: bool = False
    ) -> tuple[bool | None, str | None, str | None]:
        result = authorize_request(request.path, session=session)
        return result.authorized, result.error, result.redirect

    async def _document(
        self, context: ApplicationContext, request: ServerRequest, send: Send
    ) -> None:
        if not await self._check_method(request, send):
            return
        head = request.method.upper() == 'HEAD'
        if not await self._authenticate_http(request, send, head=head):
            return

        # Prevent the browser from caching the document page. The page embeds
        # a short-lived Bokeh session token; a cached page served after a
        # logout/login cycle would carry a stale token and the subsequent
        # WebSocket connection would fail (see e.g. holoviz/panel#8634).
        request.response_headers.append((b'cache-control', b'no-store'))  # type: ignore[attr-defined]

        core = self._core
        prefix = core.prefix
        root_path = request.root_path.rstrip('/')
        path = request.path[len(root_path):] if root_path else request.path
        if prefix and path == prefix:
            # Resources are resolved relative to the document URL, so the
            # prefixed root must be served with a trailing slash.
            query = f'?{request.query}' if request.query else ''
            await self._redirect(request, send, f'{root_path}{prefix}/{query}')
            return

        payload = t.cast('dict[str, t.Any]', token_payload_for_request(core, request))
        payload.update(await context.application.process_request_async(request))

        # Run global authorization callback
        if config.authorize_callback:
            temp_session = generate_session(
                context.application, request, payload, initialize=False
            )
            with set_curdoc(temp_session.document):
                authorized, auth_error, redirect = self._authorize(request)
            if redirect is not None:
                await self._redirect(request, send, redirect)
                return
            elif not authorized:
                page = render_auth_error(t.cast('str', auth_error))
                await self._respond(
                    request, send, 403, page.encode(), 'text/html; charset=UTF-8', head=head
                )
                return

        key_func = state._session_key_funcs.get(request.path, lambda r: r.path)
        old_request = key_func(request) in state._sessions
        try:
            session = await resolve_session(
                request, partial(core.create_session, context, request)
            )
        except SessionError as error:
            await self._respond(
                request, send, error.status, error.reason.encode(), 'text/plain', head=head
            )
            return

        if old_request and state._sessions.get(key_func(request)) is session:
            session_id = generate_session_id(
                secret_key=core.secret_key, signed=core.sign_sessions
            )
            extra_payload = dict(get_token_payload(session.token))
            extra_payload.update(payload)
            extra_payload.pop('session_expiry', None)
            token = generate_jwt_token(
                session_id,
                secret_key=core.secret_key,
                signed=core.sign_sessions,
                expiration=core.session_token_expiration,
                extra_payload=extra_payload
            )
            if config.reuse_sessions == 'warm':
                state.execute(
                    partial(
                        core.create_session_if_needed,
                        context, t.cast('ID', session_id), request, token
                    )
                )
        else:
            token = session.token

        logger.info(LOG_SESSION_CREATED, id(session.document))
        with set_curdoc(session.document):
            resources = Resources.from_bokeh(core.resources(root_path=request.root_path))
            authorized, auth_error, redirect = self._authorize(request, session=True)
            if authorized:
                page = server_html_page_for_session(
                    session, resources=resources, title=session.document.title,
                    token=token, template=session.document.template,
                    template_variables=session.document.template_variables,
                )
                status = 200
            elif redirect is not None:
                await self._redirect(request, send, redirect)
                return
            else:
                page = render_auth_error(t.cast('str', auth_error))
                status = 403

        await self._respond(
            request, send, status, page.encode(), 'text/html; charset=UTF-8', head=head
        )

    async def _autoload(
        self, context: ApplicationContext, request: ServerRequest, send: Send
    ) -> None:
        method = request.method.upper()
        if method == 'OPTIONS':
            await self._respond(
                request, send, 204, b'', 'text/plain',
                extra_headers=self._cors_headers(request)
            )
            return
        if not await self._check_method(request, send, ('GET', 'HEAD', 'OPTIONS')):
            return
        head = method == 'HEAD'
        if not await self._authenticate_http(request, send, head=head):
            return

        element_id = self._argument(request, 'bokeh-autoload-element')
        if not element_id:
            await self._respond(
                request, send, 400, b'No bokeh-autoload-element query parameter',
                'text/plain', head=head
            )
            return
        app_path = self._argument(request, 'bokeh-app-path') or '/'
        absolute_url = self._argument(request, 'bokeh-absolute-url')
        server_url = None
        if absolute_url:
            uri = urlparse(absolute_url)
            server_url = f'{uri.scheme}://{uri.netloc}'

        try:
            session = await self._core.create_session(context, request)
        except SessionError as error:
            await self._respond(
                request, send, error.status, error.reason.encode(), 'text/plain', head=head
            )
            return

        with set_curdoc(session.document):
            resources = Resources.from_bokeh(
                self._core.resources(server_url, root_path=request.root_path), absolute=True
            )
            js = autoload_js_script(
                session.document, resources, session.token, element_id,
                app_path, absolute_url, absolute=True
            )
        await self._respond(
            request, send, 200, js.encode(), 'application/javascript',
            head=head, extra_headers=self._cors_headers(request)
        )

    async def _root(self, request: ServerRequest, send: Send) -> None:
        if not await self._check_method(request, send):
            return
        head = request.method.upper() == 'HEAD'
        if not await self._authenticate_http(request, send, head=head):
            return
        app_paths = list(self._core.applications)
        if (redirect := index_redirect(app_paths, self._redirect_root)) is not None:
            await self._redirect(request, send, urljoin(request.uri, redirect))
            return
        prefix = request.root_path.rstrip('/') + self._core.prefix
        page = render_index_page(app_paths, prefix, index=self._index, uri=request.uri)
        await self._respond(
            request, send, 200, page.encode(), 'text/html; charset=UTF-8', head=head
        )


def build_asgi_app(
    panel: TViewableFuncOrPath | dict[str, TViewableFuncOrPath],
    title: str | dict[str, str] | None = None,
    location: bool | Location = True,
    admin: bool = False,
    warm: bool = False,
    websocket_origin: str | list[str] | None = None,
    **kwargs
) -> PanelASGI:
    """
    Builds a ``PanelASGI`` application from one or more Panel objects.

    Parameters
    ----------
    panel: Viewable, function or {str: Viewable}
        A Panel object, a function returning a Panel object or a
        dictionary mapping from the URL slug to either.
    title: str or {str: str}
        An HTML title for the application or a dictionary mapping
        from the URL slug to a customized title.
    location: boolean or panel.io.location.Location
        Whether to create a Location component to observe and
        set the URL location.
    admin: boolean
        Whether to enable the admin panel.
    warm: boolean
        Whether to run the applications before serving them to ensure
        all imports and caches are fully warmed up.
    websocket_origin: str or list(str)
        A list of hosts that can connect to the websocket.
    kwargs: dict
        Additional keyword arguments to pass to ``PanelASGI``, including
        the authentication arguments applied by
        ``panel.io.auth.configure_auth``, e.g. ``basic_auth`` or
        ``oauth_provider``.
    """
    auth_provider, server_config = configure_auth(**pop_auth_kwargs(kwargs))
    apps: dict[str, BkApplication] = build_applications(
        panel, title=title, location=location, admin=admin
    )
    if websocket_origin:
        if not isinstance(websocket_origin, list):
            websocket_origin = [websocket_origin]
        kwargs['extra_websocket_origins'] = websocket_origin
    if warm or config.autoreload:
        warm_applications(apps)
    return PanelASGI(
        apps, auth_provider=auth_provider, server_config=server_config, **kwargs
    )


def warm_applications(apps: Mapping[str, BkApplication]) -> None:
    """
    Runs each application once to warm up imports and caches.
    """
    for endpoint, app in apps.items():
        if endpoint == '/admin':
            continue
        if config.autoreload:
            with record_modules(list(apps.values())):
                session = generate_session(app)
        else:
            session = generate_session(app)
        with set_curdoc(session.document):
            state._on_load(None)
        _cleanup_doc(session.document, destroy=True)
