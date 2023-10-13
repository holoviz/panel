import unittest

from panel.config import config
from panel.io.notifications import NotificationArea
from panel.io.state import set_curdoc, state
from panel.template import VanillaTemplate
from panel.widgets import Button


def test_notification_instantiate_on_config(document):
    with config.set(notifications=True):
        tmpl = VanillaTemplate()

    assert isinstance(tmpl.notifications, NotificationArea)

    tmpl.server_doc(document)
    session_context = unittest.mock.Mock()
    document._session_context = lambda: session_context

    with set_curdoc(document):
        assert state.notifications is tmpl.notifications


def test_notification_explicit(document):
    tmpl = VanillaTemplate(notifications=NotificationArea())

    assert isinstance(tmpl.notifications, NotificationArea)

    tmpl.server_doc(document)
    session_context = unittest.mock.Mock()
    document._session_context = lambda: session_context

    with set_curdoc(document):
        assert state.notifications is tmpl.notifications


def test_template_pass_config_params_constructor(document):
    custom_config = {
        'raw_css': ['html { background-color: purple; }'],
        'css_files': ['stylesheet.css'],
        'js_files': {'foo': 'foo.js'},
        'js_modules': {'bar': 'bar.js'},
    }
    tmpl = VanillaTemplate(**custom_config)
    config = tmpl.config.param.values()
    del config['name']
    assert config == custom_config


def test_template_multi_refs():
    tmpl = VanillaTemplate()
    button = Button(name="Click me", button_type="primary")
    tmpl.sidebar.append(button)
    tmpl.main.append(button)

    assert len(tmpl._render_items) == 6
    assert f'nav-{id(button)}' in tmpl._render_items
    assert f'main-{id(button)}' in tmpl._render_items
