import time

import pytest

pytestmark = pytest.mark.ui

from panel.io.server import serve
from panel.pane import Markdown


def test_update_markdown_pane(page):
    md = Markdown('Initial')

    port = 7001
    serve(md, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    locator = page.locator(".bk.markdown")

    locator.all_text_contents() == ['Initial']

    md.object = 'Updated'

    time.sleep(0.2)

    assert locator.all_text_contents() == ['Updated']
