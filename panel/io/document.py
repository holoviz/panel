from __future__ import annotations

import asyncio
import dataclasses
import datetime as dt
import gc
import inspect
import json
import logging
import sys
import threading
import time
import weakref

from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from functools import partial, wraps
from typing import TYPE_CHECKING, Any
from weakref import WeakKeyDictionary

from bokeh.application.application import SessionContext
from bokeh.document.document import Document
from bokeh.document.events import DocumentChangedEvent, DocumentPatchedEvent
from bokeh.model.util import visit_immediate_value_references
from bokeh.models import CustomJS

from ..config import config
from .loading import LOADING_INDICATOR_CSS_CLASS
from .model import monkeypatch_events  # noqa: F401 API import
from .state import state

if TYPE_CHECKING:
    from asyncio.futures import Future

    from bokeh.core.enums import HoldPolicyType
    from bokeh.core.has_props import HasProps
    from bokeh.document import Document
    from bokeh.protocol.message import Message
    from bokeh.server.connection import ServerConnection
    from pyviz_comms import Comm

logger = logging.getLogger(__name__)

#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------

GC_DEBOUNCE = 5
_WRITE_FUTURES: WeakKeyDictionary[Document, list[Future]] = WeakKeyDictionary()
_WRITE_MSGS: WeakKeyDictionary[Document, dict[ServerConnection, list[Message]]] = WeakKeyDictionary()
_WRITE_BLOCK: WeakKeyDictionary[Document, bool] = WeakKeyDictionary()

_panel_last_cleanup = None
_write_tasks: list[asyncio.Task] = []

extra_socket_handlers: dict[type, Callable[[Any], None]] = {}

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
    def session(self):
        return None

    @property
    def destroyed(self) -> bool:
        return False

    @property
    def request(self):
        return Request(headers={}, cookies={}, arguments={})

def _cleanup_task(task):
    if task in _write_tasks:
        _write_tasks.remove(task)

def _dispatch_events(doc: Document, events: list[DocumentChangedEvent]) -> None:
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
    if not destroy:
        doc.callbacks._change_callbacks.clear()
    elif None not in doc.callbacks._change_callbacks:
        doc.callbacks._change_callbacks[None] = lambda e: e

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
                    p.param.watchers = {}
                    p._documents = {}
                    p._internal_callbacks = {}
            pane.param.watchers = {}
            pane._documents = {}
            pane._internal_callbacks = {}
        else:
            views[ref] = (pane, root, vdoc, comm)
    state._views = views

    # When reusing sessions we must clean up the Panel state but we
    # must **not** destroy the template or the document
    if not destroy:
        return

    # Clean up templates
    if doc in state._templates:
        tmpl = state._templates[doc]
        tmpl._documents = []
        del state._templates[doc]

    # Destroy document
    doc.destroy(None)

async def _run_write_futures(doc):
    """
    Ensure that all write_message calls are awaited and handled.
    """
    from tornado.websocket import WebSocketClosedError
    futures = _WRITE_FUTURES.pop(doc, [])
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
        _write_tasks.append(task)
        task.add_done_callback(_cleanup_task)
    except RuntimeError:
        doc.add_next_tick_callback(partial(func, *args, **kwargs))

async def _dispatch_msgs(doc):
    """
    Writes messages to a socket, ensuring that the write_lock is not
    set, otherwise re-schedules the write task on the event loop.
    """
    from tornado.websocket import WebSocketHandler
    remaining = {}
    futures = []
    conn_msgs = _WRITE_MSGS.pop(doc, {})
    for conn, msgs in conn_msgs.items():
        socket = conn._socket
        if hasattr(socket, 'write_lock') and socket.write_lock._block._value == 0:
            remaining[conn] = msgs
            continue
        for msg in msgs:
            if isinstance(conn._socket, WebSocketHandler):
                futures += dispatch_tornado(conn, msg=msg)
            elif (socket_type:= type(conn._socket)) in extra_socket_handlers:
                futures += extra_socket_handlers[socket_type](conn, msg=msg)
            else:
                futures += dispatch_django(conn, msg=msg)
    if futures:
        if doc in _WRITE_FUTURES:
            _WRITE_FUTURES[doc] += futures
        else:
            _WRITE_FUTURES[doc] = futures
        await _run_write_futures(doc)
    if not remaining:
        if doc in _WRITE_BLOCK:
            del _WRITE_BLOCK[doc]
        return
    for conn, msgs in remaining.items():
        if doc in _WRITE_MSGS:
            _WRITE_MSGS[doc][conn] = msgs + _WRITE_MSGS[doc].get(conn, [])
        else:
            _WRITE_MSGS[doc] = {conn: msgs}
    await asyncio.sleep(0.01)
    _dispatch_write_task(doc, _dispatch_msgs, doc)

def _garbage_collect():
    if (new_time:= time.monotonic()-_panel_last_cleanup) < GC_DEBOUNCE:
        at = dt.datetime.now() + dt.timedelta(seconds=new_time)
        state.schedule_task('gc.collect', _garbage_collect, at=at)
        return
    gc.collect()

