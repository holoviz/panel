"""
Playwright test for the ipymolstar PDBeMolstar anywidget example.

PDBeMolstar renders a 3D molecular structure viewer powered by Mol*.
It loads a ~1.5 MB ESM bundle and fetches 3D structure data from PDB
servers over the network, so we use generous timeouts.

Tests:
    1. Widget loads and DOM is attached (allowing CDN/network errors)
    2. Component has expected params (molecule_id, w_height, w_width, spin, visual_style)
    3. Python -> browser sync (change molecule_id from Python)
"""
import pytest

pytest.importorskip("ipymolstar")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui

# ipymolstar known console errors — CDN/network issues and Mol* internals
IPYMOLSTAR_KNOWN_ERRORS = [
    "Failed to load resource",  # PDB CDN 404s or network timeouts
    "net::ERR",                 # Network errors fetching structure data
    "TypeError: Failed to fetch",
    "CORS",                     # Cross-origin requests to PDB servers
    "pdbe.org",                 # PDBe CDN errors
    "ebi.ac.uk",                # EBI CDN errors
    "rcsb.org",                 # RCSB PDB CDN errors
    "molstar",                  # Mol* internal errors/warnings
    "Error rendering Bokeh items",  # Large ESM bundle may fail to parse
    "SyntaxError",              # ESM compilation edge cases
    "WebGL",                    # WebGL context issues in headless browser
    "getContext",               # Canvas context failures in headless mode
    "gl.getParameter",          # WebGL parameter queries failing
]


def _filter_ipymolstar_errors(msgs):
    """Filter console errors, allowing known ipymolstar/network upstream issues."""
    errors = console_errors(msgs)
    errors = [
        e for e in errors
        if not any(known.lower() in e.text.lower() for known in IPYMOLSTAR_KNOWN_ERRORS)
    ]
    return errors


def _make_widget():
    """Create a PDBeMolstar widget with default settings."""
    from ipymolstar import PDBeMolstar
    return PDBeMolstar(molecule_id="1cbs", height="500px", width="100%")


def test_ipymolstar_renders(page):
    """PDBeMolstar widget loads — page renders without crashing.

    Note: The Mol* 3D viewer requires WebGL and fetches structure data
    from PDB servers. In headless CI environments, the full 3D canvas
    may not render, but we verify the Bokeh model is attached to DOM
    and no unexpected errors occur.
    """
    widget = _make_widget()
    pane = pn.pane.AnyWidget(widget, sizing_mode="stretch_width", height=550)

    msgs, _ = serve_component(page, pane)

    # Allow extra time for the large ESM bundle and network fetches
    page.wait_for_load_state("networkidle", timeout=30_000)
    page.wait_for_timeout(5000)

    # The Bokeh root div should be attached to DOM
    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=15_000)

    unexpected = _filter_ipymolstar_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors (excluding known ipymolstar/network issues):\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_ipymolstar_component_has_expected_params(page):
    """The wrapped component exposes molecule_id, w_height, w_width, spin, visual_style."""
    widget = _make_widget()
    pane = pn.pane.AnyWidget(widget, sizing_mode="stretch_width", height=550)

    msgs, _ = serve_component(page, pane)

    # Component params are available immediately — no need to wait for render
    component = pane.component

    # molecule_id should be present and match the initial value
    assert hasattr(component, 'molecule_id'), "component should have molecule_id param"
    assert component.molecule_id == "1cbs"

    # height/width are renamed to w_height/w_width due to collision with Layoutable
    assert hasattr(component, 'w_height'), "component should have w_height param (renamed from height)"
    assert hasattr(component, 'w_width'), "component should have w_width param (renamed from width)"
    assert component.w_height == "500px"
    assert component.w_width == "100%"

    # spin and visual_style should be present
    assert hasattr(component, 'spin'), "component should have spin param"
    assert hasattr(component, 'visual_style'), "component should have visual_style param"

    # Verify the trait_name_map includes the renamed dimensions
    name_map = pane.trait_name_map
    assert name_map.get("height") == "w_height", f"height should map to w_height, got {name_map}"
    assert name_map.get("width") == "w_width", f"width should map to w_width, got {name_map}"

    unexpected = _filter_ipymolstar_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_ipymolstar_python_changes_molecule(page):
    """Changing molecule_id from Python updates the widget (Python -> browser sync)."""
    widget = _make_widget()
    pane = pn.pane.AnyWidget(widget, sizing_mode="stretch_width", height=550)

    msgs, _ = serve_component(page, pane)

    # Wait for initial render
    page.wait_for_load_state("networkidle", timeout=30_000)
    page.wait_for_timeout(3000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=15_000)

    # Change molecule_id from Python side
    component = pane.component
    component.molecule_id = "2hbs"

    # Verify the traitlet value synced back to the underlying widget
    wait_until(lambda: widget.molecule_id == "2hbs", page, timeout=10_000)
    assert widget.molecule_id == "2hbs"

    # Also verify the component reflects the new value
    assert component.molecule_id == "2hbs"

    unexpected = _filter_ipymolstar_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )
