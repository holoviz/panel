import pytest

try:
    from playwright.sync_api import expect
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

pytestmark = pytest.mark.ui

from panel.pane import Markdown
from panel.tests.util import serve_component, wait_until


def test_update_markdown_pane(page, port):
    md = Markdown('Initial')

    serve_component(page, port, md)

    expect(page.locator(".markdown").locator("div")).to_have_text('Initial\n')

    md.object = 'Updated'

    expect(page.locator(".markdown").locator("div")).to_have_text('Updated\n')


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
