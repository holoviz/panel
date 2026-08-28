from __future__ import annotations

import asyncio
import dataclasses
import datetime as dt
import gc
import inspect
import logging
import sys
import threading
import time
import typing as t
import weakref

from contextlib import ExitStack, contextmanager
from functools import partial, wraps
from weakref import WeakKeyDictionary

from bokeh.application.application import SessionContext
from bokeh.document.document import Document
from bokeh.document.events import (
    DocumentChangedEvent, DocumentPatchedEvent, MessageSentEvent,
    SessionCallbackAdded, SessionCallbackRemoved,
)
from bokeh.model.util import visit_immediate_value_references
from bokeh.models import CustomJS
from bokeh.protocol.messages import patch_doc

from ..config import config
from .loading import LOADING_INDICATOR_CSS_CLASS
from .model import monkeypatch_events  # noqa: F401 API import
from .state import state

if t.TYPE_CHECKING:
    from asyncio.futures import Future
    from collections.abc import Callable, Iterable, Iterator

    from bokeh.core.enums import HoldPolicyType
    from bokeh.core.has_props import HasProps
    from bokeh.server.connection import ServerConnection
    from bokeh.server.session import ServerSession
    from pyviz_comms import Comm

    EventBatch: t.TypeAlias = tuple[list[ServerConnection], list[DocumentPatchedEvent]]

logger = logging.getLogger(__name__)

#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------

GC_DEBOUNCE = 5
_HOLD_LOCK: WeakKeyDictionary[Document, threading.Lock] = WeakKeyDictionary()
_WRITE_FUTURES: WeakKeyDictionary[Document, list[Future[None]]] = WeakKeyDictionary()
_WRITE_EVENTS: WeakKeyDictionary[Document, list[EventBatch]] = WeakKeyDictionary()
_WRITE_BLOCK: WeakKeyDictionary[Document, bool] = WeakKeyDictionary()
_UNCONNECTED_EVENTS: WeakKeyDictionary[Document, list[DocumentChangedEvent]] = WeakKeyDictionary()

_panel_last_cleanup = None
_write_tasks: WeakKeyDictionary[Document, list[asyncio.Task]] = WeakKeyDictionary()
@dataclasses.dataclass
class Request:
    headers : dict
    cookies : dict
    arguments : dict


class MockSessionContext(SessionContext):

    def __init__(self, document: Document):
        self._document = document
        super().__init__(server_context=None, session_id=None)  # type: ignore[arg-type]

    def with_locked_document(self, *args):
        return

    @property
    def session(self):
        return None

    @property
    def destroyed(self) -> bool:
        return False

    @property
    def document(self) -> Document:
        return self._document

    @property
    def request(self):
        return Request(headers={}, cookies={}, arguments={})

def _cleanup_task(task):
    for tasks in _write_tasks.values():
        if task in tasks:
            tasks.remove(task)
            break

def _dispatch_events(doc: Document, events: list[DocumentChangedEvent]) -> None:
    """
    Handles dispatch of events which could not be processed in
    unlocked decorator.
    """
    for event in events:
        doc.callbacks.trigger_on_change(event)

def _drain_unconnected_events(doc: Document, lock: threading.Lock) -> list[DocumentChangedEvent]:
    """
    Drains events collected by a hold that exited before the session
    connected, sorting them into three groups, and returns the events
    that have to be dispatched immediately.

    Session callback events must be dispatched, since they are how
    ``add_next_tick_callback`` and friends register the callback on the
    IOLoop. Dropping them means the callback never runs at all, which
    for a scheduled ``Reactive._update_model`` silently loses the update.

    Events that carry no model state cannot be dispatched yet, since
    there are no subscribed connections to write them to, so they are
    deferred until the session connects. This currently means
    MessageSentEvent, i.e. custom events sent via ``Reactive._send_event``
    and ipywidgets comm messages.

    Everything else is dropped, since the Document is serialized in full
    once the session connects. Model property changes, title changes,
    root additions/removals and ColumnDataSource stream/patch events are
    all applied to the model before the event is emitted, so the
    serialization reproduces them.

    The events are returned rather than dispatched here so the caller can
    dispatch them after releasing ``lock``, since a change callback may
    itself enter ``hold``.
    """
    with lock:
        events = list(doc.callbacks._held_events or [])
        doc.callbacks._held_events = []
        doc.callbacks._hold = None

        dispatch: list[DocumentChangedEvent] = []
        deferred: list[DocumentChangedEvent] = []
        for event in events:
            if isinstance(event, (SessionCallbackAdded, SessionCallbackRemoved)):
                dispatch.append(event)
            elif not isinstance(event, DocumentPatchedEvent) or isinstance(event, MessageSentEvent):
                deferred.append(event)
        if deferred:
            _UNCONNECTED_EVENTS.setdefault(doc, []).extend(deferred)
    return dispatch

