import time

import pytest

pytestmark = pytest.mark.ui

from panel.io.server import serve
from panel.pane import Markdown


def test_update_markdown_pane(page, port):
    md = Markdown('Initial')

    serve(md, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    assert page.text_content(".bk.markdown") == 'Initial'

    md.object = 'Updated'

    time.sleep(0.1)

    assert page.text_content(".bk.markdown") == 'Updated'
