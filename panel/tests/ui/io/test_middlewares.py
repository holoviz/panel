import time

import pytest

pytestmark = pytest.mark.ui

import panel as pn

from panel.io.middlewares import BokehEventMiddleware
from panel.tests.util import serve_component, wait_until
from panel.widgets import Button

try:
    from playwright.sync_api import expect
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')


def test_middlware(page):
    class TimingMiddleware(BokehEventMiddleware):
        def preprocess(self, syncable, doc, event):
            self.start_time = time.time()
        def postprocess(self):
            self.process_time = time.time() - self.start_time
    timing_middleware = TimingMiddleware()
    pn.state.add_bokeh_event_middleware(timing_middleware)

    button = Button(name='Button')
    events = []
    def cb(event):
        time_to_sleep = 2
        time.sleep(time_to_sleep)
        events.append(event)
        button.name = str(time_to_sleep)
    button.on_click(cb)

    serve_component(page, button)

    page.click('.bk-btn')

    wait_until(lambda: len(events) == 1, page)

    btn = page.locator('.bk-btn')
    expect(btn).to_have_count(1)
    expect(btn).to_contain_text(str(int(timing_middleware.process_time)))