def _dispatch_unconnected_events(doc: Document) -> None:
    """
    Dispatches events deferred by ``_drain_unconnected_events`` now
    that the session has connected. Scheduled on the Document to ensure
    the events are dispatched on the Document's thread while it holds
    its lock, since ``_on_load`` may run on the thread pool.
    """
    events = _UNCONNECTED_EVENTS.pop(doc, None)
    if not events:
        return
    if doc.session_context:
        doc.add_next_tick_callback(partial(retrigger_events, doc, events))
    else:
        retrigger_events(doc, events)

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
    to_remove = []
    for ref, (pane, root, vdoc, _comm) in list(state._views.items()):
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
            to_remove.append(ref)
    for ref in to_remove:
        state._views.pop(ref, None)

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
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop on this thread (e.g. a callback offloaded to a
        # worker thread by Bokeh); avoid creating the coroutine here
        # since there is nothing to await it, and reschedule instead.
        doc.add_next_tick_callback(partial(func, *args, **kwargs))
        return
    task = loop.create_task(func(*args, **kwargs))
    _write_tasks.setdefault(doc, []).append(task)
    task.add_done_callback(_cleanup_task)

async def _dispatch_msgs(doc):
    """
    Serializes and writes queued event batches through their server
    connections, preserving the order in which they were scheduled.
    """
    if doc not in _WRITE_BLOCK:
        return
    try:
        while batches := _WRITE_EVENTS.pop(doc, []):
            for connections, events in batches:
                futures = write_events(doc, connections, events, run=False)
                if futures:
                    _WRITE_FUTURES.setdefault(doc, []).extend(futures)
                    await _run_write_futures(doc)
    finally:
        _WRITE_BLOCK.pop(doc, None)
        # A worker thread may queue a batch between the final empty check
        # above and clearing the block. Ensure it still gets a dispatcher.
        if doc in _WRITE_EVENTS and doc not in _WRITE_BLOCK:
            _WRITE_BLOCK[doc] = True
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

    # Cancel any pending write tasks for this document
    _WRITE_EVENTS.pop(self, None)
    _WRITE_BLOCK.pop(self, None)
    _UNCONNECTED_EVENTS.pop(self, None)
    for future in _WRITE_FUTURES.pop(self, []):
        future.cancel()
    for task in _write_tasks.pop(self, []):
        task.cancel()

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
    connections: Iterable[ServerConnection],
    events: list[DocumentPatchedEvent],
    run: bool = True
) -> list[Future[None]]:
    """
    Serializes the events into a single protocol message and writes it
    to all the supplied connections.

    A single message is shared between the connections since serializing
    a patch marks the models it defines as synced on the Document, so
    serializing per connection would make all but the first message
    reference models the client was never sent.
    """
    connections = list(connections)
    if not connections or not events:
        return []

    msg = patch_doc(events)
    msg.prepare()
    futures: list[Future[None]] = [
        asyncio.ensure_future(conn.send_message(msg)) for conn in connections
    ]

    if not run:
        return futures

    if doc in _WRITE_FUTURES:
        _WRITE_FUTURES[doc] += futures
    else:
        _WRITE_FUTURES[doc] = futures

    if state._unblocked(doc):
        _dispatch_write_task(doc, _run_write_futures, doc)
    else:
        doc.add_next_tick_callback(partial(_run_write_futures, doc))  # type: ignore[arg-type]
    return futures

def schedule_write_events(
    doc: Document,
    connections: Iterable[ServerConnection],
    events: list[DocumentPatchedEvent]
):
    """
    Queues events that cannot be written immediately, e.g. because the
    socket is being written to or because we are not on the event loop
    thread. The events are serialized by ``_dispatch_msgs`` when they
    are actually written.
    """
    # Set up write locks
    blocked = doc in _WRITE_BLOCK
    _WRITE_BLOCK[doc] = True
    _WRITE_EVENTS[doc] = batches = _WRITE_EVENTS.get(doc, [])
    batches.append((list(connections), events))
    if not blocked:
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

def _suppress_property_callbacks(
    events: list[DocumentChangedEvent]
) -> list[DocumentChangedEvent]:
    """
    Clears the ``callback_invoker`` on patch events so that handing them
    to bokeh only serializes and writes them.

    A held ModelChangedEvent carries the invoker that runs the
    property-level ``on_change`` callbacks, which bokeh defers until the
    event is dispatched. Since the change originated on the Python side
    inside a hold, ``Syncable._changing`` has already been torn down by
    the time the dispatch happens, so letting the invoker run makes
    ``Syncable._server_change`` treat the Python update as a frontend
    change and boomerang it back into the parameter.
    """
    for event in events:
        if isinstance(event, DocumentPatchedEvent):
            event.callback_invoker = None
    return events

