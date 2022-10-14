"""
The Panel jupyter_server_extension implements Jupyter RequestHandlers
that allow a Panel application to run inside Jupyter kernels. This
allows Panel applications to be served in the kernel (and therefore
the environment) they were written for.

The `PanelJupyterHandler` may be given the path to a notebook, .py
file or Lumen .yaml file. It will then attempt to resolve the
appropriate kernel based on the kernelspec or a query parameter. Once
the kernel has been provisioned the handler will execute a code snippet
on the kernel which creates a `PanelExecutor`. The `PanelExecutor`
creates a `bokeh.server.session.ServerSession` and connects it to a
Jupyter Comm. The `PanelJupyterHandler` will then serve the result of
executor.render().

Once the frontend has rendered the HTML it will send a request to open
a WebSocket will be sent to the `PanelWSProxy`. This in turns forwards
any messages it receives via the kernel.shell_channel and the Comm to
the PanelExecutor. This way we proxy any WS messages being sent to and
from the server to the kernel.
"""

from __future__ import annotations

import asyncio
import calendar
import datetime as dt
import inspect
import json
import logging
import os
import pathlib
import textwrap
import time
import weakref

from dataclasses import dataclass
from queue import Empty
from typing import (
    Any, Awaitable, Dict, List, Union,
)
from urllib.parse import urljoin

import tornado

from bokeh.command.util import build_single_handler_application
from bokeh.document import Document
from bokeh.embed.bundle import extension_dirs
from bokeh.protocol import Protocol
from bokeh.protocol.exceptions import ProtocolError
from bokeh.protocol.receiver import Receiver
from bokeh.server.connection import ServerConnection
from bokeh.server.contexts import BokehSessionContext
from bokeh.server.protocol_handler import ProtocolHandler
from bokeh.server.session import ServerSession
from bokeh.server.tornado import DEFAULT_KEEP_ALIVE_MS
from bokeh.server.views.multi_root_static_handler import MultiRootStaticHandler
from bokeh.server.views.static_handler import StaticHandler
from bokeh.server.views.ws import WSHandler
from bokeh.util.token import (
    generate_jwt_token, generate_session_id, get_session_id, get_token_payload,
)
from ipykernel.comm import Comm
from IPython.display import HTML, publish_display_data
from jupyter_server.base.handlers import JupyterHandler
from tornado.ioloop import PeriodicCallback
from tornado.web import StaticFileHandler

from ..config import config
from ..util import edit_readonly
from .resources import (
    DIST_DIR, ERROR_TEMPLATE, Resources, _env,
)
from .server import server_html_page_for_session
from .state import set_curdoc, state

logger = logging.getLogger(__name__)

KERNEL_TIMEOUT = 60 # Timeout for kernel startup (including app startup)
CONNECTION_TIMEOUT = 30 # Timeout for WS connection to open

KERNEL_ERROR_TEMPLATE = _env.get_template('kernel_error.html')

async def ensure_async(obj: Union[Awaitable, Any]) -> Any:
    """Convert a non-awaitable object to a coroutine if needed,
    and await it if it was not already awaited.
    """
    if inspect.isawaitable(obj):
        try:
            result = await obj
        except RuntimeError as e:
            if str(e) == 'cannot reuse already awaited coroutine':
                # obj is already the coroutine's result
                return obj
            raise
        return result
    # obj doesn't need to be awaited
    return obj

def url_path_join(*pieces):
    """Join components of url into a relative url
    Use to prevent double slash when joining subpath. This will leave the
    initial and final / in place
    """
    initial = pieces[0].startswith('/')
    final = pieces[-1].endswith('/')
    stripped = [s.strip('/') for s in pieces]
    result = '/'.join(s for s in stripped if s)
    if initial: result = '/' + result
    if final: result = result + '/'
    if result == '//': result = '/'
    return result


@dataclass
class _RequestProxy:

    arguments: Dict[str, List[bytes]]
    cookies: Dict[str, str]
    headers: Dict[str, str | List[str]]


