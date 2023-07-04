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

from queue import Empty
from typing import Any, Awaitable
from urllib.parse import urljoin

import tornado

from bokeh.embed.bundle import extension_dirs
from bokeh.protocol import Protocol
from bokeh.protocol.exceptions import ProtocolError
from bokeh.protocol.receiver import Receiver
from bokeh.server.tornado import DEFAULT_KEEP_ALIVE_MS
from bokeh.server.views.multi_root_static_handler import MultiRootStaticHandler
from bokeh.server.views.static_handler import StaticHandler
from bokeh.server.views.ws import WSHandler
from bokeh.util.token import (
    generate_jwt_token, generate_session_id, get_session_id, get_token_payload,
)
from jupyter_server.base.handlers import JupyterHandler
from tornado.ioloop import PeriodicCallback
from tornado.web import StaticFileHandler

from ..config import config
from .resources import DIST_DIR, ERROR_TEMPLATE, _env
from .state import state

logger = logging.getLogger(__name__)

KERNEL_TIMEOUT = 60 # Timeout for kernel startup (including app startup)
CONNECTION_TIMEOUT = 30 # Timeout for WS connection to open

KERNEL_ERROR_TEMPLATE = _env.get_template('kernel_error.html')

async def ensure_async(obj: Awaitable | Any) -> Any:
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

def get_server_root_dir(settings):
    if 'server_root_dir' in settings:
        # notebook >= 5.0.0 has this in the settings
        root_dir = settings['server_root_dir']
    else:
        # This copies the logic added in the notebook in
        #  https://github.com/jupyter/notebook/pull/2234
        contents_manager = settings['contents_manager']
        root_dir = contents_manager.root_dir
    return os.path.expanduser(root_dir)

EXECUTION_TEMPLATE = """
import os
import pathlib
import sys

app = r'{{ path }}'
os.chdir(str(pathlib.Path(app).parent))
sys.path = [os.getcwd()] + sys.path[1:]

from panel.io.jupyter_executor import PanelExecutor
executor = PanelExecutor(app, '{{ token }}', '{{ root_url }}')
executor.render()
"""

def generate_executor(path: str, token: str, root_url: str) -> str:
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
    execute_template = _env.from_string(EXECUTION_TEMPLATE)
    return textwrap.dedent(
        execute_template.render(path=path, token=token, root_url=root_url)
    )

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
                    raise RuntimeError("Kernel died before establishing Comm connection to Panel application.")
                continue
            if msg['parent_header'].get('msg_id') != msg_id:
                continue
            msg_type = msg['header']['msg_type']
            if msg_type == 'execute_result':
                data = msg['content']['data']
                if 'text/error' in data:
                    raise RuntimeError(data['text/error'])
                extension_dirs = data['application/bokeh-extensions']
                result = data['text/html']
            elif msg_type == 'comm_open' and msg['content']['target_name'] == self.session_id:
                comm_id = msg['content']['comm_id']
            elif msg_type == 'stream' and msg['content']['name'] == 'stderr':
                logger.error(msg['content']['text'])
            elif msg_type == "error":
                logger.error(msg['content']['traceback'])
        return result, comm_id, extension_dirs

    @tornado.web.authenticated
    async def get(self, path=None):
        root_dir = get_server_root_dir(self.application.settings)
        rel_path = pathlib.Path(self.notebook_path or path)
        if rel_path.is_absolute():
            notebook_path = str(rel_path)
        else:
            notebook_path = str((root_dir / rel_path).absolute())

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
        source = generate_executor(notebook_path, token, root_url)
        msg_id = self.kernel.execute(source)

        # Wait for comm to open and rendered HTML to be returned by the kernel
        try:
            html, comm_id, ext_dirs = await self._get_info(msg_id)
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

            msg_type = msg['header']['msg_type']
            if msg_type == 'stream' and msg['content']['name'] == 'stderr':
                logger.error(msg['content']['text'])
                continue
            elif not (msg_type == 'comm_msg' and msg['content']['comm_id'] == self.comm_id):
                continue
            content, metadata = msg['content'], msg['metadata']
            status = metadata.get('status')

            if status == 'protocol_error':
                return self._protocol_error(content['data'])
            elif status == 'internal_error':
                return self._internal_error(content['data'])
            binary = metadata.get('binary')
            if binary:
                fragment = msg['buffers'][0].tobytes()
            else:
                fragment = content['data']
                if isinstance(fragment, dict):
                    fragment = json.dumps(fragment)
            message = await self._receive(fragment)
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
        self._shutdown_futures = [
            asyncio.ensure_future(self.kernel.shutdown(reply=True)),
            asyncio.ensure_future(self.kernel_manager.shutdown_kernel(self.kernel_id, now=True))
        ]
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
