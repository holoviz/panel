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


@pytest.mark.internet
def test_serve_page_with_reactive_html_css_on_nested_route(page):
    def app():
        extension(notifications=True, template='material')
        Markdown("Initial").servable()

    msgs, _ = serve_component(page, {"/foo/bar": app})

    assert [msg for msg in msgs if msg.type == "error"] == []


def test_saved_inline_tabulator_renders_without_network(page, tmp_path):
    import pandas as pd

    from panel.widgets import Tabulator

    path = tmp_path / 'tabulator.html'
    Tabulator(pd.DataFrame({'a': [1, 2, 3]})).save(path, resources='inline')

    remote = []
    def block_remote(route):
        if route.request.url.startswith('file:'):
            route.continue_()
        else:
            remote.append(route.request.url)
            route.abort()
    page.route('**/*', block_remote)

    msgs = []
    page.on('console', lambda msg: msgs.append(msg))
    page.goto(path.as_uri())

    expect(page.locator('.tabulator-row')).to_have_count(3)
    # Padding only comes from the Tabulator stylesheet
    padding = page.locator('.tabulator-cell').first.evaluate(
        "el => getComputedStyle(el).paddingLeft"
    )
    assert padding != '0px'
    assert [url for url in remote if not url.endswith(('favicon.ico', 'apple-touch-icon.png'))] == []
