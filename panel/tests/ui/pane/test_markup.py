import time

import pytest

try:
    from playwright.async_api import async_playwright
except Exception:
    pytest.mark.skip('playwright not available')

pytestmark = pytest.mark.ui

from panel.io.server import serve
from panel.pane import Markdown


@pytest.mark.asyncio
async def test_update_markdown_pane():
    md = Markdown('Initial')

    port = 7001
    serve(md, port=port, threaded=True, show=False)

    time.sleep(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"http://localhost:{port}")

        locator = page.locator(".bk.markdown")

        assert (await locator.all_text_contents()) == ['Initial']

        md.object = 'Updated'

        assert (await locator.all_text_contents()) == ['Updated']

        await browser.close()
