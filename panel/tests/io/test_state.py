from panel.io.state import state
import panel as pn


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

def test_config_template_kwargs_are_applied():
    template_kwargs=dict(header_background="blue")
    pn.config.template="fast"
    pn.config.template_kwargs=template_kwargs
    assert pn.state.template.header_background=="blue"

def test_extension_template_kwargs_are_applied():
    template_kwargs=dict(header_background="blue")
    pn.extension(template="fast", template_kwargs=template_kwargs)
    assert pn.config.template_kwargs==template_kwargs
    assert pn.state.template.header_background=="blue"
