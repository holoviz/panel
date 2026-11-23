import asyncio
import contextvars
import gc
import json
import threading
import time
import weakref

from concurrent.futures import ThreadPoolExecutor
from functools import partial

import param
import pytest
import tornado.locks

from bokeh.core.serialization import Deserializer
from bokeh.document import Document
from bokeh.document.events import MessageSentEvent, ModelChangedEvent
from bokeh.models import Column as BkColumn, Div, Range1d
from bokeh.plotting import figure
from bokeh.protocol import Protocol

import panel as pn

from panel.io.application import _on_session_destroyed
from panel.io.browser import BrowserInfo
from panel.io.document import (
    _UNCONNECTED_EVENTS, _WRITE_BLOCK, MockSessionContext, _cleanup_doc,
    _client_has_document, _defer_until_unlocked, _destroy_document,
    _drop_undefined_changes, _is_write_blocked, _keep_unsent_models_new,
    _schedule_locked, _socket_dispatcher, _suppress_property_callbacks,
    _track_unwritten, _untrack_unwritten, _write_tasks, dispatch_django,
    dispatch_tornado, extra_socket_handlers, hold, init_doc,
    schedule_write_events, unlocked, write_events,
)
from panel.io.state import _state, set_curdoc, state
from panel.tests.util import serve_and_request, wait_until
from panel.widgets import IntSlider


def test_cleanup_doc_does_not_shadow_class_views():
    doc = Document()
    pane = pn.pane.Markdown("test")
    pane.get_root(doc)

    assert state._views
    views_id_before = id(_state._views)

    _cleanup_doc(doc, destroy=True)

    # The class-level dict should be mutated in place, not shadowed
    assert id(_state._views) == views_id_before
    # No instance-level shadow should be created
    assert '_views' not in state.__dict__
    # The entry should be cleaned up
    assert not state._views


def test_document_hold():
    slider = IntSlider()

    serve_and_request(slider)

    doc, model = list(slider._documents.items())[0]

    doc.hold()

    with set_curdoc(doc):
        with unlocked():
            model.value = 3

    assert doc.callbacks._held_events


@pytest.mark.xdist_group(name="server")
def test_hold_does_not_get_stuck_with_threaded_callbacks(threads):
    column = pn.FlexBox(*[pn.pane.Str('0') for _ in range(20)])
    layout = pn.Column(column)

    serve_and_request(layout)

    doc = list(layout._documents.keys())[0]

    def update_in_hold(i):
        with set_curdoc(doc):
            with hold(doc):
                for obj in column:
                    obj.object = str(i)

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(update_in_hold, i) for i in range(10)]
        for f in futures:
            f.result()

    wait_until(lambda: not doc.callbacks.hold_value, timeout=5000)


def test_hold_on_loop_does_not_restore_hold_released_by_other_thread(monkeypatch):
    """
    A hold on the event loop that starts while a worker thread holds the
    Document must not put the hold back after the worker released it,
    since nothing would release it again.
    """
    doc = Document()
    model = pn.pane.Markdown("a").get_root(doc)
    doc.add_root(model)
    loop_thread = threading.current_thread()
    monkeypatch.setattr(
        type(state), '_on_loop_thread',
        property(lambda self: threading.current_thread() is loop_thread)
    )
    worker_held, loop_held, worker_released = threading.Event(), threading.Event(), threading.Event()

    def worker():
        with hold(doc):
            worker_held.set()
            loop_held.wait(5)
        worker_released.set()

    thread = threading.Thread(target=worker)
    thread.start()
    assert worker_held.wait(5)
    with hold(doc):
        loop_held.set()
        assert worker_released.wait(5)
    thread.join()

    assert not doc.callbacks.hold_value
    model.text = "b"
    assert not doc.callbacks._held_events


def test_hold_before_connected_does_not_strand_events():
    """
    A hold exiting before the session connects must leave nothing queued
    on the Document, and must not swallow the session callback events
    that scheduled updates rely on to register on the IOLoop.
    """
    state_info, docs, ran = {}, [], []

    def app():
        md = pn.pane.Markdown("initial")
        doc = state.curdoc
        docs.append(doc)

        def before_ready():
            with hold(doc):
                md.object = "changed"
                doc.add_next_tick_callback(lambda: ran.append('scheduled'))
            state_info['connected'] = state._connected.get(doc)
            state_info['hold'] = doc.callbacks.hold_value
            state_info['queued'] = list(doc.callbacks._held_events)

        doc.add_next_tick_callback(before_ready)
        return md

    serve_and_request(app)
    wait_until(lambda: 'queued' in state_info)

    # The hold exited before the session was connected
    assert state_info['connected'] is None
    assert state_info['hold'] is None
    # Nothing is left queued behind the hold
    assert state_info['queued'] == []

    doc = docs[0]
    # The scheduled callback was registered and ran, so the model update
    # that Reactive schedules pre-connect is not lost
    wait_until(lambda: ran == ['scheduled'])
    wait_until(lambda: docs[0].roots[0].text == '&lt;p&gt;changed&lt;/p&gt;\n')
    assert not doc.callbacks._held_events


def test_hold_before_connected_defers_message_sent():
    """
    MessageSentEvent carries a protocol message with no representation in
    the model graph, so it cannot be dropped like a model change. It has
    to be deferred until a connection exists to write it to.
    """
    docs, state_info = [], {}

    def app():
        doc = state.curdoc
        docs.append(doc)

        def before_ready():
            with hold(doc):
                doc.callbacks.trigger_on_change(
                    MessageSentEvent(doc, "panel_test", "payload")
                )
            state_info['deferred'] = list(_UNCONNECTED_EVENTS.get(doc, []))
            state_info['queued'] = list(doc.callbacks._held_events)

        doc.add_next_tick_callback(before_ready)
        return pn.pane.Markdown("initial")

    serve_and_request(app)
    wait_until(lambda: 'deferred' in state_info)

    # Not dropped, and not left queued on the Document
    assert len(state_info['deferred']) == 1
    assert isinstance(state_info['deferred'][0], MessageSentEvent)
    assert state_info['queued'] == []


def test_hold_before_connected_drops_recoverable_events():
    """
    Model changes are dropped rather than deferred, since the Document is
    serialized in full once the session connects.
    """
    docs, state_info = [], {}

    def app():
        doc = state.curdoc
        docs.append(doc)
        slider = IntSlider(value=1)
        model = slider.get_root(doc)

        def before_ready():
            with hold(doc):
                model.value = 3
            state_info['deferred'] = list(_UNCONNECTED_EVENTS.get(doc, []))
            state_info['queued'] = list(doc.callbacks._held_events)
            state_info['value'] = model.value

        doc.add_next_tick_callback(before_ready)
        return slider

    serve_and_request(app)
    wait_until(lambda: 'queued' in state_info)

    assert state_info['queued'] == []
    assert state_info['deferred'] == []
    # The change is on the model, so the full serialization reproduces it
    assert state_info['value'] == 3


def test_threaded_hold_before_connected_does_not_strand_events():
    """
    The threaded branch must apply the same policy as the non-threaded
    one; previously it unconditionally scheduled an unhold, ignoring
    whether the session was connected.
    """
    docs, state_info, ran = [], {}, []

    def app():
        md = pn.pane.Markdown("initial")
        doc = state.curdoc
        docs.append(doc)

        def worker():
            with hold(doc):
                md.object = "changed"
                doc.add_next_tick_callback(lambda: ran.append('scheduled'))
            state_info['threaded'] = state._current_thread != state._thread_id
            state_info['connected'] = state._connected.get(doc)
            state_info['hold'] = doc.callbacks.hold_value
            state_info['queued'] = list(doc.callbacks._held_events)

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join()
        return md

    serve_and_request(app)
    wait_until(lambda: 'queued' in state_info)

    # Confirm we exercised the threaded branch while unconnected
    assert state_info['threaded']
    assert state_info['connected'] is None
    assert state_info['hold'] is None
    assert state_info['queued'] == []
    wait_until(lambda: ran == ['scheduled'])


@pytest.mark.xdist_group(name="server")
def test_hold_in_app_callable_does_not_leak_hold():
    build = {}

    def app():
        with hold():
            pass
        # A hold leaked here defers the unhold past ServerSession
        # construction, which registers this callback a second time
        # when the queued SessionCallbackAdded event is replayed.
        pn.state.add_periodic_callback(lambda: None, period=10000)
        build['thread_id'] = state._thread_id
        build['hold'] = state.curdoc.callbacks.hold_value
        return IntSlider()

    serve_and_request(app)

    assert build['thread_id'] is not None
    assert build['hold'] is None


class _FakeProtocol:
    def __init__(self):
        self.created = []

    def create(self, msgtype, events):
        msg = object()
        self.created.append(msg)
        return msg


class _FakeSocket:
    def __init__(self, lock_held):
        self.write_lock = tornado.locks.Lock()
        if lock_held:
            self.write_lock._block._value = 0
        self.ws_connection = type("W", (), {"is_closing": lambda s: True})()


