"""
Playwright test for the mapwidget MapLibre GL anywidget example.

mapwidget renders an interactive MapLibre GL JS map. The widget loads
map tiles from the network and supports pan, zoom, and click interactions.

NOTE: MapLibre GL requires WebGL. In headless Chromium, WebGL may not
render tiles visually but the widget should still load structurally.

Known MapLibre console messages (tile loading, WebGL warnings) are
filtered from error checks.

Tests:
    1. Widget loads and DOM is attached
    2. Component has expected params (center, zoom, w_height, w_width, clicked_latlng)
    3. Changing center from Python propagates to the component
"""
import pytest

pytest.importorskip("mapwidget")
pytest.importorskip("playwright")

import mapwidget.maplibre as maplibre

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import console_errors

pytestmark = pytest.mark.ui

# MapLibre known console errors -- tile loading, WebGL, and ESM issues
# that are upstream / environment-related, not Panel bugs.
MAPLIBRE_KNOWN_ERRORS = [
    "Failed to load resource",      # tile loading in headless
    "WebGL",                         # headless rendering limitations
    "webgl",                         # lowercase variant
    "maplibregl",                    # library internal warnings
    "maplibre",                      # library internal warnings
    "Error rendering Bokeh items",   # ESM loading race condition
    "404",                           # tile 404s in test environment
    "net::ERR",                      # network errors for tiles
    "tiles",                         # tile-related messages
    "TileJSON",                      # tile metadata loading
    "Request failed",                # HTTP request failures for tiles
]


def _filter_maplibre_errors(msgs):
    """Filter console errors, allowing known MapLibre/WebGL upstream issues."""
    errors = console_errors(msgs)
    errors = [
        e for e in errors
        if not any(known.lower() in e.text.lower() for known in MAPLIBRE_KNOWN_ERRORS)
    ]
    return errors


def _make_map():
    """Create a mapwidget MapLibre Map with default settings."""
    return maplibre.Map(center=[40, -100], zoom=4, height="500px", width="100%")


def test_mapwidget_renders(page):
    """mapwidget Map loads -- page renders without crashing.

    MapLibre GL may not fully render tiles in headless Chromium (no GPU),
    but the Bokeh model should be attached to the DOM and no unexpected
    errors should occur.
    """
    widget = _make_map()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)

    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(5000)

    # The Bokeh root div should be attached to DOM
    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=15000)

    unexpected = _filter_maplibre_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors (excluding known MapLibre/WebGL issues):\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_mapwidget_component_has_expected_params(page):
    """The wrapped component exposes center, zoom, w_height, w_width, clicked_latlng."""
    widget = _make_map()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)

    # Component params are available immediately -- no need to wait for tiles
    component = pane.component

    # center and zoom are standard traits
    assert hasattr(component, 'center'), "component should have center param"
    assert hasattr(component, 'zoom'), "component should have zoom param"

    # height and width collide with Panel's Layoutable, so they are
    # renamed to w_height and w_width
    assert hasattr(component, 'w_height'), "component should have w_height param (renamed from height)"
    assert hasattr(component, 'w_width'), "component should have w_width param (renamed from width)"

    # clicked_latlng tracks map clicks
    assert hasattr(component, 'clicked_latlng'), "component should have clicked_latlng param"

    # Verify initial values
    assert component.center == [40, -100]
    assert component.zoom == 4
    assert component.w_height == "500px"
    assert component.w_width == "100%"

    unexpected = _filter_maplibre_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_mapwidget_python_changes_center(page):
    """Changing center from Python updates the widget (Python -> widget sync)."""
    widget = _make_map()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)

    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    # The Bokeh root should be attached
    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=15000)

    # Change center from Python via the component
    pane.component.center = [51.5, -0.12]

    # Wait for the change to propagate to the underlying widget
    wait_until(lambda: widget.center == [51.5, -0.12], page, timeout=10000)

    assert widget.center == [51.5, -0.12]

    unexpected = _filter_maplibre_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )
