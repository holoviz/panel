import pytest

pytest.importorskip("playwright")


from panel.tests.util import serve_component, wait_until
from panel.widgets import ToggleIcon

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
    icon_element = page.locator('.ti-heart')
    assert icon_element

    events = []
    def cb(event):
        events.append(event)
    icon.param.watch(cb, "value")

    # test icon click updates value
    page.click('.bk-TablerIcon')
    wait_until(lambda: len(events) == 1, page)
    assert icon.value

def test_toggle_icon_width_height(page):
    icon = ToggleIcon(width=100, height=100)
    serve_component(page, icon)

    # test defaults
    assert icon.icon == "heart"
    assert not icon.value
    icon_element = page.locator('.ti-heart')

    wait_until(lambda: icon_element.bounding_box()['width'] == 100)

def test_toggle_icon_size(page):
    icon = ToggleIcon(size='120px')
    serve_component(page, icon)

    # test defaults
    assert icon.icon == "heart"
    assert not icon.value
    icon_element = page.locator('.ti-heart')

    wait_until(lambda: icon_element.bounding_box()['width'] == 120)

def test_toggle_icon_active_icon(page):
    icon = ToggleIcon(icon="thumb-down", active_icon="thumb-up")
    serve_component(page, icon)

    # test defaults
    assert icon.icon == "thumb-down"
    assert not icon.value
    assert page.locator('.thumb-down')

    events = []
    def cb(event):
        events.append(event)
    icon.param.watch(cb, "value")

    # test icon click updates value
    page.click('.bk-TablerIcon')
    wait_until(lambda: len(events) == 1, page)
    assert icon.value
    assert page.locator('.thumb-up')


def test_toggle_icon_update_params_dynamically(page):
    icon = ToggleIcon(icon="thumb-down", active_icon="thumb-up")
    serve_component(page, icon)

    # test defaults
    assert icon.icon == "thumb-down"
    assert not icon.value
    assert page.locator('.thumb-down')

    events = []
    def cb(event):
        events.append(event)
    icon.param.watch(cb, "value")

    # test icon click updates value
    page.click('.bk-TablerIcon')
    wait_until(lambda: len(events) == 1, page)
    assert icon.value
    assert page.locator('.thumb-up')

    # update active icon name
    icon.active_icon = ""
    assert page.locator('.heart-filled')

    # update value and icon name
    icon.value = True
    icon.icon = "heart"
    assert page.locator('.ti-heart')

    # update active icon_name to svg
    icon.active_icon = ACTIVE_SVG
    assert page.locator('.icon-tabler-ad-filled')


def test_toggle_icon_svg(page):
    icon = ToggleIcon(icon=SVG, active_icon=ACTIVE_SVG)
    serve_component(page, icon)

    # test defaults
    assert icon.icon == SVG
    assert not icon.value
    assert page.locator('.icon-tabler-ad-off')

    events = []
    def cb(event):
        events.append(event)
    icon.param.watch(cb, "value")

    # test icon click updates value
    page.click('.bk-SVGIcon')
    wait_until(lambda: len(events) == 1, page)
    assert icon.value
    assert page.locator('.icon-tabler-ad-filled')

def test_toggle_icon_tabler_to_svg(page):
    tabler = "ad-off"

    icon = ToggleIcon(icon=tabler, active_icon=ACTIVE_SVG)
    serve_component(page, icon)

    # test defaults
    assert icon.icon == tabler
    assert not icon.value
    assert page.locator('.icon-tabler-ad-off')

    events = []
    def cb(event):
        events.append(event)
    icon.param.watch(cb, "value")

    # test icon click updates value
    page.click('.bk-TablerIcon')
    wait_until(lambda: len(events) == 1, page)
    assert icon.value
    assert page.locator('.icon-tabler-ad-filled')

def test_toggle_icon_svg_to_tabler(page):
    icon = ToggleIcon(icon=SVG, active_icon="ad-filled")
    serve_component(page, icon)

    # test defaults
    assert icon.icon == SVG
    assert not icon.value
    assert page.locator('.icon-tabler-ad-off')

    events = []
    def cb(event):
        events.append(event)
    icon.param.watch(cb, "value")

    # test icon click updates value
    page.click('.bk-SVGIcon')
    wait_until(lambda: len(events) == 1, page)
    assert icon.value
    assert page.locator('.icon-tabler-ad-filled')
