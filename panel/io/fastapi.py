"""
Native FastAPI integration for Panel applications.

Panel applications are served by :class:`panel.io.asgi.PanelASGI`, a
framework neutral ASGI application. Rather than registering one route per
application on the FastAPI app, the ASGI application is installed as a
middleware which claims the paths Panel owns and delegates everything else
to FastAPI. This makes the integration insensitive to the order in which
Panel and FastAPI routes are declared.
"""
from __future__ import annotations

import asyncio
import socket
import typing as t
import uuid

from contextlib import asynccontextmanager
from functools import wraps

from .asgi import PanelASGI, build_asgi_app, dispatch_asgi
from .state import state
from .threads import StoppableThread

try:
    from fastapi import FastAPI
except ImportError as e:
    if e.name == 'fastapi':
        msg = 'fastapi must be installed to use the panel.io.fastapi module.'
        raise ImportError(msg) from None
    raise e

if t.TYPE_CHECKING:
    from bokeh.server.core import BokehServerCore
    from uvicorn import Server

    from .application import TViewableFuncOrPath
    from .asgi import Receive, Scope, Send
    from .location import Location

__all__ = (
    "add_application",
    "add_applications",
    "dispatch_fastapi",
    "get_server",
    "serve",
)

# Kept for backward compatibility, the write dispatcher is now shared by all
# ASGI transports.
dispatch_fastapi = dispatch_asgi

#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------

# Routes Panel serves as a convenience but which an explicitly declared
# FastAPI route should win, so that embedding Panel does not take over the
# root of an existing application.
DEFERRED_ROUTES = ('/', '/favicon.ico')


class PanelDispatchMiddleware:
    """
    ASGI middleware which forwards the routes owned by one or more
    ``PanelASGI`` applications and delegates all other requests to the
    wrapped application.
    """

    def __init__(self, app, fastapi: FastAPI, panel_apps: list[PanelASGI]) -> None:
        self.app = app
        self.fastapi = fastapi
        self.panel_apps = panel_apps

    def _declared_by_fastapi(self, scope: Scope) -> bool:
        from starlette.routing import Match
        return any(
            route.matches(scope)[0] is Match.FULL
            for route in self.fastapi.router.routes
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] in ('http', 'websocket'):
            for panel_app in self.panel_apps:
                if not panel_app.handles(scope):
                    continue
                if (
                    panel_app._route_path(scope) in DEFERRED_ROUTES and
                    self._declared_by_fastapi(scope)
                ):
                    break
                await panel_app(scope, receive, send)
                return
        await self.app(scope, receive, send)


class PanelFastAPI:
    """
    Handle bundling a FastAPI application with the ``PanelASGI``
    application serving the Panel application(s) added to it.
    """

    def __init__(self, app: FastAPI, asgi: PanelASGI) -> None:
        self.app = app
        self.asgi = asgi

    @property
    def core(self) -> BokehServerCore:
        return self.asgi.core

    @property
    def applications(self):
        return self.asgi.core.applications

    def __getattr__(self, name: str):
        # Forward the BokehServerCore configuration (secret_key,
        # sign_sessions, include_headers etc.) for compatibility.
        return getattr(self.asgi.core, name)


def _install_panel_asgi(app: FastAPI, asgi: PanelASGI) -> None:
    """
    Installs the dispatch middleware on the FastAPI application, reusing
    it if applications were added to the same app before, and hooks the
    Panel application into the FastAPI lifespan.
    """
    panel_apps = getattr(app.state, '_panel_asgi_apps', None)
    if panel_apps is None:
        panel_apps = []
        app.state._panel_asgi_apps = panel_apps
        app.add_middleware(
            PanelDispatchMiddleware, fastapi=app, panel_apps=panel_apps
        )
    panel_apps.append(asgi)

    # Wrap rather than replace the lifespan so that a user supplied lifespan
    # (or a previous add_applications call) keeps running. Starlette dropped
    # the add_event_handler API so composition is the only portable option.
    previous = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await asgi._ensure_started()
        try:
            async with previous(app):
                yield
        finally:
            await asgi._panel_stop()
            await asgi.core.stop()

    app.router.lifespan_context = lifespan


