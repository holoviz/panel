import datetime
import time

import pytest

from panel.io.server import serve
from panel.tests.util import wait_until
from panel.widgets import DatetimePicker, DatetimeRangePicker

try:
    from playwright.sync_api import expect
    pytestmark = pytest.mark.ui
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')


@pytest.fixture
def weekdays_as_str():
    weekdays_str = '''
        Sun
        Mon
        Tue
        Wed
        Thu
        Fri
        Sat
    '''
    return weekdays_str


@pytest.fixture
def months_as_str():
    months_str = '''
        January
        February
        March
        April
        May
        June
        July
        August
        September
        October
        November
        December
    '''
    return months_str


@pytest.fixture
def march_2021():
    march_2021_days = [
        28, 1, 2, 3, 4, 5, 6,           # 1st week
        7, 8, 9, 10, 11, 12, 13,        # 2nd week
        14, 15, 16, 17, 18, 19, 20,     # 3rd week
        21, 22, 23, 24, 25, 26, 27,     # 4th week
        28, 29, 30, 31, 1, 2, 3,        # 5th week
        4, 5, 6, 7, 8, 9, 10            # 6th week
    ]
    march_2021_str = '\n'.join([str(i) for i in march_2021_days])
    num_days = 42
    num_prev_month_days = 1
    num_next_month_days = 10
    return march_2021_str, num_days, num_prev_month_days, num_next_month_days


@pytest.fixture
def datetime_value_data():
    year, month, day, hour, min, sec = 2021, 3, 2, 23, 55, 0
    month_str = 'March'
    date_str = 'March 2, 2021'
    datetime_str = '2021-03-02 23:55:00'
    return year, month, day, hour, min, sec, month_str, date_str, datetime_str


@pytest.fixture
def datetime_start_end():
    start = datetime.datetime(2021, 3, 2)
    end = datetime.datetime(2021, 3, 3)
    selectable_dates = ['March 2, 2021', 'March 3, 2021']
    return start, end, selectable_dates


@pytest.fixture
def disabled_dates():
    disabled_list = [
        datetime.date(2021, 3, 1),
        datetime.date(2021, 3, 3),
    ]
    disabled_str_list = ['March 1, 2021', 'March 3, 2021']
    active_date = datetime.datetime(2021, 3, 2)
    return active_date, disabled_list, disabled_str_list


@pytest.fixture
def enabled_dates():
    enabled_list = [
        datetime.date(2021, 3, 1),
        datetime.date(2021, 3, 3),
    ]
    enabled_str_list = ['March 1, 2021', 'March 3, 2021']
    active_date = datetime.datetime(2021, 3, 1)
    return active_date, enabled_list, enabled_str_list


def valid_prev_time(old_value, new_value, max_value, amount=1):
    current_value = int(old_value)
    prev_value = int(new_value)
    if current_value == 0:
        assert prev_value == max_value - amount
    else:
        assert prev_value == current_value - amount
    return True


def valid_next_time(old_value, new_value, max_value, amount=1):
    current_value = int(old_value)
    next_value = int(new_value)
    if current_value == max_value - amount:
        assert next_value == 0
    else:
        assert next_value == current_value + amount
    return True


def valid_prev_month(old_month, new_month, old_year, new_year):
    assert valid_prev_time(old_month, new_month, max_value=12, amount=1)
    if int(old_month) == 0:
        assert int(new_year) == int(old_year) - 1
    else:
        assert int(new_year) == int(old_year)
    return True


def valid_next_month(old_month, new_month, old_year, new_year):
    assert valid_next_time(old_month, new_month, max_value=12, amount=1)
    if int(old_month) == 11:
        assert int(new_year) == int(old_year) + 1
    else:
        assert int(new_year) == int(old_year)
    return True