def _flush_events(curdoc: Document, session: ServerSession) -> None:
    """
    Dispatches the events held on a Document, either by writing them to
    the subscribed sockets directly, by queueing them to be serialized
    and written on a later iteration of the event loop, by letting bokeh
    dispatch them or by re-applying them at a later point in time.
    """
    connections = session._subscribed_connections

    # Events may only be scheduled for writing from the server event
    # loop thread. Bokeh dispatches locked session callbacks on a worker
    # thread, so this is frequently not the case. The transport serializes
    # concurrent writes internally.
    queued = curdoc in _WRITE_EVENTS or curdoc in _WRITE_BLOCK
    locked = queued or not state._on_loop_thread

    events = list(curdoc.callbacks._held_events or [])
    curdoc.callbacks._held_events = []
    monkeypatch_events(events)

    # If we cannot write the events ourselves we let bokeh dispatch them,
    # as long as it is inside a locked callback and will therefore write
    # them before the callback returns. Deferring the write ourselves
    # would allow events bokeh dispatches later in the same callback to
    # be written first and since an event always refers to the model it
    # applies to by reference, reordering leaves the client
    # dereferencing models it has not been sent yet.
    if locked and not queued and session._pending_writes is not None:
        curdoc.callbacks._held_events += _suppress_property_callbacks(events)
        try:
            curdoc.unhold()
        except RuntimeError:
            curdoc.add_next_tick_callback(partial(retrigger_events, curdoc, events))
        return

    remaining_events, writeable_events = [], []
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
        # be dispatched we queue them up and schedule a task to
        # serialize and write them on the next iteration of the event
        # loop. The events must not be serialized here, since that
        # would declare the models they define as synced on the
        # Document while the message is still unwritten, leaving any
        # message serialized in the meantime referencing models the
        # client has not been sent.
        serializable_events = [e for e in remaining_events if isinstance(e, DocumentPatchedEvent)]
        held_events = [e for e in remaining_events if not isinstance(e, DocumentPatchedEvent)]
        if serializable_events:
            try:
                schedule_write_events(curdoc, connections, serializable_events)
            except Exception:
                # If the scheduling fails we let bokeh handle them
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
    if (curdoc is None or session is None or not state.loaded or
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
        # either by running the write futures, by scheduling them to be
        # serialized and written on the next iteration of the event loop,
        # by having bokeh dispatch them on calling unhold or by
        # scheduling them to be triggered later.
        _flush_events(curdoc, session)

def dispatch_events(events, doc: Document | None = None):
    doc = doc or state.curdoc
    if doc is None:
        return
    with immediate_dispatch(doc):
        doc.callbacks._held_events = events

@contextmanager
def hold(
    doc: Document | None = None,
    policy: HoldPolicyType = 'combine',
    comm: Comm | None = None,
    freeze: bool = False,
):
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
    freeze: bool
        **Experimental.** Whether to freeze the Document model
        references for the duration of the hold. When True, defers
        expensive model graph recomputation
        (``doc.models.recompute()``) until the hold exits, which can
        significantly speed up batch updates that modify many models.
        Safe to nest with the per-model ``freeze_doc`` calls used
        internally, since Bokeh's freeze mechanism is
        reference-counted.
    """
    doc = doc or state.curdoc
    if doc is None:
        yield
        return
    if doc not in _HOLD_LOCK:
        _HOLD_LOCK[doc] = threading.Lock()
    hold_lock = _HOLD_LOCK[doc]
    with ExitStack() as stack:
        if freeze and hasattr(doc, 'models'):
            stack.enter_context(doc.models.freeze())
        threaded = not state._on_loop_thread
        held = doc.callbacks.hold_value
        we_held = False
        try:
            if policy is None:
                doc.unhold()
                yield
            elif threaded:
                with hold_lock:
                    held = doc.callbacks.hold_value
                    if not held:
                        doc.hold(policy)
                        we_held = True
                yield
            else:
                with unlocked(policy=policy):
                    if not doc.callbacks.hold_value:
                        doc.hold(policy)
                    yield
        finally:
            if policy is None:
                pass
            elif threaded:
                if not held or we_held:
                    if state._connected.get(doc):
                        def _unhold(lock=hold_lock, doc=doc):
                            with lock:
                                doc.unhold()
                        with hold_lock:
                            # Clear the hold around scheduling the callback
                            # so the SessionCallbackAdded event it emits is
                            # dispatched rather than collected by the hold
                            # it is releasing.
                            doc.callbacks._hold = None
                            doc.add_next_tick_callback(_unhold)
                            doc.callbacks._hold = policy
                    else:
                        _dispatch_events(doc, _drain_unconnected_events(doc, hold_lock))
            elif held:
                doc.callbacks._hold = held
            elif comm is not None:
                from .notebook import push
                push(doc, comm)
            elif not state._connected.get(doc):
                _dispatch_events(doc, _drain_unconnected_events(doc, hold_lock))
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
def freeze_doc(doc: Document, model: HasProps, properties: dict[str, t.Any], force: bool = False):
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