#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def add_applications(
    panel: TViewableFuncOrPath | dict[str, TViewableFuncOrPath],
    app: FastAPI | None = None,
    title: str | dict[str, str] | None = None,
    location: bool | Location = True,
    admin: bool = False,
    session_history: int | None = None,
    liveness: bool | str = False,
    **kwargs
) -> PanelFastAPI:
    """
    Adds application(s) to an existing FastAPI application.

    Parameters
    ----------
    app: FastAPI
        FastAPI app to add Panel application(s) to.
    panel: Viewable, function or {str: Viewable}
        A Panel object, a function returning a Panel object or a
        dictionary mapping from the URL slug to either.
    title : str or {str: str} (optional, default=None)
        An HTML title for the application or a dictionary mapping
        from the URL slug to a customized title.
    location : boolean or panel.io.location.Location
        Whether to create a Location component to observe and
        set the URL location.
    admin: boolean (default=False)
        Whether to enable the admin panel
    session_history: int (optional, default=None)
      The amount of session history to accumulate. If set to non-zero
      and non-None value will launch an endpoint at /session_info,
      which returns information about the session history.
    liveness: bool | str (optional, default=False)
      Whether to add a liveness endpoint. If a string is provided
      then this will be used as the endpoint, otherwise the endpoint
      will be hosted at /liveness.
    **kwargs:
        Additional keyword arguments to pass to the PanelASGI application
    """
    prefix = kwargs.pop('prefix', '') or ''
    if prefix:
        if not prefix.startswith('/'):
            raise ValueError("prefix must start with '/'.")
        prefix = prefix.rstrip('/')
    asgi = build_asgi_app(
        panel, title=title, location=location, admin=admin, prefix=prefix,
        session_history=session_history, liveness=liveness, **kwargs
    )
    if app is None:
        app = FastAPI()
    _install_panel_asgi(app, asgi)
    return PanelFastAPI(app, asgi)


