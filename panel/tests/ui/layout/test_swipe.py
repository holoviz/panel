import pytest

from panel.layout import Spacer, Swipe
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui

def test_swipe_fixed_width(page):
    before = Spacer(styles={'background': "red"}, height=400, width=800)
    after = Spacer(styles={'background': "green"}, height=400, width=800)
    swipe = Swipe(
        before,
        after,
    )

    serve_component(page, swipe)

    bbox = page.locator(".swipe-container").bounding_box()

    assert bbox['width'] == 800
    assert bbox['height'] == 400

    before_el = page.locator('.swipe-container .outer').first.locator('.inner div')
    assert before_el.evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')""") == 'rgb(255, 0, 0)'
    bbox_before = before_el.bounding_box()
    assert bbox_before['width'] == 800
    assert bbox_before['height'] == 400

    after_el = page.locator('.swipe-container .outer').nth(1).locator('.inner div')
    assert after_el.evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')""") == 'rgb(0, 128, 0)'
    bbox_after = after_el.bounding_box()
    assert bbox_after['width'] == 800
    assert bbox_after['height'] == 400

    slider = page.locator('.swipe-container .slider')
    slider_bbox = slider.bounding_box()
    assert slider_bbox['x'] == (bbox['width']/2. + 3)
    slider.drag_to(slider, target_position={'x': (bbox['width']/4.), 'y': 0}, force=True)

    assert page.locator('.swipe-container .outer').nth(0).evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('clip-path')""") == 'polygon(0% 0%, calc(75% + 5px) 0%, calc(75% + 5px) 100%, 0% 100%)'
    assert page.locator('.swipe-container .outer').nth(1).evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('clip-path')""") == 'polygon(calc(75% + 5px) 0%, 100% 0%, 100% 100%, calc(75% + 5px) 100%)'

    wait_until(lambda: swipe.value == 75, page)

    swipe.value = 25

    assert page.locator('.swipe-container .outer').nth(0).evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('clip-path')""") == 'polygon(0% 0%, calc(25% + 5px) 0%, calc(25% + 5px) 100%, 0% 100%)'
    assert page.locator('.swipe-container .outer').nth(1).evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('clip-path')""") == 'polygon(calc(25% + 5px) 0%, 100% 0%, 100% 100%, calc(25% + 5px) 100%)'


def test_swipe_stretch_width(page):
    before = Spacer(styles={'background': "red"}, height=400, sizing_mode='stretch_width')
    after = Spacer(styles={'background': "green"}, height=400, sizing_mode='stretch_width')
    swipe = Swipe(
        before,
        after,
        sizing_mode='stretch_width'
    )

    serve_component(page, swipe)

    bbox = page.locator(".swipe-container").bounding_box()
    assert bbox['height'] == 400

    before_el = page.locator('.swipe-container .outer').first.locator('.inner div')
    assert before_el.evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')""") == 'rgb(255, 0, 0)'
    bbox_before = before_el.bounding_box()
    assert bbox_before['width'] == bbox['width']
    assert bbox_before['height'] == 400

    after_el = page.locator('.swipe-container .outer').nth(1).locator('.inner div')
    assert after_el.evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')""") == 'rgb(0, 128, 0)'
    bbox_after = after_el.bounding_box()
    assert bbox_after['width'] == bbox['width']
    assert bbox_after['height'] == 400

    slider = page.locator('.swipe-container .slider')
    slider_bbox = slider.bounding_box()
    assert slider_bbox['x'] == (bbox['width']/2. + 3)
    slider.drag_to(slider, target_position={'x': (bbox['width']/4.), 'y': 0}, force=True)

    assert page.locator('.swipe-container .outer').nth(0).evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('clip-path')""") == 'polygon(0% 0%, calc(75% + 5px) 0%, calc(75% + 5px) 100%, 0% 100%)'
    assert page.locator('.swipe-container .outer').nth(1).evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('clip-path')""") == 'polygon(calc(75% + 5px) 0%, 100% 0%, 100% 100%, calc(75% + 5px) 100%)'

    wait_until(lambda: swipe.value == 75, page)

    swipe.value = 25

    assert page.locator('.swipe-container .outer').nth(0).evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('clip-path')""") == 'polygon(0% 0%, calc(25% + 5px) 0%, calc(25% + 5px) 100%, 0% 100%)'
    assert page.locator('.swipe-container .outer').nth(1).evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('clip-path')""") == 'polygon(calc(25% + 5px) 0%, 100% 0%, 100% 100%, calc(25% + 5px) 100%)'
