import unittest

from bokeh.document import Document

from panel.config import config
from panel.io.notifications import NotificationArea
from panel.io.state import set_curdoc, state
from panel.template import VanillaTemplate


def test_notification_instantiate_on_config():
    with config.set(notifications=True):
        tmpl = VanillaTemplate()

    assert isinstance(tmpl.notifications, NotificationArea)

    doc = Document()
    tmpl.server_doc(doc)
    session_context = unittest.mock.Mock()
    doc._session_context = lambda: session_context

    with set_curdoc(doc):
        assert state.notifications is tmpl.notifications


def test_notification_explicit():
    tmpl = VanillaTemplate(notifications=NotificationArea())

    assert isinstance(tmpl.notifications, NotificationArea)

    doc = Document()
    tmpl.server_doc(doc)
    session_context = unittest.mock.Mock()
    doc._session_context = lambda: session_context

    with set_curdoc(doc):
        assert state.notifications is tmpl.notifications
