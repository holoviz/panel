import pathlib

import param
import pytest

try:
    from playwright.sync_api import expect

    pytestmark = pytest.mark.ui
except ImportError:
    pytestmark = pytest.mark.skip("playwright not available")

from panel.config import panel_extension as extension
from panel.pane import Markdown
from panel.tests.util import _STYLESHEETS_SETTLED, serve_component, wait_until
from panel.theme import DefaultTheme, Design, Inherit


class RelativeTheme(DefaultTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'assets' / 'theme.css')


class RelativeThemeDesign(Design):

    modifiers = {
        Markdown: {
            'stylesheets': [Inherit]
        }
    }

    _themes = {'default': RelativeTheme}


class RelativeDesign(Design):

    modifiers = {
        Markdown: {
            'stylesheets': [Inherit, 'assets/design.css']
        }
    }


def _failed_requests(page):
    failed = []
    page.on('response', lambda r: failed.append((r.status, r.url)) if r.status >= 400 else None)
    page.on('requestfailed', lambda r: failed.append(('failed', r.url)))
    return failed


def test_serve_page_on_nested_route(page):
    md = Markdown("Initial")

    msgs, _ = serve_component(page, {"/foo/bar": md})

    expect(page.locator(".markdown").locator("div")).to_have_text("Initial\n")

    md.object = "Updated"

    expect(page.locator(".markdown").locator("div")).to_have_text("Updated\n")

    assert [msg for msg in msgs if msg.type == "error"] == []


@pytest.mark.parametrize('design,filename', [
    (RelativeDesign, 'design.css'), (RelativeThemeDesign, 'theme.css')
], ids=['modifiers', 'theme'])
def test_design_stylesheets_resolve_against_each_route_depth(page, design, filename):
    def app():
        return Markdown("Styled", design=design)

    failed = _failed_requests(page)
    requested = []
    page.on('request', lambda r: requested.append(r.url) if filename in r.url else None)

    # The root page resolves the Design stylesheets first, the nested route
    # must not reuse urls computed relative to the root.
    _, port = serve_component(page, {"/": app, "/foo/bar": app})
    page.goto(f"http://127.0.0.1:{port}/foo/bar")
    expect(page.locator(".markdown").locator("div")).to_have_text("Styled\n")
    page.wait_for_function(_STYLESHEETS_SETTLED, timeout=15000)

    wait_until(lambda: len(requested) >= 2, page)
    assert all('/components/' in url and '/foo/' not in url for url in requested)
    assert failed == []


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
