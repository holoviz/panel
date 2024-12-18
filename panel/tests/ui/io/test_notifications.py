import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.config import config
from panel.io.state import state
from panel.pane import Markdown
from panel.template import BootstrapTemplate
from panel.tests.util import serve_component
from panel.widgets import Button

pytestmark = pytest.mark.ui

def test_notifications_no_template(page):
    def callback(event):
        state.notifications.error('MyError')

    def app():
        config.notifications = True
        button = Button(name='Display error')
        button.on_click(callback)
        return button

    serve_component(page, app)

    page.click('.bk-btn')

    expect(page.locator('.notyf__message')).to_have_text('MyError')


def test_notifications_with_template(page):
    def callback(event):
        state.notifications.error('MyError')

    with config.set(notifications=True):
        button = Button(name='Display error')
        button.on_click(callback)
        tmpl = BootstrapTemplate()
        tmpl.main.append(button)

    serve_component(page, tmpl)

    page.click('.bk-btn')

    expect(page.locator('.notyf__message')).to_have_text('MyError')


def test_ready_notification(page):
    def app():
        config.ready_notification = 'Ready!'
        return Markdown('Ready app')

    serve_component(page, app)

    expect(page.locator('.notyf__message')).to_have_text('Ready!')


def test_disconnect_notification(page):
    def app():
        config.disconnect_notification = 'Disconnected!'
        button = Button(name='Stop server')
        button.js_on_click(code="""
        Bokeh.documents[0].event_manager.send_event({'event_name': 'connection_lost', 'publish': false})
        """)
        return button

    serve_component(page, app)

    page.click('.bk-btn')


def test_onload_notification(page):
    def onload_callback():
        state.notifications.warning("Warning", duration=0)
        state.notifications.info("Info", duration=0)

    def app():
        config.notifications = True
        state.onload(onload_callback)
        return Markdown("# Hello world")

    serve_component(page, app)

    expect(page.locator('.notyf__message')).to_have_count(2)
    expect(page.locator('.notyf__message').nth(0)).to_have_text("Warning")
    expect(page.locator('.notyf__message').nth(1)).to_have_text("Info")
