"""
Playwright test for the vizarr anywidget example.

vizarr is a minimal, client-side viewer for zarr-based images. It uses
the Viv library for GPU-accelerated rendering. The viewer loads ESM
and may fetch remote zarr stores over the network.

Key trait note: vizarr's ``height`` trait (Unicode, e.g. "600px") collides
with Panel's integer ``height`` param and is renamed to ``w_height``.

Tests:
    1. Widget renders (Bokeh root attached to DOM)
    2. Component has expected params (view_state, w_height)
    3. Python -> browser sync (change w_height from Python)
"""
import pytest

pytest.importorskip("vizarr")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui

# vizarr known console errors — CDN/network/WebGL issues
_VIZARR_KNOWN_ERRORS = [
    "Failed to load resource",
    "net::ERR",
    "TypeError: Failed to fetch",
    "CORS",
    "WebGL",
    "getContext",
    "gl.getParameter",
    "Error rendering Bokeh items",
    "SyntaxError",
    "404",
    "ResizeObserver",
    "zarr",
    "embassy.ebi.ac.uk",
    "viv",
    # MUI / material-ui warnings from vizarr's layer controls
    "MUI",
    "material",
    "findDOMNode",
]


def _filter_vizarr_errors(msgs):
    """Filter console errors, allowing known vizarr/network upstream issues."""
    errors = console_errors(msgs)
    errors = [
        e for e in errors
        if not any(known.lower() in e.text.lower() for known in _VIZARR_KNOWN_ERRORS)
    ]
    return errors


def _make_vizarr_widget():
    """Create a minimal vizarr Viewer without loading remote data."""
    import vizarr
    return vizarr.Viewer(height="500px")


def _make_pane():
    """Create a Panel AnyWidget pane wrapping a vizarr Viewer."""
    widget = _make_vizarr_widget()
    pane = pn.pane.AnyWidget(widget, sizing_mode="stretch_width")
    component = pane.component
    component.height = 500
    component.sizing_mode = "stretch_width"
    return pane, widget


def test_vizarr_renders(page):
    """vizarr widget loads and Bokeh root is attached to DOM.

    Note: We create a viewer without loading remote zarr data to avoid
    network dependencies. The viewer should still render its empty canvas.
    """
    pane, widget = _make_pane()

    msgs, _ = serve_component(page, pane)

    page.wait_for_load_state("networkidle", timeout=30_000)
    page.wait_for_timeout(3000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=15_000)

    unexpected = _filter_vizarr_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors (excluding known vizarr/network issues):\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_vizarr_component_has_expected_params(page):
    """The wrapped component exposes view_state and w_height params."""
    pane, widget = _make_pane()

    msgs, _ = serve_component(page, pane)

    component = pane.component

    # height is renamed to w_height due to collision with Layoutable
    assert hasattr(component, 'w_height'), "component should have w_height param (renamed from height)"
    assert component.w_height == "500px"

    # view_state should be present (dict)
    assert hasattr(component, 'view_state'), "component should have view_state param"

    # Verify the trait_name_map includes the renamed height
    name_map = pane.trait_name_map
    assert name_map.get("height") == "w_height", f"height should map to w_height, got {name_map}"

    unexpected = _filter_vizarr_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_vizarr_python_changes_w_height(page):
    """Changing w_height from Python updates the widget (Python -> browser sync)."""
    pane, widget = _make_pane()

    msgs, _ = serve_component(page, pane)

    page.wait_for_load_state("networkidle", timeout=30_000)
    page.wait_for_timeout(3000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=15_000)

    # Change w_height from Python side
    component = pane.component
    component.w_height = "700px"

    # Verify the traitlet value synced back to the underlying widget
    wait_until(lambda: widget.height == "700px", page, timeout=10_000)
    assert widget.height == "700px"

    # Also verify the component reflects the new value
    assert component.w_height == "700px"

    unexpected = _filter_vizarr_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )
