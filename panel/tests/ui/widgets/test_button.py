import pytest

pytest.importorskip("playwright")

from bokeh.models import Tooltip
from playwright.sync_api import Expect, expect

from panel.tests.util import serve_component, wait_until
from panel.widgets import (
    Button, CheckButtonGroup, RadioButtonGroup, TooltipIcon,
)

pytestmark = pytest.mark.ui


def test_button_click(page):
    button = Button(name='Click')

    events = []
    def cb(event):
        events.append(event)
    button.on_click(cb)

    serve_component(page, button)

    page.click('.bk-btn')

    wait_until(lambda: len(events) == 1, page)


@pytest.mark.parametrize(
    "description",
    ["Test", Tooltip(content="Test", position="right"), TooltipIcon(value="Test")],
    ids=["str", "Tooltip", "TooltipIcon"],
)
@pytest.mark.parametrize(
    "button_fn,button_locator",
    [
        (lambda **kw: Button(**kw), ".bk-btn"),
        (lambda **kw: CheckButtonGroup(options=["A", "B"], **kw), ".bk-btn-group"),
        (lambda **kw: RadioButtonGroup(options=["A", "B"], **kw), ".bk-btn-group"),
    ],
    ids=["Button", "CheckButtonGroup", "RadioButtonGroup"],
)
def test_button_tooltip(page, button_fn, button_locator, description):
    pn_button = button_fn(name="test", description=description, description_delay=0)

    serve_component(page, pn_button)

    button = page.locator(button_locator)
    expect(button).to_have_count(1)
    tooltip = page.locator(".bk-tooltip-content")
    expect(tooltip).to_have_count(0)

    # Hovering over the button should show the tooltip
    page.hover(button_locator)
    tooltip = page.locator(".bk-tooltip-content")
    expect(tooltip).to_have_count(1)
    expect(tooltip).to_have_text("Test")

    # Removing hover should hide the tooltip
    page.hover("body")
    tooltip = page.locator(".bk-tooltip-content")
    expect(tooltip).to_have_count(0)


@pytest.mark.parametrize(
    "button_fn,button_locator",
    [
        (lambda **kw: Button(**kw), ".bk-btn"),
        (lambda **kw: CheckButtonGroup(options=["A", "B"], **kw), ".bk-btn-group"),
        (lambda **kw: RadioButtonGroup(options=["A", "B"], **kw), ".bk-btn-group"),
    ],
    ids=["Button", "CheckButtonGroup", "RadioButtonGroup"],
)
def test_button_tooltip_with_delay(page, button_fn, button_locator):
    pn_button = button_fn(name="test", description="Test", description_delay=300)

    exp = Expect()
    exp.set_options(timeout=200)

    serve_component(page, pn_button)

    button = page.locator(button_locator)
    expect(button).to_have_count(1)
    tooltip = page.locator(".bk-tooltip-content")
    expect(tooltip).to_have_count(0)

    # Hovering over the button should not show the tooltip
    page.hover(button_locator)
    tooltip = page.locator(".bk-tooltip-content")
    exp(tooltip).to_have_count(0)

    # After 100 ms the tooltip should be visible
    wait_until(lambda: exp(tooltip).to_have_count(1), page)

    # Removing hover should hide the tooltip
    page.hover("body")
    tooltip = page.locator(".bk-tooltip-content")
    wait_until(lambda: exp(tooltip).to_have_count(0), page)

    # Hovering over the button for a short time should not show the tooltip
    page.hover(button_locator)
    page.wait_for_timeout(50)
    page.hover("body")
    page.wait_for_timeout(300)
    exp(tooltip).to_have_count(0)
