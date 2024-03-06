from __future__ import annotations

import asyncio
import dataclasses
import datetime as dt
import inspect
import json
import logging
import threading

from contextlib import contextmanager
from functools import partial, wraps
from typing import (
    TYPE_CHECKING, Any, Callable, Dict, Iterator, List, Optional,
)

from bokeh.application.application import SessionContext
from bokeh.core.serialization import Serializable
from bokeh.document.document import Document
from bokeh.document.events import (
    ColumnDataChangedEvent, ColumnsPatchedEvent, ColumnsStreamedEvent,
    DocumentChangedEvent, ModelChangedEvent,
)
from bokeh.model.util import visit_immediate_value_references
from bokeh.models import CustomJS

from ..config import config
from ..util import param_watchers
from .loading import LOADING_INDICATOR_CSS_CLASS
from .model import hold, monkeypatch_events  # noqa: F401 API import
from .state import curdoc_locked, state

if TYPE_CHECKING:
    from bokeh.core.has_props import HasProps

logger = logging.getLogger(__name__)

#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------

DISPATCH_EVENTS = (
    ColumnDataChangedEvent, ColumnsPatchedEvent, ColumnsStreamedEvent,
    ModelChangedEvent
)

WRITE_TASKS = []
WRITE_LOCK = asyncio.Lock()

@dataclasses.dataclass
class Request:
    headers : dict
    cookies : dict
    arguments : dict


class MockSessionContext(SessionContext):

    def __init__(self, *args, document=None, **kwargs):
        self._document = document
        super().__init__(*args, server_context=None, session_id=None, **kwargs)

    def with_locked_document(self, *args):
        return

    @property
    def destroyed(self) -> bool:
        return False

    @property
    def request(self):
        return Request(headers={}, cookies={}, arguments={})

def _cleanup_task(task):
    if task in WRITE_TASKS:
        WRITE_TASKS.remove(task)

def _dispatch_events(doc: Document, events: List[DocumentChangedEvent]) -> None:
    """
    Handles dispatch of events which could not be processed in
    unlocked decorator.
    """
    for event in events:
        doc.callbacks.trigger_on_change(event)

def _cleanup_doc(doc, destroy=True):
    for callback in doc.session_destroyed_callbacks:
        try:
            callback(None)
        except Exception:
            pass
    if hasattr(doc.callbacks, '_change_callbacks'):
        doc.callbacks._change_callbacks[None] = {}

    # Remove views
    from ..viewable import Viewable
    views = {}
    for ref, (pane, root, vdoc, comm) in list(state._views.items()):
        if vdoc is doc:
            pane._cleanup(root)
            if isinstance(pane, Viewable):
                pane._hooks = []
                for p in pane.select():
                    p._hooks = []
                    param_watchers(p, {})
                    p._documents = {}
                    p._internal_callbacks = {}
            param_watchers(pane, {})
            pane._documents = {}
            pane._internal_callbacks = {}
        else:
            views[ref] = (pane, root, doc, comm)
    state._views = views

    # When reusing sessions we must clean up the Panel state but we
    # must **not** destroy the template or the document
    if not destroy:
        return

    # Clean up templates
    if doc in state._templates:
        tmpl = state._templates[doc]
        tmpl._documents = {}
        del state._templates[doc]

    # Destroy document
    doc.destroy(None)

async def _run_write_futures(futures):
    """
    Ensure that all write_message calls are awaited and handled.
    """
    from tornado.websocket import WebSocketClosedError
    async with WRITE_LOCK:
        for future in futures:
            try:
                await future
            except WebSocketClosedError:
                logger.warning("Failed sending message as connection was closed")
            except Exception as e:
                logger.warning(f"Failed sending message due to following error: {e}")

def _dispatch_write_task(doc, func, *args, **kwargs):
    """
    Schedules tasks that write messages to the socket.
    """
    try:
        task = asyncio.ensure_future(func(*args, **kwargs))
        WRITE_TASKS.append(task)
        task.add_done_callback(_cleanup_task)
    except RuntimeError:
        doc.add_next_tick_callback(partial(func, *args, **kwargs))

async def _dispatch_msgs(doc, msgs):
    """
    Writes messages to a socket, ensuring that the write_lock is not
    set, otherwise re-schedules the write task on the event loop.
    """
    from tornado.websocket import WebSocketHandler
    remaining = {}
    for conn, msg in msgs.items():
        socket = conn._socket
        if hasattr(socket, 'write_lock') and socket.write_lock._block._value == 0:
            remaining[conn] = msg
            continue
        if isinstance(conn._socket, WebSocketHandler):
            futures = dispatch_tornado(conn, msg=msg)
        else:
            futures = dispatch_django(conn, msg=msg)
        await _run_write_futures(futures)
    if not remaining:
        return
    await asyncio.sleep(0.01)
    _dispatch_write_task(doc, _dispatch_msgs, doc, remaining)

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def create_doc_if_none_exists(doc: Optional[Document]) -> Document:
    curdoc = doc or curdoc_locked()
    if curdoc is None:
        curdoc = Document()
    elif not isinstance(curdoc, Document):
        curdoc = curdoc._doc
    return curdoc

