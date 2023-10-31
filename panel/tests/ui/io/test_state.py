import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.io.state import state
from panel.pane import Markdown
from panel.tests.util import serve_component

pytestmark = pytest.mark.ui

def test_on_load(page):
    def app():
        md = Markdown('Initial')

        def cb():
            md.object = 'Loaded'

        state.onload(cb)
        return md

    serve_component(page, app)

    expect(page.locator('.markdown').locator("div")).to_have_text('Loaded\n')
