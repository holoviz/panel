import sys
import time
import uuid

from concurrent.futures import ThreadPoolExecutor

import param
import pytest

from panel.io.callbacks import PeriodicCallback
from panel.io.state import _state, set_curdoc, state
from panel.widgets import TextInput


def test_as_cached_key_only():
    def test_fn(i=[0]):
        i[0] += 1
        return i[0]

    assert state.as_cached('test', test_fn) == 1
    assert state.as_cached('test', test_fn) == 1

def test_as_cached_key_and_kwarg():
    def test_fn(a, i=[0]):
        i[0] += 1
        return i[0]

    assert state.as_cached('test', test_fn, a=1) == 1
    assert state.as_cached('test', test_fn, a=1) == 1
    assert state.as_cached('test', test_fn, a=2) == 2
    assert state.as_cached('test', test_fn, a=1) == 1
    assert state.as_cached('test', test_fn, a=2) == 2

def test_as_cached_thread_locks():
    def test_fn(i=[0]):
        i[0] += 1
        time.sleep(0.1)
        return i[0]

    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        for _ in range(4):
            future = executor.submit(state.as_cached, 'test', test_fn)
            results.append(future)
    assert [r.result() for r in results] == [1, 1, 1, 1]
    assert len(state._cache_locks) == 1

def test_as_cached_ttl():
    def test_fn(i=[0]):
        i[0] += 1
        return i[0]

    assert state.as_cached('test', test_fn, ttl=0.1) == 1
    time.sleep(0.11)
    assert state.as_cached('test', test_fn, ttl=0.1) == 2

def test_busy_events_from_concurrent_threads_are_not_lost():
    """
    Adding and removing busy events is a read-modify-write of the counter,
    so concurrent threads could resurrect a removed event, leaving
    state.busy stuck until the event expires, or race on edit_readonly.
    """
    switch_interval = sys.getswitchinterval()
    # Forces frequent thread switches inside the read-modify-write window
    sys.setswitchinterval(1e-6)

    def toggle(n):
        for _ in range(n):
            event_id = uuid.uuid4().hex
            state._add_busy_event(event_id)
            state._remove_busy_event(event_id)

    try:
        with ThreadPoolExecutor(max_workers=8) as executor:
            for future in [executor.submit(toggle, 200) for _ in range(8)]:
                future.result()
    finally:
        sys.setswitchinterval(switch_interval)

    assert state._busy_counter == []
    assert state.busy is False


def test_busy_cleanup_not_scheduled_without_running_loop():
    state._add_busy_event('no-loop')
    state._remove_busy_event('no-loop')

    assert _state._busy_cleanup_scheduled is None


async def test_busy_cleanup_scheduled_with_running_loop():
    state._add_busy_event('loop')
    state._remove_busy_event('loop')

    cleanup = _state._busy_cleanup_scheduled
    assert cleanup is not None
    assert cleanup._cb is not None


async def test_reset_stops_busy_cleanup_and_allows_rescheduling():
    state._add_busy_event('before-reset')
    cleanup = _state._busy_cleanup_scheduled

    state.reset()

    assert not cleanup.running
    assert cleanup._cb is None
    assert _state._busy_cleanup_scheduled is None

    state._add_busy_event('after-reset')
    state._remove_busy_event('after-reset')

    assert _state._busy_cleanup_scheduled not in (None, cleanup)


def test_reset_clears_session_info():
    state.session_info['total'] = 3
    state.session_info['live'] = 1
    state.session_info['sessions']['abc'] = {}

    state.reset()

    assert state.session_info == {'total': 0, 'live': 0, 'sessions': {}}


def test_session_info_watchers_see_old_and_new(document):
    class SessionContext:
        id = 'abc'
        _document = document

    document._session_context = lambda: SessionContext()
    state.session_info['sessions']['abc'] = {
        'launched': 0.0, 'started': None, 'rendered': None, 'ended': None,
        'user_agent': None,
    }
    events = []
    watcher = state.param.watch(events.append, 'session_info')
    try:
        with set_curdoc(document):
            state._init_session(None)
        state._destroy_session(SessionContext())
    finally:
        state.param.unwatch(watcher)

    rendered, ended = events
    assert rendered.old is not rendered.new
    assert rendered.old['live'] == 0
    assert rendered.new['live'] == 1
    assert rendered.old['sessions']['abc']['rendered'] is None
    assert rendered.new['sessions']['abc']['rendered'] is not None
    assert ended.old['live'] == 1
    assert ended.new['live'] == 0
    assert ended.old['sessions']['abc']['ended'] is None
    assert ended.new['sessions']['abc']['ended'] is not None


async def test_periodic_callback_failed_thread_submit_does_not_leak_busy_event():
    class _ShutdownPool:
        def submit(self, *args, **kwargs):
            raise RuntimeError('cannot schedule new futures after shutdown')

    cb = PeriodicCallback(callback=lambda: None, period=1000)
    thread_pool = state._thread_pool
    state._thread_pool = _ShutdownPool()
    try:
        with pytest.raises(RuntimeError):
            await cb._periodic_callback()
    finally:
        state._thread_pool = thread_pool

    assert state._busy_counter == []
    assert state.busy is False


def test_destroy_session_cleans_up_stylesheets(document, comm):
    TextInput().get_root(document, comm)

    assert document in state._stylesheets

    session_context = param.Parameterized()
    session_context.id = 'test'
    session_context._document = document
    state._destroy_session(session_context)

    assert document not in state._stylesheets


@pytest.mark.parametrize('period', ['90', '1h30', 'abc', '0s'])
def test_schedule_task_rejects_invalid_period(period):
    with pytest.raises(ValueError):
        state.schedule_task('invalid_period', lambda: None, period=period)
    assert not any(key.endswith('_invalid_period') for key in state._scheduled)


def test_served_in_converted_pyodide_app(document, monkeypatch):
    from panel.io.document import MockSessionContext

    assert not state.served
    monkeypatch.setitem(sys.modules, '_pyodide', object())
    assert not state.served
    document._session_context = lambda: MockSessionContext(document=document)
    with set_curdoc(document):
        assert state.served