class PanelExecutor(WSHandler):
    """
    The PanelExecutor is intended to be run inside a kernel where it
    runs a Panel application renders the HTML and then establishes a
    Jupyter Comm channel to communicate with the PanelWSProxy in order
    to send and receive messages to and from the frontend.
    """

    _code = """
    from panel.io.jupyter_server_extension import PanelExecutor
    executor = PanelExecutor('{{ path }}', '{{ token }}', '{{ root_url }}')
    executor.render()
    """

    def __init__(self, path, token, root_url):
        self.path = path
        self.token = token
        self.root_url = root_url
        self.payload = self._get_payload(token)
        self.session_id = get_session_id(token)
        self.comm = Comm(target_name=self.session_id)
        self.comm.on_msg(self._receive_msg)
        self.protocol = Protocol()
        self.receiver = Receiver(self.protocol)
        self.handler = ProtocolHandler()
        self.write_lock = tornado.locks.Lock()

        self.resources = Resources(
            mode="server", root_url=self.root_url,
            path_versioner=StaticHandler.append_version
        )
        self._set_state()
        self.session = self._create_server_session()
        self.connection = ServerConnection(self.protocol, self, None, self.session)
        publish_display_data({'application/bokeh-extensions': extension_dirs})

    def _get_payload(self, token: str) -> Dict[str, Any]:
        payload = get_token_payload(token)
        if ('cookies' in payload and 'headers' in payload
            and not 'Cookie' in payload['headers']):
            # Restore Cookie header from cookies dictionary
            payload['headers']['Cookie'] = '; '.join([
                f'{k}={v}' for k, v in payload['cookies'].items()
            ])
        return payload

    def _set_state(self):
        with edit_readonly(state):
            state.base_url = self.root_url + '/'
            state.rel_path = self.root_url

    def _receive_msg(self, msg) -> None:
        asyncio.ensure_future(self._receive_msg_async(msg))

    async def _receive_msg_async(self, msg) -> None:
        try:
            message = await self._receive(msg['content']['data'])
        except Exception as e:
            # If you go look at self._receive, it's catching the
            # expected error types... here we have something weird.
            self._internal_error(f"server failed to parse a message: {e}")
            message = None

        try:
            if message:
                work = await self._handle(message)
                if work:
                    await self._schedule(work)
        except Exception as e:
            self._internal_error(f"server failed to handle a message: {e}")

    def _internal_error(self, msg: str) -> None:
        self.comm.send(msg, {'status': 'internal_error'})

    def _protocol_error(self, msg: str) -> None:
        self.comm.send(msg, {'status': 'protocol_error'})

    def _create_server_session(self) -> ServerSession:
        doc = Document()

        session_context = BokehSessionContext(
            self.session_id, None, doc
        )

        # using private attr so users only have access to a read-only property
        session_context._request = _RequestProxy(
            arguments={k: [v.encode('utf-8') for v in vs] for k, vs in self.payload.get('arguments', {})},
            cookies=self.payload.get('cookies'),
            headers=self.payload.get('headers')
        )
        session_context._token = self.token

        # expose the session context to the document
        # use the _attribute to set the public property .session_context
        doc._session_context = weakref.ref(session_context)

        app = build_single_handler_application(self.path)
        with set_curdoc(doc):
            app.initialize_document(doc)

        loop = tornado.ioloop.IOLoop.current()
        session = ServerSession(self.session_id, doc, io_loop=loop, token=self.token)
        session_context._set_session(session)
        return session

    @classmethod
    def code(cls, path: str, token: str, root_url: str) -> str:
        """
        Generates the code to instantiate a PanelExecutor that is to
        be be run on the kernel to start a server session.

        Arguments
        ---------
        path: str
            The path of the Panel application to execute.
        token: str
            The Bokeh JWT token containing the session_id, request arguments,
            headers and cookies.
        root_url: str
            The root_url the server is running on.

        Returns
        -------
        The code to be executed inside the kernel.
        """
        execute_template = _env.from_string(cls._code)
        return textwrap.dedent(
            execute_template.render(path=path, token=token, root_url=root_url)
        )

    async def write_message(
        self, message: Union[bytes, str, Dict[str, Any]],
        binary: bool = False, locked: bool = True
    ) -> None:
        metadata = {'binary': binary}
        if binary:
            self.comm.send({}, metadata=metadata, buffers=[binary])
        else:
            self.comm.send(message, metadata=metadata)

    def render(self) -> HTML:
        """
        Renders the application to an IPython.display.HTML object to
        be served by the `PanelJupyterHandler`.
        """
        return HTML(server_html_page_for_session(
            self.session,
            resources=self.resources,
            title=self.session.document.title,
            template=self.session.document.template,
            template_variables=self.session.document.template_variables
        ))


