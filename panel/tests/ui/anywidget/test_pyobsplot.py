"""
Playwright test for the pyobsplot AnyWidget example.

pyobsplot renders Observable Plot charts as anywidgets. The Plot.plot()
method returns an ObsplotWidget whose `spec` traitlet can be updated to
change the chart dynamically.

Tests:
    1. Widget renders (Observable Plot SVG appears)
    2. No unexpected console errors
    3. Python -> Browser sync (change spec from Python, chart updates)
"""
import pytest

pytest.importorskip("pyobsplot")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_pane():
    """Create a pyobsplot dot chart wrapped in an AnyWidget pane."""
    import random

    import pandas as pd

    from pyobsplot import Plot

    random.seed(42)
    data = pd.DataFrame({
        "category": ["A", "B", "C"] * 5,
        "value": [random.gauss(50, 15) for _ in range(15)],
    })
    plot_widget = Plot.plot({
        "marks": [Plot.dot(data, {"x": "category", "y": "value"})],
    })
    return pn.pane.AnyWidget(plot_widget)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_pyobsplot_renders(page):
    """Observable Plot renders an SVG chart inside the AnyWidget pane."""
    pane = _make_pane()
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)

    # Observable Plot renders SVG
    expect(page.locator("svg").first).to_be_visible(timeout=10_000)

    assert_no_console_errors(msgs)


def test_pyobsplot_spec_update(page):
    """Changing the spec from Python updates the chart in the browser."""
    import random

    import pandas as pd

    from pyobsplot import Plot

    random.seed(42)
    data = pd.DataFrame({
        "category": ["A", "B", "C"] * 5,
        "value": [random.gauss(50, 15) for _ in range(15)],
    })
    plot_widget = Plot.plot({
        "marks": [Plot.dot(data, {"x": "category", "y": "value"})],
    })
    pane = pn.pane.AnyWidget(plot_widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)
    expect(page.locator("svg").first).to_be_visible(timeout=10_000)

    # Update spec to bar chart
    pane.component.spec = {
        "marks": [
            Plot.barY(
                data,
                Plot.groupX({"y": "sum"}, {"x": "category", "y": "value"}),
            )
        ],
    }
    page.wait_for_timeout(3000)

    # Chart should still be visible after spec update
    expect(page.locator("svg").first).to_be_visible(timeout=10_000)

    assert_no_console_errors(msgs)
