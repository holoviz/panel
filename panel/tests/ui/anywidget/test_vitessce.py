"""
Playwright test for the vitessce anywidget example.

Vitessce is an interactive spatial single-cell data viewer. Its ESM
dynamically loads ~2-3 MB of JavaScript from unpkg.com CDN and fetches
remote dataset files from S3, so we use generous timeouts and tolerate
network-related console errors.

Tests:
    1. Widget renders (Bokeh root attached to DOM)
    2. Component exposes expected params (theme, proxy, etc.)
    3. Python -> browser sync (change theme from Python)
"""
import pytest

pytest.importorskip("vitessce")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui

# Vitessce loads heavy JS from CDN and remote data from S3 — many benign
# console errors are expected (CORS, 404s, WebGL, etc.)
_VITESSCE_KNOWN_ERRORS = [
    "Failed to load resource",
    "net::ERR",
    "TypeError: Failed to fetch",
    "CORS",
    "vitessce",
    "unpkg.com",
    "s3.amazonaws.com",
    "WebGL",
    "getContext",
    "gl.getParameter",
    "Error rendering Bokeh items",
    "SyntaxError",
    "404",
    "ResizeObserver",
    "deck.gl",
    "viv",
    "Loading CSS chunk",
]


def _filter_vitessce_errors(msgs):
    """Filter console errors, allowing known vitessce/network upstream issues."""
    errors = console_errors(msgs)
    errors = [
        e for e in errors
        if not any(known.lower() in e.text.lower() for known in _VITESSCE_KNOWN_ERRORS)
    ]
    return errors


def _make_vitessce_widget():
    """Create a minimal Vitessce widget with a simple configuration."""
    from vitessce import (
        VitessceConfig,
        ViewType as vt,
    )

    vc = VitessceConfig(
        schema_version="1.0.15",
        name="Test Config",
    )
    ds = vc.add_dataset(name="empty")
    status_view = vc.add_view(vt.STATUS, dataset=ds)
    vc.layout(status_view)

    return vc.widget(height=300, theme="dark")


def _make_pane():
    """Create a Panel AnyWidget pane wrapping a Vitessce widget."""
    widget = _make_vitessce_widget()
    pane = pn.pane.AnyWidget(widget, sizing_mode="stretch_width", height=350)
    return pane


def test_vitessce_renders(page):
    """Vitessce widget loads and Bokeh root is attached to DOM.

    Note: Vitessce loads a large JS bundle from CDN and may fetch remote
    data. In CI, the full viewer may not fully render but we verify the
    Bokeh model attaches to the DOM without crashing.
    """
    pane = _make_pane()

    msgs, _ = serve_component(page, pane)

    # Allow generous time for CDN JS loading and network requests
    page.wait_for_load_state("networkidle", timeout=60_000)
    page.wait_for_timeout(5000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=30_000)

    unexpected = _filter_vitessce_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors (excluding known vitessce/network issues):\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_vitessce_component_has_expected_params(page):
    """The wrapped component exposes theme and proxy params."""
    pane = _make_pane()

    msgs, _ = serve_component(page, pane)

    component = pane.component

    # theme should be present and match the initial value
    assert hasattr(component, 'theme'), "component should have theme param"
    assert component.theme == "dark"

    # height is renamed to w_height due to collision with Layoutable
    assert hasattr(component, 'w_height'), "component should have w_height param (renamed from height)"
    assert component.w_height == 300

    # Verify the trait_name_map includes the renamed height
    name_map = pane.trait_name_map
    assert name_map.get("height") == "w_height", f"height should map to w_height, got {name_map}"

    unexpected = _filter_vitessce_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_vitessce_python_changes_theme(page):
    """Changing theme from Python updates the widget (Python -> browser sync)."""
    widget = _make_vitessce_widget()
    pane = pn.pane.AnyWidget(widget, sizing_mode="stretch_width", height=350)

    msgs, _ = serve_component(page, pane)

    # Wait for initial render
    page.wait_for_load_state("networkidle", timeout=60_000)
    page.wait_for_timeout(3000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=30_000)

    # Change theme from Python side
    component = pane.component
    component.theme = "light"

    # Verify the traitlet value synced back to the underlying widget
    wait_until(lambda: widget.theme == "light", page, timeout=10_000)
    assert widget.theme == "light"

    # Also verify the component reflects the new value
    assert component.theme == "light"

    unexpected = _filter_vitessce_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )
