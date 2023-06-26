import time

import pytest

try:
    from playwright.sync_api import expect
    pytestmark = pytest.mark.ui
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

from panel.config import config
from panel.io.server import serve
from panel.pane import Markdown


def test_global_loading_indicator(page, port):
    def app():
        config.global_loading_spinner = True
        return Markdown('Blah')

    serve(app, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    expect(page.locator("body")).not_to_have_class('pn-loading')
