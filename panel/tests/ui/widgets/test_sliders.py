import time

import pytest

pytestmark = pytest.mark.ui

from panel.io.server import serve
from panel.tests.util import wait_until
from panel.widgets import (
    EditableFloatSlider, EditableIntSlider, EditableRangeSlider,
)


class _editable_text_input:
    """
    This function is added for convenience, as it is pretty
    cumbersome to find and update the value of Editable text input.
    """

    def __init__(self, page, nth=0):
        self.page = page
        self.text_input = page.locator("input.bk-input").nth(nth)

    @property
    def value(self):
        return self.text_input.input_value()

    @value.setter
    def value(self, value):
        self.text_input.fill(str(value))
        self.text_input.press("Enter")


@pytest.mark.parametrize(
    "widget,val1,val2,val3,func",
    [
       (EditableIntSlider, 25, 24, 20, int),
       (EditableFloatSlider, 25.5, 24.5, 19.5, float),
    ],
    ids=["EditableIntSlider", "EditableFloatSlider"]
)
def test_editableslider_textinput_end(page, port, widget, val1, val2, val3, func):
    widget = widget()

    serve(widget, port=port, threaded=True, show=False)
    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    text_input = _editable_text_input(page)

    text_input.value = val1
    wait_until(lambda: widget.value == val1, page)
    assert widget._slider.end == val1
    assert func(text_input.value) == val1

    text_input.value = val2
    wait_until(lambda: widget.value == val2, page)
    assert widget._slider.end == val1
    assert func(text_input.value) == val2

    # Setting fixed end
    widget.fixed_end = val3
    wait_until(lambda: widget.value == val3, page)
    assert widget._slider.end == val3
    assert func(text_input.value) == val3

@pytest.mark.parametrize(
    "widget,val1,val2,val3,func",
    [
       (EditableIntSlider, -25, -24, -20, int),
       (EditableFloatSlider, -25.5, -24.5, -19.5, float),
    ],
    ids=["EditableIntSlider", "EditableFloatSlider"]
)
def test_editableslider_textinput_start(page, port, widget, val1, val2, val3, func):
    widget = widget()

    serve(widget, port=port, threaded=True, show=False)
    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    text_input = _editable_text_input(page)

    text_input.value = val1
    wait_until(lambda: widget.value == val1, page)
    assert widget._slider.start == val1
    assert func(text_input.value) == val1

    text_input.value = val2
    wait_until(lambda: widget.value == val2, page)
    assert widget._slider.start == val1
    assert func(text_input.value) == val2

    # Setting fixed start
    widget.fixed_start = val3
    wait_until(lambda: widget.value == val3, page)
    assert widget._slider.start == val3
    assert func(text_input.value) == val3

@pytest.mark.parametrize(
    "widget",
    [
       EditableIntSlider,
       EditableFloatSlider,
    ],
    ids=["EditableIntSlider", "EditableFloatSlider"]
)
def test_editableslider_button_end(page, port, widget):
    widget = widget(step=1)
    default_value = widget.value
    step = widget.step
    end = widget.end

    serve(widget, port=port, threaded=True, show=False)
    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    up = page.locator("button").nth(0)
    down = page.locator("button").nth(1)

    up.click()
    wait_until(lambda: widget.value == default_value + step, page)
    assert widget.value == default_value + step
    assert widget._slider.end == end

    up.click()
    wait_until(lambda: widget.value == default_value + 2 * step, page)
    assert widget._slider.end == end + step

    down.click()
    wait_until(lambda: widget.value == default_value + step, page)
    assert widget._slider.end == end + step


@pytest.mark.parametrize(
    "widget",
    [
       EditableIntSlider,
       EditableFloatSlider
    ],
    ids=["EditableIntSlider", "EditableFloatSlider"]
)
def test_editableslider_button_start(page, port, widget):
    widget = widget(step=1)
    default_value = widget.value
    step = widget.step
    start = widget.start

    serve(widget, port=port, threaded=True, show=False)
    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    up = page.locator("button").nth(0)
    down = page.locator("button").nth(1)

    down.click()
    wait_until(lambda: widget.value == default_value - step, page)
    assert widget._slider.start == start - step

    down.click()
    wait_until(lambda: widget.value == default_value - 2 * step, page)
    assert widget._slider.start == start - 2 * step

    up.click()
    wait_until(lambda: widget.value == default_value - step, page)
    assert widget._slider.start == start - 2 * step


