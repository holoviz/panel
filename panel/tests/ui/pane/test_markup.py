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

    assert page.locator(".markdown").locator("div").text_content() == 'Initial\n'
    md.object = 'Updated'
    time.sleep(0.1)
    assert page.locator(".markdown").locator("div").text_content() == 'Updated\n'


def test_update_markdown_pane_resizes(page, port):
    md = Markdown('Initial')

    serve(md, port=port, threaded=True, show=False)

    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    height = page.locator(".markdown").bounding_box()['height']
    assert int(height) == 18
    md.object = """
    - Bullet
    - Points
    """
    time.sleep(0.1)
    height = page.locator(".markdown").bounding_box()['height']
    assert int(height) == 37


def test_markdown_pane_visible_toggle(page, port):
    md = Markdown('Initial', visible=False)

    serve(md, port=port, threaded=True, show=False)

    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    assert page.locator(".markdown").locator("div").text_content() == 'Initial\n'
    assert not page.locator(".markdown").locator("div").is_visible()

    md.visible = True

    time.sleep(0.2)

    assert page.locator(".markdown").locator("div").is_visible()
