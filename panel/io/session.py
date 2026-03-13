from __future__ import annotations

import asyncio
import logging
import threading
import weakref

from typing import TYPE_CHECKING

from bokeh.document import Document
from bokeh.protocol.exceptions import ProtocolError
from bokeh.server.contexts import (
    ApplicationContext, BokehSessionContext, _RequestProxy,
)
from bokeh.server.session import ServerSession
from bokeh.settings import settings
from bokeh.util.token import (
    generate_jwt_token, generate_session_id, get_token_payload,
)

if TYPE_CHECKING:
    from bokeh.core.types import ID
    from bokeh.document.events import DocumentPatchedEvent
    from bokeh.server.callbacks import SessionCallback
    from tornado.httputil import HTTPServerRequest

from .state import state

log = logging.getLogger(__name__)

class ServerSessionStub(ServerSession):
    """
    Stubs out ServerSession methods since the session is only used for
    warming up the cache.
    """

    def _document_patched(self, event: DocumentPatchedEvent) -> None:
        return

    def _session_callback_added(self, event: SessionCallback):
        return

    def _session_callback_removed(self, event):
        return

def generate_session(application, request=None, payload=None, initialize=True):
    secret_key = settings.secret_key_bytes()
    sign_sessions = settings.sign_sessions()
    session_id = generate_session_id(
        secret_key=secret_key,
        signed=sign_sessions
    )
    payload = payload or {}
    token = generate_jwt_token(
        session_id,
        secret_key=secret_key,
        signed=sign_sessions,
        extra_payload=payload
    )
    doc = Document()
    session_context = BokehSessionContext(
        session_id,
        None,
        doc
    )
    session_context._request = _RequestProxy(
        request,
        arguments=payload.get('arguments'),
        cookies=payload.get('cookies'),
        headers=payload.get('headers')
    )
    session_context._token = token
    doc._session_context = lambda: session_context
    if initialize:
        application.initialize_document(doc)

    # We have to unset any session callbacks so bokeh does not attempt
    # to schedule them on the event loop
    callbacks = doc.callbacks._session_callbacks
    doc.callbacks._session_callbacks = set()
    session = ServerSessionStub(session_id, doc, io_loop=None, token=token)
    doc.callbacks._session_callbacks = callbacks
    return session


class PanelApplicationContext(ApplicationContext):

    async def create_session_if_needed(
        self, session_id: ID, request: HTTPServerRequest | None = None, token: str | None = None
    ) -> ServerSession:
        # this is because empty session_ids would be "falsey" and
        # potentially open up a way for clients to confuse us
        if len(session_id) == 0:
            raise ProtocolError("Session ID must not be empty")

        if session_id not in self._sessions and \
           session_id not in self._pending_sessions:
            future = self._pending_sessions[session_id] = asyncio.Future()

            doc = Document()

            session_context = BokehSessionContext(session_id,
                                                  self.server_context,
                                                  doc,
                                                  logout_url=self._logout_url)
            if request is not None:
                payload = get_token_payload(token) if token else {}
                if ('cookies' in payload and 'headers' in payload
                    and 'Cookie' not in payload['headers']):
                    # Restore Cookie header from cookies dictionary
                    payload['headers']['Cookie'] = '; '.join([
                        f'{k}={v}' for k, v in payload['cookies'].items()
                    ])
                # using private attr so users only have access to a read-only property
                session_context._request = _RequestProxy(request,
                                                         arguments=payload.get('arguments'),
                                                         cookies=payload.get('cookies'),
                                                         headers=payload.get('headers'))
            session_context._token = token

            # expose the session context to the document
            # use the _attribute to set the public property .session_context
            doc._session_context = weakref.ref(session_context)

            try:
                await self._application.on_session_created(session_context)
            except Exception as e:
                log.error("Failed to run session creation hooks %r", e, exc_info=True)

            if state._thread_pool:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(state._thread_pool, self._application.initialize_document, doc)
                thread_id = threading.get_ident()
                if thread_id:
                    state._thread_id_[doc] = thread_id
            else:
                self._application.initialize_document(doc)

            session = ServerSession(session_id, doc, io_loop=self._loop, token=token)
            del self._pending_sessions[session_id]
            self._sessions[session_id] = session
            session_context._set_session(session)
            self._session_contexts[session_id] = session_context

            # notify anyone waiting on the pending session
            future.set_result(session)

        if session_id in self._pending_sessions:
            # another create_session_if_needed is working on
            # creating this session
            session = await self._pending_sessions[session_id]
        else:
            session = self._sessions[session_id]

        return session
