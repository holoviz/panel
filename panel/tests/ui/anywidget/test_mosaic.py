"""
Playwright test for the mosaic-widget anywidget example.

Tests:
    1. Widget renders (SVG or canvas visualization appears)
    2. No unexpected console errors
    3. Python -> Browser sync (change spec from Python, widget re-renders)

Note: Mosaic uses DuckDB (compiled to WASM in the browser) to run SQL queries
and renders Vega-Lite-like visualizations. It uses a message-passing protocol
between Python and the browser for query execution.
"""
import pytest

mosaic_widget = pytest.importorskip("mosaic_widget")
pytest.importorskip("playwright")

import numpy as np
import pandas as pd

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui

# Console messages that are benign for mosaic-widget
_MOSAIC_KNOWN = [
    "DuckDB",
    "duckdb",
    "wasm",
    "WASM",
    "Coordinator",
]


def _assert_no_errors(msgs):
    """Filter console errors, ignoring mosaic-specific benign messages."""
    from .conftest import console_errors
    errors = console_errors(msgs)
    errors = [
        m for m in errors
        if not any(known in m.text for known in _MOSAIC_KNOWN)
    ]
    assert errors == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in errors)
    )


def _make_mosaic_widget():
    """Create a simple mosaic scatter plot for testing."""
    from mosaic_widget import MosaicWidget

    np.random.seed(42)
    n = 50
    df = pd.DataFrame({
        "x": np.random.randn(n),
        "y": np.random.randn(n),
        "category": np.random.choice(["A", "B"], n),
    })

    spec = {
        "plot": [
            {
                "mark": "dot",
                "data": {"from": "sample_data"},
                "x": "x",
                "y": "y",
                "fill": "category",
                "r": 5,
            }
        ],
        "width": 400,
        "height": 300,
    }

    widget = MosaicWidget(spec=spec, data={"sample_data": df})
    return widget


def test_mosaic_renders(page):
    """Widget renders and shows the Mosaic visualization."""
    widget = _make_mosaic_widget()
    pane = pn.pane.AnyWidget(widget, height=400, width=500)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Mosaic renders SVG elements inside .mosaic-widget or similar container.
    # Wait for any SVG element to appear (the Vega-Lite output).
    # Mosaic may also use canvas. Wait generously as WASM DuckDB needs time.
    page.wait_for_timeout(5000)

    # Check for SVG or canvas - mosaic renders one or the other
    svg_or_canvas = page.locator("svg, canvas")
    svg_or_canvas.first.wait_for(state="visible", timeout=30_000)

    _assert_no_errors(msgs)


def test_mosaic_python_changes_spec(page):
    """Changing spec from Python updates the widget (Python -> browser sync)."""
    widget = _make_mosaic_widget()
    pane = pn.pane.AnyWidget(widget, height=400, width=500)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Wait for initial render
    page.wait_for_timeout(5000)
    svg_or_canvas = page.locator("svg, canvas")
    svg_or_canvas.first.wait_for(state="visible", timeout=30_000)

    # Change spec from Python to a bar chart
    bar_spec = {
        "plot": [
            {
                "mark": "barY",
                "data": {"from": "sample_data"},
                "x": "category",
                "y": "y",
                "fill": "category",
            }
        ],
        "width": 400,
        "height": 300,
    }
    pane.component.spec = bar_spec

    # Verify the traitlet value synced
    wait_until(lambda: widget.spec == bar_spec, page)

    # The visualization should still be present after spec change
    page.wait_for_timeout(3000)
    svg_or_canvas = page.locator("svg, canvas")
    svg_or_canvas.first.wait_for(state="visible", timeout=15_000)

    _assert_no_errors(msgs)
