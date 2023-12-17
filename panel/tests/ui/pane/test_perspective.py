import pandas as pd
import pytest

from panel.pane import Perspective
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui

def test_perspective_no_console_errors(page):
    perspective = Perspective(pd._testing.makeMixedDataFrame())

    msgs, _ = serve_component(page, perspective)

    page.wait_for_timeout(1000)

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []


def test_perspective_click_event(page):
    events = []
    perspective = Perspective(pd._testing.makeMixedDataFrame())
    perspective.on_click(lambda e: events.append(e))

    serve_component(page, perspective)

    page.locator('tr').nth(3).click()

    wait_until(lambda: len(events) == 1, page)

    event = events[0]

    assert event.config == {'filter': []}
    assert event.column_names == ['C']
    assert event.row == {'index': 2, 'A': 2, 'B': 0, 'C': 'foo3', 'D': 1231113600000}
