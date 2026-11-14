import time

import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.pane import panel
from panel.tests.util import serve_component

pytestmark = pytest.mark.ui


def test_param_defer_load(page):
    def defer_load():
        time.sleep(0.5)
        return 'I render after load!'

    component = panel(defer_load, defer_load=True)

    serve_component(page, component)

    assert page.locator(".pn-loading")

    expect(page.locator(".markdown").locator("div")).to_have_text('I render after load!\n')


def test_param_throttled_slider_repeated_exclusive_boundary(page):
    import param

    from panel import Param
    from panel.tests.util import wait_until

    class Test(param.Parameterized):
        value = param.Number(default=1, bounds=(0, 2), inclusive_bounds=(False, True))

    obj = Test()
    controls = Param(obj, widgets={'value': {'throttled': True}})
    serve_component(page, controls)
    handle = page.locator('.noUi-handle')
    expect(handle).to_be_visible()
    for _ in range(2):
        handle.hover()
        page.mouse.down()
        track = page.locator('.noUi-base').bounding_box()
        page.mouse.move(track['x'], track['y'] + track['height'] / 2, steps=5)
        page.mouse.up()
        wait_until(lambda: controls._widgets['value'].value == 1, page)
        assert obj.value == 1
        wait_until(lambda: float(handle.get_attribute('aria-valuenow')) == 1, page)


@pytest.mark.parametrize('parameter_type', ['DateRange', 'CalendarDateRange'])
def test_param_date_range_without_default(page, parameter_type):
    from datetime import date, datetime

    import param

    from panel import Param
    from panel.tests.util import wait_until

    class Test(param.Parameterized):
        value = getattr(param, parameter_type)(bounds=(date(2020, 1, 1), date(2020, 1, 5)))

    obj = Test()
    controls = Param(obj)
    serve_component(page, controls)
    handles = page.locator('.noUi-handle')
    expect(handles).to_have_count(2)
    expect(handles.first).to_be_visible()
    expect(handles.last).to_be_visible()
    assert obj.value is None
    expect(page.locator('.noUi-connect')).to_be_visible()
    handles.first.focus()
    page.keyboard.press('ArrowRight')
    selected = ((datetime(2020, 1, 1, 0, 1), datetime(2020, 1, 5))
                if parameter_type == 'DateRange' else (date(2020, 1, 2), date(2020, 1, 5)))
    wait_until(lambda: obj.value == selected, page)
