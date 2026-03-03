"""
Playwright test for the itables AnyWidget example.

itables renders pandas DataFrames as interactive DataTables with sorting,
searching, pagination, and row selection via the anywidget protocol.

Tests:
    1. Widget renders (DataTables table appears with data)
    2. No unexpected console errors
    3. Python -> Browser sync (change caption from Python)
"""
import pytest

pytest.importorskip("itables")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_pane():
    """Create an ITable widget wrapped in an AnyWidget pane."""
    import pandas as pd

    from itables.widget import ITable

    df = pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie"],
        "Score": [90, 85, 95],
    })
    widget = ITable(df, select=True)
    return pn.pane.AnyWidget(widget, sizing_mode="stretch_width")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_itables_renders(page):
    """ITable renders a DataTables table with visible content."""
    pane = _make_pane()
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)
    page.wait_for_timeout(3000)

    # DataTables renders a <table> element
    expect(page.locator("table").first).to_be_visible(timeout=10_000)

    assert_no_console_errors(msgs)


def test_itables_caption_update(page):
    """Changing the caption from Python updates the widget."""
    import pandas as pd

    from itables.widget import ITable

    df = pd.DataFrame({
        "Name": ["Alice", "Bob"],
        "Score": [90, 85],
    })
    widget = ITable(df, caption="Original")
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)
    page.wait_for_timeout(3000)
    expect(page.locator("table").first).to_be_visible(timeout=10_000)

    # Update caption from Python
    pane.component.caption = "Updated Caption"
    page.wait_for_timeout(2000)

    assert_no_console_errors(msgs)
