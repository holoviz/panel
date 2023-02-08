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

    assert page.locator(".markdown").locator(".bk-clearfix").text_content() == 'Initial'
    md.object = 'Updated'
    time.sleep(0.1)
    assert page.locator(".markdown").locator(".bk-clearfix").text_content() == 'Updated'


def test_update_markdown_pane_resizes(page, port):
    md = Markdown('Initial')

    serve(md, port=port, threaded=True, show=False)

    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    assert page.locator(".markdown").bounding_box()['height'] == 18.5625
    md.object = """
    - Bullet
    - Points
    """
    time.sleep(0.1)
    assert page.locator(".markdown").bounding_box()['height'] == 63.125