def add_application(
    path: str,
    app: FastAPI,
    title: str = "Panel App",
    location: bool | Location = True,
    admin: bool = False,
    **kwargs
):
    """
    Decorator that adds a Panel app to a FastAPI application.

    Parameters
    ----------
    path: str
        The path to serve the application on.
    app: FastAPI
        FastAPI app to add Panel application(s) to.
    title : str
        An HTML title for the application.
    location : boolean or panel.io.location.Location
        Whether to create a Location component to observe and
        set the URL location.
    admin: boolean (default=False)
        Whether to enable the admin panel
    **kwargs:
        Additional keyword arguments to pass to the PanelASGI application
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Register the Panel application after the function is defined
        add_applications(
            {path: func}, app=app, title=title, location=location,
            admin=admin, **kwargs
        )
        return wrapper

    return decorator


def get_server(
    panel: TViewableFuncOrPath | dict[str, TViewableFuncOrPath],
    port: int | None = 0,
    show: bool = True,
    start: bool = False,
    title: str | dict[str, str] | None = None,
    location: bool | Location = True,
    admin: bool = False,
    **kwargs
) -> Server:
    """
    Creates a FastAPI server running the provided Panel application(s).

    Parameters
    ----------
    panel: Viewable, function or {str: Viewable}
        A Panel object, a function returning a Panel object or a
        dictionary mapping from the URL slug to either.
    port: int (optional, default=0)
      Allows specifying a specific port.
    show : boolean (optional, default=True)
      Whether to open the server in a new browser tab on start
    start : boolean(optional, default=False)
      Whether to start the Server.
    title : str or {str: str} (optional, default=None)
        An HTML title for the application or a dictionary mapping
        from the URL slug to a customized title.
    location : boolean or panel.io.location.Location
        Whether to create a Location component to observe and
        set the URL location.
    admin: boolean (default=False)
        Whether to enable the admin panel
    liveness: bool | str (optional, default=False)
      Whether to add a liveness endpoint. If a string is provided
      then this will be used as the endpoint, otherwise the endpoint
      will be hosted at /liveness.
    session_history: int (optional, default=None)
      The amount of session history to accumulate. If set to non-zero
      and non-None value will launch an endpoint at /session_info,
      which returns information about the session history.
    **kwargs:
        Additional keyword arguments to pass to the PanelASGI application
    """
    try:
        import uvicorn
    except Exception as e:
        raise ImportError(
            "Running a FastAPI server requires uvicorn to be available. "
            "If you want to use a different server implementation use the "
            "panel.io.fastapi.add_applications API."
        ) from e

    address = kwargs.pop('address', None)
    if not port:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 0))  # Bind to any available port
        port = sock.getsockname()[1]  # Get the dynamically assigned port
        sock.close()

    loop = kwargs.pop('loop', None)
    config_kwargs: dict[str, t.Any] = {'port': port}
    if loop:
        config_kwargs['loop'] = loop
        asyncio.set_event_loop(loop)
    if address:
        config_kwargs['host'] = address
    server_id = kwargs.pop('server_id', uuid.uuid4().hex)
    prefix = kwargs.get('prefix', '') or ''

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if show:
            address_string = address if address else 'localhost'
            from bokeh.util.browser import view
            view(f"http://{address_string}:{port}{prefix}", new='tab')
        yield

    application = add_applications(
        panel, app=FastAPI(lifespan=lifespan), title=title, location=location,
        admin=admin, **kwargs
    )

    uv_config = uvicorn.Config(application.app, **config_kwargs)
    server = uvicorn.Server(uv_config)

    # uvicorn.Server does not expose the address, port or prefix it is
    # serving on, so record them for the benefit of state._servers consumers
    # such as Location._sync_pathname.
    server.address = address  # type: ignore[attr-defined]
    server.port = port  # type: ignore[attr-defined]
    server.prefix = application.core.prefix  # type: ignore[attr-defined]

    state._servers[server_id] = (server, panel, [])
    if not start:
        return server

    if loop:
        try:
            loop.run_until_complete(server.serve())
        except asyncio.CancelledError:
            pass
    else:
        server.run()

    return server


def serve(
    panels: TViewableFuncOrPath | dict[str, TViewableFuncOrPath],
    port: int = 0,
    address: str | None = None,
    websocket_origin: str | list[str] | None = None,
    loop: asyncio.AbstractEventLoop | None = None,
    show: bool = True,
    start: bool = True,
    title: str | None = None,
    location: bool = True,
    threaded: bool = False,
    admin: bool = False,
    session_history: int | None = None,
    liveness: bool | str = False,
    **kwargs
) -> StoppableThread | Server:
    """
    Allows serving one or more panel objects on a single server.
    The panels argument should be either a Panel object or a function
    returning a Panel object or a dictionary of these two. If a
    dictionary is supplied the keys represent the slugs at which
    each app is served, e.g. `serve({'app': panel1, 'app2': panel2})`
    will serve apps at /app and /app2 on the server.

    Reference: https://panel.holoviz.org/user_guide/Server_Configuration.html#serving-multiple-apps

    Parameters
    ----------
    panel: Viewable, function or {str: Viewable or function}
      A Panel object, a function returning a Panel object or a
      dictionary mapping from the URL slug to either.
    port: int (optional, default=0)
      Allows specifying a specific port
    address : str
      The address the server should listen on for HTTP requests.
    websocket_origin: str or list(str) (optional)
      A list of hosts that can connect to the websocket.

      This is typically required when embedding a server app in
      an external web site.

      If None, "localhost" is used.
    loop : asyncio.AbstractEventLoop (optional)
      The event loop to run the Server on
    show : boolean (optional, default=True)
      Whether to open the server in a new browser tab on start
    start : boolean(optional, default=True)
      Whether to start the Server
    title: str or {str: str} (optional, default=None)
      An HTML title for the application or a dictionary mapping
      from the URL slug to a customized title
    location : boolean or panel.io.location.Location
      Whether to create a Location component to observe and
      set the URL location.
    threaded: boolean (default=False)
      Whether to start the server on a new Thread
    admin: boolean (default=False)
      Whether to enable the admin panel
    liveness: bool | str (optional, default=False)
      Whether to add a liveness endpoint. If a string is provided
      then this will be used as the endpoint, otherwise the endpoint
      will be hosted at /liveness.
    session_history: int (optional, default=None)
      The amount of session history to accumulate. If set to non-zero
      and non-None value will launch an endpoint at /session_info,
      which returns information about the session history.
    kwargs: dict
      Additional keyword arguments to pass to the PanelASGI application
    """
    kwargs = dict(kwargs, **dict(
        port=port, address=address, websocket_origin=websocket_origin,
        loop=loop, show=show, start=start, title=title,
        location=location, admin=admin, liveness=liveness,
        session_history=session_history
    ))
    if threaded:
        # To ensure that we have correspondence between state._threads and state._servers
        # we must provide a server_id here
        owns_loop = loop is None
        kwargs['loop'] = loop = asyncio.new_event_loop() if owns_loop else loop
        if 'server_id' not in kwargs:
            kwargs['server_id'] = uuid.uuid4().hex
        server = StoppableThread(
            target=get_server, io_loop=loop, args=(panels,), kwargs=kwargs, owns_loop=owns_loop
        )
        server_id = kwargs['server_id']
        state._threads[server_id] = server
        server.start()
    else:
        return get_server(panels, **kwargs)
    return server