class PanelJupyterHandler(JupyterHandler):
    """
    The PanelJupyterHandler expects to be given a path to a notebook,
    .py file or Lumen .yaml file. Based on the kernelspec in the
    notebook or the kernel query parameter it will then provision
    a Jupyter kernel to run the Panel application in.

    Once the kernel is launched it will instantiate a PanelExecutor
    inside the kernel and serve the HTML returned by it. If successful
    it will store the kernel and comm_id on `panel.state`.
    """

    def initialize(self, **kwargs):
        super().initialize(**kwargs)
        self.notebook_path = kwargs.pop('notebook_path', [])
        self.kernel_started = False

    async def _get_info(self, msg_id, timeout=KERNEL_TIMEOUT):
        deadline = time.monotonic() + timeout
        result, comm_id, extension_dirs = None, None, None
        while result is None or comm_id is None or extension_dirs is None:
            if time.monotonic() > deadline:
                raise TimeoutError('Timed out while waiting for kernel to open Comm channel to Panel application.')
            try:
                msg = await ensure_async(self.kernel.iopub_channel.get_msg(timeout=None))
            except Empty:
                if not await ensure_async(self.kernel.is_alive()):
                    raise RuntimeError("Kernel died before establishing Comm connection to Panel app.")
                continue
            if msg['parent_header'].get('msg_id') != msg_id:
                continue
            msg_type = msg['header']['msg_type']
            if msg_type == 'display_data' and 'application/bokeh-extensions' in msg['content']['data']:
                extension_dirs = msg['content']['data']['application/bokeh-extensions']
            elif msg_type == 'execute_result':
                result = msg
            elif msg_type == 'comm_open' and msg['content']['target_name'] == self.session_id:
                comm_id = msg['content']['comm_id']
        return result, comm_id, extension_dirs

    @tornado.web.authenticated
    async def get(self, path=None):
        notebook_path = str(pathlib.Path(self.notebook_path or path).absolute())

        if (
            self.notebook_path and path
        ):  # when we are in single notebook mode but have a path
            self.redirect_to_file(path)
            return

        cwd = os.path.dirname(notebook_path)
        root_url = url_path_join(self.base_url, 'panel-preview')

        # Compose reply
        self.set_header('Content-Type', 'text/html')
        self.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.set_header('Pragma', 'no-cache')
        self.set_header('Expires', '0')

        # Provision a kernel with the desired kernelspec
        if self.request.arguments.get('kernel'):
            requested_kernel = self.request.arguments.pop('kernel')[0].decode('utf-8')
        elif notebook_path.endswith('.ipynb'):
            with open(notebook_path) as f:
                nb = json.load(f)
            requested_kernel = nb.get('metadata', {}).get('kernelspec', {}).get('name')
        else:
            requested_kernel = None

        if requested_kernel:
            available_kernels = list(self.kernel_manager.kernel_spec_manager.find_kernel_specs())
            if requested_kernel not in available_kernels:
                logger.error('Could not start server session, no such kernel %r.', requested_kernel)
                html = KERNEL_ERROR_TEMPLATE.render(
                    base_url=f'{root_url}/',
                    kernels=available_kernels,
                    error_type='Kernel error',
                    error=f"No such kernel '{requested_kernel}'",
                    title='Panel: Kernel not found'
                )
                self.finish(html)
                return
        kernel_env = {**os.environ}
        kernel_id = await ensure_async(
            (
                self.kernel_manager.start_kernel(
                    kernel_name=requested_kernel,
                    path=cwd,
                    env=kernel_env,
                )
            )
        )
        kernel_future = self.kernel_manager.get_kernel(kernel_id)
        km = await ensure_async(kernel_future)
        self.kernel = km.client()
        await ensure_async(self.kernel.start_channels())
        await ensure_async(self.kernel.wait_for_ready(timeout=None))

        # Run PanelExecutor inside the kernel
        self.session_id = generate_session_id()
        args = {
            k: [v.decode('utf-8') for v in vs]
            for k, vs in self.request.arguments.items()
        }
        payload = {
            'arguments': args,
            'headers': dict(self.request.headers.items()),
            'cookies': dict(self.request.cookies.items())
        }
        token = generate_jwt_token(self.session_id, extra_payload=payload)
        source = PanelExecutor.code(notebook_path, token, root_url)
        msg_id = self.kernel.execute(source)

        # Wait for comm to open and rendered HTML to be returned by the kernel
        try:
            msg, comm_id, ext_dirs = await self._get_info(msg_id)
        except (TimeoutError, RuntimeError) as e:
            await self.kernel_manager.shutdown_kernel(kernel_id, now=True)
            html = ERROR_TEMPLATE.render(
                npm_cdn=config.npm_cdn,
                base_url=f'{root_url}/',
                error_type="Kernel error",
                error="Failed to start kernel",
                error_msg=str(e),
                title="Panel: Kernel Error"
            )
            self.finish(html)
        else:
            # Sync extension_dirs from kernel to ensure dynamically loaded extensions are served
            extension_dirs.update(ext_dirs)
            state._kernels[self.session_id] = (self.kernel, comm_id, kernel_id, False)
            loop = tornado.ioloop.IOLoop.current()
            loop.call_later(CONNECTION_TIMEOUT, self._check_connected)
            html = msg['content']['data']['text/html']
            self.finish(html)

    async def _check_connected(self):
        if self.session_id not in state._kernels:
            return
        _, _, kernel_id, connected = state._kernels[self.session_id]
        if not connected:
            await self.kernel_manager.shutdown_kernel(kernel_id, now=True)