def _destroy_document(self, session):
    """
    Override for Document.destroy() without calling gc.collect directly.
    The gc.collect() call is scheduled as a task, ensuring that when
    multiple documents are destroyed in quick succession we do not
    schedule excessive garbage collection.
    """
    if session is not None:
        self.remove_on_change(session)

    del self._roots
    del self._theme
    del self._template
    self._session_context = None

    self.callbacks.destroy()
    self.models.destroy()

    # Module cleanup without trawling through referrers (as self.modules.destroy() does)
    for module in self.modules._modules:
        # remove the reference from sys.modules
        if module.__name__ in sys.modules:
            del sys.modules[module.__name__]

        # explicitly clear the module contents and the module here itself
        module.__dict__.clear()
        del module
    self.modules._modules = []

    # Clear periodic callbacks
    for cb in state._periodic.get(self, []):
        cb.stop()

    # Clean up pn.state to avoid tasks getting executed on dead session
    for attr in dir(state):
        # _param_watchers is deprecated in Param 2.0 and will raise a warning
        if not attr.startswith('_') or attr == "_param_watchers":
            continue
        state_obj = getattr(state, attr)
        if isinstance(state_obj, weakref.WeakKeyDictionary) and self in state_obj:
            del state_obj[self]

    # Schedule GC
    global _panel_last_cleanup
    _panel_last_cleanup = time.monotonic()
    at = dt.datetime.now() + dt.timedelta(seconds=GC_DEBOUNCE)
    state.schedule_task('gc.collect', _garbage_collect, at=at)

    del self.destroy

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def retrigger_events(doc: Document, events: list[DocumentChangedEvent]):
    """
    Applies events that could not be processed previously.
    """
    if doc.callbacks.hold_value:
        doc.callbacks._held_events = events + list(doc.callbacks._held_events)
    else:
        _dispatch_events(doc, events)

def write_events(
    doc: Document,
    connections: list[ServerConnection],
    events: list[DocumentPatchedEvent]
):
    from tornado.websocket import WebSocketHandler

    futures: list[Future] = []
    for conn in connections:
        if isinstance(conn._socket, WebSocketHandler):
            futures += dispatch_tornado(conn, events)
        elif (socket_type:= type(conn._socket)) in extra_socket_handlers:
            futures += extra_socket_handlers[socket_type](conn, events)
        else:
            futures += dispatch_django(conn, events)

    if doc in _WRITE_FUTURES:
        _WRITE_FUTURES[doc] += futures
    else:
        _WRITE_FUTURES[doc] = futures

    if state._unblocked(doc):
        _dispatch_write_task(doc, _run_write_futures, doc)
    else:
        doc.add_next_tick_callback(partial(_run_write_futures, doc))

def schedule_write_events(
    doc: Document,
    connections: list[ServerConnection],
    events: list[DocumentPatchedEvent]
):
    # Set up write locks
    _WRITE_BLOCK[doc] = True
    _WRITE_MSGS[doc] = msgs = _WRITE_MSGS.get(doc, {})
    # Create messages for remaining events
    for conn in connections:
        # Create a protocol message for any events that cannot be immediately dispatched
        msg = conn.protocol.create('PATCH-DOC', events)
        if conn in msgs:
            msgs[conn].append(msg)
        else:
            msgs[conn] = [msg]
    _dispatch_write_task(doc, _dispatch_msgs, doc)

def create_doc_if_none_exists(doc: Document | None) -> Document:
    curdoc = doc or state.curdoc
    if curdoc is None:
        curdoc = Document()
    elif not isinstance(curdoc, Document):
        curdoc = curdoc._doc
    return curdoc

def init_doc(doc: Document | None) -> Document:
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

    Parameters
    ----------
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

def dispatch_tornado(
    conn: ServerConnection,
    events: list[DocumentPatchedEvent] | None = None,
    msg: Message | None = None
) -> Sequence[Future]:
    from tornado.websocket import WebSocketHandler
    socket = conn._socket
    ws_conn = getattr(socket, 'ws_connection', False)
    if not ws_conn or ws_conn.is_closing(): # type: ignore
        return []
    elif msg is None:
        if events:
            msg = conn.protocol.create('PATCH-DOC', events)
        else:
            return []
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

