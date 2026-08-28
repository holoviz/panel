import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.layout import Tabs
from panel.pane.image import PNG
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui


def test_tabs_toggle_visible(page):
    tabs = Tabs(("Foo", "Foo"), ("Bar", "Bar"))

    serve_component(page, tabs)

    tabs_root = page.locator('.bk-panel-models-tabs-Tabs')
    expect(tabs_root).to_have_count(1)

    tab_panels = tabs_root.locator(".bk-panel-models-markup-HTML")
    expect(tab_panels).to_have_count(1)

    expect(tab_panels.first).to_have_text("Foo")

    tabs_root.locator('.bk-tab').last.click(force=True)

    expect(tab_panels.last).to_have_text("Bar")


def test_tabs_toggle_clickable(page):
    url = "https://assets.holoviz.org/panel/samples/png_sample.png"
    png_pane = PNG(url, link_url=url, target="_self")

    tabs = Tabs(("Foo", png_pane), ("Bar", "Bar"), active=1)

    serve_component(page, tabs)

    tabs_root = page.locator('.bk-panel-models-tabs-Tabs')
    expect(tabs_root).to_have_count(1)

    tab_panels = tabs_root.locator(".bk-panel-models-markup-HTML")
    expect(tab_panels).to_have_count(1)
    expect(tab_panels.last).to_be_visible()

    page.mouse.click(200, 200)

    assert page.url.startswith('http://localhost')

    tabs_root.locator('.bk-tab').first.click(force=True)

    expect(tab_panels.first).to_be_visible()

    page.mouse.click(200, 200)

    wait_until(lambda: page.url == url, page)
