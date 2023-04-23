from __future__ import annotations

import logging

from bokeh.document import Document
from bokeh.server.contexts import BokehSessionContext, _RequestProxy
from bokeh.server.session import ServerSession
from bokeh.settings import settings
from bokeh.util.token import generate_jwt_token, generate_session_id

log = logging.getLogger(__name__)

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
    return ServerSession(session_id, doc, io_loop=None, token=token)
