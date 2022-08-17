from __future__ import annotations

import asyncio
import calendar
import datetime as dt
import inspect
import json
import os
import weakref

from typing import (
    Any, Awaitable, Dict, List, Union, cast,
)
from urllib.parse import urljoin

import tornado

from bokeh.command.util import build_single_handler_application
from bokeh.document import Document
from bokeh.embed.bundle import extension_dirs
from bokeh.protocol import Protocol, messages as msg
from bokeh.protocol.exceptions import (
    MessageError, ProtocolError, ValidationError,
)
from bokeh.protocol.message import Message
from bokeh.protocol.receiver import Receiver
from bokeh.server.auth_provider import NullAuth
from bokeh.server.connection import ServerConnection
from bokeh.server.contexts import BokehSessionContext
from bokeh.server.protocol_handler import ProtocolHandler
from bokeh.server.session import ServerSession
from bokeh.server.views.multi_root_static_handler import MultiRootStaticHandler
from bokeh.server.views.static_handler import StaticHandler
from bokeh.util.token import (
    generate_jwt_token, generate_session_id, get_session_id, get_token_payload,
)
from ipykernel.comm import Comm
from IPython.display import HTML
from jupyter_server.base.handlers import JupyterHandler
from tornado.web import StaticFileHandler
from tornado.websocket import WebSocketClosedError, WebSocketHandler

from ..config import config
from ..util import edit_readonly, fullpath
from .resources import DIST_DIR, Resources, _env as _pn_env
from .server import server_html_page_for_session
from .state import set_curdoc, state

_RESOURCES = None


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

    @property
    def root_dir(self):
        """
        Gets the root directory of the jupyter server app

        This is useful as the path sent received by the handler
        may be different from the root dir.
        Reference: https://github.com/holoviz/panel/issues/3170
        """
        return fullpath(self._app.settings['server_root_dir'])

    def __getattr__(self, key):
        return getattr(self._app, key)


class _RequestProxy():

    def __init__(self, arguments=None, cookies=None, headers=None):
        self._arguments = arguments
        self._cookies = cookies
        self._headers = headers

    @property
    def arguments(self):
        return self._arguments

    @property
    def cookies(self):
        return self._cookies

    @property
    def headers(self):
        return self._headers


