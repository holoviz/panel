from __future__ import annotations

import asyncio
import socket
import typing as t
import uuid

from functools import wraps

from bokeh.server.asgi import BokehASGI
from bokeh.server.core import SessionError

from ..config import config
from .application import build_applications
from .document import _cleanup_doc
from .resources import COMPONENT_PATH
from .server import (
    ComponentResourceHandler, _sanitize_route_context, _strip_prefixed_path,
    server_html_page_for_session,
)
from .state import set_curdoc, state
from .threads import StoppableThread

try:
    from fastapi import (
        FastAPI, HTTPException, Query, Request,
    )
    from fastapi.responses import FileResponse
    from starlette.routing import Route, WebSocketRoute
except ImportError as e:
    if e.name in ("fastapi", "starlette"):
        msg = "fastapi must be installed to use the panel.io.fastapi module."
        raise ImportError(msg) from None
    raise e

if t.TYPE_CHECKING:
    from bokeh.application import Application as BkApplication
    from uvicorn import Server

    from .application import TViewableFuncOrPath
    from .location import Location

#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------


def _route_context(
    request_or_scope: Request | dict[str, t.Any], suffix: str = '', prefix: str = ''
) -> tuple[dict[str, str], str | None]:
    if isinstance(request_or_scope, dict):
        path_params = request_or_scope.get('path_params') or {}
        path = request_or_scope.get('path')
    else:
        path_params = request_or_scope.path_params
        path = request_or_scope.url.path
    if path and prefix:
        path = _strip_prefixed_path(path, prefix)
        if not path.startswith('/'):
            path = '/' + path
    if path and suffix and path.endswith(suffix):
        path = path[:-len(suffix)] or '/'
    return _sanitize_route_context(path_params, path)


def _prefix_path(path: str, prefix: str) -> str:
    if not prefix:
        return path
    if not path.startswith('/'):
        path = '/' + path
    if path == '/':
        return prefix
    if path.startswith(prefix + '/') or path == prefix:
        return path
    return f"{prefix}{path}"


class _BokehRoute:

    def __init__(self, application: _PanelBokehASGI, app_path: str | None = None, suffix: str = ''):
        self.application = application
        self.app_path = app_path
        self.suffix = suffix

    async def __call__(self, scope, receive, send):
        if self.app_path is not None:
            scope = dict(scope)
            scope['_panel_app_path'] = self.app_path
            scope['_panel_app_suffix'] = self.suffix
        await self.application(scope, receive, send)


class _PanelBokehASGI(BokehASGI):

    def _route_path(self, scope):
        app_path = scope.get('_panel_app_path')
        if app_path is None:
            return super()._route_path(scope)
        suffix = scope.get('_panel_app_suffix', '')
        base = '' if app_path == '/' else app_path
        return f'{base}{suffix}' or '/'

    def _request(self, scope):
        request = super()._request(scope)
        suffix = scope.get('_panel_app_suffix', '')
        route_params, app_path = _route_context(
            scope, suffix=suffix, prefix=self.core.prefix
        )
        request.route_params = route_params
        request.app_path = app_path
        return request

    async def _document(self, context, request, send):
        method = request.method.upper()
        head = method == 'HEAD'
        if method not in ('GET', 'HEAD'):
            await self._method_not_allowed(send, ('GET', 'HEAD'))
            return
        if not await self._authenticate_http(request, send, head=head):
            return
        try:
            session = await self.core.create_session(context, request)
        except SessionError as error:
            await self._response(
                send, error.status, error.reason.encode(), 'text/plain', head=head
            )
            return
        with set_curdoc(session.document):
            resources = self.core.resources(root_path=request.root_path)
            page = server_html_page_for_session(
                session, resources=resources, title=session.document.title,
                template=session.document.template,
                template_variables=session.document.template_variables,
            )
        await self._response(
            send, 200, page.encode(), 'text/html; charset=UTF-8', head=head
        )


class BokehFastAPI:

    def __init__(
        self, applications: dict[str, BkApplication], app: FastAPI | None = None,
        prefix: str = '', **kwargs
    ):
        self.app = app or FastAPI()
        self.asgi = _PanelBokehASGI(applications, prefix=prefix, **kwargs)
        self.core = self.asgi.core

        self.app.router.add_event_handler('startup', self.core.start)
        self.app.router.add_event_handler('shutdown', self.core.stop)

        static_path = _prefix_path('/static/{path:path}', prefix)
        self.app.router.routes.append(Route(
            static_path, _BokehRoute(self.asgi), methods=['GET'],
            include_in_schema=False,
        ))

        for app_path in applications:
            route = _prefix_path(app_path, prefix)
            self.app.router.routes.append(WebSocketRoute(
                f"{route.rstrip('/')}/ws", _BokehRoute(self.asgi, app_path, '/ws')
            ))
            self.app.router.routes.append(Route(
                route, _BokehRoute(self.asgi, app_path), methods=['GET'],
                include_in_schema=False,
            ))


