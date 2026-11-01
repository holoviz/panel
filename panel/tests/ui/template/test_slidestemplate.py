import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.pane import Markdown
from panel.template import SlidesTemplate
from panel.tests.util import serve_component

pytestmark = pytest.mark.ui


def test_slides_template_no_console_errors(page):
    tmpl = SlidesTemplate()
    md = Markdown('Initial')

    tmpl.main.append(md)

    msgs, _ = serve_component(page, tmpl)

    expect(page.locator(".markdown").locator("div")).to_have_text('Initial\n')

    assert [msg for msg in msgs if msg.type == 'error'] == []


def test_slides_template_updates(page):
    tmpl = SlidesTemplate()
    md = Markdown('Initial')

    tmpl.main.append(md)

    serve_component(page, tmpl)

    expect(page.locator(".markdown").locator("div")).to_have_text('Initial\n')
    md.object = 'Updated'
    expect(page.locator(".markdown").locator("div")).to_have_text('Updated\n')


def test_slides_template_main_max_width(page):
    tmpl = SlidesTemplate(main_max_width='600px')
    tmpl.main.append(Markdown('Initial'))

    serve_component(page, tmpl)

    expect(page.locator(".markdown")).to_be_visible()
    box = page.locator(".reveal").bounding_box()
    assert box['height'] > 50
    assert box['width'] <= 600
