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

def test_update_markdown_pane_empty(page):
    md = Markdown('Initial')

    serve_component(page, md)

    expect(page.locator(".markdown").locator("div")).to_have_text('Initial\n')

    md.object = ''

    expect(page.locator(".markdown").locator("div")).to_have_text('')

def test_update_markdown_height(page):
    md = Markdown('Initial', height=50)

    serve_component(page, md)

    md_el = page.locator(".markdown")
    expect(md_el.locator("div")).to_have_text('Initial\n')
    wait_until(lambda: md_el.bounding_box()['height'] == 50, page)

    md.height = 300

    wait_until(lambda: md_el.bounding_box()['height'] == 300, page)

def test_update_markdown_width(page):
    md = Markdown('Initial', width=50)

    serve_component(page, md)

    md_el = page.locator(".markdown")
    expect(md_el.locator("div")).to_have_text('Initial\n')
    wait_until(lambda: md_el.bounding_box()['width'] == 50, page)

    md.width = 300

    wait_until(lambda: md_el.bounding_box()['width'] == 300, page)

def test_update_markdown_pane_resizes(page):
    md = Markdown('Initial')

    serve_component(page, md)

    height = page.locator(".markdown").bounding_box()['height']

    assert int(height) == 17

    md.object = """
    - Bullet
    - Points
    """
    wait_until(lambda: int(page.locator(".markdown").bounding_box()['height']) == 34, page)


def test_markdown_pane_visible_toggle(page):
    md = Markdown('Initial', visible=False)

    serve_component(page, md)

    assert page.locator(".markdown").locator("div").text_content() == 'Initial\n'
    assert not page.locator(".markdown").locator("div").is_visible()

    md.visible = True

    wait_until(lambda: page.locator(".markdown").locator("div").is_visible(), page)
