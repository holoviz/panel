import pytest

pytestmark = pytest.mark.ui

from panel.pane import Markdown
from panel.tests.util import serve_component, wait_until


def test_update_markdown_pane(page, port):
    md = Markdown('Initial')

    serve_component(page, port, md)

    assert page.locator(".markdown").locator("div").text_content() == 'Initial\n'
    md.object = 'Updated'
    assert page.locator(".markdown").locator("div").text_content() == 'Updated\n'


def test_update_markdown_pane_resizes(page, port):
    md = Markdown('Initial')

    serve_component(page, port, md)

    height = page.locator(".markdown").bounding_box()['height']

    assert int(height) == 18

    md.object = """
    - Bullet
    - Points
    """
    wait_until(lambda: int(page.locator(".markdown").bounding_box()['height']) == 37, page)
