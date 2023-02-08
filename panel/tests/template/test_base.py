import unittest

from panel.config import config
from panel.io.notifications import NotificationArea
from panel.io.state import set_curdoc, state
from panel.template import VanillaTemplate


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
