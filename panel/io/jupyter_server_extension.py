from urllib.parse import urljoin

from tornado.web import StaticFileHandler

from .resources import DIST_DIR


def load_jupyter_server_extension(notebook_app):
    web_app = notebook_app.web_app
    route_pattern = urljoin(web_app.settings["base_url"], "panel_dist/(.*)")
    web_app.add_handlers(
        host_pattern=".*$",
        host_handlers=[
            (
                route_pattern,
                StaticFileHandler,
                {"path": DIST_DIR}
            ),
        ]
    )
