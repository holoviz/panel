import asyncio
import gc
import threading
import weakref

from concurrent.futures import ThreadPoolExecutor
from functools import partial

import pytest
import tornado.locks

from bokeh.document import Document
from bokeh.document.events import MessageSentEvent

import panel as pn

from panel.io.document import (
    _UNCONNECTED_EVENTS, _WRITE_BLOCK, _cleanup_doc, _destroy_document,
    _write_tasks, extra_socket_handlers, hold, schedule_write_events, unlocked,
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
    def create(self, msgtype, events):
        return object()


class _FakeSocket:
    def __init__(self, lock_held):
        self.write_lock = tornado.locks.Lock()
        if lock_held:
            self.write_lock._block._value = 0
        self.ws_connection = type("W", (), {"is_closing": lambda s: True})()


class _FakeConn:
    def __init__(self, lock_held):
        self._socket = _FakeSocket(lock_held)
        self.protocol = _FakeProtocol()


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
