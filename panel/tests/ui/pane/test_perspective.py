import pandas as pd
import pytest

from panel.pane import Perspective
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui

@pytest.fixture
def perspective_data():
    data = {
        "A": [0.0, 1.0, 2.0, 3.0, 4.0],
        "B": [0.0, 1.0, 0.0, 1.0, 0.0],
        "C": ["foo1", "foo2", "foo3", "foo4", "foo5"],
        "D": pd.bdate_range("1/1/2009", periods=5),
    }
    return pd.DataFrame(data)

def test_perspective_no_console_errors(page, perspective_data):
    perspective = Perspective(perspective_data)

    msgs, _ = serve_component(page, perspective)

    page.wait_for_timeout(1000)

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []


def test_perspective_no_console_errors_with_nested_path(page, perspective_data):
    perspective = Perspective(perspective_data)

    msgs, _ = serve_component(page, {'/foo/perspective': perspective}, suffix='/foo/perspective')

    page.wait_for_timeout(1000)

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []


def test_perspective_click_event(page, perspective_data):
    perspective = Perspective(perspective_data)

    events = []
    perspective.on_click(lambda e: events.append(e))

    serve_component(page, perspective)

    page.locator('.pnx-perspective-viewer').locator('tr').nth(4).locator('td').nth(3).click(force=True)

    wait_until(lambda: len(events) == 1, page)

    event = events[0]

    assert event.config == {'filter': []}
    assert event.column_names == ['C']
    assert event.row == {'index': 2, 'A': 2, 'B': 0, 'C': 'foo3', 'D': 1231113600000}
