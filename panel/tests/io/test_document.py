import asyncio
import gc
import threading
import weakref

from concurrent.futures import ThreadPoolExecutor
from functools import partial

import pytest

from bokeh.document import Document
from bokeh.document.events import MessageSentEvent

import panel as pn

from panel.io.document import (
    _UNCONNECTED_EVENTS, _WRITE_BLOCK, _WRITE_EVENTS, _cleanup_doc,
    _destroy_document, _write_tasks, hold, schedule_write_events, unlocked,
    write_events,
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


class _FakeMessage:

    def __init__(self):
        self.prepared = False

    def prepare(self):
        self.prepared = True


class _FakeConn:

    def __init__(self, block: bool = False):
        self.messages = []
        self._block = block
        self.release = asyncio.Event()

    async def send_message(self, msg):
        self.messages.append(msg)
        if self._block:
            await self.release.wait()


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


@pytest.mark.asyncio
async def test_write_events_shares_one_message_across_connections(monkeypatch):
    """
    Serializing a patch marks the models it defines as synced on the
    Document, so a message must be created once and shared, otherwise
    every connection but the first receives references to models it was
    never sent.
    """
    messages = []

    def patch_doc(events):
        message = _FakeMessage()
        messages.append(message)
        return message

    monkeypatch.setattr("panel.io.document.patch_doc", patch_doc)
    doc = Document()
    conns = [_FakeConn() for _ in range(3)]

    futures = write_events(doc, conns, [object()], run=False)
    await asyncio.gather(*futures)

    assert len(messages) == 1
    assert messages[0].prepared
    assert [conn.messages for conn in conns] == [[messages[0]]] * 3


def test_write_events_with_nothing_to_write(monkeypatch):
    messages = []
    monkeypatch.setattr("panel.io.document.patch_doc", lambda events: messages.append(_FakeMessage()))
    doc = Document()
    conn = _FakeConn()

    assert write_events(doc, [conn], []) == []
    assert write_events(doc, [], [object()]) == []
    assert not messages
    assert not conn.messages


@pytest.mark.asyncio
async def test_schedule_write_events_defers_and_orders_serialization(monkeypatch):
    """
    Queued events must be serialized when they are written, not when they
    are queued, otherwise a message serialized later can be written first
    and reference models the client has not been sent yet.
    """
    serialized = []

    def patch_doc(events):
        message = _FakeMessage()
        serialized.append((events, message))
        return message

    monkeypatch.setattr("panel.io.document.patch_doc", patch_doc)
    doc = Document()
    conn = _FakeConn(block=True)
    first, second = object(), object()

    schedule_write_events(doc, [conn], [first])
    assert serialized == []
    for _ in range(10):
        await asyncio.sleep(0.01)
        if conn.messages:
            break

    assert [events for events, _ in serialized] == [[first]]
    assert conn.messages == [serialized[0][1]]

    # This batch arrives while the first message is still being sent. It
    # must be drained by the active dispatcher rather than left stranded.
    schedule_write_events(doc, [conn], [second])
    assert [events for events, _ in serialized] == [[first]]

    conn.release.set()
    for _ in range(10):
        await asyncio.sleep(0.01)
        if doc not in _WRITE_BLOCK:
            break

    assert [events for events, _ in serialized] == [[first], [second]]
    assert conn.messages == [message for _, message in serialized]
    assert all(message.prepared for _, message in serialized)
    assert doc not in _WRITE_EVENTS
    assert doc not in _WRITE_BLOCK


@pytest.mark.asyncio
async def test_dispatch_msgs_terminates_on_document_destroy(monkeypatch):
    """Pending _dispatch_msgs loop must stop after document is destroyed."""
    monkeypatch.setattr("panel.io.document.patch_doc", lambda events: _FakeMessage())
    doc = Document()
    conn = _FakeConn(block=True)
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
