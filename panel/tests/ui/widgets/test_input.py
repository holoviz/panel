import time

import pytest

from panel.io.server import serve
from panel.widgets import DatetimePicker

try:
    from playwright.sync_api import expect
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

pytestmark = pytest.mark.ui


def test_datetimepicker_default(page, port):
    datetime_picker_widget = DatetimePicker(name='Datetime Picker')
    serve(datetime_picker_widget, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    datetime_picker = page.locator('.flatpickr-calendar')
    expect(datetime_picker).to_have_count(1)

    datetime_value = page.locator('.flatpickr-input')
    expect(datetime_value).to_have_count(1)
    # no value set at initialization, this locator has an empty string
    expect(datetime_value).to_have_text('', use_inner_text=True)

    datetime_value.click()
