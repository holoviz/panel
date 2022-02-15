import time

from concurrent.futures import ThreadPoolExecutor

from panel.io.state import state


def test_as_cached_key_only():
    global i
    i = 0

    def test_fn():
        global i
        i += 1
        return i

    assert state.as_cached('test', test_fn) == 1
    assert state.as_cached('test', test_fn) == 1

def test_as_cached_key_and_kwarg():
    global i
    i = 0

    def test_fn(a):
        global i
        i += 1
        return i

    assert state.as_cached('test', test_fn, a=1) == 1
    assert state.as_cached('test', test_fn, a=1) == 1
    assert state.as_cached('test', test_fn, a=2) == 2
    assert state.as_cached('test', test_fn, a=1) == 1
    assert state.as_cached('test', test_fn, a=2) == 2

def test_as_cached_thread_locks():
    global j
    j = 0

    def test_fn():
        global j
        j += 1
        time.sleep(0.1)
        return j

    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        for i in range(4):
            future = executor.submit(state.as_cached, 'test', test_fn)
            results.append(future)
    assert [r.result() for r in results] == [1, 1, 1, 1]
    assert len(state._cache_locks) == 1

def test_as_cached_ttl():
    global i
    i = 0

    def test_fn():
        global i
        i += 1
        return i

    assert state.as_cached('test', test_fn, ttl=0.1) == 1
    time.sleep(0.1)
    assert state.as_cached('test', test_fn, ttl=0.1) == 2
