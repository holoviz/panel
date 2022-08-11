import time

import pytest

try:
    import playwright  # noqa
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

pytestmark = pytest.mark.ui

from panel.io.server import serve
from panel.widgets import EditableFloatSlider, EditableIntSlider


class _editable_text_input:
    """
    This function is added for convenience, as it is pretty
    cumbersome to find and update the value of Editable text input.
    """

    def __init__(self, page, nth=0):
        self.page = page
        self.text_input = page.locator("[placeholder=\"\\30 \"]").nth(nth)

    @property
    def value(self):
        # Needs reload of page to update attribute
        # Should be reimplemented without the need for update
        self.page.reload()
        return self.text_input.get_attribute("value")

    @value.setter
    def value(self, value):
        self.text_input.fill(str(value))
        self.text_input.press("Enter")


@pytest.mark.parametrize(
    "widget,val1,val2,val3,func",
    [
       (EditableIntSlider, 25, 24, 20, int),
       (EditableFloatSlider, 24.5, 24.5, 19.5, float),
    ]
)
def test_editableslider_textinput_end(page, port, widget, val1, val2, val3, func):
    widget = widget()

    serve(widget, port=port, threaded=True, show=False)
    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    text_input = _editable_text_input(page)

    text_input.value = val1
    page.wait_for_timeout(200)
    assert widget.value == val1
    assert widget._slider.end == val1
    assert func(text_input.value) == val1

    text_input.value = val2
    page.wait_for_timeout(200)
    assert widget.value == val2
    assert widget._slider.end == val1
    assert func(text_input.value) == val2

    # Setting fixed end
    widget.fixed_end = val3
    page.wait_for_timeout(200)
    assert widget.value == val3
    assert widget._slider.end == val3
    assert func(text_input.value) == val3


@pytest.mark.parametrize(
    "widget,val1,val2,val3,func",
    [
       (EditableIntSlider, -25, -24, -20, int),
       (EditableFloatSlider, -24.5, -24.5, -19.5, float),
    ]
)
def test_editableslider_textinput_start(page, port, widget, val1, val2, val3, func):
    widget = widget()

    serve(widget, port=port, threaded=True, show=False)
    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    text_input = _editable_text_input(page)

    text_input.value = val1
    page.wait_for_timeout(200)
    assert widget.value == val1
    assert widget._slider.start == val1
    assert func(text_input.value) == val1

    text_input.value = val2
    page.wait_for_timeout(200)
    assert widget.value == val2
    assert widget._slider.start == val1
    assert func(text_input.value) == val2

    # Setting fixed start
    widget.fixed_start = val3
    page.wait_for_timeout(200)
    assert widget.value == val3
    assert widget._slider.start == val3
    assert func(text_input.value) == val3

@pytest.mark.parametrize(
    "widget",
    [
       EditableIntSlider,
       EditableFloatSlider
    ]
)
def test_editableslider_button_end(page, port, widget):
    widget = widget(step=1)

    serve(widget, port=port, threaded=True, show=False)
    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")


    default_value = widget.value
    step = widget.step
    end = widget.end

    up = page.locator("button").nth(0)
    down = page.locator("button").nth(1)

    up.click()
    page.wait_for_timeout(200)
    assert widget.value == default_value + step
    assert widget._slider.end == end

    up.click()
    page.wait_for_timeout(200)
    assert widget.value == default_value + 2 * step
    assert widget._slider.end == end + step

    down.click()
    page.wait_for_timeout(200)
    assert widget.value == default_value + step
    assert widget._slider.end == end + step


@pytest.mark.parametrize(
    "widget",
    [
       EditableIntSlider,
       EditableFloatSlider
    ]
)
def test_editableslider_button_start(page, port, widget):
    widget = widget(step=1)

    serve(widget, port=port, threaded=True, show=False)
    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")


    default_value = widget.value
    step = widget.step
    start = widget.start

    up = page.locator("button").nth(0)
    down = page.locator("button").nth(1)

    down.click()
    page.wait_for_timeout(200)
    assert widget.value == default_value - step
    assert widget._slider.start == start - step

    down.click()
    page.wait_for_timeout(200)
    assert widget.value == default_value - 2 * step
    assert widget._slider.start == start - 2 * step

    up.click()
    page.wait_for_timeout(200)
    assert widget.value == default_value - step
    assert widget._slider.start == start - 2 * step