class _FakeConn:
    def __init__(self, lock_held, socket_cls=_FakeSocket):
        self._socket = socket_cls(lock_held)
        self.protocol = _FakeProtocol()


def _asgi_transport():
    """
    Builds the real ASGI websocket transport Bokeh writes to, whose write
    lock wraps an asyncio.Lock rather than exposing Tornado's semaphore.
    """
    from bokeh.server.asgi import _ASGIWebSocketTransport
    return _ASGIWebSocketTransport(lambda event: None, supports_close_reason=True)


class _FakeASGISocket:
    """An ASGI transport shaped socket which can be handed a held lock."""

    def __init__(self, lock_held):
        from bokeh.server.asgi import _WriteLock
        self.write_lock = _WriteLock()
        if lock_held:
            # Acquiring is a coroutine, so lock the wrapped asyncio.Lock
            # directly to hold the lock without an event loop.
            self.write_lock._lock._locked = True


def test_socket_dispatcher_resolves_transport():
    from bokeh.server.asgi import _ASGIWebSocketTransport
    from tornado.websocket import WebSocketHandler

    import panel.io.asgi as asgi_module

    class FakeTornadoSocket(WebSocketHandler):
        def __init__(self):
            pass

    class ASGISubclass(_ASGIWebSocketTransport):
        pass

    assert _socket_dispatcher(FakeTornadoSocket()) is dispatch_tornado
    assert _socket_dispatcher(_asgi_transport()) is asgi_module.dispatch_asgi
    # A subclass of a registered transport must resolve via the MRO rather
    # than falling through to the Django consumer API.
    subclass = ASGISubclass(lambda event: None, supports_close_reason=True)
    assert _socket_dispatcher(subclass) is asgi_module.dispatch_asgi
    assert _socket_dispatcher(object()) is dispatch_django


def test_is_write_blocked_across_transports():
    # Tornado exposes the lock state on an internal semaphore
    tornado_socket = _FakeSocket(lock_held=False)
    assert not _is_write_blocked(tornado_socket)
    tornado_socket.write_lock._block._value = 0
    assert _is_write_blocked(tornado_socket)

    # Bokeh's ASGI _WriteLock wraps an asyncio.Lock
    asgi_socket = _asgi_transport()
    assert not _is_write_blocked(asgi_socket)
    asgi_socket.write_lock._lock._locked = True
    assert _is_write_blocked(asgi_socket)

    # A socket without a write lock is never blocked
    assert not _is_write_blocked(object())


@pytest.mark.xdist_group(name="server")
def test_unlocked_dispatches_from_worker_thread():
    """
    A model change made inside unlocked() from a worker thread (as happens
    when Bokeh runs a locked callback via asyncio.to_thread) must be
    scheduled for write rather than silently dropped with an error.
    """
    slider = IntSlider()

    serve_and_request(slider)
    wait_until(lambda: bool(slider._documents))

    doc, model = list(slider._documents.items())[0]
    session = doc.session_context.session
    asyncio_loop = doc.session_context.server_context.application_context.io_loop.asyncio_loop

    seen = {}

    def callback():
        # On Bokeh the synchronous body of a locked callback runs on a
        # worker thread via asyncio.to_thread. Previously unlocked() logged an
        # error and dropped events when off the loop thread.
        seen['thread'] = threading.get_ident()
        seen['on_loop'] = state._on_loop_thread
        with unlocked():
            model.value = 3

    async def trigger():
        # with_document_locked routes through _needs_document_lock, the same
        # wrapper Bokeh uses to dispatch protocol messages and session
        # callbacks. Entered without already holding the document lock, as
        # Bokeh does when handling an incoming message.
        result = session.with_document_locked(callback)
        if asyncio.iscoroutine(result):
            await result

    # Drive the locked callback from the server event loop thread.
    future = asyncio.run_coroutine_threadsafe(trigger(), asyncio_loop)
    future.result(timeout=5)

    # The model change made inside unlocked() must land regardless of which
    # thread the locked callback body ran on.
    wait_until(lambda: model.value == 3)
    assert 'on_loop' in seen


@pytest.mark.xdist_group(name="server")
def test_unblocked_only_for_document_lock_holder():
    """
    While a locked callback holds the document lock on a worker thread,
    only that thread may write to the Document directly. Any other
    thread has to schedule its changes, otherwise Bokeh raises because
    the writes race with the holder releasing the lock.
    """
    slider = IntSlider()

    serve_and_request(slider)
    wait_until(lambda: bool(slider._documents))

    doc = list(slider._documents)[0]
    session = doc.session_context.session
    asyncio_loop = doc.session_context.server_context.application_context.io_loop.asyncio_loop
    state._connected[doc] = True

    entered, release = threading.Event(), threading.Event()
    seen = {}

    def holder():
        with set_curdoc(doc):
            seen['holder'] = state._unblocked(doc)
        entered.set()
        release.wait(timeout=5)

    def other():
        with set_curdoc(doc):
            seen['other'] = state._unblocked(doc)

    async def trigger():
        await session.with_document_locked(holder)

    future = asyncio.run_coroutine_threadsafe(trigger(), asyncio_loop)
    try:
        assert entered.wait(timeout=5)
        thread = threading.Thread(target=other)
        thread.start()
        thread.join()
    finally:
        release.set()
    future.result(timeout=5)

    assert seen == {'holder': True, 'other': False}

    # Once released the holder's context no longer counts as owning the lock
    with set_curdoc(doc):
        assert not state._document_lock_held


@pytest.mark.xdist_group(name="server")
def test_unlocked_writes_immediately_only_for_document_lock_holder(monkeypatch):
    """
    Only the context holding the document lock may serialize and write
    its events right away. Another thread using unlocked() while the
    lock is held must leave its events to the holder's pending writes.
    """
    import panel.io.document as document

    slider = IntSlider()

    serve_and_request(slider)
    wait_until(lambda: bool(slider._documents))

    doc, model = list(slider._documents.items())[0]
    session = doc.session_context.session
    asyncio_loop = doc.session_context.server_context.application_context.io_loop.asyncio_loop
    monkeypatch.setitem(state._loaded, doc, True)

    socket_writes, bokeh_writes = [], []

    async def send_message(message):
        bokeh_writes.append(message)

    conn = _FakeConn(lock_held=False)
    conn.protocol = Protocol()
    conn.send_message = send_message
    monkeypatch.setattr(session, '_subscribed_connections', {conn})
    monkeypatch.setitem(
        extra_socket_handlers, _FakeSocket,
        lambda conn, msg=None: socket_writes.append(msg) or []
    )

    written = []
    write_from_worker_thread = document._write_from_worker_thread

    def spy(doc, connections, events):
        result = write_from_worker_thread(doc, connections, events)
        written.append(result)
        return result

    monkeypatch.setattr(document, '_write_from_worker_thread', spy)

    entered, release = threading.Event(), threading.Event()
    pending = {}

    def holder():
        with set_curdoc(doc), unlocked():
            model.value = 1
        pending['holder'] = len(session._pending_writes)
        entered.set()
        release.wait(timeout=5)

    def other():
        with set_curdoc(doc), unlocked():
            model.value = 2
        pending['other'] = len(session._pending_writes)

    async def trigger():
        await session.with_document_locked(holder)

    future = asyncio.run_coroutine_threadsafe(trigger(), asyncio_loop)
    try:
        assert entered.wait(timeout=5)
        thread = threading.Thread(target=other)
        thread.start()
        thread.join()
    finally:
        release.set()
    future.result(timeout=5)

    assert written[0] and not any(written[1:])
    assert pending == {'holder': 0, 'other': 1}
    wait_until(lambda: len(socket_writes) == 1 and len(bokeh_writes) == 1)


@pytest.mark.xdist_group(name="server")
def test_unblocked_only_for_patch_holder(threads):
    """
    While a client patch is applied on a worker thread only that thread
    may write to the Document directly, other pool threads must schedule.
    """
    slider = IntSlider()

    serve_and_request(slider)
    wait_until(lambda: bool(slider._documents))

    doc = list(slider._documents)[0]
    session = doc.session_context.session
    asyncio_loop = doc.session_context.server_context.application_context.io_loop.asyncio_loop
    state._connected[doc] = True

    seen = {}

    def other():
        with set_curdoc(doc):
            seen['other'] = state._unblocked(doc)

    class Patch:
        def apply_to_document(self, document, setter):
            with set_curdoc(document):
                seen['holder'] = state._unblocked(document)
            state._thread_pool.submit(other).result(timeout=5)

    class Connection:
        def ok(self, message):
            return None

    future = asyncio.run_coroutine_threadsafe(
        session._handle_patch(Patch(), Connection()), asyncio_loop
    )
    future.result(timeout=5)

    assert seen == {'holder': True, 'other': False}


def test_own_document_lock_restores_outer_owner():
    class Session:
        pass

    session = Session()
    with state._own_document_lock(session):
        outer = state._document_lock_owners[session]
        with state._own_document_lock(session):
            assert state._document_lock_owners[session] is not outer
        assert state._document_lock_owners[session] is outer
    assert session not in state._document_lock_owners