def dispatch_django(
    conn: ServerConnection,
    events: list[DocumentPatchedEvent] | None = None,
    msg: Message | None = None
) -> Sequence[Future]:
    socket = conn._socket
    if msg is None:
        return []
    elif msg is None:
        if events:
            msg = conn.protocol.create('PATCH-DOC', events)
        else:
            return
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
def unlocked(policy: HoldPolicyType = 'combine') -> Iterator:
    """
    Context manager which unlocks a Document and dispatches
    ModelChangedEvents triggered in the context body to all sockets
    on current sessions.

    Parameters
    ----------
    policy: Literal['combine' | 'collect']
        One of 'combine' or 'collect' determining whether events
        setting the same property are combined or accumulated to be
        dispatched when the context manager exits.
    """
    curdoc = state.curdoc
    session_context = getattr(curdoc, 'session_context', None)
    session = getattr(session_context, 'session', None)
    if state._current_thread != state._thread_id and state.loaded and session:
        logger.error(
            "Using the unlocked decorator when running inside a thread "
            "is not safe! Ensure you check that pn.state._current_thread "
            "matches the current thread id."
        )
        yield
        return
    elif (curdoc is None or session is None or not state.loaded or
          state._jupyter_kernel_context):
        yield
        return
    elif curdoc.callbacks.hold_value:
        yield
        monkeypatch_events(curdoc.callbacks._held_events)
        return

    curdoc.hold(policy=policy)
    try:
        yield
    finally:
        # Whether or not there was an error in the body of context manager
        # we may have captured some events. We will dispatch these
        # either by running the write futures, by serializing them
        # as actual messages and scheduling these messages to be written,
        # by having bokeh dispatch them on calling unhold or by
        # scheduling them to be triggered later.
        connections = session._subscribed_connections
        locked = curdoc in _WRITE_MSGS or curdoc in _WRITE_BLOCK
        for conn in connections:
            socket = conn._socket
            if hasattr(socket, 'write_lock') and socket.write_lock._block._value == 0:
                locked = True
                break

        remaining_events, writeable_events = [], []
        events = list(curdoc.callbacks._held_events or [])
        curdoc.callbacks._held_events = []
        monkeypatch_events(events)
        for event in events:
            if isinstance(event, DocumentPatchedEvent) and not locked:
                writeable_events.append(event)
            else:
                remaining_events.append(event)

        try:
            if writeable_events:
                write_events(curdoc, connections, writeable_events)
        except Exception:
            remaining_events = events
        finally:
            # If for whatever reasons there are still events that couldn't
            # be dispatched we create a protocol message for these immediately
            # and then schedule a task to write the message to the websocket
            # on the next iteration of the event loop. This ensures that
            # the message reflects the event at the time it was generated
            # potentially avoiding issues serializing subsequent models
            # which assume the serializer has previously seen them.
            serializable_events = [e for e in remaining_events if isinstance(e, DocumentPatchedEvent)]
            held_events = [e for e in remaining_events if not isinstance(e, DocumentPatchedEvent)]
            if serializable_events:
                try:
                    schedule_write_events(curdoc, connections, serializable_events)
                except Exception:
                    # If the serialization fails we let bokeh handle them
                    held_events = remaining_events
            curdoc.callbacks._held_events += held_events

            # Last we attempt to let bokeh handle these remaining events
            # if this also fails we reapply the event at a later point in
            # time. This should not happen but since network writes
            # are fickle we handle this case anyway.
            try:
                retriggered_events = list(curdoc.callbacks._held_events)
                curdoc.unhold()
            except RuntimeError:
                curdoc.add_next_tick_callback(partial(retrigger_events, curdoc, retriggered_events))

def dispatch_events(events, doc: Document | None = None):
    doc = doc or state.curdoc
    if doc is None:
        return
    with immediate_dispatch(doc):
        doc.callbacks._held_events = events

@contextmanager
def hold(doc: Document | None = None, policy: HoldPolicyType = 'combine', comm: Comm | None = None):
    """
    Context manager that holds events on a particular Document
    allowing them all to be collected and dispatched when the context
    manager exits. This allows multiple events on the same object to
    be combined if the policy is set to 'combine'.

    Parameters
    ----------
    doc: Document
        The Bokeh Document to hold events on.
    policy: HoldPolicyType
        One of 'combine', 'collect' or None determining whether events
        setting the same property are combined or accumulated to be
        dispatched when the context manager exits.
    comm: Comm
        The Comm to dispatch events on when the context manager exits.
    """
    doc = doc or state.curdoc
    if doc is None:
        yield
        return
    threaded = state._current_thread != state._thread_id
    held = doc.callbacks.hold_value
    try:
        if policy is None:
            doc.unhold()
            yield
        elif threaded:
            doc.hold(policy)
            yield
        else:
            with unlocked(policy=policy):
                if not doc.callbacks.hold_value:
                    doc.hold(policy)
                yield
    finally:
        if held:
            doc.callbacks._hold = held
        elif comm is not None:
            from .notebook import push
            push(doc, comm)
        elif not state._connected.get(doc):
            doc.callbacks._hold = None
        elif threaded:
            doc.callbacks._hold = None
            doc.add_next_tick_callback(doc.unhold)
            doc.callbacks._hold = policy
        else:
            doc.unhold()

@contextmanager
def immediate_dispatch(doc: Document | None = None):
    """
    Context manager to trigger immediate dispatch of events triggered
    inside the execution context even when Document events are
    currently on hold.

    Parameters
    ----------
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
def freeze_doc(doc: Document, model: HasProps, properties: dict[str, Any], force: bool = False):
    """
    Freezes the document model references if any of the properties
    are themselves a model.
    """
    if not hasattr(doc, '_roots'):
        dirty_count = 0
    elif force:
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
