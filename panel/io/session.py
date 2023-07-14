from __future__ import annotations

import logging

from typing import TYPE_CHECKING

from bokeh.document import Document
from bokeh.server.contexts import BokehSessionContext, _RequestProxy
from bokeh.server.session import ServerSession
from bokeh.settings import settings
from bokeh.util.token import generate_jwt_token, generate_session_id

if TYPE_CHECKING:
    from bokeh.document.events import DocumentPatchedEvent
    from bokeh.server.callbacks import SessionCallback


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

def generate_session(application):
    secret_key = settings.secret_key_bytes()
    sign_sessions = settings.sign_sessions()
    session_id = generate_session_id(
        secret_key=secret_key,
        signed=sign_sessions
    )
    token = generate_jwt_token(
        session_id,
        secret_key=secret_key,
        signed=sign_sessions,
        extra_payload={'headers': {}, 'cookies': {}, 'arguments': {}}
    )
    doc = Document()
    session_context = BokehSessionContext(
        session_id,
        None,
        doc
    )
    session_context._request = _RequestProxy(
        None, arguments={}, cookies={}, headers={}
    )
    doc._session_context = lambda: session_context
    application.initialize_document(doc)

    # We have to unset any session callbacks so bokeh does not attempt
    # to schedule them on the event loop
    callbacks = doc.callbacks._session_callbacks
    doc.callbacks._session_callbacks = set()
    session = ServerSessionStub(session_id, doc, io_loop=None, token=token)
    doc.callbacks._session_callbacks = callbacks
    return session