def test_thread_pool_tasks_do_not_inherit_document_lock():
    from panel.io.state import _run_without_document_lock

    seen = []
    token = state._document_lock.set(object())
    try:
        _run_without_document_lock(lambda: seen.append(state._document_lock.get()))
    finally:
        state._document_lock.reset(token)

    assert seen == [None]


@pytest.mark.xdist_group(name="server")
def test_threaded_hold_does_not_boomerang_python_changes():
    """
    A Python-side change made inside a hold on a worker thread is
    released on a later tick, after ``Syncable._changing`` is torn down,
    so it must not be re-processed as a frontend change.
    """
    slider = IntSlider()

    serve_and_request(slider)
    wait_until(lambda: bool(slider._documents))

    doc, model = list(slider._documents.items())[0]
    # Stands in for a client, so the hold is released on a later tick
    state._connected[doc] = True

    received = []
    process_events = slider._process_events
    slider._process_events = lambda events: received.append(events) or process_events(events)

    seen = {}

    def callback():
        # Bokeh runs locked next-tick callbacks on a worker thread
        seen['on_loop'] = state._on_loop_thread
        with hold(doc):
            slider.value = 3

    doc.add_next_tick_callback(callback)

    wait_until(lambda: model.value == 3 and not doc.callbacks.hold_value)
    # Leave time for a boomerang to pass through the change debounce
    time.sleep(0.5)

    assert seen['on_loop'] is False
    assert received == []


@pytest.mark.xdist_group(name="server")
def test_loop_hold_before_load_does_not_boomerang_python_changes():
    """
    Before the session has loaded, ``hold`` on the loop thread releases
    the events itself, after ``Syncable._changing`` is torn down.
    """
    slider = IntSlider()

    serve_and_request(slider)
    wait_until(lambda: bool(slider._documents))

    doc, model = list(slider._documents.items())[0]
    state._connected[doc] = True

    received = []
    process_events = slider._process_events
    slider._process_events = lambda events: received.append(events) or process_events(events)

    seen = {}

    def callback():
        with set_curdoc(doc):
            seen['on_loop'] = state._on_loop_thread
            seen['loaded'] = state.loaded
            with hold(doc):
                slider.value = 3

    _schedule_locked(doc, callback)

    wait_until(lambda: model.value == 3 and not doc.callbacks.hold_value)
    # Leave time for a boomerang to pass through the change debounce
    time.sleep(0.5)

    assert seen == {'on_loop': True, 'loaded': False}
    assert received == []


@pytest.mark.xdist_group(name="server")
def test_frontend_patch_applied_while_held_is_not_echoed():
    """
    A client patch applied while a worker thread holds the Document is
    collected by the hold and dispatched when it is released, after the
    patch has finished. It must still reach Python, but must not be sent
    back to the connection it came from, where it would overwrite
    anything the user typed since, e.g. dropping characters from a text
    input on a high latency connection.
    """
    slider = IntSlider()

    serve_and_request(slider)
    wait_until(lambda: bool(slider._documents))

    doc, model = list(slider._documents.items())[0]
    session = doc.session_context.session
    asyncio_loop = doc.session_context.server_context.application_context.io_loop.asyncio_loop
    state._connected[doc] = True

    class Connection:
        protocol = Protocol()

        def __init__(self):
            self.values = []

        async def send_message(self, message):
            if message.msgtype == 'PATCH-DOC':
                self.values += [
                    event['new'] for event in message.content['events']
                    if event.get('attr') == 'value'
                ]

        def ok(self, message):
            return None

    origin, other = Connection(), Connection()
    session.subscribe(origin)
    session.subscribe(other)

    patch = Protocol().create('PATCH-DOC', [ModelChangedEvent(doc, model, 'value', 5)])

    def worker():
        with set_curdoc(doc), hold(doc):
            asyncio.run_coroutine_threadsafe(
                session._handle_patch(patch, origin), asyncio_loop
            ).result(timeout=5)
            assert doc.callbacks.hold_value

    try:
        thread = threading.Thread(target=worker)
        thread.start()
        thread.join()

        wait_until(lambda: slider.value == 5 and not doc.callbacks.hold_value)
        # Leave time for an echo to be written
        time.sleep(0.2)
    finally:
        session.unsubscribe(origin)
        session.unsubscribe(other)

    assert origin.values == []
    assert other.values == [5]


def test_suppress_property_callbacks_keeps_frontend_changes():
    doc = Document()
    model = IntSlider().get_root(doc)
    doc.add_root(model)

    def invoker():
        pass

    python_event = ModelChangedEvent(doc, model, 'value', 1, callback_invoker=invoker)
    frontend_event = ModelChangedEvent(doc, model, 'value', 2, setter=object(), callback_invoker=invoker)

    _suppress_property_callbacks([python_event, frontend_event])

    assert python_event.callback_invoker is None
    assert frontend_event.callback_invoker is invoker


def test_write_events_shares_one_message_across_connections():
    """
    Serializing a patch marks the models it defines as synced on the
    Document, so a message must be created once and shared, otherwise
    every connection but the first receives references to models it was
    never sent.
    """
    written = []
    extra_socket_handlers[_FakeSocket] = lambda conn, msg=None: written.append((conn, msg)) or []

    try:
        doc = Document()
        conns = [_FakeConn(lock_held=False) for _ in range(3)]

        assert write_events(doc, conns, [object()], run=False) == []

        assert len(conns[0].protocol.created) == 1
        assert [conn for conn, _ in written] == conns
        assert {id(msg) for _, msg in written} == {id(conns[0].protocol.created[0])}
        assert not any(conn.protocol.created for conn in conns[1:])
    finally:
        extra_socket_handlers.pop(_FakeSocket, None)


def test_write_events_with_nothing_to_write():
    doc = Document()
    conn = _FakeConn(lock_held=False)

    assert write_events(doc, [conn], []) == []
    assert write_events(doc, [], [object()]) == []
    assert not conn.protocol.created


@pytest.mark.asyncio
async def test_schedule_write_events_defers_serialization():
    """
    Queued events must be serialized when they are written, not when they
    are queued, otherwise a message serialized later can be written first
    and reference models the client has not been sent yet.
    """
    written = []
    extra_socket_handlers[_FakeSocket] = lambda conn, msg=None: written.append(msg) or []

    try:
        doc = Document()
        conn = _FakeConn(lock_held=True)

        schedule_write_events(doc, [conn], [object()])
        await asyncio.sleep(0.05)

        # The socket is being written to, so nothing has been serialized
        assert conn.protocol.created == []
        assert written == []

        # Release the socket and let the write task drain the queue
        conn._socket.write_lock.release()
        await asyncio.sleep(0.05)

        assert len(conn.protocol.created) == 1
        assert written == conn.protocol.created
    finally:
        extra_socket_handlers.pop(_FakeSocket, None)
        _WRITE_BLOCK.pop(doc, None)


@pytest.mark.asyncio
async def test_schedule_write_events_defers_on_asgi_socket():
    """
    The write lock of an ASGI transport wraps an asyncio.Lock, so it has to
    be probed differently from Tornado's. If it is not detected, queued
    events are serialized and written while the socket is being written to,
    reordering messages relative to the ones Bokeh writes itself.
    """
    written = []
    extra_socket_handlers[_FakeASGISocket] = lambda conn, msg=None: written.append(msg) or []

    try:
        doc = Document()
        conn = _FakeConn(lock_held=True, socket_cls=_FakeASGISocket)

        schedule_write_events(doc, [conn], [object()])
        await asyncio.sleep(0.05)

        assert conn.protocol.created == []
        assert written == []

        conn._socket.write_lock._lock.release()
        await asyncio.sleep(0.05)

        assert len(conn.protocol.created) == 1
        assert written == conn.protocol.created
    finally:
        extra_socket_handlers.pop(_FakeASGISocket, None)
        _WRITE_BLOCK.pop(doc, None)


@pytest.mark.asyncio
async def test_schedule_write_events_writes_to_asgi_transport():
    """
    The queued write holds the transport's write lock while dispatching,
    so the ASGI dispatcher must not acquire the (non reentrant) lock again.
    """
    from bokeh.server.asgi import _ASGIWebSocketTransport

    import panel.io.asgi  # noqa: F401 registers the ASGI dispatcher

    sent = []

    async def send(event):
        sent.append(event)

    class ACKProtocol(_FakeProtocol):
        def create(self, msgtype, events):
            msg = Protocol().create('ACK')
            self.created.append(msg)
            return msg

    doc = Document()
    conn = _FakeConn(lock_held=False)
    conn._socket = _ASGIWebSocketTransport(send, supports_close_reason=True)
    conn.protocol = ACKProtocol()
    try:
        schedule_write_events(doc, [conn], [object()])
        await asyncio.wait_for(asyncio.gather(*_write_tasks.get(doc, [])), timeout=5)

        msg = conn.protocol.created[0]
        assert [e['text'] for e in sent] == [msg.header_json, msg.metadata_json, msg.content_json]
        assert not conn._socket.write_lock._lock.locked()
    finally:
        _WRITE_BLOCK.pop(doc, None)


