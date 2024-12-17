from contextlib import contextmanager
from urllib.parse import urljoin, urlparse

try:
    from bokeh_django.consumers import AutoloadJsConsumer, DocConsumer
except Exception:
    from bokeh.server.django.consumers import AutoloadJsConsumer, DocConsumer  # type: ignore

from ..util import edit_readonly
from .resources import Resources
from .server import autoload_js_script, server_html_page_for_session
from .state import state


async def doc_handle(self, body):
    session = await self._get_session()
    resources = Resources.from_bokeh(self.resources())
    page = server_html_page_for_session(
        session, resources=resources, title=session.document.title,
        template=session.document.template,
        template_variables=session.document.template_variables
    )
    await self.send_response(200, page.encode(), headers=[(b"Content-Type", b"text/html")])


@contextmanager
def _session_prefix(consumer):
    prefix = consumer.scope.get('root_path', '').replace(consumer.application_context._url, '')
    if not prefix.endswith('/'):
        prefix += '/'
    base_url = urljoin('/', prefix)
    rel_path = '/'.join(['..'] * consumer.application_context._url.strip('/').count('/'))
    old_url, old_rel = state.base_url, state.rel_path

    # Handle autoload.js absolute paths
    abs_url = consumer.get_argument('bokeh-absolute-url', default=None)
    if abs_url is not None:
        app_path = consumer.get_argument('bokeh-app-path', default='')
        rel_path = abs_url.replace(app_path, '')

    with edit_readonly(state):
        state.base_url = base_url
        state.rel_path = rel_path
    try:
        yield
    finally:
        with edit_readonly(state):
            state.base_url = old_url
            state.rel_path = old_rel


async def autoload_handle(self, body):
    with _session_prefix(self):
        session = await self._get_session()

        element_id = self.get_argument("bokeh-autoload-element", default=None)
        if not element_id:
            raise RuntimeError("No bokeh-autoload-element query parameter")

        app_path = self.get_argument("bokeh-app-path", default="/")
        absolute_url = self.get_argument("bokeh-absolute-url", default=None)

        if absolute_url:
            server_url = f'{urlparse(absolute_url).scheme}://{urlparse(absolute_url).netloc}/'
        else:
            server_url = None

        absolute = server_url not in absolute_url
        resources = self.resources(server_url)
        js = autoload_js_script(
            session.document, resources, session.token, element_id, app_path, absolute_url, absolute=absolute
        )

    headers = [
        (b"Access-Control-Allow-Headers", b"*"),
        (b"Access-Control-Allow-Methods", b"PUT, GET, OPTIONS"),
        (b"Access-Control-Allow-Origin", b"*"),
        (b"Content-Type", b"application/javascript")
    ]
    await self.send_response(200, js.encode(), headers=headers)


DocConsumer.handle = doc_handle
AutoloadJsConsumer.handle = autoload_handle
