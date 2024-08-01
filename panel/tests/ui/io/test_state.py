import asyncio

import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.io.state import state
from panel.pane import Markdown
from panel.tests.util import serve_component, wait_until
from panel.widgets import Button

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


def test_server_async_local_state_button_click(page, bokeh_curdoc):
    docs = {}
    buttons = {}

    async def task(event):
        assert buttons[event.obj] is state.curdoc
        await asyncio.sleep(0.5)
        docs[state.curdoc] = []
        for _ in range(10):
            await asyncio.sleep(0.1)
            docs[state.curdoc].append(state.curdoc)

    def app():
        button = Button(on_click=task)
        buttons[button] = state.curdoc
        return button

    _, port = serve_component(page, app)

    page.click('.bk-btn')

    page.goto(f"http://localhost:{port}")

    page.click('.bk-btn')

    page.goto(f"http://localhost:{port}")

    page.click('.bk-btn')

    # Ensure state.curdoc was consistent despite asyncio context switching
    wait_until(lambda: len(docs) == 3)
    wait_until(lambda: all([len(set(docs)) == 1 and docs[0] is doc for doc, docs in docs.items()]))
