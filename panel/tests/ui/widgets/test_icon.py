import pytest

pytest.importorskip("playwright")


from panel.layout import Row
from panel.tests.util import serve_component, wait_until
from panel.widgets import (
    ButtonIcon, IntInput, StaticText, ToggleIcon,
)

pytestmark = pytest.mark.ui

SVG = """
<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-ad-off" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M9 5h10a2 2 0 0 1 2 2v10m-2 2h-14a2 2 0 0 1 -2 -2v-10a2 2 0 0 1 2 -2" /><path d="M7 15v-4a2 2 0 0 1 2 -2m2 2v4" /><path d="M7 13h4" /><path d="M17 9v4" /><path d="M16.115 12.131c.33 .149 .595 .412 .747 .74" /><path d="M3 3l18 18" /></svg>
"""  # noqa: E501
ACTIVE_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-ad-filled" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M19 4h-14a3 3 0 0 0 -3 3v10a3 3 0 0 0 3 3h14a3 3 0 0 0 3 -3v-10a3 3 0 0 0 -3 -3zm-10 4a3 3 0 0 1 2.995 2.824l.005 .176v4a1 1 0 0 1 -1.993 .117l-.007 -.117v-1h-2v1a1 1 0 0 1 -1.993 .117l-.007 -.117v-4a3 3 0 0 1 3 -3zm0 2a1 1 0 0 0 -.993 .883l-.007 .117v1h2v-1a1 1 0 0 0 -1 -1zm8 -2a1 1 0 0 1 .993 .883l.007 .117v6a1 1 0 0 1 -.883 .993l-.117 .007h-1.5a2.5 2.5 0 1 1 .326 -4.979l.174 .029v-2.05a1 1 0 0 1 .883 -.993l.117 -.007zm-1.41 5.008l-.09 -.008a.5 .5 0 0 0 -.09 .992l.09 .008h.5v-.5l-.008 -.09a.5 .5 0 0 0 -.318 -.379l-.084 -.023z" stroke-width="0" fill="currentColor" /></svg>
"""  # noqa: E501


def test_toggle_icon_click(page):
    icon = ToggleIcon()
    serve_component(page, icon)

    # test defaults
    assert icon.icon == "heart"
    assert not icon.value
    icon_element = page.locator(".ti-heart")
    assert icon_element

    events = []

    def cb(event):
        events.append(event)

    icon.param.watch(cb, "value")

    # test icon click updates value
    page.click(".bk-TablerIcon")
    wait_until(lambda: len(events) == 1, page)
    assert icon.value


def test_toggle_icon_width_height(page):
    icon = ToggleIcon(width=100, height=100)
    serve_component(page, icon)

    # test defaults
    assert icon.icon == "heart"
    assert not icon.value
    icon_element = page.locator(".ti-heart")

    wait_until(lambda: icon_element.bounding_box()["width"] == 100)


def test_toggle_icon_size(page):
    icon = ToggleIcon(size="120px")
    serve_component(page, icon)

    # test defaults
    assert icon.icon == "heart"
    assert not icon.value
    icon_element = page.locator(".ti-heart")

    wait_until(lambda: icon_element.bounding_box()["width"] == 120)


def test_toggle_icon_active_icon(page):
    icon = ToggleIcon(icon="thumb-down", active_icon="thumb-up")
    serve_component(page, icon)

    # test defaults
    assert icon.icon == "thumb-down"
    assert not icon.value
    assert page.locator(".thumb-down")

    events = []

    def cb(event):
        events.append(event)

    icon.param.watch(cb, "value")

    # test icon click updates value
    page.click(".bk-TablerIcon")
    wait_until(lambda: len(events) == 1, page)
    assert icon.value
    assert page.locator(".thumb-up")


def test_toggle_icon_update_params_dynamically(page):
    icon = ToggleIcon(icon="thumb-down", active_icon="thumb-up")
    serve_component(page, icon)

    # test defaults
    assert icon.icon == "thumb-down"
    assert not icon.value
    assert page.locator(".thumb-down")

    events = []

    def cb(event):
        events.append(event)

    icon.param.watch(cb, "value")

    # test icon click updates value
    page.click(".bk-TablerIcon")
    wait_until(lambda: len(events) == 1, page)
    assert icon.value
    assert page.locator(".thumb-up")

    # update active icon name
    icon.active_icon = ""
    assert page.locator(".heart-filled")

    # update value and icon name
    icon.value = True
    icon.icon = "heart"
    assert page.locator(".ti-heart")

    # update active icon_name to svg
    icon.active_icon = ACTIVE_SVG
    assert page.locator(".icon-tabler-ad-filled")

    # update size
    icon.size = "8em"
    wait_until(lambda: page.locator(".icon-tabler-ad-filled").bounding_box() is not None, page)
    wait_until(lambda: page.locator(".icon-tabler-ad-filled").bounding_box()["width"] > 96, page)

    icon.size = "1em"
    wait_until(lambda: page.locator(".icon-tabler-ad-filled").bounding_box() is not None, page)
    wait_until(lambda: page.locator(".icon-tabler-ad-filled").bounding_box()["width"] < 24, page)


def test_toggle_icon_svg(page):
    icon = ToggleIcon(icon=SVG, active_icon=ACTIVE_SVG)
    serve_component(page, icon)

    # test defaults
    assert icon.icon == SVG
    assert not icon.value
    assert page.locator(".icon-tabler-ad-off")

    events = []

    def cb(event):
        events.append(event)

    icon.param.watch(cb, "value")

    # test icon click updates value
    page.click(".bk-SVGIcon")
    wait_until(lambda: len(events) == 1, page)
    assert icon.value
    assert page.locator(".icon-tabler-ad-filled")


def test_toggle_icon_tabler_to_svg(page):
    tabler = "ad-off"

    icon = ToggleIcon(icon=tabler, active_icon=ACTIVE_SVG)
    serve_component(page, icon)

    # test defaults
    assert icon.icon == tabler
    assert not icon.value
    assert page.locator(".icon-tabler-ad-off")

    events = []

    def cb(event):
        events.append(event)

    icon.param.watch(cb, "value")

    # test icon click updates value
    page.click(".bk-TablerIcon")
    wait_until(lambda: len(events) == 1, page)
    assert icon.value
    assert page.locator(".icon-tabler-ad-filled")


def test_toggle_icon_svg_to_tabler(page):
    icon = ToggleIcon(icon=SVG, active_icon="ad-filled")
    serve_component(page, icon)

    # test defaults
    assert icon.icon == SVG
    assert not icon.value
    assert page.locator(".icon-tabler-ad-off")

    events = []

    def cb(event):
        events.append(event)

    icon.param.watch(cb, "value")

    # test icon click updates value
    page.click(".bk-SVGIcon")
    wait_until(lambda: len(events) == 1, page)
    assert icon.value
    assert page.locator(".icon-tabler-ad-filled")


def test_button_icon(page):
    icon = ButtonIcon(
        icon="clipboard", active_icon="check", toggle_duration=2000, size="5em"
    )
    serve_component(page, icon)

    # test defaults
    assert icon.icon == "clipboard"
    assert not icon.disabled
    assert page.locator(".clipboard")

    events = []

    def cb(event):
        events.append(event)

    icon.param.watch(cb, "clicks")

    # test icon click updates clicks
    page.click(".bk-TablerIcon")
    wait_until(lambda: len(events) == 1, page)
    assert len(events) == 1
    assert icon.clicks == 1
    assert page.locator(".check")

    # reverts back to original icon after toggle_duration
    wait_until(lambda: not icon.disabled, page)
    assert not icon.disabled
    assert page.locator(".clipboard")


def test_button_icon_disabled(page):
    icon = ButtonIcon(
        icon="clipboard",
        active_icon="check",
        toggle_duration=2000,
        size="5em",
        disabled=True,
    )
    serve_component(page, icon)

    # test defaults
    assert icon.icon == "clipboard"
    assert icon.disabled
    assert page.locator(".clipboard")

    events = []

    def cb(event):
        events.append(event)

    icon.param.watch(cb, "clicks")

    # test icon click does NOT update clicks
    page.click(".bk-TablerIcon")
    assert len(events) == 0
    assert icon.clicks == 0
    assert page.locator(".clipboard")

    # now enable the button
    icon.disabled = False
    wait_until(lambda: not icon.disabled, page)
    assert not icon.disabled
    assert page.locator(".clipboard")

    # test icon click updates clicks
    page.click(".bk-TablerIcon")
    wait_until(lambda: icon.disabled, page)
    wait_until(lambda: len(events) == 1, page)
    assert icon.clicks == 1
    assert page.locator(".check")

    # reverts back to original icon after toggle_duration
    wait_until(lambda: not icon.disabled, page, timeout=2100)
    assert page.locator(".clipboard")
    assert len(events) == 1


def test_button_icon_on_click_method(page):
    def on_click(event):
        static_text.value = f"Clicks: {button.clicks}"

    static_text = StaticText(value="Clicks: 0")
    button = ButtonIcon()
    button.on_click(on_click)
    row = Row(button, static_text)

    serve_component(page, row)

    page.click(".bk-TablerIcon")
    wait_until(lambda: static_text.value == "Clicks: 1", page)
    assert static_text.value == "Clicks: 1"

    button.clicks += 1
    assert static_text.value == "Clicks: 2"


def test_button_icon_on_click_kwarg(page):
    def on_click(event):
        static_text.value = f"Clicks: {button.clicks}"

    static_text = StaticText(value="Clicks: 0")
    button = ButtonIcon(on_click=on_click)
    row = Row(button, static_text)

    serve_component(page, row)

    page.click(".bk-TablerIcon")
    wait_until(lambda: static_text.value == "Clicks: 1", page)
    assert static_text.value == "Clicks: 1"

    button.clicks += 1
    assert static_text.value == "Clicks: 2"


def test_button_icon_js_on_click(page):
    button = ButtonIcon()
    int_slider = IntInput(value=0)
    button.js_on_click(args={"int_slider": int_slider}, code="int_slider.value += 1")
    row = Row(button, int_slider)

    serve_component(page, row)

    page.click(".bk-TablerIcon")
    wait_until(lambda: int_slider.value == 1, page)
    assert int_slider.value == 1


def test_button_icon_tooltip(page):
    button = ButtonIcon(description="Click me")
    serve_component(page, button)

    page.hover(".bk-TablerIcon")
    wait_until(lambda: page.locator(".bk-tooltip-content") is not None, page)
    assert page.locator(".bk-tooltip-content").text_content() == "Click me"


def test_button_icon_name(page):
    button = ButtonIcon(name="Like")
    serve_component(page, button)

    assert button.name == "Like"
    wait_until(lambda: page.locator(".bk-IconLabel").text_content() == "Like", page)


def test_button_icon_name_dynamically(page):
    button = ButtonIcon(name="Like")
    serve_component(page, button)

    assert button.name == "Like"
    assert page.locator(".bk-IconLabel").text_content() == "Like"

    button.name = "Dislike"
    assert button.name == "Dislike"
    wait_until(lambda: page.locator(".bk-IconLabel").text_content() == "Dislike", page)

    assert page.locator(".bk-IconLabel").bounding_box()["width"] < 40

    button.size = "2em"
    # check size
    wait_until(lambda: page.locator(".bk-IconLabel").bounding_box()["width"] >= 40, page)


def test_button_icon_description_dynamically(page):
    button = ButtonIcon(description="Like")
    serve_component(page, button)

    assert button.description == "Like"
    wait_until(lambda: page.locator(".bk-TablerIcon") is not None, page)
    page.locator(".bk-TablerIcon").click()
    assert page.locator(".bk-tooltip-content").text_content() == "Like"

    button.description = "Dislike"
    page.locator(".bk-TablerIcon").click()
    wait_until(lambda: page.locator(".bk-tooltip-content").text_content() == "Dislike", page)
