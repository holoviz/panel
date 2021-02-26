from urllib.parse import urlparse

from bokeh.server.django.consumers import DocConsumer, AutoloadJsConsumer

from .resources import Resources
from .server import (
    autoload_js_script, server_html_page_for_session
)

async def doc_handle(self, body):
    session = await self._get_session()
    resources = Resources.from_bokeh(self.application.resources())
    page = server_html_page_for_session(
        session, resources=resources, title=session.document.title,
        template=session.document.template,
        template_variables=session.document.template_variables
    )
    await self.send_response(200, page.encode(), headers=[(b"Content-Type", b"text/html")])


async def autoload_handle(self, body):
    session = await self._get_session()

    element_id = self.get_argument("bokeh-autoload-element", default=None)
    if not element_id:
        raise RuntimeError("No bokeh-autoload-element query parameter")

    app_path = self.get_argument("bokeh-app-path", default="/")
    absolute_url = self.get_argument("bokeh-absolute-url", default=None)

    if absolute_url:
        server_url = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(absolute_url))
    else:
        server_url = None

    resources = self.resources(server_url)
    js = autoload_js_script(resources, session.token, element_id, app_path, absolute_url)

    headers = [
        (b"Access-Control-Allow-Headers", b"*"),
        (b"Access-Control-Allow-Methods", b"PUT, GET, OPTIONS"),
        (b"Access-Control-Allow-Origin", b"*"),
        (b"Content-Type", b"application/javascript")
    ]
    await self.send_response(200, js.encode(), headers=headers)


DocConsumer.handle = doc_handle
AutoloadJsConsumer.handle = autoload_handle