@pytest.mark.asyncio
async def test_dispatch_msgs_terminates_on_document_destroy():
    """Pending _dispatch_msgs loop must stop after document is destroyed."""
    extra_socket_handlers[_FakeSocket] = lambda conn, msg=None: []

    try:
        doc = Document()
        conn = _FakeConn(lock_held=True)
        ref = weakref.ref(doc)

        schedule_write_events(doc, [conn], [object()])
        await asyncio.sleep(0.05)

        assert doc in _write_tasks
        assert doc in _WRITE_BLOCK

        doc.destroy = partial(_destroy_document, doc)
        doc.destroy(None)
        del doc, conn
        await asyncio.sleep(0.05)
        gc.collect()

        assert ref() is None
    finally:
        extra_socket_handlers.pop(_FakeSocket, None)


class _ClosingWSConnection:
    """
    Mimics a Tornado websocket whose peer disconnects during a write: the
    first frame fails asynchronously and aborts the connection, so the
    following writes raise synchronously.
    """

    def __init__(self):
        self.closing = False

    def is_closing(self):
        return self.closing

    def write_message(self, message, binary=False):
        from tornado.websocket import WebSocketClosedError

        async def fail():
            raise WebSocketClosedError()

        self.closing = True
        return asyncio.ensure_future(fail())


@pytest.mark.asyncio
async def test_write_message_handles_connection_closed_mid_message(caplog):
    from tornado.websocket import WebSocketHandler

    from panel.io.document import _dispatch_write_task, _write_message

    class ClosingSocket(WebSocketHandler):
        def __init__(self):
            self.write_lock = tornado.locks.Lock()
            self.ws_connection = _ClosingWSConnection()

    conn = _FakeConn(lock_held=False)
    conn._socket = ClosingSocket()
    doc = Document()
    message = Protocol().create('ACK')

    loop = asyncio.get_running_loop()
    unhandled = []
    handler = loop.get_exception_handler()
    loop.set_exception_handler(lambda loop, context: unhandled.append(context))
    try:
        with caplog.at_level('WARNING', logger='panel.io.document'):
            _dispatch_write_task(doc, _write_message, doc, [conn], message)
            tasks = list(_write_tasks.get(doc, []))
            await asyncio.wait(tasks, timeout=5)
            del tasks
            await asyncio.sleep(0.01)
            gc.collect()
    finally:
        loop.set_exception_handler(handler)

    assert unhandled == []
    assert [r.getMessage() for r in caplog.records] == [
        "Failed sending message as connection was closed"
    ]


def test_keep_unsent_models_new_across_client_patch():
    doc = Document()
    column = pn.Column()
    root = column.get_root(doc)
    doc.add_root(root)
    _keep_unsent_models_new(doc)
    doc.to_json()

    with set_curdoc(doc):
        column.append(pn.pane.Markdown('unsent'))
    unsent = set(doc.models._new_models)
    assert unsent

    doc.apply_json_patch({'events': [
        {'kind': 'ModelChanged', 'model': {'id': root.id}, 'attr': 'name', 'new': 'renamed'}
    ]})

    assert unsent <= doc.models._new_models


def test_keep_unsent_models_new_still_flushes_own_patches():
    doc = Document()
    column = pn.Column()
    doc.add_root(column.get_root(doc))
    _keep_unsent_models_new(doc)
    doc.to_json()

    sizes = []
    with set_curdoc(doc):
        for i in range(3):
            doc.hold()
            column.append(pn.pane.Markdown(f'item {i}'))
            events, doc.callbacks._held_events = list(doc.callbacks._held_events), []
            sizes.append(len(Protocol().create('PATCH-DOC', events).content_json))
            doc.callbacks._hold = None

    assert sizes[2] == pytest.approx(sizes[1], abs=100)


def test_client_has_document_handles_destroyed_document():
    doc = Document()
    doc.add_root(pn.Column().get_root(doc))
    doc._session_context = lambda: MockSessionContext(doc)
    assert not _client_has_document(doc)

    doc.to_json()
    assert _client_has_document(doc)

    doc.models.destroy()
    assert not _client_has_document(doc)


def test_client_has_document_ignores_sessionless_document():
    doc = Document()
    doc.add_root(pn.Column().get_root(doc))

    doc.to_json()
    assert not _client_has_document(doc)


def test_client_has_document_counts_a_notebook_comm():
    doc = Document()
    root = pn.Column().get_root(doc)
    doc.add_root(root)

    doc.to_json()
    _state._views[root.ref['id']] = (None, root, doc, object())
    try:
        assert _client_has_document(doc)
    finally:
        del _state._views[root.ref['id']]


def test_client_has_document_counts_a_change_subscriber():
    doc = Document()
    doc.add_root(pn.Column().get_root(doc))
    assert not _client_has_document(doc)

    doc.on_change(lambda event: None)
    assert _client_has_document(doc)


class _ESMValue(pn.custom.JSComponent):

    value = param.Integer(default=0)

    _esm = "export function render() {}"


@pytest.mark.parametrize('threaded', [False, True])
def test_hold_dispatches_to_sessionless_change_subscriber(threaded, monkeypatch):
    """
    An embedder that syncs a sessionless Document over its own transport
    subscribes to its changes and must receive changes made in a hold,
    e.g. by ReactiveESM._update_model.
    """
    if threaded:
        monkeypatch.setattr(type(state), '_on_loop_thread', property(lambda self: False))
    component = _ESMValue()
    doc = Document()
    model = component.get_root(doc)
    doc.add_root(model)
    events = []
    doc.on_change(events.append)

    component.value = 3

    assert doc.callbacks.hold_value is None
    assert [
        (event.attr, event.new) for event in events if isinstance(event, ModelChangedEvent)
    ] == [('value', 3)]
    _cleanup_doc(doc, destroy=True)


def test_keep_unsent_models_new_skips_a_bokeh_without_new_models():
    doc = Document()
    doc.add_root(pn.Column().get_root(doc))
    doc._session_context = lambda: MockSessionContext(doc)
    del doc.models._new_models
    _keep_unsent_models_new(doc)

    assert not getattr(doc.apply_json_patch, '_panel_keeps_unsent', False)


def test_init_doc_keeps_unsent_models_new_once():
    doc = Document()
    doc.add_root(pn.Column().get_root(doc))
    doc._session_context = lambda: MockSessionContext(doc)

    init_doc(doc)
    wrapper = doc.apply_json_patch
    assert getattr(wrapper, '_panel_keeps_unsent', False)

    init_doc(doc)
    assert doc.apply_json_patch is wrapper


def test_comm_patch_with_multiple_changes_syncs_all_properties():
    doc = Document()
    comm = state._comm_manager.get_server_comm()
    info = BrowserInfo()
    model = info._render_model(doc, comm)
    doc.unhold()

    doc.hold()
    for attr, value in [
        ('dark_mode', False), ('device_pixel_ratio', 2.0),
        ('language', 'en'), ('timezone', 'Europe/Berlin'),
    ]:
        model.set_from_json(attr, value, setter=comm.id)
    doc.unhold()

    assert info.dark_mode is False
    assert info.device_pixel_ratio == 2.0
    assert info.language == 'en'
    assert info.timezone == 'Europe/Berlin'
    assert doc.callbacks._held_events == []


def test_comm_patch_syncs_changes_across_models():
    doc = Document()
    comm = state._comm_manager.get_server_comm()
    info = BrowserInfo()
    info_model = info._render_model(doc, comm)
    slider = IntSlider(start=0, end=10, value=0)
    slider_model = slider._render_model(doc, comm)
    doc.unhold()

    doc.hold()
    info_model.set_from_json('dark_mode', True, setter=comm.id)
    slider_model.set_from_json('value', 5, setter=comm.id)
    doc.unhold()

    assert info.dark_mode is True
    assert slider.value == 5


def test_hold_with_comm_restores_unheld_state(monkeypatch):
    pushed = []
    monkeypatch.setattr('panel.io.notebook.push', lambda doc, comm: pushed.append(comm))
    doc = Document()
    comm = state._comm_manager.get_server_comm()

    with hold(doc, comm=comm):
        pass

    assert doc.callbacks.hold_value is None
    assert pushed == [comm]


def test_hold_with_comm_keeps_persistent_hold(monkeypatch):
    monkeypatch.setattr('panel.io.notebook.push', lambda doc, comm: None)
    doc = Document()
    comm = state._comm_manager.get_server_comm()
    doc.hold('combine')

    with hold(doc, comm=comm):
        pass

    assert doc.callbacks.hold_value == 'combine'


def test_cleanup_doc_releases_document():
    doc = Document()
    col = pn.Column(IntSlider(), pn.pane.Markdown('# Title'))
    col.server_doc(doc)
    ref = weakref.ref(doc)
    assert doc in state._locations

    _cleanup_doc(doc)

    assert doc not in state._locations
    assert not col._documents
    assert not col._models
    del doc
    gc.collect()
    assert ref() is None


