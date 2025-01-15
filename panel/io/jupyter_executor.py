from __future__ import annotations

import asyncio
import html
import os
import weakref

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import tornado

from bokeh.document import Document
from bokeh.embed.bundle import extension_dirs
from bokeh.protocol import Protocol
from bokeh.protocol.receiver import Receiver
from bokeh.server.connection import ServerConnection
from bokeh.server.contexts import BokehSessionContext
from bokeh.server.protocol_handler import ProtocolHandler
from bokeh.server.session import ServerSession
from bokeh.server.views.static_handler import StaticHandler
from bokeh.server.views.ws import WSHandler
from bokeh.util.token import get_session_id, get_token_payload
from ipykernel.comm import Comm

from ..util import edit_readonly
from .application import build_single_handler_application
from .resources import Resources
from .server import server_html_page_for_session
from .state import set_curdoc, state

if TYPE_CHECKING:
    from bokeh.document.events import DocumentPatchedEvent


@dataclass
class _RequestProxy:

    arguments: dict[str, list[bytes]]
    cookies: dict[str, str]
    headers: dict[str, str | list[str]]

class Mimebundle:

    def __init__(self, mimebundle):
        self._mimebundle = mimebundle

    def _repr_mimebundle_(self, include=None, exclude=None):
        return self._mimebundle, {}


class JupyterServerSession(ServerSession):

    _tasks: set[asyncio.Task] = set()

    def _document_patched(self, event: DocumentPatchedEvent) -> None:
        may_suppress = event.setter is self
        for connection in self._subscribed_connections:
            if may_suppress and connection is self._current_patch_connection:
                continue
            task = asyncio.ensure_future(connection.send_patch_document(event))
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)


class PanelExecutor(WSHandler):
    """
    The PanelExecutor is intended to be run inside a kernel where it
    runs a Panel application renders the HTML and then establishes a
    Jupyter Comm channel to communicate with the PanelWSProxy in order
    to send and receive messages to and from the frontend.
    """

    _tasks: set[asyncio.Task] = set()

    def __init__(self, path, token, root_url, resources='server'):
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
        self._context = None

        resources = os.environ.get('BOKEH_RESOURCES', resources)
        root_url = self.root_url if resources == 'server' else None
        self.resources = Resources(
            mode=resources, root_url=root_url,
            path_versioner=StaticHandler.append_version, absolute=True
        )
        self._set_state()
        try:
            self.session, self._error = self._create_server_session()
            self.connection = ServerConnection(self.protocol, self, None, self.session)
        except Exception as e:
            self.exception = e
            self.session = None

    def _get_payload(self, token: str) -> dict[str, Any]:
        payload = get_token_payload(token)
        if ('cookies' in payload and 'headers' in payload
            and 'Cookie' not in payload['headers']):
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
        task = asyncio.ensure_future(self._receive_msg_async(msg))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

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

    def _create_server_session(self) -> tuple[ServerSession, str | None]:
        doc = Document()

        self._context = session_context = BokehSessionContext(
            self.session_id, None, doc  # type: ignore
        )

        # using private attr so users only have access to a read-only property
        session_context._request = _RequestProxy(  # type: ignore
            arguments={k: [v.encode('utf-8') for v in vs] for k, vs in self.payload.get('arguments', {}).items()},
            cookies=self.payload.get('cookies'),
            headers=self.payload.get('headers')
        )
        session_context._token = self.token

        # expose the session context to the document
        # use the _attribute to set the public property .session_context
        doc._session_context = weakref.ref(session_context)
        state._jupyter_kernel_context = session_context

        if self.path.endswith('.yaml') or self.path.endswith('.yml'):
            from lumen.command import (
                build_single_handler_application as build_lumen_app,
            )
            app = build_lumen_app(self.path, argv=None)
        else:
            app = build_single_handler_application(self.path)
        with set_curdoc(doc):
            app.initialize_document(doc)

        runner = app._handlers[0]._runner
        loop = tornado.ioloop.IOLoop.current()
        session = JupyterServerSession(self.session_id, doc, io_loop=loop, token=self.token)
        session_context._set_session(session)
        return session, runner.error_detail

    async def write_message(  # type: ignore
        self, message: bytes | str | dict[str, Any],
        binary: bool = False, locked: bool = True
    ) -> None:
        metadata = {'binary': binary}
        if locked:
            with await self.write_lock.acquire():
                if binary:
                    self.comm.send({}, metadata=metadata, buffers=[message])
                else:
                    self.comm.send(message, metadata=metadata)
        else:
            if binary:
                self.comm.send({}, metadata=metadata, buffers=[message])
            else:
                self.comm.send(message, metadata=metadata)

    def render_mime(self) -> Mimebundle:
        """
        Renders the application to an IPython.display.HTML object to
        be served by the `PanelJupyterHandler`.
        """
        if self.session is None:
            return Mimebundle({'text/error': f'Session did not start correctly: {self.exception}'})
        with set_curdoc(self.session.document):
            if not self.session.document.roots:
                if self._error:
                    lines = self._error.split('\n')
                    error = html.escape('\n'.join(lines[:1]+lines[3:]))
                    return Mimebundle({
                        'text/error': (
                            "<span>Application errored while starting up:</span>"
                            "<br><br>"
                            "<div style='overflow: auto'>"
                            f"  <code style='font-size: 0.75em; white-space: pre;'>{error}</code>"
                            "</div>"
                        )
                    })
                return Mimebundle({
                    'text/error': (
                        "The Panel application being served did not serve any contents. "
                        "Ensure you mark one or more Panel components in your notebook or "
                        "script with .servable(), e.g. pn.Row('Hello World!').servable()."
                    )
                })
            html_page = server_html_page_for_session(
                self.session,
                resources=self.resources,
                title=self.session.document.title,
                template=self.session.document.template,
                template_variables=self.session.document.template_variables
            )
        return Mimebundle({
            'text/html': html_page,
            'application/bokeh-extensions': {
                name: str(ext) for name, ext in extension_dirs.items()
            }
        })
