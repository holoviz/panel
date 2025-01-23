from __future__ import annotations

import asyncio
import socket
import uuid

from functools import wraps
from typing import TYPE_CHECKING, Any, cast

from ..config import config
from .application import build_applications
from .document import _cleanup_doc, extra_socket_handlers
from .resources import COMPONENT_PATH
from .server import ComponentResourceHandler, server_html_page_for_session
from .state import state
from .threads import StoppableThread

try:
    from bokeh_fastapi import BokehFastAPI
    from bokeh_fastapi.handler import DocHandler, WSHandler
    from fastapi import (
        FastAPI, HTTPException, Query, Request,
    )
    from fastapi.responses import FileResponse
except ImportError:
    msg = "bokeh_fastapi must be installed to use the panel.io.fastapi module."
    raise ImportError(msg) from None

if TYPE_CHECKING:
    from bokeh.application import Application as BkApplication
    from bokeh.document.events import DocumentPatchedEvent
    from bokeh.protocol.message import Message
    from uvicorn import Server

    from .application import TViewableFuncOrPath
    from .location import Location

#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------

DocHandler.render_session = server_html_page_for_session


def dispatch_fastapi(conn, events: list[DocumentPatchedEvent] | None = None, msg: Message | None = None):
    if msg is None:
        msg = conn.protocol.create("PATCH-DOC", events)
    return [conn._socket.send_message(msg)]

extra_socket_handlers[WSHandler] = dispatch_fastapi


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
    @app.get(endpoint, response_model=dict[str, int | dict[str, Any]])
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
    apps = build_applications(panel, title=title, location=location, admin=admin)
    ws_origins = kwargs.pop('websocket_origin', [])
    if ws_origins and not isinstance(ws_origins, list):
        ws_origins = [ws_origins]
    kwargs['websocket_origins'] = ws_origins

    application = BokehFastAPI(apps, app=app, **kwargs)
    if session_history is not None:
        config.session_history = session_history
        add_history_handler(application.app, endpoint='/session_info')
    if liveness:
        liveness_endpoint = liveness if isinstance(liveness, str) else '/liveness'
        add_liveness_handler(application.app, endpoint=liveness_endpoint, applications=apps)

    @application.app.get(
        f"/{COMPONENT_PATH.rstrip('/')}" + "/{path:path}", include_in_schema=False
    )
    def get_component_resource(path: str):
        # ComponentResourceHandler.parse_url_path only ever accesses
        # self._resource_attrs, which fortunately is a class attribute. Thus, we can
        # get away with using the method without actually instantiating the class
        self_ = cast(ComponentResourceHandler, ComponentResourceHandler)
        resolved_path = ComponentResourceHandler.parse_url_path(self_, path)
        return FileResponse(resolved_path)

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

    loop = kwargs.pop('loop')
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
        kwargs['loop'] = loop = asyncio.new_event_loop() if loop is None else loop
        if 'server_id' not in kwargs:
            kwargs['server_id'] = uuid.uuid4().hex
        server = StoppableThread(
            target=get_server, io_loop=loop, args=(panels,), kwargs=kwargs
        )
        server_id = kwargs['server_id']
        state._threads[server_id] = server
        server.start()
    else:
        return get_server(panels, **kwargs)
    return server
