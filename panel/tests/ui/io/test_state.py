import time

import pytest

pytestmark = pytest.mark.ui

try:
    from playwright.sync_api import expect
    pytestmark = pytest.mark.ui
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

from panel.io.server import serve
from panel.io.state import state
from panel.pane import Markdown


def test_on_load(page, port):
    def app():
        md = Markdown('Initial')

        def cb():
            md.object = 'Loaded'

        state.onload(cb)
        return md

    serve(app, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expect(page.locator('.markdown').locator("div")).to_have_text('Loaded\n')
