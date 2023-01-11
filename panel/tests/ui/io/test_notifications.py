import time

import pytest

pytestmark = pytest.mark.ui

from panel.config import config
from panel.io.server import serve
from panel.io.state import state
from panel.template import BootstrapTemplate
from panel.widgets import Button


def test_notifications_no_template(page, port):
    def callback(event):
        state.notifications.error('MyError')

    def app():
        config.notifications = True
        button = Button(name='Display error')
        button.on_click(callback)
        return button

    serve(app, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    page.click('.bk.bk-btn')

    time.sleep(0.1)

    assert page.text_content('.notyf__message') == 'MyError'


def test_notifications_with_template(page, port):
    def callback(event):
        state.notifications.error('MyError')

    with config.set(notifications=True):
        button = Button(name='Display error')
        button.on_click(callback)
        tmpl = BootstrapTemplate()
        tmpl.main.append(button)
        serve(tmpl, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    page.click('.bk.bk-btn')

    time.sleep(0.1)

    assert page.text_content('.notyf__message') == 'MyError'
