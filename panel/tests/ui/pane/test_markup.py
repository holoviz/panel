from html import escape

import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.layout import Row
from panel.models import HTML
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

    expect(page.locator(".markdown").locator("div")).to_have_text('Initial\n')
    expect(page.locator(".markdown").locator("div")).not_to_be_visible()

    md.visible = True

    expect(page.locator(".markdown").locator("div")).to_be_visible()


def test_markdown_pane_stream(page):
    md = Markdown('Empty', enable_streaming=True)

    serve_component(page, md)

    expect(page.locator('.markdown')).to_have_text('Empty')

    md.object = ''
    for i in range(100):
        md.object += str(i)

    assert md.object == ''.join(map(str, range(100)))

    expect(page.locator('.markdown')).to_have_text(md.object)


def test_html_model_no_stylesheet(page):
    # regression test for https://github.com/holoviz/holoviews/issues/5963
    text = "<h1>Header</h1>"
    html = HTML(text=escape(text), width=200, height=200)
    serve_component(page, html)

    header_element = page.locator('h1:has-text("Header")')
    expect(header_element).to_be_visible()
    assert header_element.text_content() == "Header"

def test_anchor_scroll(page):
    md = ''
    for tag in ['tag1', 'tag2', 'tag3']:
        md += f'# {tag}\n\n'
        md += f'{tag} content  \n' * 50

    content = Markdown(md)
    link = Markdown('<a id="link1" href="#tag1">Link1</a><a id="link3" href="#tag3">Link</a>')

    serve_component(page, Row(link, content))

    expect(page.locator('#tag1')).to_be_in_viewport()
    expect(page.locator('#tag3')).not_to_be_in_viewport()

    page.locator('#link3').click()

    expect(page.locator('#tag1')).not_to_be_in_viewport()
    expect(page.locator('#tag3')).to_be_in_viewport()

    page.locator('#link1').click()

    expect(page.locator('#tag1')).to_be_in_viewport()
    expect(page.locator('#tag3')).not_to_be_in_viewport()

def test_anchor_scroll_on_init(page):
    md = ''
    for tag in ['tag1', 'tag2', 'tag3']:
        md += f'# {tag}\n\n'
        md += f'{tag} content  \n' * 50

    content = Markdown(md)

    serve_component(page, content, suffix='#tag3')

    expect(page.locator('#tag1')).not_to_be_in_viewport()
    expect(page.locator('#tag3')).to_be_in_viewport()
