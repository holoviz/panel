import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.pane import Markdown
from panel.template import FastGridTemplate
from panel.tests.util import serve_component

pytestmark = pytest.mark.ui


def test_fast_grid_template_no_console_errors(page):
    tmpl = FastGridTemplate()
    md = Markdown('Initial')

    tmpl.main[0:3, 0:3] = md

    msgs, _ = serve_component(page, tmpl)

    expect(page.locator(".markdown").locator("div")).to_have_text('Initial\n')

    expected = ['maxWidth', 'maxHeight']
    assert [
        msg for msg in msgs if msg.type == 'error' and not any(e in msg.text for e in expected)
    ] == []


def test_fast_grid_template_updates(page):
    tmpl = FastGridTemplate()
    md = Markdown('Initial')

    tmpl.main[0:3, 0:3] = md

    serve_component(page, tmpl)

    expect(page.locator(".markdown").locator("div")).to_have_text('Initial\n')
    md.object = 'Updated'
    expect(page.locator(".markdown").locator("div")).to_have_text('Updated\n')
