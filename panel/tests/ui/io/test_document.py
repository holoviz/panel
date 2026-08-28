import asyncio
import threading

import pytest

pytest.importorskip("playwright")

from contextlib import contextmanager

from playwright.sync_api import expect

from panel.io import document as pdoc
from panel.io.document import (
    _WRITE_BLOCK, _WRITE_EVENTS, hold, immediate_dispatch, unlocked,
)
from panel.io.state import state
from panel.layout import Column
from panel.pane import Markdown
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui


@contextmanager
def record_dispatch():
    """
    Records whether events were written straight to the sockets or
    queued to be written on a later iteration of the event loop.
    """
    calls: dict[str, list] = {'write': [], 'schedule': []}
    write, schedule = pdoc.write_events, pdoc.schedule_write_events

    def _write(doc, connections, events, run=True):
        calls['write'].append(list(events))
        return write(doc, connections, events, run=run)

    def _schedule(doc, connections, events):
        calls['schedule'].append(list(events))
        return schedule(doc, connections, events)

    pdoc.write_events, pdoc.schedule_write_events = _write, _schedule
    try:
        yield calls
    finally:
        pdoc.write_events, pdoc.schedule_write_events = write, schedule


def run_on_loop(callback):
    """
    Schedules a coroutine to be run once on the server event loop thread
    after the application has loaded.
    """
    def schedule():
        state.add_periodic_callback(callback, period=50, count=1)
    state.onload(schedule)


def test_unlocked_writes_events_immediately_on_loop_thread(page):
    """
    On the event loop thread with an idle socket the events must be
    written directly rather than queued for a later write.
    """
    md = Markdown('0')
    info = {}

    def app():
        doc = state.curdoc

        async def update():
            with record_dispatch() as calls:
                with unlocked():
                    md.object = '1'
            info['write'] = len(calls['write'])
            info['schedule'] = len(calls['schedule'])
            info['queued'] = doc in _WRITE_EVENTS or doc in _WRITE_BLOCK
            info['held'] = list(doc.callbacks._held_events)

        run_on_loop(update)
        return Column(md)

    serve_component(page, app)

    expect(page.locator('.markdown')).to_have_text('1')

    wait_until(lambda: 'write' in info, page)
    assert info['write'] == 1
    assert info['schedule'] == 0
    # Nothing was left queued behind a write block
    assert not info['queued']
    # All the events were dispatched, none handed back to Bokeh
    assert info['held'] == []


def test_immediate_dispatch_reaches_client_while_document_held(page):
    """
    ``immediate_dispatch`` must push its events to the client straight
    away even though the enclosing hold has not been released yet, and
    must leave the events that hold collected queued.
    """
    proceed = threading.Event()
    first, second = Markdown('A0'), Markdown('B0')
    info = {}

    def app():
        doc = state.curdoc

        async def update():
            with hold(doc):
                first.object = 'A1'
                info['held_before'] = len(doc.callbacks._held_events)
                with record_dispatch() as calls:
                    with immediate_dispatch(doc):
                        second.object = 'B1'
                info['write'] = len(calls['write'])
                info['schedule'] = len(calls['schedule'])
                info['queued'] = doc in _WRITE_EVENTS or doc in _WRITE_BLOCK
                info['held_after'] = len(doc.callbacks._held_events)
                # Hold the document open so the test can observe that the
                # immediately dispatched event arrived on its own.
                for _ in range(200):
                    if proceed.is_set():
                        break
                    await asyncio.sleep(0.05)

        run_on_loop(update)
        return Column(first, second)

    serve_component(page, app)

    try:
        # Dispatched immediately, i.e. before the hold was released
        expect(page.locator('.markdown').nth(1)).to_have_text('B1')
        # Collected by the hold, so not on the client yet
        expect(page.locator('.markdown').nth(0)).to_have_text('A0')
    finally:
        proceed.set()

    # Releasing the hold dispatches the events it collected
    expect(page.locator('.markdown').nth(0)).to_have_text('A1')

    assert info['held_before'] >= 1
    assert info['write'] == 1
    assert info['schedule'] == 0
    assert not info['queued']
    # The events the hold collected were restored, not dispatched
    assert info['held_after'] == info['held_before']
