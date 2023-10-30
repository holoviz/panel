import pytest

try:
    from playwright.sync_api import expect

    pytestmark = pytest.mark.ui
except ImportError:
    pytestmark = pytest.mark.skip("playwright not available")

from panel.config import panel_extension as extension
from panel.pane import Markdown
from panel.tests.util import serve_component


def test_serve_page_on_nested_route(page):
    md = Markdown("Initial")

    msgs, _ = serve_component(page, {"/foo/bar": md})

    expect(page.locator(".markdown").locator("div")).to_have_text("Initial\n")

    md.object = "Updated"

    expect(page.locator(".markdown").locator("div")).to_have_text("Updated\n")

    assert [msg for msg in msgs if msg.type == "error"] == []


def test_serve_page_with_reactive_html_css_on_nested_route(page):
    def app():
        extension(notifications=True, template='material')
        Markdown("Initial").servable()

    msgs, _ = serve_component(page, {"/foo/bar": app})

    assert [msg for msg in msgs if msg.type == "error"] == []
