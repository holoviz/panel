import datetime

import pytest

from panel.tests.util import serve_component, wait_until
from panel.widgets import TimePicker

pytestmark = pytest.mark.ui


def test_time_picker(page):

    time_picker = TimePicker(value="18:08", format="H:i")

    serve_component(page, time_picker)

    # test init corrected timezone
    locator = page.locator("#input")
    assert locator.get_attribute("value") == "18:08:00"

    # test UI change
    locator = page.locator("input.bk-input.form-control.input")
    locator.click()
    wait_until(lambda: page.locator("input.numInput.flatpickr-hour").is_visible())
    locator = page.locator("input.numInput.flatpickr-hour")
    locator.press("ArrowDown")
    locator.press("Enter")
    wait_until(lambda: time_picker.value == datetime.time(17, 8))

    # test str value change
    time_picker.value = "04:08"
    locator = page.locator("#input")
    page.wait_for_timeout(200)
    assert locator.get_attribute("value") == "04:08:00"

    # test datetime.time value change
    time_picker.value = datetime.time(18, 8)
    page.wait_for_timeout(200)
    locator = page.locator("#input")
    assert locator.get_attribute("value") == "18:08:00"


@pytest.mark.parametrize("timezone_id", [
    "America/New_York",
    "Europe/Berlin",
    "UTC",
])
def test_time_picker_timezone_different(page, timezone_id):
    context = page.context.browser.new_context(
        timezone_id=timezone_id,
    )
    page = context.new_page()

    time_picker = TimePicker(value="18:08", format="H:i")
    serve_component(page, time_picker)

    locator = page.locator("#input")
    assert locator.get_attribute("value") == "18:08:00"
