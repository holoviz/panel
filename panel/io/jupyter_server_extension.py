from urllib.parse import urljoin

import tornado

from bokeh.command.util import build_single_handler_application
from bokeh.embed.bundle import extension_dirs
from bokeh.embed.server import server_html_page_for_session
from bokeh.protocol import Protocol
from bokeh.protocol.exceptions import MessageError, ProtocolError, ValidationError
from bokeh.protocol.receiver import Receiver
from bokeh.server.connection import ServerConnection
from bokeh.server.contexts import ApplicationContext
from bokeh.server.protocol_handler import ProtocolHandler
from bokeh.server.views.doc_handler import DocHandler
from bokeh.server.views.multi_root_static_handler import MultiRootStaticHandler
from bokeh.server.views.static_handler import StaticHandler
from bokeh.server.views.ws import WSHandler
from bokeh.server.auth_provider import NullAuth
from tornado.web import StaticFileHandler, RequestHandler

from ..util import edit_readonly
from .state import state
from .resources import DIST_DIR, Resources


_sessions = {
}

_RESOURCES = None


class PanelHandler(DocHandler):

    def __init__(self, *args, **kw):
        kw['application_context'] = None
        kw['bokeh_websocket_path'] = None
        super().__init__(*args, **kw)
        app = self.application
        app.auth_provider = NullAuth()
        app.generate_session_ids = True
        app.sign_sessions = False
        app.include_headers = None
        app.include_cookies = None
        app.exclude_headers = None
        app.exclude_cookies = None
        app.session_token_expiration = 300
        app.secret_key = None

    def initialize(self, *args, **kws):
        pass

    async def get(self, *args, **kwargs):
        path = self.request.path.split('panel-preview/render/')[-1]

        app = build_single_handler_application(path)
        context = ApplicationContext(app, url=path)
        context._loop = tornado.ioloop.IOLoop.current()
        self.application_context = context

        _sessions[path] = session = await self.get_session()

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

    def __init__(self, *args, **kw):
        kw['application_context'] = None
        super().__init__(*args, **kw)
        app = self.application
        self.application.websocket_origins = '*'

    def initialize(self, *args, **kws):
        print(args)

    async def open(self, *args, **kwargs):
        try:
            session = list(_sessions.values())[0] # FIX
            protocol = Protocol()
            self.receiver = Receiver(protocol)
            self.handler = ProtocolHandler()
            self.connection = self.new_connection(
                protocol, self.application_context, session)
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
    render_route = urljoin(base_url, r"panel-preview/render/(.*)\.ipynb")
    ws_route = urljoin(base_url, r"panel-preview/render/(.*)/ws")
    ext_route = urljoin(base_url, r"panel-preview/static/extensions/(.*)")
    static_route = urljoin(base_url, r"panel-preview/static/(.*)") 
    dist_route = urljoin(base_url, r"panel_dist/(.*)")
    
    RESOURCES = Resources(
        mode="server", root_url=urljoin(base_url, 'panel-preview'),
        path_versioner=StaticHandler.append_version
    )

    with edit_readonly(state):
        state.base_url = '/panel-preview/'
        state.rel_path = '/panel-preview'

    print(extension_dirs)

    notebook_app.web_app.add_handlers(
        host_pattern=r".*$",
        host_handlers=[
            (ext_route, MultiRootStaticHandler, dict(root=extension_dirs)),
            (static_route, StaticHandler),
            (ws_route, PanelWSHandler),
            (render_route, PanelHandler, {}),
            (dist_route, StaticFileHandler, dict(path=DIST_DIR))
        ]
    )


# compat for older versions of Jupyter
load_jupyter_server_extension = _load_jupyter_server_extension
