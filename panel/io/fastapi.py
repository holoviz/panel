from __future__ import annotations

import asyncio
import uuid

from typing import TYPE_CHECKING, Mapping, cast

from bokeh_fastapi import BokehFastAPI
from bokeh_fastapi.handler import WSHandler
from fastapi import FastAPI
from fastapi.responses import FileResponse

from .application import build_applications
from .document import extra_socket_handlers
from .resources import COMPONENT_PATH
from .server import ComponentResourceHandler
from .state import state
from .threads import StoppableThread

if TYPE_CHECKING:
    from uvicorn import Server

    from .application import TViewableFuncOrPath
    from .location import Location


def dispatch_fastapi(conn, events=None, msg=None):
    if msg is None:
        msg = conn.protocol.create("PATCH-DOC", events)
    return [conn._socket.send_message(msg)]

extra_socket_handlers[WSHandler] = dispatch_fastapi


def add_applications(
    panel: TViewableFuncOrPath | Mapping[str, TViewableFuncOrPath],
    server: FastAPI | None = None,
    title: str | dict[str, str] | None = None,
    location: bool | Location = True,
    admin: bool = False,
    **kwargs
):
    """
    Adds application(s) to an existing uvicorn based FastAPI server.

    Arguments
    ---------
    panel: Viewable, function or {str: Viewable}
        A Panel object, a function returning a Panel object or a
        dictionary mapping from the URL slug to either.
    server: FastAPI
        FastAPI server to add Panel application(s) to
    title : str or {str: str} (optional, default=None)
        An HTML title for the application or a dictionary mapping
        from the URL slug to a customized title.
    location : boolean or panel.io.location.Location
        Whether to create a Location component to observe and
        set the URL location.
    admin: boolean (default=False)
        Whether to enable the admin panel
    **kwargs:
        Additional keyword arguments to pass to the BokehFastAPI application
    """
    apps = build_applications(panel)
    application = BokehFastAPI(apps, server=server, **kwargs)

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


def get_server(
    panel: TViewableFuncOrPath | Mapping[str, TViewableFuncOrPath],
    port: int | None = 0,
    start: bool = False,
    title: str | dict[str, str] | None = None,
    location: bool | Location = True,
    admin: bool = False,
    **kwargs
):
    """
    Creates a FastAPI server running the provided Panel application(s).

    Arguments
    ---------
    panel: Viewable, function or {str: Viewable}
        A Panel object, a function returning a Panel object or a
        dictionary mapping from the URL slug to either.
    port: int (optional, default=0)
      Allows specifying a specific port.
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
    start : boolean(optional, default=False)
      Whether to start the Server.
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

    loop = kwargs.pop('loop')
    if loop:
        asyncio.set_event_loop(loop)
    server_id = kwargs.pop('server_id', uuid.uuid4().hex)
    application = add_applications(
        panel, title=title, location=location, admin=admin, **kwargs
    )
    config = uvicorn.Config(application.app, port=port, loop=loop)
    server = uvicorn.Server(config)

    state._servers[server_id] = (server, panel, [])
    if start:
        if loop:
            try:
                loop.run_until_complete(server.serve())
            except asyncio.CancelledError:
                pass
        else:
            server.run()
    return server


def serve(
    panels: TViewableFuncOrPath | Mapping[str, TViewableFuncOrPath],
    port: int = 0,
    address: str | None = None,
    websocket_origin: str | list[str] | None = None,
    loop: asyncio.AbstractEventLoop | None = None,
    show: bool = True,
    start: bool = True,
    title: str | None = None,
    verbose: bool = True,
    location: bool = True,
    threaded: bool = False,
    admin: bool = False,
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

    Arguments
    ---------
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
    verbose: boolean (optional, default=True)
      Whether to print the address and port
    location : boolean or panel.io.location.Location
      Whether to create a Location component to observe and
      set the URL location.
    threaded: boolean (default=False)
      Whether to start the server on a new Thread
    admin: boolean (default=False)
      Whether to enable the admin panel
    kwargs: dict
      Additional keyword arguments to pass to Server instance
    """
    # Empty layout are valid and the Bokeh warning is silenced as usually
    # not relevant to Panel users.
    kwargs = dict(kwargs, **dict(
        port=port, address=address, websocket_origin=websocket_origin,
        loop=loop, show=show, start=start, title=title, verbose=verbose,
        location=location, admin=admin
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
