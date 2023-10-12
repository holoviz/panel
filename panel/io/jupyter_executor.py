from __future__ import annotations

import asyncio
import os
import weakref

from dataclasses import dataclass
from typing import (
    Any, Dict, List, Union,
)

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
from .markdown import build_single_handler_application
from .resources import Resources
from .server import server_html_page_for_session
from .state import set_curdoc, state


@dataclass
class _RequestProxy:

    arguments: Dict[str, List[bytes]]
    cookies: Dict[str, str]
    headers: Dict[str, str | List[str]]

class Mimebundle:

    def __init__(self, mimebundle):
        self._mimebundle = mimebundle

    def _repr_mimebundle_(self, include=None, exclude=None):
        return self._mimebundle, {}


class PanelExecutor(WSHandler):
    """
    The PanelExecutor is intended to be run inside a kernel where it
    runs a Panel application renders the HTML and then establishes a
    Jupyter Comm channel to communicate with the PanelWSProxy in order
    to send and receive messages to and from the frontend.
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
        self._context = None

        self.resources = Resources(
            mode=os.environ.get('BOKEH_RESOURCES', 'server'), root_url=self.root_url,
            path_versioner=StaticHandler.append_version, absolute=True
        )
        self._set_state()
        try:
            self.session = self._create_server_session()
            self.connection = ServerConnection(self.protocol, self, None, self.session)
        except Exception as e:
            self.exception = e
            self.session = None

    def _get_payload(self, token: str) -> Dict[str, Any]:
        payload = get_token_payload(token)
        if ('cookies' in payload and 'headers' in payload
            and 'Cookie' not in payload['headers']):
            # Restore Cookie header from cookies dictionary
            payload['headers']['Cookie'] = '; '.join([
                f'{k}={v}' for k, v in payload['cookies'].items()
            ])
        return payload

    def _set_state(self):
        state._jupyter_kernel_context = True
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

        self._context = session_context = BokehSessionContext(
            self.session_id, None, doc
        )

        # using private attr so users only have access to a read-only property
        session_context._request = _RequestProxy(
            arguments={k: [v.encode('utf-8') for v in vs] for k, vs in self.payload.get('arguments', {}).items()},
            cookies=self.payload.get('cookies'),
            headers=self.payload.get('headers')
        )
        session_context._token = self.token

        # expose the session context to the document
        # use the _attribute to set the public property .session_context
        doc._session_context = weakref.ref(session_context)

        if self.path.endswith('.yaml') or self.path.endswith('.yml'):
            from lumen.command import (
                build_single_handler_application as build_lumen_app,
            )
            app = build_lumen_app(self.path, argv=None)
        else:
            app = build_single_handler_application(self.path)
        with set_curdoc(doc):
            app.initialize_document(doc)

        loop = tornado.ioloop.IOLoop.current()
        session = ServerSession(self.session_id, doc, io_loop=loop, token=self.token)
        session_context._set_session(session)
        return session

    async def write_message(
        self, message: Union[bytes, str, Dict[str, Any]],
        binary: bool = False, locked: bool = True
    ) -> None:
        metadata = {'binary': binary}
        if binary:
            self.comm.send({}, metadata=metadata, buffers=[message])
        else:
            self.comm.send(message, metadata=metadata)

    def render(self) -> Mimebundle:
        """
        Renders the application to an IPython.display.HTML object to
        be served by the `PanelJupyterHandler`.
        """
        if self.session is None:
            return Mimebundle({'text/error': f'Session did not start correctly: {self.exception}'})
        with set_curdoc(self.session.document):
            if not self.session.document.roots:
                return Mimebundle({
                    'text/error': (
                        "The Panel application being served did not serve any contents. "
                        "Ensure you mark one or more Panel components in your notebook or "
                        "script with .servable(), e.g. pn.Row('Hello World!').servable()."
                    )
                })
            html = server_html_page_for_session(
                self.session,
                resources=self.resources,
                title=self.session.document.title,
                template=self.session.document.template,
                template_variables=self.session.document.template_variables
            )
        return Mimebundle({
            'text/html': html,
            'application/bokeh-extensions': {
                name: str(ext) for name, ext in extension_dirs.items()
            }
        })
