import pandas as pd
import pytest

from panel.pane import Perspective
from panel.tests.util import serve_component, wait_until


pytestmark = pytest.mark.ui

def test_perspective_no_console_errors(page, port):
    perspective = Perspective(pd._testing.makeMixedDataFrame())

    msgs = serve_component(page, port, perspective)

    page.wait_for_timeout(1000)

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []


def test_perspective_click_event(page, port):
    events = []
    perspective = Perspective(pd._testing.makeMixedDataFrame())
    perspective.on_click(lambda e: events.append(e))

    serve(perspective, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    page.locator('tr').nth(3).click()

    wait_until(lambda: len(events) == 1, page)

    event = events[0]

    assert event.config == {'filter': []}
    assert event.column_names == ['C']
    assert event.row == {'index': 2, 'A': 2, 'B': 0, 'C': 'foo3', 'D': 1231113600000}
