import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.pane import Markdown
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui


def test_update_markdown_pane(page):
    md = Markdown('Initial')

    serve_component(page, md)

    expect(page.locator(".markdown").locator("div")).to_have_text('Initial\n')

    md.object = 'Updated'

    expect(page.locator(".markdown").locator("div")).to_have_text('Updated\n')


def test_update_markdown_pane_resizes(page):
    md = Markdown('Initial')

    serve_component(page, md)

    height = page.locator(".markdown").bounding_box()['height']

    assert int(height) == 18

    md.object = """
    - Bullet
    - Points
    """
    wait_until(lambda: int(page.locator(".markdown").bounding_box()['height']) == 37, page)


def test_markdown_pane_visible_toggle(page):
    md = Markdown('Initial', visible=False)

    serve_component(page, md)

    assert page.locator(".markdown").locator("div").text_content() == 'Initial\n'
    assert not page.locator(".markdown").locator("div").is_visible()

    md.visible = True

    wait_until(lambda: page.locator(".markdown").locator("div").is_visible(), page)