def test_cleanup_doc_runs_session_destroyed_callbacks_with_context():
    doc = Document()
    col = pn.Column(IntSlider())
    col.server_doc(doc)
    contexts = []
    doc.on_session_destroyed(contexts.append)

    _cleanup_doc(doc)

    assert len(contexts) == 1
    assert contexts[0].document is doc


def test_destroy_document_releases_document_held_by_model():
    doc = Document()
    doc.destroy = partial(_destroy_document, doc)
    col = pn.Column(IntSlider())
    col.server_doc(doc)
    # The Location is not cleaned up with the root and keeps its model
    location = state._locations[doc]
    ref = weakref.ref(doc)

    _cleanup_doc(doc)
    del doc, col
    gc.collect()

    assert location._models
    assert ref() is None


def test_server_session_destroyed_releases_document():
    refs = []
    def app():
        refs.append(weakref.ref(state.curdoc))
        return pn.Column(IntSlider(), pn.pane.Markdown('# Title'))

    serve_and_request(
        app, n=3, check_unused_sessions_milliseconds=200,
        unused_session_lifetime_milliseconds=200
    )

    assert len(refs) == 3
    def collected():
        gc.collect()
        return all(ref() is None for ref in refs)
    wait_until(collected, timeout=10000)


@pytest.fixture
def recompute_count(monkeypatch):
    from bokeh.document.models import DocumentModelManager

    count = []
    recompute = DocumentModelManager.recompute
    def counting_recompute(self):
        count.append(1)
        recompute(self)
    monkeypatch.setattr(DocumentModelManager, 'recompute', counting_recompute)
    return count


def _rendered_column(n=3):
    doc = Document()
    column = pn.Column(*[pn.pane.Markdown(f'item {i}') for i in range(n)])
    root = column.get_root(doc)
    doc.add_root(root)
    doc.models.flush_synced()
    return doc, column, root


def _assert_graph_matches_recompute(doc):
    incremental = dict(doc.models._models)
    doc.models.recompute()
    assert incremental == doc.models._models


def test_freeze_doc_attaches_appended_models_without_recompute(recompute_count):
    doc, column, root = _rendered_column()
    recompute_count.clear()
    new = pn.Row(pn.pane.Markdown('appended'), pn.widgets.IntSlider())
    existing = set(doc.models._models)

    with set_curdoc(doc):
        column.append(new)

    assert not recompute_count
    models = new._models[root.ref['id']][0].references()
    assert len(models) > 2
    for model in models:
        assert model.document is doc
        assert doc.models._models[model.id] is model
        # Stylesheets are shared with the existing children and so were synced before
        assert (model in doc.models._new_models) == (model.id not in existing)
    _assert_graph_matches_recompute(doc)


def test_freeze_doc_reorder_does_not_recompute(recompute_count):
    doc, column, root = _rendered_column()
    recompute_count.clear()

    with set_curdoc(doc):
        column.objects = column.objects[::-1]

    assert not recompute_count
    assert [c.text.strip() for c in root.children] == [
        '&lt;p&gt;item 2&lt;/p&gt;', '&lt;p&gt;item 1&lt;/p&gt;', '&lt;p&gt;item 0&lt;/p&gt;'
    ]
    _assert_graph_matches_recompute(doc)


def test_freeze_doc_recomputes_when_models_are_removed(recompute_count):
    doc, column, root = _rendered_column()
    recompute_count.clear()
    removed = root.children[0]

    with set_curdoc(doc):
        column.pop(0)

    assert len(recompute_count) == 1
    assert removed.document is None
    assert removed.id not in doc.models._models
    with set_curdoc(doc):
        column[0] = pn.pane.Markdown('replaced')

    assert len(recompute_count) == 2
    _assert_graph_matches_recompute(doc)


def test_freeze_doc_recomputes_when_graph_changed_while_frozen(recompute_count):
    from bokeh.models import CustomJS

    from panel.io.document import freeze_doc

    doc, column, root = _rendered_column()
    recompute_count.clear()
    added = pn.pane.Markdown('added')._get_model(doc, root, root)
    added.name = 'added'
    children = list(root.children) + [added]

    with freeze_doc(doc, root, {'children': children}):
        root.children = children
        root.children[0].js_on_change('text', CustomJS(code=''))

    assert len(recompute_count) == 1
    callback = root.children[0].js_property_callbacks['change:text'][0]
    assert callback.document is doc
    assert added.document is doc
    assert doc.get_model_by_name('added') is added
    _assert_graph_matches_recompute(doc)


def test_freeze_doc_nested_freezes_recompute_once(recompute_count):
    from panel.io.document import freeze_doc

    doc, column, root = _rendered_column()
    recompute_count.clear()
    outer = pn.pane.Markdown('outer')._get_model(doc, root, root)
    inner = pn.pane.Markdown('inner')._get_model(doc, root, root)
    outer.name, inner.name = 'outer', 'inner'

    with freeze_doc(doc, root, {'children': list(root.children) + [outer]}):
        root.children = list(root.children) + [outer]
        with freeze_doc(doc, root, {'children': list(root.children) + [inner]}):
            root.children = list(root.children) + [inner]
        assert inner.document is None

    assert len(recompute_count) == 1
    assert outer.document is doc
    assert inner.document is doc
    assert doc.get_model_by_name('outer') is outer
    assert doc.get_model_by_name('inner') is inner
    _assert_graph_matches_recompute(doc)


def test_freeze_doc_releases_freeze_on_error():
    from panel.io.document import freeze_doc

    doc, column, root = _rendered_column()

    with pytest.raises(RuntimeError):
        with freeze_doc(doc, root, {'children': []}):
            raise RuntimeError('boom')

    assert doc.models._freeze_count == 0
    assert 'invalidate' not in doc.models.__dict__


def test_freeze_doc_unchanged_properties_do_not_freeze(recompute_count):
    from panel.io.document import freeze_doc

    doc, column, root = _rendered_column()
    recompute_count.clear()

    with freeze_doc(doc, root, {'children': list(root.children), 'width': 100}):
        assert doc.models._freeze_count == 0
        root.width = 100

    assert not recompute_count


def test_combine_events_matches_bokeh_combine_policy():
    """
    Holding with 'collect' and combining on release must produce the
    same events as bokeh's quadratic 'combine' policy.
    """
    import copy
    import random

    from bokeh.document.callbacks import _combine_document_events
    from bokeh.document.events import RootAddedEvent, TitleChangedEvent

    from panel.io.document import _combine_events

    rng = random.Random(1)
    doc = Document()
    models = [Div() for _ in range(5)]
    setters = [None, object()]
    events = []
    for _ in range(500):
        r = rng.random()
        if r < 0.85:
            events.append(ModelChangedEvent(
                doc, rng.choice(models), rng.choice(['text', 'visible']),
                rng.random(), setter=rng.choice(setters), callback_invoker=object()
            ))
        elif r < 0.95:
            events.append(TitleChangedEvent(doc, str(rng.random()), setter=rng.choice(setters)))
        else:
            events.append(RootAddedEvent(doc, rng.choice(models)))

    expected = []
    for event in events:
        _combine_document_events(copy.copy(event), expected)
    combined = _combine_events(events)

    def signature(event):
        return (
            type(event), getattr(event, 'model', None), getattr(event, 'attr', None),
            getattr(event, 'new', None), getattr(event, 'title', None),
            event.setter, event.callback_invoker,
        )

    assert len(combined) < len(events)
    assert [signature(e) for e in combined] == [signature(e) for e in expected]


def test_hold_collects_and_combines_on_release():
    """
    Panel holds the Document with the 'collect' policy and combines the
    events when it releases the hold, so only the last value of a
    property set repeatedly inside the hold is dispatched.
    """
    doc = Document()
    doc.callbacks._change_callbacks[None] = lambda e: e
    model = IntSlider().get_root(doc)
    doc.add_root(model)
    state._connected[doc] = True

    dispatched = []
    doc.on_change(dispatched.append)

    with set_curdoc(doc):
        with hold(doc):
            assert doc.callbacks.hold_value == 'collect'
            for i in range(1, 11):
                model.value = i
            assert len(doc.callbacks._held_events) == 10

    assert doc.callbacks.hold_value is None
    assert [(e.attr, e.new) for e in dispatched] == [('value', 10)]


@pytest.mark.asyncio
async def test_dispatch_msgs_merges_queued_batches_into_one_message():
    """
    Batches queued while the socket was busy are written in one message
    once it is released, in the order they were queued.
    """
    written = []
    extra_socket_handlers[_FakeSocket] = lambda conn, msg=None: written.append(msg) or []

    class RecordingProtocol(_FakeProtocol):
        def create(self, msgtype, events):
            self.created.append(list(events))
            return self.created[-1]

    try:
        doc = Document()
        conn = _FakeConn(lock_held=True)
        conn.protocol = RecordingProtocol()
        first, second = object(), object()

        schedule_write_events(doc, [conn], [first])
        schedule_write_events(doc, [conn], [second])
        await asyncio.sleep(0.05)

        assert len(_write_tasks[doc]) == 1
        assert conn.protocol.created == []

        conn._socket.write_lock.release()
        await asyncio.sleep(0.05)

        assert conn.protocol.created == [[first, second]]
        assert written == conn.protocol.created
        assert doc not in _WRITE_BLOCK
    finally:
        extra_socket_handlers.pop(_FakeSocket, None)
        _WRITE_BLOCK.pop(doc, None)


