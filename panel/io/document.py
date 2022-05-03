from __future__ import annotations

import datetime as dt
import inspect
import threading

from contextlib import contextmanager
from functools import partial, wraps
from typing import Callable, List, Optional

from bokeh.document.document import Document
from bokeh.document.events import DocumentChangedEvent, ModelChangedEvent
from bokeh.io import curdoc as _curdoc

from .model import patch_events
from .state import set_curdoc, state


def init_doc(doc: Optional[Document]) -> Document:
    curdoc = doc or _curdoc()
    if not curdoc.session_context:
        return curdoc

    thread = threading.current_thread()
    if thread:
        with set_curdoc(curdoc):
            state._thread_id = thread.ident

    session_id = curdoc.session_context.id
    sessions = state.session_info['sessions']
    if session_id not in sessions:
        return curdoc

    sessions[session_id].update({
        'started': dt.datetime.now().timestamp()
    })
    curdoc.on_event('document_ready', state._init_session)
    return curdoc

def with_lock(func: Callable) -> Callable:
    """
    Wrap a callback function to execute with a lock allowing the
    function to modify bokeh models directly.

    Arguments
    ---------
    func: callable
      The callable to wrap

    Returns
    -------
    wrapper: callable
      Function wrapped to execute without a Document lock.
    """
    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def wrapper(*args, **kw):
            return await func(*args, **kw)
    else:
        @wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
    wrapper.lock = True # type: ignore
    return wrapper

def _dispatch_events(doc: Document, events: List[DocumentChangedEvent]) -> None:
    """
    Handles dispatch of events which could not be processed in
    unlocked decorator.
    """
    for event in events:
        doc.callbacks.trigger_on_change(event)

@contextmanager
def unlocked():
    """
    Context manager which unlocks a Document and dispatches
    ModelChangedEvents triggered in the context body to all sockets
    on current sessions.
    """
    curdoc = state.curdoc
    if curdoc is None or curdoc.session_context is None or curdoc.session_context.session is None:
        yield
        return
    from tornado.websocket import WebSocketHandler
    connections = curdoc.session_context.session._subscribed_connections

    hold = curdoc.callbacks.hold_value
    if hold:
        old_events = list(curdoc.callbacks._held_events)
    else:
        old_events = []
        curdoc.hold()
    try:
        yield

        locked = False
        for conn in connections:
            socket = conn._socket
            if hasattr(socket, 'write_lock') and socket.write_lock._block._value == 0:
                locked = True
                break

        events = curdoc.callbacks._held_events
        patch_events(events)
        remaining_events = []
        for event in events:
            if not isinstance(event, ModelChangedEvent) or event in old_events or locked:
                remaining_events.append(event)
                continue
            for conn in connections:
                socket = conn._socket
                ws_conn = getattr(socket, 'ws_connection', False)
                if (not hasattr(socket, 'write_message') or
                    ws_conn is None or (ws_conn and ws_conn.is_closing())):
                    continue
                msg = conn.protocol.create('PATCH-DOC', [event])
                WebSocketHandler.write_message(socket, msg.header_json)
                WebSocketHandler.write_message(socket, msg.metadata_json)
                WebSocketHandler.write_message(socket, msg.content_json)
                for header, payload in msg._buffers:
                    WebSocketHandler.write_message(socket, header)
                    WebSocketHandler.write_message(socket, payload, binary=True)
        curdoc.callbacks._held_events = remaining_events
    finally:
        if hold:
            return
        try:
            curdoc.unhold()
        except RuntimeError:
            curdoc.add_next_tick_callback(partial(_dispatch_events, curdoc, remaining_events))
