from urllib.parse import urljoin

import tornado

from bokeh.command.util import build_single_handler_application
from bokeh.embed.bundle import extension_dirs
from bokeh.embed.server import server_html_page_for_session
from bokeh.protocol import Protocol
from bokeh.protocol.exceptions import ProtocolError
from bokeh.protocol.receiver import Receiver
from bokeh.server.connection import ServerConnection
from bokeh.server.contexts import ApplicationContext
from bokeh.server.protocol_handler import ProtocolHandler
from bokeh.server.views.doc_handler import DocHandler
from bokeh.server.views.multi_root_static_handler import MultiRootStaticHandler
from bokeh.server.views.static_handler import StaticHandler
from bokeh.server.views.ws import WSHandler
from bokeh.server.auth_provider import NullAuth
from bokeh.util.token import get_session_id
from tornado.web import StaticFileHandler

from ..config import config
from ..util import edit_readonly
from .state import state
from .resources import DIST_DIR, Resources

_RESOURCES = None

_APPS = {

}


class ServerApplicationProxy:
    """
    A wrapper around the jupyter_server.serverapp.ServerWebApplication
    to make it compatible with the expected BokehTornado application
    API.
    """

    auth_provider = NullAuth()
    generate_session_ids = True
    sign_sessions = False
    include_headers = None
    include_cookies = None
    exclude_headers = None
    exclude_cookies = None
    session_token_expiration = 300
    secret_key = None
    websocket_origins = '*'

    def __init__(self, app, **kw):
        self._app = app

    def __getattr__(self, key):
        return getattr(self._app, key)


class PanelHandler(DocHandler):

    def __init__(self, app, request, *args, **kw):
        kw['application_context'] = None
        kw['bokeh_websocket_path'] = None
        proxy = ServerApplicationProxy(app)
        super().__init__(proxy, request, *args, **kw)

    def initialize(self, *args, **kws):
        pass

    async def get(self, path, *args, **kwargs):
        if path in _APPS:
            app, context = _APPS[path]
        else:
            if path.endswith('yml') or path.endswith('.yaml'):
                from lumen.config import config
                from lumen.command import build_single_handler_application as build_lumen
                config.dev = True
                app = build_lumen(path, argv=None)
            else:
                app = build_single_handler_application(path)
            context = ApplicationContext(app, url=path)
            context._loop = tornado.ioloop.IOLoop.current()
            _APPS[path] = (app, context)

        self.application_context = context

        session = await self.get_session()

        page = server_html_page_for_session(
            session,
            resources=RESOURCES,
            title=session.document.title,
            template=session.document.template,
            template_variables=session.document.template_variables
        )

        self.set_header("Content-Type", 'text/html')
        self.write(page)


class PanelWSHandler(WSHandler):

    def __init__(self, app, request, *args, **kw):
        kw['application_context'] = None
        proxy = ServerApplicationProxy(app)
        super().__init__(proxy, request, *args, **kw)

    def initialize(self, *args, **kwargs):
        pass

    async def open(self, path, *args, **kwargs):
        _, context = _APPS[path]

        token = self._token
        if self.selected_subprotocol != 'bokeh':
            self.close()
            raise ProtocolError("Subprotocol header is not 'bokeh'")
        elif token is None:
            self.close()
            raise ProtocolError("No token received in subprotocol header")

        session_id = get_session_id(token)

        await context.create_session_if_needed(session_id, self.request, token)
        session = context.get_session(session_id)

        try:
            protocol = Protocol()
            self.receiver = Receiver(protocol)
            self.handler = ProtocolHandler()
            self.connection = self.new_connection(protocol, context, session)
        except ProtocolError as e:
            self.close()
            raise e

        msg = self.connection.protocol.create('ACK')
        await self.send_message(msg)

    def new_connection(self, protocol, application_context, session):
        connection = ServerConnection(protocol, self, application_context, session)
        return connection

    def on_close(self):
        if self.connection is not None:
            self.connection.detach_session()


def _load_jupyter_server_extension(notebook_app):
    global RESOURCES

    base_url = notebook_app.web_app.settings["base_url"]

    # Configure Panel
    RESOURCES = Resources(
        mode="server", root_url=urljoin(base_url, 'panel-preview'),
        path_versioner=StaticHandler.append_version
    )
    config.autoreload = True
    with edit_readonly(state):
        state.base_url = '/panel-preview/'
        state.rel_path = '/panel-preview'

    # Set up handlers
    notebook_app.web_app.add_handlers(
        host_pattern=r".*$",
        host_handlers=[
            (urljoin(base_url, r"panel-preview/static/extensions/(.*)"),
             MultiRootStaticHandler, dict(root=extension_dirs)),
            (urljoin(base_url, r"panel-preview/static/(.*)"),
             StaticHandler),
            (urljoin(base_url, r"panel-preview/render/(.*)/ws"),
             PanelWSHandler),
            (urljoin(base_url, r"panel-preview/render/(.*)"),
             PanelHandler, {}),
            (urljoin(base_url, r"panel_dist/(.*)"),
             StaticFileHandler, dict(path=DIST_DIR))
        ]
    )


# compat for older versions of Jupyter
load_jupyter_server_extension = _load_jupyter_server_extension
