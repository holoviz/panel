from datetime import date

import pytest

pytest.importorskip("playwright")

from panel.tests.util import serve_component
from panel.widgets import Calendar

pytestmark = pytest.mark.ui


def test_calendar_current_date_view(page):
    calendar = Calendar(current_date="2020-01-01", current_view="timeGridDay")
    serve_component(page, calendar)

    assert page.locator(".fc-toolbar-title").first.inner_text() == "January 1, 2020"
    assert (
        page.locator(".fc-timeGridDay-button").first.get_attribute("class").split()[-1]
        == "fc-button-active"
    )


def test_calendar_change_view(page):
    calendar = Calendar(current_date="2020-01-01")
    serve_component(page, calendar)

    assert calendar.current_view == "dayGridMonth"
    assert (
        page.locator(".fc-dayGridMonth-button").first.get_attribute("class").split()[-1]
        == "fc-button-active"
    )

    calendar.change_view("timeGridDay")
    assert (
        page.locator(".fc-timeGridDay-button").first.get_attribute("class").split()[-1]
        == "fc-button-active"
    )
    assert calendar.current_view == "timeGridDay"


def test_calendar_go_to_date(page):
    calendar = Calendar(current_date="2020-01-01", current_view="timeGridDay")
    serve_component(page, calendar)

    assert calendar.current_date == "2020-01-01"
    assert page.locator(".fc-toolbar-title").first.inner_text() == "January 1, 2020"

    calendar.go_to_date("2021-01-01")
    assert calendar.current_date == "2020-01-01T08:00:00.000Z"
    assert page.locator(".fc-toolbar-title").first.inner_text() == "January 1, 2021"


def test_calendar_click_next(page):
    calendar = Calendar(current_date="2020-01-01", current_view="dayGridMonth")
    serve_component(page, calendar)

    assert page.locator(".fc-toolbar-title").first.inner_text() == "January 2020"

    calendar.click_next()
    assert page.locator(".fc-toolbar-title").first.inner_text() == "February 2020"


def test_calendar_click_prev(page):
    calendar = Calendar(current_date="2020-01-01", current_view="dayGridMonth")
    serve_component(page, calendar)

    assert page.locator(".fc-toolbar-title").first.inner_text() == "January 2020"

    calendar.click_prev()
    assert page.locator(".fc-toolbar-title").first.inner_text() == "December 2019"


def test_calendar_click_next_year(page):
    calendar = Calendar(current_date="2020-01-01", current_view="dayGridMonth")
    serve_component(page, calendar)

    assert page.locator(".fc-toolbar-title").first.inner_text() == "January 2020"

    calendar.click_next_year()
    assert page.locator(".fc-toolbar-title").first.inner_text() == "January 2021"


def test_calendar_click_prev_year(page):
    calendar = Calendar(current_date="2020-01-01", current_view="dayGridMonth")
    serve_component(page, calendar)

    assert page.locator(".fc-toolbar-title").first.inner_text() == "January 2020"

    calendar.click_prev_year()
    assert page.locator(".fc-toolbar-title").first.inner_text() == "January 2019"


def test_calendar_click_today(page):
    calendar = Calendar(current_date="2020-01-01", current_view="dayGridMonth")
    serve_component(page, calendar)

    assert page.locator(".fc-toolbar-title").first.inner_text() == "January 2020"

    calendar.click_today()
    today = date.today().strftime("%B %Y")
    assert page.locator(".fc-toolbar-title").first.inner_text() == today


def test_calendar_scroll_to_time(page):
    calendar = Calendar(current_date="2020-01-01", current_view="timeGridDay")
    serve_component(page, calendar)

    assert page.locator(".fc-toolbar-title").first.inner_text() == "January 1, 2020"

    calendar.scroll_to_time("18:00:00")

    found_in_viewport = False
    for label in page.locator(".fc-timegrid-slot-label").all():
        if label.inner_text() == "6pm":
            box = label.bounding_box()
            if box and box['y'] >= 0:
                found_in_viewport = True
                break
    assert found_in_viewport
