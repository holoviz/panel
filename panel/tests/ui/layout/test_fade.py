import time

import pytest

from panel.io.server import serve
from panel.layout import Fade, Spacer

pytestmark = pytest.mark.ui


def test_fade_fixed_width(page, port):
    before = Spacer(styles={"background": "red"}, height=400, width=800)
    after = Spacer(styles={"background": "green"}, height=400, width=800)
    fade = Fade(before, after, value=25)

    serve(fade, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    bbox = page.locator(".fade-container").bounding_box()

    assert bbox["width"] == 800
    assert bbox["height"] == 400

    before_el = page.locator(".fade-container .outer").first.locator(".inner div")
    assert (
        before_el.evaluate(
            """(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')"""
        )
        == "rgb(255, 0, 0)"
    )
    bbox_before = before_el.bounding_box()
    assert bbox_before["width"] == 800
    assert bbox_before["height"] == 400

    after_el = page.locator(".fade-container .outer").nth(1).locator(".inner div")
    assert (
        after_el.evaluate(
            """(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')"""
        )
        == "rgb(0, 128, 0)"
    )
    bbox_after = after_el.bounding_box()
    assert bbox_after["width"] == 800
    assert bbox_after["height"] == 400

    slider = page.locator(".fade-container .slider")
    slider_bbox = slider.bounding_box()
    assert slider_bbox["x"] == 188

    after_el = page.locator(".fade-container .outer").nth(1)
    assert (
        after_el.evaluate(
            "element => window.getComputedStyle(element).getPropertyValue('opacity')"
        )
        == "0.25"
    )

    slider.drag_to(
        slider, target_position={"x": bbox["width"] - 12, "y": 0}, force=True
    )

    assert (
        after_el.evaluate(
            "element => window.getComputedStyle(element).getPropertyValue('opacity')"
        )
        == "1"
    )