@pytest.mark.xdist_group(name="server")
def test_scheduled_updates_from_thread_are_batched_without_loss(threads, monkeypatch):
    """
    Updates made from a thread that does not hold the document lock are
    applied by a single locked callback and written in one message,
    with every intermediate value, in order.
    """
    slider = IntSlider()

    serve_and_request(slider)
    wait_until(lambda: bool(slider._documents))

    doc, model = list(slider._documents.items())[0]
    session = doc.session_context.session
    monkeypatch.setitem(state._loaded, doc, True)
    monkeypatch.setitem(state._connected, doc, True)

    messages = []
    conn = _FakeConn(lock_held=False)
    conn.protocol = Protocol()
    monkeypatch.setattr(session, '_subscribed_connections', {conn})
    monkeypatch.setitem(
        extra_socket_handlers, _FakeSocket,
        lambda conn, msg=None: messages.append(msg) or []
    )

    n = 50
    expected = list(range(1, n + 1))

    def update():
        with set_curdoc(doc):
            for value in expected:
                slider.value = value

    # Batching coalesces whatever is queued when the locked callback runs,
    # so pause the event loop until every update is queued; otherwise the
    # loop may apply each update before the next one is made.
    asyncio_loop = doc.session_context.server_context.application_context.io_loop.asyncio_loop
    paused, resume = threading.Event(), threading.Event()

    def pause():
        paused.set()
        resume.wait(timeout=5)

    asyncio_loop.call_soon_threadsafe(pause)
    assert paused.wait(timeout=5)
    try:
        state._thread_pool.submit(update).result(timeout=5)
    finally:
        resume.set()

    def values():
        return [
            event['new'] for msg in messages for event in msg.content['events']
            if event['kind'] == 'ModelChanged' and event['attr'] == 'value'
        ]

    wait_until(lambda: len(values()) >= n)
    assert values() == expected
    assert len(messages) == 1
    assert model.value == n


class _RunningESM(pn.custom.JSComponent):

    running = param.Boolean()

    _esm = 'export function render() {}'


def _discard_session(doc):
    # The order of bokeh's session discard: the Document is destroyed
    # before the session_destroyed callbacks clean up the Panel views.
    _destroy_document(doc, None)
    _on_session_destroyed(MockSessionContext(doc))


def test_destroy_document_stops_periodic_callback_bound_to_esm_component():
    doc = Document()
    with set_curdoc(doc):
        cb = state.add_periodic_callback(lambda: None, period=1000)
    component = _RunningESM(running=cb.param.running)
    component.server_doc(doc)
    assert component.running
    ref = weakref.ref(doc)

    _discard_session(doc)

    assert not cb.running
    assert not component.running
    assert not component._models
    del doc
    gc.collect()
    assert ref() is None


def test_esm_property_change_while_document_is_destroyed():
    doc = Document()
    component = _RunningESM()
    component.server_doc(doc)

    _destroy_document(doc, None)
    component.running = True
    component.width = 300
    _on_session_destroyed(MockSessionContext(doc))

    assert component.running
    assert not component._models


@pytest.mark.xdist_group(name="server")
def test_held_batch_handed_to_bokeh_is_written_in_one_message(monkeypatch):
    """
    A held batch that cannot be written right away because the socket is
    being written to is left to Bokeh, which must still write it to the
    client in one message.
    """
    col = pn.Column(*(pn.pane.Markdown('a') for _ in range(5)))

    serve_and_request(col)
    wait_until(lambda: bool(col._documents))

    doc = list(col._documents)[0]
    session = doc.session_context.session
    asyncio_loop = doc.session_context.server_context.application_context.io_loop.asyncio_loop
    monkeypatch.setitem(state._loaded, doc, True)
    monkeypatch.setitem(state._connected, doc, True)

    messages = []

    async def send_message(message):
        messages.append(message)

    conn = _FakeConn(lock_held=True)
    conn.protocol = Protocol()
    conn.send_message = send_message
    monkeypatch.setattr(session, '_subscribed_connections', {conn})

    async def callback():
        with set_curdoc(doc), hold():
            for md in col:
                md.object = 'b'

    async def trigger():
        await session.with_document_locked(callback)

    asyncio.run_coroutine_threadsafe(trigger(), asyncio_loop).result(timeout=5)

    assert len(messages) == 1
    assert [event['attr'] for event in messages[0].content['events']] == ['text'] * 5


def _undefined_references(messages, known):
    """
    Returns the ids of models a sequence of PATCH-DOC messages refers to
    before any message, or the initial Document, defined them.
    """
    def walk(obj, defined, referenced):
        if isinstance(obj, dict):
            if obj.get('type') == 'object' and 'id' in obj:
                defined.append(obj['id'])
            elif set(obj) == {'id'}:
                referenced.append(obj['id'])
            for value in obj.values():
                walk(value, defined, referenced)
        elif isinstance(obj, (list, tuple)):
            for value in obj:
                walk(value, defined, referenced)

    known, undefined = set(known), []
    for msg in messages:
        defined, referenced = [], []
        walk(msg.content, defined, referenced)
        known |= set(defined)
        undefined += [ref for ref in referenced if ref not in known]
    return undefined


def _text_changes(messages):
    return [
        event for msg in messages for event in msg.content['events']
        if event['kind'] == 'ModelChanged' and event['attr'] == 'text'
    ]


def _sends_text(messages, text):
    """
    Whether a message sets a Markdown to ``text``, either as a change or
    in the definition of a model the client was not sent yet, which
    already carries changes made before it was written.
    """
    html = f'&lt;p&gt;{text}&lt;/p&gt;'
    return any(html in json.dumps(msg.content, default=str) for msg in messages)


def _serve_with_message_log(obj, monkeypatch):
    """
    Serves obj and records every message written to a fake connection,
    whether Panel writes it to the socket directly or Bokeh sends it
    after a locked callback, in the order they are written.
    """
    serve_and_request(obj)
    wait_until(lambda: bool(obj._documents))

    doc = list(obj._documents)[0]
    session = doc.session_context.session
    monkeypatch.setitem(state._loaded, doc, True)
    monkeypatch.setitem(state._connected, doc, True)

    messages = []

    async def send_message(message):
        messages.append(message)

    conn = _FakeConn(lock_held=False)
    conn.protocol = Protocol()
    conn.send_message = send_message
    monkeypatch.setattr(session, '_subscribed_connections', {conn})
    monkeypatch.setitem(
        extra_socket_handlers, _FakeSocket,
        lambda conn, msg=None: messages.append(msg) or []
    )
    # The client has been sent the Document
    doc.models.flush_synced()
    known = {model.id for model in doc.models}
    return doc, messages, known


@pytest.mark.xdist_group(name="server")
@pytest.mark.parametrize('pending', [False, True])
def test_unlocked_change_on_loop_is_ordered_after_locked_callback(pending, monkeypatch):
    """
    An unlocked change made on the event loop, e.g. by an async
    callback, while a locked callback on a worker thread attaches the
    model it changes must not reach the client ahead of the model.
    """
    col = pn.Column(pn.pane.Markdown('a'))
    doc, messages, known = _serve_with_message_log(col, monkeypatch)
    session = doc.session_context.session
    asyncio_loop = doc.session_context.server_context.application_context.io_loop.asyncio_loop

    md = pn.pane.Markdown('b')
    entered, release = threading.Event(), threading.Event()
    paused, resume = threading.Event(), threading.Event()

    def pause():
        paused.set()
        resume.wait(timeout=5)

    def change():
        with set_curdoc(doc):
            md.object = 'c'

    def holder():
        with set_curdoc(doc):
            if pending:
                # A change Bokeh writes once the callback has returned
                doc.roots[0].css_classes = ['pending']
            # Block the event loop so that the unlocked change is queued
            # to run before the loop writes the attached model.
            asyncio_loop.call_soon_threadsafe(pause)
            assert paused.wait(timeout=5)
            # A fresh context, so the change does not inherit the lock
            asyncio_loop.call_soon_threadsafe(change, context=contextvars.Context())
            col.append(md)
            resume.set()
        entered.set()
        release.wait(timeout=5)

    async def trigger():
        await session.with_document_locked(holder)

    future = asyncio.run_coroutine_threadsafe(trigger(), asyncio_loop)
    try:
        assert entered.wait(timeout=5)
    finally:
        resume.set()
        release.set()
    future.result(timeout=5)

    wait_until(lambda: _sends_text(messages, 'c'))
    assert _undefined_references(messages, known) == []