class PanelWSProxy(WSHandler, JupyterHandler):
    """
    The PanelWSProxy serves as a proxy between the frontend and the
    Jupyter kernel that is running the Panel application. It send and
    receives Bokeh protocol messages via a Jupyter Comm.
    """

    def __init__(self, tornado_app, *args, **kw) -> None:
        # Note: tornado_app is stored as self.application
        kw['application_context'] = None
        super().__init__(tornado_app, *args, **kw)

    def initialize(self, *args, **kwargs):
        self._ping_count = 0
        self._ping_job = PeriodicCallback(self._keep_alive, DEFAULT_KEEP_ALIVE_MS)

    def _keep_alive(self):
        self.ping(str(self._ping_count).encode("utf-8"))
        self._ping_count += 1

    async def prepare(self):
        pass

    def get_current_user(self):
        return "default_user"

    def check_origin(self, origin: str) -> bool:
        return True

    @tornado.web.authenticated
    async def open(self, path, *args, **kwargs) -> None:
        ''' Initialize a connection to a client.

        Returns:
            None

        '''
        token = self._token

        if self.selected_subprotocol != 'bokeh':
            self.close()
            raise ProtocolError("Subprotocol header is not 'bokeh'")
        elif token is None:
            self.close()
            raise ProtocolError("No token received in subprotocol header")

        now = calendar.timegm(dt.datetime.utcnow().utctimetuple())
        payload = get_token_payload(token)
        if 'session_expiry' not in payload:
            self.close()
            raise ProtocolError("Session expiry has not been provided")
        elif now >= payload['session_expiry']:
            self.close()
            raise ProtocolError("Token is expired.")

        try:
            protocol = Protocol()
            self.receiver = Receiver(protocol)
        except ProtocolError as e:
            logger.error("Could not create new server session, reason: %s", e)
            self.close()
            raise e

        self.session_id = get_session_id(token)
        if self.session_id not in state._kernels:
            self.close()
        kernel_info = state._kernels[self.session_id]
        self.kernel, self.comm_id, self.kernel_id, _ = kernel_info
        state._kernels[self.session_id] = kernel_info[:-1] + (True,)

        msg = protocol.create('ACK')
        await self.send_message(msg)

        self._ping_job.start()
        asyncio.create_task(self._check_for_message())

    async def _check_for_message(self):
        while True:
            if self.kernel is None:
                break
            try:
                msg = await ensure_async(self.kernel.iopub_channel.get_msg(timeout=None))
            except Empty:
                if not await ensure_async(self.kernel.is_alive()):
                    raise RuntimeError("Kernel died before expected shutdown of Panel app.")
                continue
            if not (
                msg['header']['msg_type'] == 'comm_msg' and
                msg['content']['comm_id'] == self.comm_id
            ):
                continue
            content, metadata = msg['content'], msg['metadata']
            status = metadata.get('status')

            if status == 'protocol_error':
                return self._protocol_error(content['data'])
            elif status == 'internal_error':
                return self._internal_error(content['data'])
            binary = metadata.get('binary')
            if binary:
                data = msg['buffers'][0]
            else:
                data = content['data']
            message = await self._receive(data)
            if message:
                await self.send_message(message)

    async def on_message(self, fragment: str | bytes) -> None:
        content = dict(data=fragment, comm_id=self.comm_id, target_name=self.session_id)
        msg = self.kernel.session.msg("comm_msg", content)
        self.kernel.shell_channel.send(msg)

    def on_close(self) -> None:
        """
        Clean up when the connection is closed.
        """
        logger.info('WebSocket connection closed: code=%s, reason=%r', self.close_code, self.close_reason)
        if self.session_id in state._kernels:
            del state._kernels[self.session_id]
        self._ping_job.stop()
        future = self.kernel_manager.shutdown_kernel(self.kernel_id, now=True)
        asyncio.ensure_future(future)
        self.kernel = None


def _load_jupyter_server_extension(notebook_app):
    base_url = notebook_app.web_app.settings["base_url"]

    # Set up handlers
    notebook_app.web_app.add_handlers(
        host_pattern=r".*$",
        host_handlers=[
            (urljoin(base_url, r"panel-preview/static/extensions/(.*)"),
             MultiRootStaticHandler, dict(root=extension_dirs)),
            (urljoin(base_url, r"panel-preview/static/(.*)"),
             StaticHandler),
            (urljoin(base_url, r"panel-preview/render/(.*)/ws"),
             PanelWSProxy),
            (urljoin(base_url, r"panel-preview/render/(.*)"),
             PanelJupyterHandler, {}),
            (urljoin(base_url, r"panel_dist/(.*)"),
             StaticFileHandler, dict(path=DIST_DIR))
        ]
    )


# compat for older versions of Jupyter
load_jupyter_server_extension = _load_jupyter_server_extension