def add_liveness_handler(app, endpoint: str, applications: dict[str, BkApplication]):
    @app.get(endpoint, response_model=dict[str, bool])
    async def liveness_handler(request: Request, endpoint: str | None = Query(None)):
        if endpoint is not None:
            if endpoint not in applications:
                raise HTTPException(status_code=400, detail=f"Endpoint {endpoint!r} does not exist.")
            app_instance = applications[endpoint]
            try:
                doc = app_instance.create_document()
                _cleanup_doc(doc)
                return {endpoint: True}
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Endpoint {endpoint!r} could not be served. Application raised error: {e}"
                ) from e
        else:
            return {str(request.url.path): True}

def add_history_handler(app, endpoint):
    @app.get(endpoint, response_model=dict[str, int | dict[str, t.Any]])
    async def history_handler(request: Request):
        return state.session_info

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
):
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
      and non-None value will launch a REST endpoint at
      /rest/session_info, which returns information about the session
      history.
    liveness: bool | str (optional, default=False)
      Whether to add a liveness endpoint. If a string is provided
      then this will be used as the endpoint, otherwise the endpoint
      will be hosted at /liveness.
    **kwargs:
        Additional keyword arguments to pass to the BokehFastAPI application
    """
    prefix = kwargs.get('prefix', '') or ''
    if prefix:
        if not prefix.startswith('/'):
            raise ValueError("prefix must start with '/'.")
        prefix = prefix.rstrip('/') or '/'
        kwargs['prefix'] = prefix
    apps = build_applications(panel, title=title, location=location, admin=admin)
    ws_origins = kwargs.pop('websocket_origin', None)
    if ws_origins and not isinstance(ws_origins, list):
        ws_origins = [ws_origins]
    if ws_origins:
        kwargs['extra_websocket_origins'] = ws_origins

    app = app or FastAPI()

    @app.get(
        _prefix_path(f"/{COMPONENT_PATH.rstrip('/')}" + "/{path:path}", prefix),
        include_in_schema=False
    )
    def get_component_resource(path: str):
        # ComponentResourceHandler.parse_url_path only ever accesses
        # self._resource_attrs, which fortunately is a class attribute. Thus, we can
        # get away with using the method without actually instantiating the class
        self_ = t.cast("ComponentResourceHandler", ComponentResourceHandler)
        resolved_path = ComponentResourceHandler.parse_url_path(self_, path)
        return FileResponse(resolved_path)

    application = BokehFastAPI(apps, app=app, **kwargs)
    if session_history is not None:
        config.session_history = session_history
        add_history_handler(application.app, endpoint=_prefix_path('/session_info', prefix))
    if liveness:
        liveness_endpoint = liveness if isinstance(liveness, str) else '/liveness'
        add_liveness_handler(
            application.app, endpoint=_prefix_path(liveness_endpoint, prefix), applications=apps
        )

    return application


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
        Additional keyword arguments to pass to the BokehFastAPI application
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Register the Panel application after the function is defined
        add_applications(
            {path: func},
            app=app,
            title=title
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
):
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
      and non-None value will launch a REST endpoint at
      /rest/session_info, which returns information about the session
      history.
    **kwargs:
        Additional keyword arguments to pass to the BokehFastAPI application
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
    config_kwargs = {}
    if loop:
        config_kwargs['loop'] = loop
        asyncio.set_event_loop(loop)
    if port:
        config_kwargs['port'] = port
    server_id = kwargs.pop('server_id', uuid.uuid4().hex)
    application = add_applications(
        panel, title=title, location=location, admin=admin, **kwargs
    )

    if show:
        @application.app.on_event('startup')
        def show_callback():
            prefix = kwargs.get('prefix', '')
            address_string = 'localhost'
            if address is not None and address != '':
                address_string = address
            url = f"http://{address_string}:{config.port}{prefix}"
            from bokeh.util.browser import view
            view(url, new='tab')
    config = uvicorn.Config(application.app, **config_kwargs)
    server = uvicorn.Server(config)

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
    loop : tornado.ioloop.IOLoop (optional, default=IOLoop.current())
      The tornado IOLoop to run the Server on
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
      and non-None value will launch a REST endpoint at
      /rest/session_info, which returns information about the session
      history.
    kwargs: dict
      Additional keyword arguments to pass to Server instance
    """
    # Empty layout are valid and the Bokeh warning is silenced as usually
    # not relevant to Panel users.
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