@pytest.mark.xdist_group(name="server")
def test_unlocked_change_while_locked_callback_writes_is_deferred(monkeypatch):
    """
    An unlocked change made while the context holding the document lock
    is writing the changes of its callback must be written after them.
    """
    col = pn.Column(pn.pane.Markdown('a'))
    doc, messages, known = _serve_with_message_log(col, monkeypatch)
    session = doc.session_context.session
    asyncio_loop = doc.session_context.server_context.application_context.io_loop.asyncio_loop

    md = pn.pane.Markdown('b')
    send_pending_patches = session._send_pending_patches

    def change():
        with set_curdoc(doc):
            md.object = 'c'

    async def send_while_changing(pending):
        contextvars.Context().run(change)
        await send_pending_patches(pending)

    monkeypatch.setattr(session, '_send_pending_patches', send_while_changing)

    def holder():
        with set_curdoc(doc):
            doc.roots[0].css_classes = ['pending']
            col.append(md)

    async def trigger():
        await session.with_document_locked(holder)

    asyncio.run_coroutine_threadsafe(trigger(), asyncio_loop).result(timeout=5)

    wait_until(lambda: _sends_text(messages, 'c'))
    assert _undefined_references(messages, known) == []


def _rerender_with_linked_range(holder, other):
    """
    Re-renders ``holder`` twice, linking ``other`` to a range that only
    the first render defined, like two HoloViews plots with a shared axis.
    Combining folds the second render into the first, discarding the
    only definition of the range ahead of the change to its start.
    """
    shared = Range1d(0, 1)
    holder.children = [figure(x_range=shared)]
    shared.start = 5
    other.x_range = shared
    holder.children = [figure()]


@pytest.mark.xdist_group(name="server")
@pytest.mark.parametrize('threaded', [False, True])
def test_hold_drops_changes_to_unsent_models_when_combining(threaded, monkeypatch):
    holder, other = BkColumn(children=[figure()]), figure()
    pane = pn.pane.Bokeh(BkColumn(children=[holder, other]))
    doc, messages, _ = _serve_with_message_log(pane, monkeypatch)
    client_models = list(doc.models)
    asyncio_loop = doc.session_context.server_context.application_context.io_loop.asyncio_loop
    holder, other = doc.select_one({'id': holder.id}), doc.select_one({'id': other.id})

    def rerender():
        with set_curdoc(doc), hold(doc):
            _rerender_with_linked_range(holder, other)

    if threaded:
        thread = threading.Thread(target=rerender)
        thread.start()
        thread.join()
    else:
        async def run():
            rerender()
        asyncio.run_coroutine_threadsafe(run(), asyncio_loop).result(timeout=5)

    wait_until(lambda: any(
        event.get('attr') == 'x_range'
        for msg in messages for event in msg.content['events']
    ))
    # Bokeh resolves references in order, even within one message
    deserializer = Deserializer(references=client_models)
    for msg in messages:
        deserializer.decode(msg.content)


def test_hold_with_comm_drops_changes_to_unsent_models_when_combining(monkeypatch):
    sent = []
    monkeypatch.setattr('panel.io.notebook.send', lambda comm, msg: sent.append(msg))
    holder, other = BkColumn(children=[figure()]), figure()
    doc = Document()
    doc.add_root(BkColumn(children=[holder, other]))
    doc.models.flush_synced()
    client_models = list(doc.models)
    comm = state._comm_manager.get_server_comm()
    comm._comm = object()

    with hold(doc, comm=comm):
        _rerender_with_linked_range(holder, other)

    [msg] = sent
    Deserializer(references=client_models).decode(msg.content)


def _serialize_append_blocked_before_flush(doc, col, md, monkeypatch):
    """
    Appends md in a locked callback with a pending write, so Bokeh
    serializes it once the callback returned, and blocks that
    serialization after encoding the message but before marking the
    models it defines as sent.
    """
    session = doc.session_context.session
    asyncio_loop = doc.session_context.server_context.application_context.io_loop.asyncio_loop
    encoded, resume = threading.Event(), threading.Event()
    flush_synced = doc.models.flush_synced

    def blocking_flush_synced(*args, **kwargs):
        if not encoded.is_set():
            encoded.set()
            resume.wait(timeout=5)
        return flush_synced(*args, **kwargs)

    monkeypatch.setattr(doc.models, 'flush_synced', blocking_flush_synced)

    def holder():
        with set_curdoc(doc):
            doc.roots[0].css_classes = ['pending']
            col.append(md)

    async def trigger():
        await session.with_document_locked(holder)

    future = asyncio.run_coroutine_threadsafe(trigger(), asyncio_loop)
    return future, encoded, resume


@pytest.mark.xdist_group(name="server")
@pytest.mark.parametrize('append', [False, True])
def test_unlocked_keeps_change_to_model_a_message_is_serializing(append, monkeypatch):
    """
    Bokeh marks the models a message defines as sent only once it has
    serialized the whole message, so a change made meanwhile to a model
    it already encoded must not be dropped as one to an unsent model,
    also when the same changes refer to that model again.
    """
    col = pn.Column(pn.pane.Markdown('a'))
    doc, messages, known = _serve_with_message_log(col, monkeypatch)
    asyncio_loop = doc.session_context.server_context.application_context.io_loop.asyncio_loop
    md = pn.pane.Markdown('b')
    future, encoded, resume = _serialize_append_blocked_before_flush(doc, col, md, monkeypatch)

    async def change():
        with set_curdoc(doc), unlocked():
            model.text = model.text.replace('&lt;p&gt;b', '&lt;p&gt;c')
            if append:
                col.append(pn.pane.Markdown('z'))

    try:
        assert encoded.wait(timeout=5)
        model = next(iter(md._models.values()))[0]
        assert model in doc.models._new_models
        asyncio.run_coroutine_threadsafe(change(), asyncio_loop).result(timeout=5)
    finally:
        resume.set()
    future.result(timeout=5)

    wait_until(lambda: _sends_text(messages, 'c'))
    if append:
        wait_until(lambda: _sends_text(messages, 'z'))
    assert _undefined_references(messages, known) == []


def test_drop_undefined_changes_keeps_changes_to_models_the_events_define():
    holder = BkColumn()
    doc = Document()
    doc.add_root(BkColumn(children=[holder]))
    doc.models.flush_synced()

    doc.hold('collect')
    div = Div(text='a')
    holder.children = [div]
    div.text = 'b'
    attach, change = doc.callbacks._held_events
    doc.callbacks._held_events = []
    doc.callbacks._hold = None

    assert _drop_undefined_changes(doc, [attach, change]) == [attach, change]
    assert _drop_undefined_changes(doc, [change]) == []


@pytest.mark.xdist_group(name="server")
def test_async_locked_callback_writes_while_it_awaits(monkeypatch):
    """
    An async callback holding the document lock owns it across awaits,
    so its changes are written before it returns.
    """
    md = pn.pane.Markdown('a')
    doc, messages, _ = _serve_with_message_log(md, monkeypatch)
    session = doc.session_context.session
    asyncio_loop = doc.session_context.server_context.application_context.io_loop.asyncio_loop

    seen = []

    async def holder():
        with set_curdoc(doc):
            md.object = 'progress'
        await asyncio.sleep(0.2)
        seen.append(len(_text_changes(messages)))

    async def trigger():
        await session.with_document_locked(holder)

    asyncio.run_coroutine_threadsafe(trigger(), asyncio_loop).result(timeout=5)
    assert seen == [1]


@pytest.mark.xdist_group(name="server")
def test_deferred_unlocked_change_precedes_later_locked_callback(monkeypatch):
    """
    Events held back while the lock holder writes its changes are written
    before the changes of the next context to take the lock.
    """
    md = pn.pane.Markdown('a')
    doc, messages, _ = _serve_with_message_log(md, monkeypatch)
    session = doc.session_context.session
    asyncio_loop = doc.session_context.server_context.application_context.io_loop.asyncio_loop

    send_pending_patches = session._send_pending_patches
    later = {}

    def change():
        with set_curdoc(doc):
            md.object = 'unlocked'

    def locked_later():
        with set_curdoc(doc):
            md.object = 'locked'

    async def send_while_changing(pending):
        later['future'] = asyncio.ensure_future(session.with_document_locked(locked_later))
        await asyncio.sleep(0)
        contextvars.Context().run(change)
        await send_pending_patches(pending)

    monkeypatch.setattr(session, '_send_pending_patches', send_while_changing)

    def holder():
        with set_curdoc(doc):
            doc.roots[0].css_classes = ['pending']

    async def trigger():
        await session.with_document_locked(holder)
        await later['future']

    asyncio.run_coroutine_threadsafe(trigger(), asyncio_loop).result(timeout=5)

    wait_until(lambda: len(_text_changes(messages)) == 2)
    assert md.object == 'locked'
    texts = [event['new'] for event in _text_changes(messages)]
    assert ['unlocked' in text for text in texts] == [True, False]


def test_owning_document_lock_closes_callback_coroutine_closed_before_awaiting():
    from panel.io.document import _run_owning_document_lock

    class Session:
        document = Document()

    async def callback():
        pass

    coroutine = callback()
    awaiting = _run_owning_document_lock(Session(), lambda: coroutine)
    awaiting.close()
    del awaiting
    gc.collect()
    assert coroutine.cr_frame is None