def init_doc(doc: Optional[Document]) -> Document:
    curdoc = create_doc_if_none_exists(doc)
    if not curdoc.session_context:
        return curdoc

    thread_id = threading.get_ident()
    if thread_id:
        state._thread_id_[curdoc] = thread_id

    if config.global_loading_spinner:
        curdoc.js_on_event(
            'document_ready', CustomJS(code=f"""
            const body = document.getElementsByTagName('body')[0]
            body.classList.remove({LOADING_INDICATOR_CSS_CLASS!r}, {config.loading_spinner!r})
            """)
        )

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

def dispatch_tornado(conn, events=None, msg=None):
    from tornado.websocket import WebSocketHandler
    socket = conn._socket
    ws_conn = getattr(socket, 'ws_connection', False)
    if not ws_conn or ws_conn.is_closing(): # type: ignore
        return []
    if msg is None:
        msg = conn.protocol.create('PATCH-DOC', events)
    futures = [
        WebSocketHandler.write_message(socket, msg.header_json),
        WebSocketHandler.write_message(socket, msg.metadata_json),
        WebSocketHandler.write_message(socket, msg.content_json)
    ]
    for buffer in msg._buffers:
        header = json.dumps(buffer.ref)
        payload = buffer.to_bytes()
        futures.extend([
            WebSocketHandler.write_message(socket, header),
            WebSocketHandler.write_message(socket, payload, binary=True)
        ])
    return futures

def dispatch_django(conn, events=None, msg=None):
    socket = conn._socket
    if msg is None:
        msg = conn.protocol.create('PATCH-DOC', events)
    futures = [
        socket.send(text_data=msg.header_json),
        socket.send(text_data=msg.metadata_json),
        socket.send(text_data=msg.content_json)
    ]
    for buffer in msg._buffers:
        header = json.dumps(buffer.ref)
        payload = buffer.to_bytes()
        futures.extend([
            socket.send(text_data=header),
            socket.send(binary_data=payload)
        ])
    return futures

@contextmanager
def unlocked() -> Iterator:
    """
    Context manager which unlocks a Document and dispatches
    ModelChangedEvents triggered in the context body to all sockets
    on current sessions.
    """
    curdoc = state.curdoc
    session_context = getattr(curdoc, 'session_context', None)
    session = getattr(session_context, 'session', None)
    if state._current_thread != state._thread_id:
        logger.error(
            "Using the unlocked decorator when running inside a thread "
            "is not safe! Ensure you check that pn.state._current_thread "
            "matches the current thread id."
        )
        yield
        return
    elif curdoc is None or session_context is None or session is None or state._jupyter_kernel_context:
        yield
        return
    elif curdoc.callbacks.hold_value:
        yield
        monkeypatch_events(curdoc.callbacks._held_events)
        return

    from tornado.websocket import WebSocketHandler
    connections = session._subscribed_connections

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
        curdoc.callbacks._held_events = []
        monkeypatch_events(events)
        remaining_events, dispatch_events = [], []
        for event in events:
            if isinstance(event, DISPATCH_EVENTS) and not locked:
                dispatch_events.append(event)
            else:
                remaining_events.append(event)

        futures = []
        for conn in connections:
            if not dispatch_events:
                continue
            elif isinstance(conn._socket, WebSocketHandler):
                futures += dispatch_tornado(conn, dispatch_events)
            else:
                futures += dispatch_django(conn, dispatch_events)

        if futures:
            if state._unblocked(curdoc):
                _dispatch_write_task(curdoc, _run_write_futures, futures)
            else:
                curdoc.add_next_tick_callback(partial(_run_write_futures, futures))
    except Exception:
        remaining_events = events

    if not remaining_events:
        curdoc.unhold()
        return

    # Separate serializable and non-serializable events
    leftover_events = [e for e in remaining_events if not isinstance(e, Serializable)]
    remaining_events = [e for e in remaining_events if isinstance(e, Serializable)]

    # Create messages for remaining events
    msgs = {}
    for conn in connections:
        if not remaining_events:
            continue
        # Create a protocol message for any events that cannot be immediately dispatched
        msgs[conn] = conn.protocol.create('PATCH-DOC', remaining_events)
    _dispatch_write_task(curdoc, _dispatch_msgs, curdoc, msgs)
    curdoc.callbacks._held_events = leftover_events
    curdoc.unhold()

@contextmanager
def immediate_dispatch(doc: Document | None = None):
    """
    Context manager to trigger immediate dispatch of events triggered
    inside the execution context even when Document events are
    currently on hold.

    Arguments
    ---------
    doc: Document
        The document to dispatch events on (if `None` then `state.curdoc` is used).
    """
    doc = doc or state.curdoc

    # Skip if not in a server context
    if not doc or not doc._session_context or not state._unblocked(doc):
        yield
        return

    old_events = doc.callbacks._held_events
    held = doc.callbacks._hold
    doc.callbacks._held_events = []
    doc.callbacks.unhold()
    with unlocked():
        yield
    doc.callbacks._hold = held
    doc.callbacks._held_events = old_events

@contextmanager
def freeze_doc(doc: Document, model: HasProps, properties: Dict[str, Any], force: bool = False):
    """
    Freezes the document model references if any of the properties
    are themselves a model.
    """
    if force:
        dirty_count = 1
    else:
        dirty_count = 0
        def mark_dirty(_: HasProps):
            nonlocal dirty_count
            dirty_count += 1
        for key, value in properties.items():
            visit_immediate_value_references(getattr(model, key, None), mark_dirty)
            visit_immediate_value_references(value, mark_dirty)
    if dirty_count:
        doc.models._push_freeze()
    yield
    if dirty_count:
        doc.models._pop_freeze()
