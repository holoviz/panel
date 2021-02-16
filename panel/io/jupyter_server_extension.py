from urllib.parse import urljoin

from notebook.notebookapp import NotebookApp
from tornado.web import StaticFileHandler
from tornado.web import Application

from .server import PANEL_DIST_DIR

print('ABC')

def load_jupyter_server_extension(notebook_app):
    web_app = notebook_app.web_app
    route_pattern = urljoin(web_app.settings["base_url"], "_panel/(.*)")
    web_app.add_handlers(
        host_pattern=".*$",
        host_handlers=[
            (route_pattern, StaticFileHandler, {"path": PANEL_DIST_DIR}),
        ]
    )
