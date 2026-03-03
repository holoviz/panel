"""
Playwright test for the Altair JupyterChart anywidget example.

Tests:
    1. Widget renders (Vega-Lite chart appears with SVG/canvas content)
    2. No unexpected console errors
    3. Python -> Browser sync (change spec via component, chart updates)
    4. Browser -> Python sync (brush selection syncs _vl_selections)
"""
import pytest

alt = pytest.importorskip("altair")
pytest.importorskip("vega_datasets")
pytest.importorskip("playwright")

from playwright.sync_api import expect
from vega_datasets import data as vega_data

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_chart(x="Horsepower", y="Miles_per_Gallon"):
    """Build an Altair chart with brush selection."""
    source = vega_data.cars()
    brush = alt.selection_interval()
    chart = (
        alt.Chart(source)
        .mark_circle(size=60)
        .encode(
            x=alt.X(f"{x}:Q"),
            y=alt.Y(f"{y}:Q"),
            color=alt.condition(brush, "Origin:N", alt.value("lightgray")),
        )
        .properties(width=400, height=300)
        .add_params(brush)
    )
    return chart


def _wait_for_vega(page, timeout=30_000):
    """Wait for the Vega-Lite chart to appear in the DOM."""
    # Vega renders into a <canvas> or <svg> inside a div.vega-embed
    page.wait_for_selector("canvas, svg.marks", timeout=timeout)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_altair_renders(page):
    """JupyterChart renders and shows visible chart content."""
    chart = _make_chart()
    jupyter_chart = alt.JupyterChart(chart)
    pane = pn.pane.AnyWidget(jupyter_chart)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)
    _wait_for_vega(page)

    # The chart should produce either a canvas or SVG marks element
    chart_el = page.locator("canvas, svg.marks").first
    expect(chart_el).to_be_visible()

    assert_no_console_errors(msgs)


def test_altair_python_to_browser(page):
    """Changing the spec from Python updates the chart in the browser."""
    chart = _make_chart(x="Horsepower", y="Miles_per_Gallon")
    jupyter_chart = alt.JupyterChart(chart)
    pane = pn.pane.AnyWidget(jupyter_chart)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)
    _wait_for_vega(page)

    # The initial chart should be visible
    chart_el = page.locator("canvas, svg.marks").first
    expect(chart_el).to_be_visible()

    # Change the spec from Python (different axes)
    new_chart = _make_chart(x="Weight_in_lbs", y="Acceleration")
    pane.component.spec = new_chart.to_dict()

    # Wait for the new chart to render — the vega embed div should still exist
    page.wait_for_timeout(2000)
    chart_el = page.locator("canvas, svg.marks").first
    expect(chart_el).to_be_visible()

    assert_no_console_errors(msgs)


def test_altair_brush_selection_syncs(page):
    """Brush-selecting points on the chart syncs _vl_selections back to Python."""
    chart = _make_chart()
    jupyter_chart = alt.JupyterChart(chart)
    pane = pn.pane.AnyWidget(jupyter_chart)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)
    _wait_for_vega(page)

    # _vl_selections starts with an empty-valued selection entry
    # e.g. {'param_xxx': {'store': [], 'value': {}}}
    component = pane.component
    initial_selections = component._vl_selections or {}

    # Find the selection key(s) — should have one for the brush param
    def _selection_has_data(sel):
        """Check if any selection entry has a non-empty 'value' dict."""
        if not sel or not isinstance(sel, dict):
            return False
        for key, entry in sel.items():
            if isinstance(entry, dict):
                value = entry.get("value", {})
                if isinstance(value, dict) and len(value) > 0:
                    return True
        return False

    assert not _selection_has_data(initial_selections), (
        f"Expected empty selections initially, got: {initial_selections}"
    )

    # Perform a brush selection by dragging on the chart canvas
    chart_el = page.locator("canvas, svg.marks").first
    box = chart_el.bounding_box()
    assert box is not None, "Chart element has no bounding box"

    # Drag from ~25% to ~75% of the chart to create a brush selection
    start_x = box["x"] + box["width"] * 0.25
    start_y = box["y"] + box["height"] * 0.25
    end_x = box["x"] + box["width"] * 0.75
    end_y = box["y"] + box["height"] * 0.75

    page.mouse.move(start_x, start_y)
    page.mouse.down()
    page.mouse.move(end_x, end_y, steps=10)
    page.mouse.up()

    # Wait for the selection to contain non-empty value data
    wait_until(lambda: _selection_has_data(component._vl_selections), page, timeout=10000)

    assert isinstance(component._vl_selections, dict)
    assert _selection_has_data(component._vl_selections)

    assert_no_console_errors(msgs)
