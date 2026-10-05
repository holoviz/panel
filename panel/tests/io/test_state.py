import sys
import time
import uuid

from concurrent.futures import ThreadPoolExecutor

import param
import pytest

from panel.io.state import state
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