def _run_on_loop_unlocked(asyncio_loop, func):
    # A fresh context, so the change does not inherit the lock holder's
    done = threading.Event()

    def run():
        try:
            func()
        finally:
            done.set()

    asyncio_loop.call_soon_threadsafe(run, context=contextvars.Context())
    assert done.wait(timeout=5)


@pytest.mark.xdist_group(name="server")
def test_unrelated_unlocked_change_is_written_while_locked_callback_runs(monkeypatch):
    """
    An unlocked change to a model the client has is written right away
    even while another callback holds the lock and has unwritten changes.
    """
    md = pn.pane.Markdown('a')
    col = pn.Column(md)
    doc, messages, _ = _serve_with_message_log(col, monkeypatch)
    session = doc.session_context.session
    asyncio_loop = doc.session_context.server_context.application_context.io_loop.asyncio_loop

    entered, release = threading.Event(), threading.Event()
    seen = []

    def change():
        with set_curdoc(doc):
            md.object = 'progress'

    def holder():
        with set_curdoc(doc):
            doc.roots[0].css_classes = ['pending']
            col.append(pn.pane.Markdown('new'))
        entered.set()
        release.wait(timeout=5)

    async def trigger():
        await session.with_document_locked(holder)

    future = asyncio.run_coroutine_threadsafe(trigger(), asyncio_loop)
    try:
        assert entered.wait(timeout=5)
        _run_on_loop_unlocked(asyncio_loop, change)
        wait_until(lambda: len(_text_changes(messages)) == 1)
        seen.append(session._lock.locked())
    finally:
        release.set()
    future.result(timeout=5)

    assert seen == [True]
    assert 'progress' in _text_changes(messages)[0]['new']


def _hold_lock(session, asyncio_loop):
    """
    Starts a locked callback that holds the document lock until the
    returned event is set.
    """
    entered, release = threading.Event(), threading.Event()

    def holder():
        entered.set()
        release.wait(timeout=5)

    async def trigger():
        await session.with_document_locked(holder)

    future = asyncio.run_coroutine_threadsafe(trigger(), asyncio_loop)
    assert entered.wait(timeout=5)
    return future, release


@pytest.mark.xdist_group(name="server")
def test_deferred_change_is_written_once_the_message_it_waits_for_is_written(monkeypatch):
    """
    A change held back until an unwritten message is written goes out as
    soon as that message is, rather than waiting for the document lock,
    which a busy lock holder may hardly ever release. Only the latest of
    several held back values of a property is written.
    """
    md = pn.pane.Markdown('a')
    doc, messages, _ = _serve_with_message_log(md, monkeypatch)
    session = doc.session_context.session
    asyncio_loop = doc.session_context.server_context.application_context.io_loop.asyncio_loop
    model = doc.roots[0]

    future, release = _hold_lock(session, asyncio_loop)
    try:
        record = []

        def defer():
            record.append(_track_unwritten(doc, [], []))
            _defer_until_unlocked(doc, [
                ModelChangedEvent(doc, model, 'text', text) for text in ('one', 'two')
            ])

        _run_on_loop_unlocked(asyncio_loop, defer)
        assert _text_changes(messages) == []
        _run_on_loop_unlocked(asyncio_loop, lambda: _untrack_unwritten(doc, record[0]))
        wait_until(lambda: len(_text_changes(messages)) == 1)
        assert session._lock.locked()
    finally:
        release.set()
    future.result(timeout=5)

    assert [event['new'] for event in _text_changes(messages)] == ['two']


@pytest.mark.xdist_group(name="server")
def test_unlocked_change_while_socket_is_written_does_not_wait_for_lock_holder(monkeypatch):
    """
    An unlocked change made while the socket is being written to is
    queued, rather than joining the writes of a callback holding the
    lock, which would also hold back all later changes to the property
    until that callback finished.
    """
    md = pn.pane.Markdown('a')
    doc, messages, _ = _serve_with_message_log(md, monkeypatch)
    session = doc.session_context.session
    asyncio_loop = doc.session_context.server_context.application_context.io_loop.asyncio_loop
    conn = next(iter(session._subscribed_connections))

    def change():
        with set_curdoc(doc):
            md.object = 'progress'

    future, release = _hold_lock(session, asyncio_loop)
    try:
        conn._socket.write_lock._block._value = 0
        _run_on_loop_unlocked(asyncio_loop, change)
        _run_on_loop_unlocked(asyncio_loop, conn._socket.write_lock.release)
        wait_until(lambda: len(_text_changes(messages)) == 1)
        assert session._lock.locked()
    finally:
        release.set()
    future.result(timeout=5)

    assert 'progress' in _text_changes(messages)[0]['new']


@pytest.mark.xdist_group(name="server")
def test_unlocked_change_to_property_the_lock_holder_changed_is_written_after(monkeypatch):
    """
    An unlocked change to a property the lock holder has changed but not
    written yet must follow the holder's change, otherwise the client
    ends up with the holder's older value.
    """
    md = pn.pane.Markdown('a')
    doc, messages, _ = _serve_with_message_log(md, monkeypatch)
    session = doc.session_context.session
    asyncio_loop = doc.session_context.server_context.application_context.io_loop.asyncio_loop

    entered, release = threading.Event(), threading.Event()

    def change():
        with set_curdoc(doc):
            md.object = 'unlocked'

    def holder():
        with set_curdoc(doc):
            doc.roots[0].css_classes = ['pending']
            md.object = 'holder'
        entered.set()
        release.wait(timeout=5)

    async def trigger():
        await session.with_document_locked(holder)

    future = asyncio.run_coroutine_threadsafe(trigger(), asyncio_loop)
    try:
        assert entered.wait(timeout=5)
        _run_on_loop_unlocked(asyncio_loop, change)
    finally:
        release.set()
    future.result(timeout=5)

    wait_until(lambda: len(_text_changes(messages)) == 2)
    texts = [event['new'] for event in _text_changes(messages)]
    assert ['unlocked' in text for text in texts] == [False, True]
    assert md.object == 'unlocked'


@pytest.mark.xdist_group(name="server")
def test_unlocked_change_referring_to_model_in_unwritten_message_is_written_after(monkeypatch):
    """
    An unlocked change whose new value refers to a model that only a
    serialized but unwritten message of the lock holder defines must not
    be written ahead of that message.
    """
    col = pn.Column(pn.pane.Markdown('a'))
    doc, messages, known = _serve_with_message_log(col, monkeypatch)
    session = doc.session_context.session
    asyncio_loop = doc.session_context.server_context.application_context.io_loop.asyncio_loop
    conn = next(iter(session._subscribed_connections))
    send_message = conn.send_message
    changed = []

    def change():
        with set_curdoc(doc), unlocked():
            doc.roots[0].children[0].tags = [doc.roots[0].children[-1]]

    async def send_after_changing(message):
        if not changed:
            changed.append(True)
            contextvars.Context().run(change)
        await send_message(message)

    conn.send_message = send_after_changing

    def holder():
        with set_curdoc(doc):
            doc.roots[0].css_classes = ['pending']
            col.append(pn.pane.Markdown('b'))

    async def trigger():
        await session.with_document_locked(holder)

    asyncio.run_coroutine_threadsafe(trigger(), asyncio_loop).result(timeout=5)

    wait_until(lambda: any(
        event.get('attr') == 'tags' for msg in messages for event in msg.content['events']
    ))
    assert _undefined_references(messages, known) == []


@pytest.mark.xdist_group(name="server")
def test_unlocked_message_to_model_attached_by_lock_holder_is_written_after(monkeypatch):
    """
    A message sent from an unlocked context to a model the lock holder
    has attached but not written yet must follow the holder's changes.
    """
    from panel.models.layout import ScrollToEvent

    col = pn.Column(pn.pane.Markdown('a'))
    doc, messages, known = _serve_with_message_log(col, monkeypatch)
    session = doc.session_context.session
    asyncio_loop = doc.session_context.server_context.application_context.io_loop.asyncio_loop
    new = pn.Column('b')
    paused, resume = threading.Event(), threading.Event()

    def pause():
        paused.set()
        resume.wait(timeout=5)

    def change():
        with set_curdoc(doc), unlocked():
            doc.callbacks.send_event(ScrollToEvent(model=doc.roots[0].children[-1], index=0))

    def holder():
        with set_curdoc(doc):
            # Block the event loop so the message is sent before the loop
            # writes the attached model.
            asyncio_loop.call_soon_threadsafe(pause)
            assert paused.wait(timeout=5)
            col.append(new)
            asyncio_loop.call_soon_threadsafe(change, context=contextvars.Context())
            resume.set()

    async def trigger():
        await session.with_document_locked(holder)

    try:
        asyncio.run_coroutine_threadsafe(trigger(), asyncio_loop).result(timeout=5)
    finally:
        resume.set()

    wait_until(lambda: any(
        event['kind'] == 'MessageSent' for msg in messages for event in msg.content['events']
    ))
    assert _undefined_references(messages, known) == []