@pytest.mark.parametrize(
    "widget,val1,val2,val3,func",
    [
       (EditableRangeSlider, 25.5, 24.5, 19.5, float),
    ],
    ids=["EditableRangeSlider"]
)
def test_editablerangeslider_textinput_end(page, port, widget, val1, val2, val3, func):
    widget = widget()

    serve(widget, port=port, threaded=True, show=False)
    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    text_input = _editable_text_input(page, nth=1)

    text_input.value = val1
    wait_until(lambda: widget.value == (0, val1), page)
    assert widget._slider.end == val1
    assert func(text_input.value) == val1

    text_input.value = val2
    wait_until(lambda: widget.value == (0, val2), page)
    assert widget._slider.end == val1
    assert func(text_input.value) == val2

    # Setting fixed end
    widget.fixed_end = val3
    wait_until(lambda: widget.value == (0, val3), page)
    assert widget._slider.end == val3
    assert func(text_input.value) == val3


@pytest.mark.parametrize(
    "widget,val1,val2,val3,func",
    [
       (EditableRangeSlider, -25.5, -24.5, -19.5, float),
    ],
    ids=["EditableRangeSlider"]
)
def test_editablerangeslider_textinput_start(page, port, widget, val1, val2, val3, func):
    widget = widget()

    serve(widget, port=port, threaded=True, show=False)
    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    text_input = _editable_text_input(page, nth=0)

    text_input.value = val1
    wait_until(lambda: widget.value == (val1, 1), page)
    assert widget._slider.start == val1
    assert func(text_input.value) == val1

    text_input.value = val2
    wait_until(lambda: widget.value == (val2, 1), page)
    assert widget._slider.start == val1
    assert func(text_input.value) == val2

    # Setting fixed start
    widget.fixed_start = val3
    wait_until(lambda: widget.value == (val3, 1), page)
    assert widget._slider.start == val3
    assert func(text_input.value) == val3


@pytest.mark.parametrize(
    "widget",
    [
       EditableRangeSlider,
    ],
    ids=["EditableRangeSlider"]
)
def test_editablerangeslider_button_end(page, port, widget):
    widget = widget(step=1)
    default_value = widget.value
    step = widget.step
    end = widget.end

    serve(widget, port=port, threaded=True, show=False)
    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    up = page.locator("button").nth(2)
    down = page.locator("button").nth(3)

    up.click()
    wait_until(lambda: widget.value == (0, default_value[1] + step), page)
    assert widget._slider.end == end + step

    up.click()
    wait_until(lambda: widget.value == (0, default_value[1] + 2 * step), page)
    assert widget._slider.end == end + 2 * step

    down.click()
    wait_until(lambda: widget.value == (0, default_value[1] + step), page)
    assert widget._slider.end == end + 2 * step



@pytest.mark.parametrize(
    "widget",
    [
       EditableRangeSlider,
    ],
    ids=["EditableRangeSlider"]
)
def test_editablerangeslider_button_start(page, port, widget):
    widget = widget(step=1)
    default_value = widget.value
    step = widget.step
    start = widget.start

    serve(widget, port=port, threaded=True, show=False)
    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    up = page.locator("button").nth(0)
    down = page.locator("button").nth(1)

    down.click()
    wait_until(lambda: widget.value == (default_value[0] - step, 1), page)
    assert widget._slider.start == start - step

    down.click()
    wait_until(lambda: widget.value == (default_value[0] - 2 * step, 1), page)
    assert widget._slider.start == start - 2 * step

    up.click()
    wait_until(lambda: widget.value == (default_value[0] - step, 1), page)
    assert widget._slider.start == start - 2 * step


def test_editablerangeslider_no_overlap(page, port):
    widget = EditableRangeSlider(value=(0, 2), step=1)

    serve(widget, port=port, threaded=True, show=False)
    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    up_start = page.locator("button").nth(0)
    down_start = page.locator("button").nth(1)
    down_end = page.locator("button").nth(3)

    up_start.click(click_count=3)
    wait_until(lambda: widget.value == (2, 2), page)

    down_start.click()
    wait_until(lambda: widget.value == (1, 2), page)

    down_end.click(click_count=3)
    wait_until(lambda: widget.value == (1, 1), page)
