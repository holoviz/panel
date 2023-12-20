import pytest

pytest.importorskip("playwright")


from panel.tests.util import serve_component, wait_until
from panel.widgets import ToggleIcon

pytestmark = pytest.mark.ui


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
