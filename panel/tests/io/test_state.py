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
    state.cache.clear()



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
    state.cache.clear()
