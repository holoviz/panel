import pytest

pytest.importorskip("playwright")

from bokeh.models import Tooltip
from playwright.sync_api import expect

from panel import config
from panel.tests.util import serve_component, wait_until
from panel.widgets import TooltipIcon
from panel.widgets.indicators import Number, String

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


def test_number_indicator_dark_theme_color(page):
    """Test that Number indicator maintains white color in dark theme on value changes"""
    # Set dark theme
    config.theme = 'dark'
    try:
        number = Number(name="Test", value=0)
        
        serve_component(page, number)
        
        # Find the value div (second div, after the title)
        value_div = page.locator('div[style*="font-size: 54pt"]')
        expect(value_div).to_have_count(1)
        
        # Get the computed style to check the color
        initial_color = value_div.evaluate('el => getComputedStyle(el).color')
        
        # White color in RGB is "rgb(255, 255, 255)"
        # Check that it's not black "rgb(0, 0, 0)"
        assert initial_color == "rgb(255, 255, 255)", f"Initial color should be white, got {initial_color}"
        
        # Update the value
        number.value = 42
        
        # Wait for the update
        def check_value():
            return value_div.inner_text() == "42"
        wait_until(check_value, page, timeout=5000)
        
        # Check color is still white after value change
        updated_color = value_div.evaluate('el => getComputedStyle(el).color')
        assert updated_color == "rgb(255, 255, 255)", f"Color after update should be white, got {updated_color}"
    finally:
        config.theme = 'default'


def test_string_indicator_dark_theme_color(page):
    """Test that String indicator maintains white color in dark theme on value changes"""
    # Set dark theme
    config.theme = 'dark'
    try:
        string = String(name="Test", value="Hello")
        
        serve_component(page, string)
        
        # Find the value div (second div, after the title)
        value_div = page.locator('div[style*="font-size: 54pt"]')
        expect(value_div).to_have_count(1)
        
        # Get the computed style to check the color
        initial_color = value_div.evaluate('el => getComputedStyle(el).color')
        
        # White color in RGB is "rgb(255, 255, 255)"
        assert initial_color == "rgb(255, 255, 255)", f"Initial color should be white, got {initial_color}"
        
        # Update the value
        string.value = "World"
        
        # Wait for the update
        def check_value():
            return value_div.inner_text() == "World"
        wait_until(check_value, page, timeout=5000)
        
        # Check color is still white after value change
        updated_color = value_div.evaluate('el => getComputedStyle(el).color')
        assert updated_color == "rgb(255, 255, 255)", f"Color after update should be white, got {updated_color}"
    finally:
        config.theme = 'default'
