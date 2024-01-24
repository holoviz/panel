import pytest

pytest.importorskip("playwright")

from bokeh.models import Tooltip
from playwright.sync_api import expect

from panel.tests.util import serve_component, wait_until
from panel.widgets import TooltipIcon

pytestmark = pytest.mark.ui


@pytest.mark.parametrize(
    "value", ["Test", Tooltip(content="Test", position="right")], ids=["str", "Tooltip"]
)
def test_plaintext_tooltip(page, value):
    tooltip_icon = TooltipIcon(value="Test")

    serve_component(page, tooltip_icon)

    icon = page.locator(".bk-icon")
    expect(icon).to_have_count(1)
    tooltip = page.locator(".bk-tooltip-content")
    expect(tooltip).to_have_count(0)

    # Hovering over the icon should show the tooltip
    page.hover(".bk-icon")
    tooltip = page.locator(".bk-tooltip-content")
    expect(tooltip).to_have_count(1)
    expect(tooltip).to_have_text("Test")

    # Removing hover should hide the tooltip
    page.hover("body")
    tooltip = page.locator(".bk-tooltip-content")
    expect(tooltip).to_have_count(0)

    # Clicking the icon should show the tooltip
    page.click(".bk-icon")
    tooltip = page.locator(".bk-tooltip-content")
    expect(tooltip).to_have_count(1)

    # Removing the hover should keep the tooltip
    page.hover("body")
    tooltip = page.locator(".bk-tooltip-content")
    expect(tooltip).to_have_count(1)

    # Clicking should remove the tooltip
    page.click("body")
    tooltip = page.locator(".bk-tooltip-content")
    expect(tooltip).to_have_count(0)


def test_tooltip_text_updates(page):
    tooltip_icon = TooltipIcon(value="Test")

    serve_component(page, tooltip_icon)

    icon = page.locator(".bk-icon")
    expect(icon).to_have_count(1)
    tooltip = page.locator(".bk-tooltip-content")
    expect(tooltip).to_have_count(0)

    # Hovering over the icon should show the tooltip
    page.hover(".bk-icon")
    tooltip = page.locator(".bk-tooltip-content")
    expect(tooltip).to_have_count(1)
    expect(tooltip).to_have_text("Test")

    tooltip_icon.value = "Updated"

    def hover():
        page.hover(".bk-icon")
        visible = page.locator(".bk-tooltip-content").count() == 1
        page.hover("body")
        return visible
    wait_until(hover, page)

    page.hover(".bk-icon")
    tooltip = page.locator(".bk-tooltip-content")
    expect(tooltip).to_have_count(1)
    expect(tooltip).to_have_text("Updated")