class PanelExecutor():

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

    def _get_payload(self, token):
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

    async def send_message(self, message) -> None:
        ''' Send a Bokeh Server protocol message to the connected client.

        Args:
            message (Message) : a message to send

        '''
        try:
            await message.send(self)
        except Exception:
            pass
        return None

    async def write_message(
        self, message: Union[bytes, str, Dict[str, Any]],
        binary: bool = False, locked: bool = True
    ) -> None:
        metadata = {'binary': binary}
        if binary:
            self.comm.send({}, metadata=metadata, buffers=[binary])
        else:
            self.comm.send(message, metadata=metadata)

    def _receive_msg(self, msg):
        asyncio.ensure_future(self._receive_msg_async(msg))

    async def _receive_msg_async(self, msg):
        try:
            message = await self._receive(msg)
        except Exception as e:
            # If you go look at self._receive, it's catching the
            # expected error types... here we have something weird.
            self._internal_error(f"server failed to parse a message: {e}")
            message = None

        try:
            if message:
                work = await self._handle(message)
                print(work)
                if work:
                    await self._schedule(work)
        except Exception as e:
            self._internal_error(f"server failed to handle a message: {e}")

    async def _receive(self, msg):
        print(msg)
        try:
            message = await self.receiver.consume(msg['content']['data'])
            return message
        except (MessageError, ProtocolError, ValidationError) as e:
            self._protocol_error(str(e))
            return None
        return message

    async def _handle(self, message) -> Any | None:
        # Handle the message, possibly resulting in work to do
        try:
            work = await self.handler.handle(message, self)
            return work
        except (MessageError, ProtocolError, ValidationError) as e: # TODO (other exceptions?)
            self._internal_error(str(e))
            return None

    async def _schedule(self, work: Any) -> None:
        if isinstance(work, Message):
            await self.send_message(cast(Message[Any], work))
        else:
            self._internal_error(f"expected a Message not {work!r}")

        return None

    def ok(self, message: Message[Any]) -> msg.ok:
        return self.protocol.create('OK', message.header['msgid'])

    def error(self, message: Message[Any], text: str) -> msg.error:
        return self.protocol.create('ERROR', message.header['msgid'], text)

    def _internal_error(self, msg):
        self.comm.send(msg, {'status': 'internal_error'})

    def _protocol_error(self, msg):
                self.comm.send(msg, {'status': 'protocol_error'})

    def _create_server_session(self):
        doc = Document()

        session_context = BokehSessionContext(
            self.session_id, None, doc
        )

        # using private attr so users only have access to a read-only property
        session_context._request = _RequestProxy(
            arguments=self.payload.get('arguments'),
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

    def render(self):
        return HTML(server_html_page_for_session(
            self.session,
            resources=self.resources,
            title=self.session.document.title,
            template=self.session.document.template,
            template_variables=self.session.document.template_variables
        ))


KERNEL_TEMPLATE = """
from panel.io.jupyter_server_extension import PanelExecutor
executor = PanelExecutor('{{ path }}', '{{ token }}', '{{ root_url }}')
executor.render()
"""

class PanelHandler(JupyterHandler):

    def initialize(self, **kwargs):
        super().initialize(**kwargs)
        self.notebook_path = kwargs.pop('notebook_path', [])
        self.kernel_started = False

    async def _get_execute_result(self, kc, msg_id, timeout=60):
        while True:
            msg = await ensure_async(kc.iopub_channel.get_msg(timeout=None))
            if msg['parent_header'].get('msg_id') == msg_id:
                if msg['header']['msg_type'] == 'execute_result':
                    break
        return msg

    @tornado.web.authenticated
    async def get(self, path=None):
        notebook_path = self.notebook_path or path

        if (
            self.notebook_path and path
        ):  # when we are in single notebook mode but have a path
            self.redirect_to_file(path)
            return

        cwd = os.path.dirname(notebook_path)

        # Compose reply
        self.set_header('Content-Type', 'text/html')
        self.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.set_header('Pragma', 'no-cache')
        self.set_header('Expires', '0')

        with open(notebook_path) as f:
            nb = json.load(f)

        kernelspec = nb.get('metadata', {}).get('kernelspec', {})
        kernel_env = {**os.environ}
        kernel_id = await ensure_async(
            (
                self.kernel_manager.start_kernel(
                    kernel_name=kernelspec.get('name'),
                    path=cwd,
                    env=kernel_env,
                )
            )
        )
        kernel_future = self.kernel_manager.get_kernel(kernel_id)

        km = await ensure_async(kernel_future)
        kc = km.client()
        await ensure_async(kc.start_channels())
        await ensure_async(kc.wait_for_ready(timeout=None))

        session_id = generate_session_id()
        payload = {
            'arguments': dict(self.request.arguments.items()),
            'headers': dict(self.request.headers.items()),
            'cookies': dict(self.request.cookies.items())
        }
        token = generate_jwt_token(session_id, extra_payload=payload)

        execute_template = _pn_env.from_string(KERNEL_TEMPLATE)
        source = execute_template.render(
            path=notebook_path, token=token,
            root_url=url_path_join(self.base_url, 'panel-preview')
        )

        msg_id = kc.execute(source)
        while True:
            msg = await ensure_async(kc.iopub_channel.get_msg(timeout=None))
            if msg.get('header', {})['msg_type'] == 'comm_open' and msg['content']['target_name'] == session_id:
                comm_id = msg['content']['comm_id']
                break
        state._kernels[session_id] = (kc, comm_id)
        while True:
            msg = await ensure_async(kc.shell_channel.get_msg(timeout=None))
            if msg['parent_header'].get('msg_id') == msg_id:
                break
        msg = await self._get_execute_result(kc, msg_id)
        html = msg['content']['data']['text/html']
        self.finish(html)


class PanelWSHandler(WebSocketHandler):

    def __init__(self, tornado_app, *args, **kw) -> None:
        self.receiver = None
        self.kernel = None
        self.latest_pong = -1
        self.session_id = None

        # write_lock allows us to lock the connection to send multiple
        # messages atomically.
        self.write_lock = tornado.locks.Lock()
        self._token = None

        # Note: tornado_app is stored as self.application
        super().__init__(tornado_app, *args, **kw)

    def initialize(self):
        pass

    def select_subprotocol(self, subprotocols: List[str]) -> str | None:
        if not len(subprotocols) == 2:
            return None
        self._token = subprotocols[1]
        return subprotocols[0]

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
            self.close()
            raise e

        self.session_id = get_session_id(token)
        if self.session_id not in state._kernels:
            self.close()
        self.kernel, self.comm_id = state._kernels[self.session_id]

        msg = protocol.create('ACK')
        await self.send_message(msg)

        asyncio.create_task(self._check_for_message())

    async def _check_for_message(self):
        while True:
            msg = await ensure_async(self.kernel.iopub_channel.get_msg(timeout=None))
            if not (
                msg['header']['msg_type'] == 'comm_msg' and
                msg['content']['comm_id'] == self.comm_id
            ):
                print(msg)
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

    async def _receive(self, fragment: str | bytes) -> Message[Any] | None:
        # Receive fragments until a complete message is assembled
        try:
            message = await self.receiver.consume(fragment)
            return message
        except (MessageError, ProtocolError, ValidationError) as e:
            self._protocol_error(str(e))
            return None

    async def on_message(self, fragment: str | bytes) -> None:
        content = dict(data=fragment, comm_id=self.comm_id, target_name=self.session_id)
        msg = self.kernel.session.msg("comm_msg", content)
        self.kernel.shell_channel.send(msg)

    def on_pong(self, data: bytes) -> None:
        self.latest_pong = int(data.decode("utf-8"))

    def on_close(self) -> None:
        ''' Clean up when the connection is closed.

        '''
        pass

    async def send_message(self, message) -> None:
        ''' Send a Bokeh Server protocol message to the connected client.

        Args:
            message (Message) : a message to send

        '''
        try:
            await message.send(self)
        except WebSocketClosedError:
            pass
        return None

    async def write_message(self, message: Union[bytes, str, Dict[str, Any]],
            binary: bool = False, locked: bool = True) -> None:
        ''' Override parent write_message with a version that acquires a
        write lock before writing.

        '''
        if locked:
            with await self.write_lock.acquire():
                await super().write_message(message, binary)
        else:
            await super().write_message(message, binary)

    def _internal_error(self, message: str) -> None:
        print("Bokeh Server internal error: %s, closing connection" %message)
        self.close(10000, message)

    def _protocol_error(self, message: str) -> None:
        print("Bokeh Server protocol error: %s, closing connection" % message)
        self.close(10001, message)


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
        state.base_url = url_path_join(base_url, '/panel-preview/')
        state.rel_path = url_path_join(base_url, '/panel-preview')

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
