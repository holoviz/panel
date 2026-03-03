"""
Playwright tests for the drawdata anywidget components.

drawdata exposes two anywidget components:
    - ScatterWidget : freehand scatter-draw canvas (multi-class point drawing)
    - BarWidget     : interactive bar chart editor

KNOWN UPSTREAM ISSUE: drawdata's ESM bundle has a ``circle_brush``
initialization error (``Cannot access 'circle_brush' before initialization``).
This is a drawdata library bug, not a Panel AnyWidget issue. We tolerate this
error in tests.

Tests:
    ScatterWidget:
        1. Widget renders (SVG canvas appears)
        2. Console errors are limited to known drawdata bugs
        3. Python -> Browser sync (change brushsize via component)
    BarWidget:
        4. Widget renders (SVG canvas appears)
        5. Console errors are limited to known drawdata bugs
        6. Python -> Browser sync (change n_bins via component)
        7. Python -> Browser sync (change y_max via component)
        8. Python -> Browser sync (change collection_names via component)
"""
import pytest

pytest.importorskip("drawdata")
pytest.importorskip("playwright")

from drawdata import BarWidget, ScatterWidget
from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui

# drawdata's known console error — upstream bug, not a Panel issue
DRAWDATA_KNOWN_ERRORS = [
    "circle_brush",
    "Cannot access",
    "Expected length",  # <svg> attribute height: Expected length, "auto"
]


def _filter_drawdata_errors(msgs):
    """Filter console errors, allowing known drawdata upstream bugs."""
    errors = console_errors(msgs)
    # Also filter out drawdata's circle_brush initialization error
    errors = [
        e for e in errors
        if not any(known in e.text for known in DRAWDATA_KNOWN_ERRORS)
    ]
    return errors


# ---------------------------------------------------------------------------
# ScatterWidget
# ---------------------------------------------------------------------------

def test_drawdata_scatter_renders(page):
    """ScatterWidget renders and shows an SVG drawing canvas."""
    widget = ScatterWidget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # drawdata renders an SVG element for the drawing canvas
    # Wait longer as the ESM bundle is large (~487KB)
    page.wait_for_timeout(3000)

    # The widget should produce some visible content
    root = page.locator("[data-root-id]").first
    expect(root).to_be_visible()

    # drawdata renders an SVG element for the canvas
    svg = page.locator("svg").first
    expect(svg).to_be_visible(timeout=10000)

    unexpected = _filter_drawdata_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors (excluding known drawdata bugs):\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_drawdata_scatter_python_to_browser_brushsize(page):
    """Changing brushsize from Python updates the widget's internal state."""
    widget = ScatterWidget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)
    page.wait_for_timeout(3000)

    component = pane.component

    # Initial brushsize
    initial = component.brushsize
    assert isinstance(initial, int)

    # Change brushsize from Python
    component.brushsize = 25

    # Verify the traitlet on the original widget is updated
    wait_until(lambda: widget.brushsize == 25, page)
    assert widget.brushsize == 25

    unexpected = _filter_drawdata_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


# ---------------------------------------------------------------------------
# BarWidget
# ---------------------------------------------------------------------------

def test_drawdata_bar_renders(page):
    """BarWidget renders and shows an SVG bar chart canvas."""
    widget = BarWidget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    page.wait_for_timeout(3000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_visible()

    # drawdata BarWidget also renders SVG content
    svg = page.locator("svg").first
    expect(svg).to_be_visible(timeout=15000)

    unexpected = _filter_drawdata_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors (excluding known drawdata bugs):\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_drawdata_bar_python_to_browser_n_bins(page):
    """Changing n_bins from Python updates the traitlet."""
    widget = BarWidget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)
    page.wait_for_timeout(3000)

    component = pane.component

    # Default n_bins is 24
    assert component.n_bins == 24

    component.n_bins = 10

    wait_until(lambda: widget.n_bins == 10, page)
    assert widget.n_bins == 10

    unexpected = _filter_drawdata_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_drawdata_bar_python_to_browser_y_max(page):
    """Changing y_max from Python updates the traitlet."""
    widget = BarWidget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)
    page.wait_for_timeout(3000)

    component = pane.component

    # Default y_max is 1.0
    assert component.y_max == 1.0

    component.y_max = 2.0

    wait_until(lambda: widget.y_max == 2.0, page)
    assert widget.y_max == 2.0

    unexpected = _filter_drawdata_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_drawdata_bar_python_to_browser_collection_names(page):
    """Changing collection_names from Python updates the traitlet."""
    widget = BarWidget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)
    page.wait_for_timeout(3000)

    component = pane.component

    # Default collection_names
    assert component.collection_names == ["collection1", "collection2"]

    component.collection_names = ["series_A", "series_B"]

    wait_until(lambda: widget.collection_names == ["series_A", "series_B"], page)
    assert widget.collection_names == ["series_A", "series_B"]

    unexpected = _filter_drawdata_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )
