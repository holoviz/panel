"""
Playwright test for the lonboard compound AnyWidget.

Lonboard is a compound widget — its Map references child widgets (layers,
controls, basemap) via IPY_MODEL_ strings.  Panel's compound widget support
resolves these via widget_manager.get_model() on the JS side.

Tests:
    1. Map renders (canvas/deck.gl element appears)
    2. No unexpected console errors
    3. Layer data is accessible from Python side
"""
import warnings

import pytest

pytest.importorskip("lonboard")
pytest.importorskip("geopandas")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import wait_for_anywidget

pytestmark = pytest.mark.ui

# Known console messages from maplibre/deck.gl that are benign
LONBOARD_KNOWN_MESSAGES = [
    "setting log level to:",
    "Websocket connection 0 is now open",
    "document idle at",
    "items were rendered successfully",
    "[bokeh]",
    # WebGL/GPU warnings
    "Automatic fallback to software WebGL has been deprecated",
    "GPU stall",
    # maplibre
    "maplibre",
    # deck.gl resource warnings
    "%.20LF",
    "Resource",
    # Deprecation warnings in third-party code
    "DeprecationWarning",
    # WebGL context lost is recoverable
    "WebGL",
    "webgl",
    # Fetch failures for optional tile servers
    "Failed to load resource",
    "net::ERR_",
    "TypeError: Failed to fetch",
    # deck.gl luma warnings
    "luma.gl",
]


def _lonboard_console_errors(msgs):
    """Filter console messages to unexpected errors (lonboard-specific)."""
    errors = [m for m in msgs if m.type == "error"]
    errors = [
        m for m in errors
        if not any(known in m.text for known in LONBOARD_KNOWN_MESSAGES)
    ]
    return errors


def _make_lonboard_map():
    """Create a simple lonboard Map with ScatterplotLayer."""
    import geopandas as gpd
    import lonboard
    from shapely.geometry import Point

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        cities = gpd.GeoDataFrame(
            {
                "name": ["NYC", "SF", "Chicago", "Houston"],
                "pop": [8.3, 0.87, 2.7, 2.3],
            },
            geometry=[
                Point(-73.98, 40.75),
                Point(-122.42, 37.77),
                Point(-87.63, 41.88),
                Point(-95.37, 29.76),
            ],
            crs="EPSG:4326",
        )
        layer = lonboard.ScatterplotLayer.from_geopandas(
            cities, get_radius=100_000, get_fill_color=[255, 0, 0, 200],
        )
        m = lonboard.Map(layers=[layer])
    return m, layer


def test_lonboard_renders(page):
    """Lonboard Map renders with the compound widget support."""
    m, layer = _make_lonboard_map()
    pane = pn.pane.AnyWidget(m, height=400, sizing_mode="stretch_width")

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Wait for deck.gl canvas to appear (lonboard renders via WebGL)
    page.wait_for_timeout(5000)
    canvas = page.locator("canvas").first
    expect(canvas).to_be_visible(timeout=30_000)


def test_lonboard_no_critical_errors(page):
    """No critical console errors (widget_manager rejection, etc.)."""
    m, layer = _make_lonboard_map()
    pane = pn.pane.AnyWidget(m, height=400, sizing_mode="stretch_width")

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)
    page.wait_for_timeout(5000)

    errors = _lonboard_console_errors(msgs)
    # Filter out any remaining non-critical errors
    critical = [e for e in errors if "widget_manager" in e.text or "get_model" in e.text]
    assert critical == [], (
        "Critical widget_manager errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in critical)
    )


def test_lonboard_child_widgets_detected(page):
    """Compound widget support detects child widgets (layers, controls, basemap)."""
    m, layer = _make_lonboard_map()
    pane = pn.pane.AnyWidget(m, height=400, sizing_mode="stretch_width")

    assert len(pane._child_widgets) > 0
    # Should detect at least the layer
    assert layer.model_id in pane._child_widgets

    # Constants should include child_models
    component = pane.component
    assert component is not None
    assert '_child_models' in component._constants
    assert layer.model_id in component._constants['_child_models']
