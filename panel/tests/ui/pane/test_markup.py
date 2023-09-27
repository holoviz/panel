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


def test_markdown_pane_visible_toggle(page, port):
    md = Markdown('Initial', visible=False)

    serve(md, port=port, threaded=True, show=False)

    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    assert page.locator(".markdown").locator("div").text_content() == 'Initial\n'
    assert not page.locator(".markdown").locator("div").is_visible()

    md.visible = True

    wait_until(lambda: page.locator(".markdown").locator("div").is_visible(), page)
