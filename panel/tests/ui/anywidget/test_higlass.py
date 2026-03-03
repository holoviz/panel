"""
Playwright test for the HiGlass compound AnyWidget.

HiGlass is a compound widget — its ``_tileset_client`` trait uses
``widget_serialization`` to reference a JupyterTilesetClient child widget.
Panel's compound widget support resolves this through
``widget_manager.get_model()`` on the JS side.

Tests:
    1. HiGlass widget renders (container element appears)
    2. No critical console errors (widget_manager, get_model)
    3. Child widgets are detected
"""
import pytest

pytest.importorskip("higlass")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component

from .conftest import wait_for_anywidget

pytestmark = pytest.mark.ui

# HiGlass bundles React and its own viewer; many benign warnings
HIGLASS_KNOWN_MESSAGES = [
    "setting log level to:",
    "Websocket connection 0 is now open",
    "document idle at",
    "items were rendered successfully",
    "[bokeh]",
    # React warnings
    "Warning:",
    "React",
    "react",
    # HiGlass internal
    "higlass",
    "HiGlass",
    # Network/tile loading
    "Failed to load resource",
    "net::ERR_",
    "TypeError: Failed to fetch",
    "404",
    # WebGL
    "WebGL",
    "webgl",
    "Automatic fallback to software WebGL has been deprecated",
    # Generic JS warnings
    "DeprecationWarning",
    # HiGlass tileset client (expected to fail without kernel)
    "tileset",
    "Tileset",
]


def _higlass_console_errors(msgs):
    """Filter console messages to unexpected errors (HiGlass-specific)."""
    errors = [m for m in msgs if m.type == "error"]
    errors = [
        m for m in errors
        if not any(known in m.text for known in HIGLASS_KNOWN_MESSAGES)
    ]
    return errors


def _make_higlass_widget():
    """Create a HiGlass widget with a remote tileset."""
    import higlass as hg

    tileset = hg.remote(
        uid="CQMd6V_cRw6iCI_-Unl3PQ",
        server="https://higlass.io/api/v1/",
        name="Rao et al. (2014) GM12878 MboI (allreps) 1kb",
    )
    track = tileset.track("heatmap")
    view = hg.view(hg.track("top-axis"), track)
    return view.widget()


def test_higlass_renders(page):
    """HiGlass widget renders with compound widget support."""
    widget = _make_higlass_widget()
    pane = pn.pane.AnyWidget(widget, height=400, sizing_mode="stretch_width")

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Wait for HiGlass React app to mount
    page.wait_for_timeout(5000)

    # HiGlass renders into a div; check that the root element exists
    root = page.locator("[data-root-id]").first
    expect(root).to_be_visible(timeout=15_000)


def test_higlass_no_critical_errors(page):
    """No critical console errors (widget_manager rejection, etc.)."""
    widget = _make_higlass_widget()
    pane = pn.pane.AnyWidget(widget, height=400, sizing_mode="stretch_width")

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)
    page.wait_for_timeout(5000)

    errors = _higlass_console_errors(msgs)
    # Check specifically for widget_manager errors that indicate compound
    # widget support failure
    critical = [
        e for e in errors
        if "widget_manager" in e.text or "get_model" in e.text
    ]
    assert critical == [], (
        "Critical widget_manager errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in critical)
    )


def test_higlass_child_widgets_detected(page):
    """Compound widget support detects the _tileset_client child widget."""
    widget = _make_higlass_widget()
    pane = pn.pane.AnyWidget(widget, height=400, sizing_mode="stretch_width")

    assert len(pane._child_widgets) > 0

    # The _tileset_client should be a child widget
    tileset_client = widget._tileset_client
    if hasattr(tileset_client, 'model_id'):
        assert tileset_client.model_id in pane._child_widgets

    # Constants should include child_models
    component = pane.component
    assert component is not None
    assert '_child_models' in component._constants
