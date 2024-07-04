"""
Tests pn.config variables
"""
import pytest

from panel import config, state
from panel.pane import HTML, panel
from panel.param import ParamFunction
from panel.tests.conftest import set_env_var


def test_env_var_console_output():
    with set_env_var('PANEL_CONSOLE_OUTPUT', 'disable'):
        assert config.console_output == 'disable'
    with set_env_var('PANEL_CONSOLE_OUTPUT', 'replace'):
        assert config.console_output == 'replace'
    with config.set(console_output='disable'):
        with set_env_var('PANEL_DOC_BUILD', 'accumulate'):
            assert config.console_output == 'disable'


def test_config_set_console_output():
    with config.set(console_output=False):
        assert config.console_output == 'disable'
    with config.set(console_output='disable'):
        assert config.console_output == 'disable'
    with config.set(console_output='replace'):
        assert config.console_output == 'replace'
    with config.set(console_output='disable'):
        with config.set(console_output='accumulate'):
            assert config.console_output == 'accumulate'


@pytest.mark.usefixtures("with_curdoc")
def test_session_override():
    config.sizing_mode = 'stretch_width'
    assert config.sizing_mode == 'stretch_width'
    assert state.curdoc in config._session_config
    assert config._session_config[state.curdoc] == {'sizing_mode': 'stretch_width'}
    state.curdoc = None
    assert config.sizing_mode is None

@pytest.mark.usefixtures("with_curdoc")
def test_defer_load():
    try:
        defer_load_old = config.defer_load
        config.defer_load = True

        def test():
            return 1

        assert ParamFunction.applies(test)
        assert isinstance(panel(test), ParamFunction)
    finally:
        config.defer_load = defer_load_old

def test_console_output_replace_stdout(document, comm, get_display_handle):
    pane = HTML()
    with set_env_var('PANEL_CONSOLE_OUTPUT', 'replace'):
        model = pane.get_root(document, comm)
        handle = get_display_handle(model)

        pane._on_stdout(model.ref['id'], ['print output'])
        assert handle == {'text/html': 'print output</br>', 'raw': True}

        pane._on_stdout(model.ref['id'], ['new output'])
        assert handle == {'text/html': 'new output</br>', 'raw': True}

        pane._cleanup(model)
        assert model.ref['id'] not in state._handles


def test_console_output_accumulate_stdout(document, comm, get_display_handle):
    pane = HTML()
    model = pane.get_root(document, comm)
    handle = get_display_handle(model)

    pane._on_stdout(model.ref['id'], ['print output'])
    assert handle == {'text/html': 'print output</br>', 'raw': True}

    pane._on_stdout(model.ref['id'], ['new output'])
    assert handle == {'text/html': 'print output</br>\nnew output</br>', 'raw': True}

    pane._cleanup(model)
    assert model.ref['id'] not in state._handles


def test_console_output_disable_stdout(document, comm, get_display_handle):
    pane = HTML()
    with set_env_var('PANEL_CONSOLE_OUTPUT', 'disable'):
        model = pane.get_root(document, comm)
        handle = get_display_handle(model)

        pane._on_stdout(model.ref['id'], ['print output'])
        assert handle == {}

        pane._cleanup(model)
        assert model.ref['id'] not in state._handles


def test_console_output_replace_error(document, comm, get_display_handle):
    pane = HTML()
    with set_env_var('PANEL_CONSOLE_OUTPUT', 'replace'):
        model = pane.get_root(document, comm)
        handle = get_display_handle(model)

        try:
            1/0  # noqa: B018
        except Exception as e:
            pane._on_error(model.ref['id'], e)
        assert 'text/html' in handle
        assert 'ZeroDivisionError' in handle['text/html']

        try:
            1 + '2'  # noqa: B018
        except Exception as e:
            pane._on_error(model.ref['id'], e)
        assert 'text/html' in handle
        assert 'ZeroDivisionError' not in handle['text/html']
        assert 'TypeError' in handle['text/html']

        pane._cleanup(model)
        assert model.ref['id'] not in state._handles


def test_console_output_accumulate_error(document, comm, get_display_handle):
    pane = HTML()
    model = pane.get_root(document, comm)
    handle = get_display_handle(model)

    try:
        1/0  # noqa: B018
    except Exception as e:
        pane._on_error(model.ref['id'], e)
    assert 'text/html' in handle
    assert 'ZeroDivisionError' in handle['text/html']

    try:
        1 + '2' # noqa: B018
    except Exception as e:
        pane._on_error(model.ref['id'], e)
    assert 'text/html' in handle
    assert 'ZeroDivisionError' in handle['text/html']
    assert 'TypeError' in handle['text/html']

    pane._cleanup(model)
    assert model.ref['id'] not in state._handles


def test_console_output_disable_error(document, comm, get_display_handle):
    pane = HTML()
    with set_env_var('PANEL_CONSOLE_OUTPUT', 'disable'):
        model = pane.get_root(document, comm)
        handle = get_display_handle(model)

        try:
            1/0  # noqa: B018
        except Exception as e:
            pane._on_error(model.ref['id'], e)
        assert handle == {}

        pane._cleanup(model)
        assert model.ref['id'] not in state._handles
