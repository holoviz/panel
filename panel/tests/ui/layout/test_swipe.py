import time

import pytest

from panel.io.server import serve
from panel.layout import Fade, Spacer

pytestmark = pytest.mark.ui

def test_fade_layout(page, port):
    before = Spacer(styles={'background': "red"}, height=400, width=800)
    after = Spacer(styles={'background': "green"}, height=400, width=800)
    fade = Fade(before, after)

    serve(fade, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    container = page.locator("#container")

    assert container.evaluate("el => el.style.position") == "relative"
    assert container.evaluate("el => el.style.width") == "800px"
    assert container.evaluate("el => el.style.height") == "400px"

    before_el = page.locator("#before-inner")
    assert before_el.evaluate("el => el.style.background") == "red"
    before_bbox = before_el.bounding_box()
    assert before_bbox["width"] == 800
    assert before_bbox["height"] == 400

    after_el = page.locator("#after-inner")
    assert after_el.evaluate("el => el.style.background") == "green"
    after_bbox = after_el.bounding_box()
    assert after_bbox["width"] == 800
    assert after_bbox["height"] == 400

    slider = page.locator("#slider")
    slider_bbox = slider.bounding_box()
    assert slider_bbox["width"] == fade.slider_width
    assert slider_bbox["background"] == fade.slider_color

    slider.drag_to(slider, target_position={"x": 100, "y": 0}, force=True)

    assert after_el.evaluate("el => el.style.opacity") == "1"
    assert slider.evaluate("el => el.style.marginLeft") == f"calc({fade.value}% - {fade.slider_width / 2}px)"

    time.sleep(0.2)

    assert fade.value == 100

    fade.value = 50

    time.sleep(0.2)

    assert after_el.evaluate("el => el.style.opacity") == "0.5"
    assert slider.evaluate("el => el.style.marginLeft") == f"calc({fade.value}% - {fade.slider_width / 2}px)"