def test_datetimepicker_default(page, port, weekdays_as_str, months_as_str):
    datetime_picker_widget = DatetimePicker()
    serve(datetime_picker_widget, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    datetime_picker = page.locator('.flatpickr-calendar')
    expect(datetime_picker).to_have_count(1)

    datetime_value = page.locator('.flatpickr-input')
    expect(datetime_value).to_have_count(1)
    # no value set at initialization, this locator has an empty string
    expect(datetime_value).to_have_text('', use_inner_text=True)

    # click to show the datetime picker
    datetime_value.dblclick()
    # ensure the datetime picker is shown
    datetime_value_active = page.locator('.flatpickr-input.active')
    expect(datetime_value_active).to_have_count(1)

    # month and year
    months_container = page.locator('.flatpickr-calendar .flatpickr-months')
    expect(months_container).to_have_count(1)
    expect(months_container).to_contain_text(months_as_str, use_inner_text=True)

    prev_month_button = page.locator('.flatpickr-prev-month')
    next_month_button = page.locator('.flatpickr-next-month')
    month_dropdown = page.locator('.flatpickr-current-month select.flatpickr-monthDropdown-months')
    all_months = page.locator('.flatpickr-calendar .flatpickr-monthDropdown-month')
    year_input = page.locator('.flatpickr-current-month .numInput.cur-year')
    year_up = page.locator('.flatpickr-current-month .arrowUp')
    year_down = page.locator('.flatpickr-current-month .arrowDown')
    expect(prev_month_button).to_have_count(1)
    expect(next_month_button).to_have_count(1)
    expect(month_dropdown).to_have_count(1)
    expect(all_months).to_have_count(12)
    expect(prev_month_button).to_have_count(1)
    expect(year_input).to_have_count(1)
    expect(year_up).to_have_count(1)
    expect(year_down).to_have_count(1)

    # change to previous month
    year_before_click = year_input.input_value()
    month_before_click = month_dropdown.input_value()
    # click to select prev month
    prev_month_button.click()
    month_after_click = month_dropdown.input_value()
    year_after_click = year_input.input_value()
    assert valid_prev_month(
        month_before_click, month_after_click, year_before_click, year_after_click
    )

    # change to next month
    year_before_click = year_input.input_value()
    month_before_click = month_dropdown.input_value()
    # click to select next month
    next_month_button.click()
    month_after_click = month_dropdown.input_value()
    year_after_click = year_input.input_value()
    assert valid_next_month(
        month_before_click, month_after_click, year_before_click, year_after_click
    )

    # TODO: check selected option for month dropdown
    # month_dropdown.click()
    # month_dropdown.select_option(index=0)

    # change to previous year
    year_before_click = year_input.input_value()
    # click to select prev year
    year_down.click()
    year_after_click = year_input.input_value()
    assert int(year_before_click) == int(year_after_click) + 1

    # change to next year
    year_before_click = year_input.input_value()
    # click to select prev year
    year_up.click()
    year_after_click = year_input.input_value()
    assert int(year_before_click) == int(year_after_click) - 1

    # weekdays
    weekdays_container = page.locator('.flatpickr-calendar .flatpickr-weekdays')
    expect(weekdays_container).to_have_count(1)
    expect(weekdays_container).to_contain_text(weekdays_as_str, use_inner_text=True)

    # days
    days_container = page.locator('.flatpickr-calendar .flatpickr-days')
    expect(days_container).to_have_count(1)
    # only 1 date circled as current date
    current_date = page.locator('.flatpickr-calendar .flatpickr-days .flatpickr-day.today')
    expect(current_date).to_have_count(1)

    # time value
    time_container = page.locator('.flatpickr-calendar .flatpickr-time')
    expect(time_container).to_have_count(1)

    time_inputs = page.locator('.flatpickr-calendar .flatpickr-time .numInputWrapper')
    time_up_buttons = page.locator('.flatpickr-calendar .flatpickr-time .arrowUp')
    time_down_buttons = page.locator('.flatpickr-calendar .flatpickr-time .arrowDown')
    # 3 inputs and up/down buttons for hour, min, and sec
    expect(time_inputs).to_have_count(3)
    expect(time_up_buttons).to_have_count(3)
    expect(time_down_buttons).to_have_count(3)
    # 2 separators `:` hour:min:sec
    time_separators = page.locator('.flatpickr-calendar .flatpickr-time .flatpickr-time-separator')
    expect(time_separators).to_have_count(2)

    hour_input = page.locator('.flatpickr-calendar .flatpickr-time .numInput.flatpickr-hour')
    expect(hour_input).to_have_count(1)
    hour_up = time_up_buttons.nth(0)
    hour_down = time_down_buttons.nth(0)

    # click down arrow button to decrease hour
    hour_before_click = hour_input.input_value()
    hour_down.click()
    hour_after_click = hour_input.input_value()
    assert valid_prev_time(hour_before_click, hour_after_click, max_value=24, amount=1)

    # click up arrow button to increase hour
    hour_before_click = hour_input.input_value()
    hour_up.click()
    hour_after_click = hour_input.input_value()
    assert valid_next_time(hour_before_click, hour_after_click, max_value=24, amount=1)

    min_input = page.locator('.flatpickr-calendar .flatpickr-time .numInput.flatpickr-minute')
    expect(min_input).to_have_count(1)
    min_up = time_up_buttons.nth(1)
    min_down = time_down_buttons.nth(1)

    # click down arrow button to decrease minute
    min_before_click = min_input.input_value()
    min_down.click()
    min_after_click = min_input.input_value()
    assert valid_prev_time(min_before_click, min_after_click, max_value=60, amount=5)

    # click up arrow button to increase minutes
    min_before_click = min_input.input_value()
    min_up.click()
    min_after_click = min_input.input_value()
    assert valid_next_time(min_before_click, min_after_click, max_value=60, amount=5)

    sec_input = page.locator('.flatpickr-calendar .flatpickr-time .numInput.flatpickr-second')
    expect(sec_input).to_have_count(1)
    sec_up = time_up_buttons.nth(2)
    sec_down = time_down_buttons.nth(2)

    # click down arrow button to decrease second
    sec_before_click = sec_input.input_value()
    sec_down.click()
    sec_after_click = sec_input.input_value()
    assert valid_prev_time(sec_before_click, sec_after_click, max_value=60, amount=5)

    # click up arrow button to increase second
    sec_before_click = sec_input.input_value()
    sec_up.click()
    sec_after_click = sec_input.input_value()
    assert valid_next_time(sec_before_click, sec_after_click, max_value=60, amount=5)


def test_datetimepicker_value(page, port, march_2021, datetime_value_data):

    year, month, day, hour, min, sec, month_str, date_str, datetime_str = datetime_value_data

    march_2021_str, num_days, num_prev_month_days, num_next_month_days = march_2021

    datetime_picker_widget = DatetimePicker(
        value=datetime.datetime(year, month, day, hour, min, sec)
    )
    serve(datetime_picker_widget, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    datetime_value = page.locator('.flatpickr-input')
    assert datetime_value.input_value() == datetime_str

    # click to show the datetime picker container
    datetime_value.dblclick()

    year_input = page.locator('.flatpickr-current-month .numInput.cur-year')
    assert int(year_input.input_value()) == year

    # days container contains all days of March and some days of previous month and next month
    days_container = page.locator('.flatpickr-calendar .flatpickr-days .dayContainer')
    expect(days_container).to_have_text(march_2021_str, use_inner_text=True)

    prev_month_days = page.locator('.flatpickr-calendar .flatpickr-day.prevMonthDay')
    expect(prev_month_days).to_have_count(num_prev_month_days)

    next_month_days = page.locator('.flatpickr-calendar .flatpickr-day.nextMonthDay')
    expect(next_month_days).to_have_count(num_next_month_days)

    all_days = page.locator('.flatpickr-calendar .flatpickr-day')
    expect(all_days).to_have_count(num_days)

    # value of selected date
    selected_day = page.locator('.flatpickr-calendar .flatpickr-day.selected')
    assert selected_day.get_attribute('aria-label') == date_str

    hour_input = page.locator('.flatpickr-calendar .flatpickr-time .numInput.flatpickr-hour')
    assert int(hour_input.input_value()) == hour
    min_input = page.locator('.flatpickr-calendar .flatpickr-time .numInput.flatpickr-minute')
    assert int(min_input.input_value()) == min
    sec_input = page.locator('.flatpickr-calendar .flatpickr-time .numInput.flatpickr-second')
    assert int(sec_input.input_value()) == sec

    time_up_buttons = page.locator('.flatpickr-calendar .flatpickr-time .arrowUp')
    time_down_buttons = page.locator('.flatpickr-calendar .flatpickr-time .arrowDown')
    hour_up = time_up_buttons.nth(0)
    min_up = time_up_buttons.nth(1)
    sec_down = time_down_buttons.nth(2)

    # click up arrow button to increase hour: 23h -> 0h
    hour_before_click = hour_input.input_value()
    hour_up.click()
    hour_after_click = hour_input.input_value()
    assert valid_next_time(hour_before_click, hour_after_click, max_value=24, amount=1)

    # click up arrow button to increase minutes: 55m -> 0m
    min_before_click = min_input.input_value()
    min_up.click()
    min_after_click = min_input.input_value()
    assert valid_next_time(min_before_click, min_after_click, max_value=60, amount=5)

    # click down arrow button to decrease second: 0s -> 55s
    sec_before_click = sec_input.input_value()
    sec_down.click()
    sec_after_click = sec_input.input_value()
    assert valid_prev_time(sec_before_click, sec_after_click, max_value=60, amount=5)


def test_datetimepicker_start_end(page, port, march_2021, datetime_start_end):
    start, end, selectable_dates = datetime_start_end

    march_2021_str, num_days, _, _ = march_2021

    datetime_picker_widget = DatetimePicker(start=start, end=end)
    serve(datetime_picker_widget, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    datetime_value = page.locator('.flatpickr-input')
    # click to show the datetime picker container
    datetime_value.dblclick()

    # days container contains all days of March and some days of previous month and next month
    days_container = page.locator('.flatpickr-calendar .flatpickr-days .dayContainer')
    expect(days_container).to_have_text(march_2021_str, use_inner_text=True)

    # disabled days
    disabled_days = page.locator('.flatpickr-calendar .flatpickr-day.flatpickr-disabled')
    expect(disabled_days).to_have_count(num_days - len(selectable_dates))


def test_datetimepicker_disabled_dates(page, port, disabled_dates):
    active_date, disabled_list, disabled_str_list = disabled_dates

    datetime_picker_widget = DatetimePicker(
        disabled_dates=disabled_list, value=active_date
    )
    serve(datetime_picker_widget, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    # click to show the datetime picker container
    datetime_value = page.locator('.flatpickr-input')
    datetime_value.dblclick()

    # disabled days
    disabled_days = page.locator('.flatpickr-calendar .flatpickr-day.flatpickr-disabled')
    expect(disabled_days).to_have_count(len(disabled_list))
    for i in range(len(disabled_list)):
        assert disabled_days.nth(i).get_attribute('aria-label') == disabled_str_list[i]


def test_datetimepicker_enabled_dates(page, port, march_2021, enabled_dates):
    active_date, enabled_list, enabled_str_list = enabled_dates
    datetime_picker_widget = DatetimePicker(
        enabled_dates=enabled_list, value=active_date
    )
    serve(datetime_picker_widget, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    # click to show the datetime picker container
    datetime_value = page.locator('.flatpickr-input')
    datetime_value.dblclick()

    _, num_days, _, _ = march_2021
    # num disabled days
    disabled_days = page.locator('.flatpickr-calendar .flatpickr-day.flatpickr-disabled')
    expect(disabled_days).to_have_count(num_days - len(enabled_list))

    # enable all days
    datetime_picker_widget.enabled_dates = None
    disabled_days = page.locator('.flatpickr-calendar .flatpickr-day.flatpickr-disabled')
    expect(disabled_days).to_have_count(0)


def test_datetimepicker_enable_time(page, port):
    datetime_picker_widget = DatetimePicker(enable_time=False)
    serve(datetime_picker_widget, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    # click to show the datetime picker container
    datetime_value = page.locator('.flatpickr-input')
    datetime_value.dblclick()

    # no time editor
    time_editor = page.locator('.flatpickr-calendar .flatpickr-time.time24hr.hasSeconds')
    expect(time_editor).to_have_count(0)


def test_datetimepicker_enable_seconds(page, port):
    datetime_picker_widget = DatetimePicker(enable_seconds=False)
    serve(datetime_picker_widget, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    # click to show the datetime picker container
    datetime_value = page.locator('.flatpickr-input')
    datetime_value.dblclick()

    # no seconds in time editor
    time_editor_with_sec = page.locator('.flatpickr-calendar .flatpickr-time.time24hr.hasSeconds')
    expect(time_editor_with_sec).to_have_count(0)

    # time editor
    time_editor_with_sec = page.locator('.flatpickr-calendar .flatpickr-time.time24hr')
    expect(time_editor_with_sec).to_have_count(1)

    time_inputs = page.locator('.flatpickr-calendar .flatpickr-time .numInputWrapper')
    time_up_buttons = page.locator('.flatpickr-calendar .flatpickr-time .arrowUp')
    time_down_buttons = page.locator('.flatpickr-calendar .flatpickr-time .arrowDown')
    # 2 inputs and up/down buttons for hour, min, no sec
    expect(time_inputs).to_have_count(2)
    expect(time_up_buttons).to_have_count(2)
    expect(time_down_buttons).to_have_count(2)
    # 1 separator `:` hour:min
    time_separators = page.locator('.flatpickr-calendar .flatpickr-time .flatpickr-time-separator')
    expect(time_separators).to_have_count(1)


def test_datetimepicker_military_time(page, port):
    datetime_picker_widget = DatetimePicker(military_time=False)
    serve(datetime_picker_widget, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    # click to show the datetime picker container
    datetime_value = page.locator('.flatpickr-input')
    datetime_value.dblclick()

    # no 24h format in time editor
    time_editor_with_sec = page.locator('.flatpickr-calendar .flatpickr-time.time24hr.hasSeconds')
    expect(time_editor_with_sec).to_have_count(0)

    # time editor
    time_editor_with_sec = page.locator('.flatpickr-calendar .flatpickr-time.hasSeconds')
    expect(time_editor_with_sec).to_have_count(1)

    time_inputs = page.locator('.flatpickr-calendar .flatpickr-time .numInputWrapper')
    time_am_pm = page.locator('.flatpickr-calendar .flatpickr-time .flatpickr-am-pm')
    time_up_buttons = page.locator('.flatpickr-calendar .flatpickr-time .arrowUp')
    time_down_buttons = page.locator('.flatpickr-calendar .flatpickr-time .arrowDown')
    # 3 inputs and up/down buttons for hour, min, sec
    expect(time_inputs).to_have_count(3)
    expect(time_up_buttons).to_have_count(3)
    expect(time_down_buttons).to_have_count(3)
    # 1 am-pm toggle
    expect(time_am_pm).to_have_count(1)
    # 2 separators `:` hour:min:sec
    time_separators = page.locator('.flatpickr-calendar .flatpickr-time .flatpickr-time-separator')
    expect(time_separators).to_have_count(2)

    hour_input = page.locator('.flatpickr-calendar .flatpickr-time .numInput.flatpickr-hour')
    hour_up = time_up_buttons.nth(0)
    hour_down = time_down_buttons.nth(0)

    hour_before_click = hour_input.input_value()
    # click down arrow button to decrease hour
    hour_down.click()
    hour_after_click = hour_input.input_value()
    # check data are updated in 12h format
    assert valid_prev_time(hour_before_click, hour_after_click, max_value=13, amount=1)

    # click up arrow button to increase hour
    hour_before_click = hour_input.input_value()
    hour_up.click()
    hour_after_click = hour_input.input_value()
    # check data are updated in 12h format
    assert valid_next_time(hour_before_click, hour_after_click, max_value=13, amount=1)


def test_datetimepicker_disable_editing(page, port):
    datetime_picker_widget = DatetimePicker(disabled=True)
    serve(datetime_picker_widget, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")
    expect(page.locator('.flatpickr-input')).to_have_attribute('disabled', 'true')


def test_datetimepicker_visible(page, port):
    # add css class to search for name more easily
    datetime_picker_widget = DatetimePicker(
        visible=False, css_classes=['invisible-datetimepicker']
    )
    serve(datetime_picker_widget, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    expect(page.locator('.invisible-datetimepicker')).to_have_css('display', 'none')


def test_datetimepicker_name(page, port):
    name = 'Datetime Picker'
    # add css class to search for name more easily
    datetime_picker_widget = DatetimePicker(
        name=name, css_classes=['datetimepicker-with-name']
    )
    serve(datetime_picker_widget, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    expect(page.locator('.datetimepicker-with-name > .bk-input-group > label')).to_have_text(name)

def test_datetimepicker_no_value(page, port, datetime_start_end):
    datetime_picker_widget = DatetimePicker()

    serve(datetime_picker_widget, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    datetime_picker = page.locator('.flatpickr-input')
    assert datetime_picker.input_value() == ""

    datetime_picker_widget.value = datetime_start_end[0]
    wait_until(lambda: datetime_picker.input_value() == '2021-03-02 00:00:00', page)

    datetime_picker_widget.value = None
    wait_until(lambda: datetime_picker.input_value() == '', page)


def test_datetimerangepicker_no_value(page, port, datetime_start_end):
    datetime_picker_widget = DatetimeRangePicker()

    serve(datetime_picker_widget, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    datetime_picker = page.locator('.flatpickr-input')
    assert datetime_picker.input_value() == ""

    datetime_picker_widget.value = datetime_start_end[:2]
    expected = '2021-03-02 00:00:00 to 2021-03-03 00:00:00'
    wait_until(lambda: datetime_picker.input_value() == expected, page)

    datetime_picker_widget.value = None
    wait_until(lambda: datetime_picker.input_value() == '', page)


def test_datetimepicker_remove_value(page, port, datetime_start_end):
    datetime_picker_widget = DatetimePicker(value=datetime_start_end[0])

    serve(datetime_picker_widget, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    datetime_picker = page.locator('.flatpickr-input')
    assert datetime_picker.input_value() == "2021-03-02 00:00:00"

    # Remove values from the browser
    datetime_picker.dblclick()
    datetime_picker.press("Backspace")
    datetime_picker.press("Escape")

    wait_until(lambda: datetime_picker_widget.value is None, page)
