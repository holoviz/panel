"""
Tests pn.config variables
"""
from __future__ import absolute_import, division, unicode_literals

from panel import config, state
from panel.pane import HTML

from panel.tests.conftest import set_env_var


def test_env_var_debug():
    with set_env_var('PANEL_DEBUG', 'disable'):
        assert config.debug == 'disable'
    with set_env_var('PANEL_DEBUG', 'replace'):
        assert config.debug == 'replace'
    with set_env_var('PANEL_DOC_BUILD', 'true'):
        assert config.debug == 'disable'


def test_debug_replace_stdout(document, comm, get_display_handle):
    pane = HTML()
    with set_env_var('PANEL_DEBUG', 'replace'):
        model = pane.get_root(document, comm)
        handle = get_display_handle(model)

        pane._on_stdout(model.ref['id'], ['print output'])
        assert handle == {'text/html': 'print output</br>', 'raw': True}

        pane._on_stdout(model.ref['id'], ['new output'])
        assert handle == {'text/html': 'new output</br>', 'raw': True}

        pane._cleanup(model)
        assert model.ref['id'] not in state._handles


def test_debug_accumulate_stdout(document, comm, get_display_handle):
    pane = HTML()
    model = pane.get_root(document, comm)
    handle = get_display_handle(model)

    pane._on_stdout(model.ref['id'], ['print output'])
    assert handle == {'text/html': 'print output</br>', 'raw': True}

    pane._on_stdout(model.ref['id'], ['new output'])
    assert handle == {'text/html': 'print output</br>\nnew output</br>', 'raw': True}

    pane._cleanup(model)
    assert model.ref['id'] not in state._handles


def test_debug_disable_stdout(document, comm, get_display_handle):
    pane = HTML()
    with set_env_var('PANEL_DEBUG', 'disable'):
        model = pane.get_root(document, comm)
        handle = get_display_handle(model)

        pane._on_stdout(model.ref['id'], ['print output'])
        assert handle == {}

        pane._cleanup(model)
        assert model.ref['id'] not in state._handles


def test_debug_replace_error(document, comm, get_display_handle):
    pane = HTML()
    with set_env_var('PANEL_DEBUG', 'replace'):
        model = pane.get_root(document, comm)
        handle = get_display_handle(model)

        try:
            1/0
        except Exception as e:
            pane._on_error(model.ref['id'], e)
        assert 'text/html' in handle
        assert 'ZeroDivisionError' in handle['text/html']

        try:
            1 + '2'
        except Exception as e:
            pane._on_error(model.ref['id'], e)
        assert 'text/html' in handle
        assert 'ZeroDivisionError' not in handle['text/html']
        assert 'TypeError' in handle['text/html']

        pane._cleanup(model)
        assert model.ref['id'] not in state._handles


def test_debug_accumulate_error(document, comm, get_display_handle):
    pane = HTML()
    model = pane.get_root(document, comm)
    handle = get_display_handle(model)

    try:
        1/0
    except Exception as e:
        pane._on_error(model.ref['id'], e)
    assert 'text/html' in handle
    assert 'ZeroDivisionError' in handle['text/html']

    try:
        1 + '2'
    except Exception as e:
        pane._on_error(model.ref['id'], e)
    assert 'text/html' in handle
    assert 'ZeroDivisionError' in handle['text/html']
    assert 'TypeError' in handle['text/html']

    pane._cleanup(model)
    assert model.ref['id'] not in state._handles


def test_debug_disable_error(document, comm, get_display_handle):
    pane = HTML()
    with set_env_var('PANEL_DEBUG', 'disable'):
        model = pane.get_root(document, comm)
        handle = get_display_handle(model)

        try:
            1/0
        except Exception as e:
            pane._on_error(model.ref['id'], e)
        assert handle == {}

        pane._cleanup(model)
        assert model.ref['id'] not in state._handles
