import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.config import config
from panel.pane import Markdown
from panel.tests.util import serve_component

pytestmark = pytest.mark.ui


def test_global_loading_indicator(page):
    def app():
        config.global_loading_spinner = True
        return Markdown('Blah')

    serve_component(page, app)

    expect(page.locator("body")).not_to_have_class('pn-loading')


def test_base_template_loader_hides_once_idle(page):
    serve_component(page, Markdown('Blah'))

    expect(page.locator('#loader')).to_be_hidden()
    expect(page.locator('#loader-error')).to_be_hidden()
    expect(page.locator('.markdown')).to_have_text('Blah')


def test_base_template_loader_reports_failed_connection(page):
    # Redirecting the websocket to a closed port leaves Bokeh loaded but the
    # session unconnected.
    page.add_init_script("""
      const NativeWebSocket = window.WebSocket;
      window.WebSocket = function(url, protocols) {
        return new NativeWebSocket('ws://127.0.0.1:9/ws', protocols);
      };
      window.WebSocket.prototype = NativeWebSocket.prototype;
    """)
    serve_component(page, Markdown('Blah'), wait=False)

    expect(page.locator('#loader-error')).to_have_text(
        'Connection with the server could not be established.'
    )
