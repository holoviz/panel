import asyncio
import gc
import threading
import time
import weakref

from concurrent.futures import ThreadPoolExecutor
from functools import partial

import param
import pytest
import tornado.locks

from bokeh.core.serialization import DeserializationError, Deserializer
from bokeh.document import Document
from bokeh.document.events import MessageSentEvent, ModelChangedEvent
from bokeh.models import Column, Range1d
from bokeh.plotting import figure
from bokeh.protocol import Protocol

import panel as pn

from panel.io.browser import BrowserInfo
from panel.io.document import (
    _UNCONNECTED_EVENTS, _WRITE_BLOCK, MockSessionContext, _cleanup_doc,
    _client_has_document, _destroy_document, _drop_unsent_model_changes,
    _is_write_blocked, _keep_unsent_models_new, _socket_dispatcher,
    _suppress_property_callbacks, _write_tasks, dispatch_django,
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

    assert written == [True, False]
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


def _combined_patch_with_linked_range():
    holder = Column(children=[figure()])
    other = figure()
    doc = Document()
    doc.add_root(Column(children=[holder, other]))
    doc.models.flush_synced()
    client_models = list(doc.models)

    doc.hold('combine')
    shared = Range1d(0, 1)
    holder.children = [figure(x_range=shared)]
    shared.start = 5
    other.x_range = shared
    # Combined into the first children event, discarding its definition of the range
    holder.children = [figure()]
    return doc, list(doc.callbacks._held_events), client_models, holder, other


def _decode_patch(events, client_models):
    msg = Protocol().create('PATCH-DOC', events)
    Deserializer(references=client_models).decode(msg.content)


def test_combined_patch_references_unsent_model():
    _, events, client_models, _, _ = _combined_patch_with_linked_range()

    with pytest.raises(DeserializationError):
        _decode_patch(events, client_models)


def test_drop_unsent_model_changes_keeps_combined_patch_decodable():
    doc, events, client_models, holder, other = _combined_patch_with_linked_range()

    filtered = _drop_unsent_model_changes(doc, events)

    assert [(event.model, event.attr) for event in filtered] == [(holder, 'children'), (other, 'x_range')]
    _decode_patch(filtered, client_models)


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
        conn._socket.write_lock._block._value = 1
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

        conn._socket.write_lock._lock._locked = False
        await asyncio.sleep(0.05)

        assert len(conn.protocol.created) == 1
        assert written == conn.protocol.created
    finally:
        extra_socket_handlers.pop(_FakeASGISocket, None)
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
