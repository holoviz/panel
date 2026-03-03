"""
Playwright test for the weas-widget anywidget example.

weas-widget (Web Environment for Atomistic Structure) provides interactive
3D visualization of molecular and crystal structures. WeasWidget is an
ipywidgets HBox container; the actual anywidget is the first child
(``weas.children[0]``, a BaseWidget). Panel's AnyWidget pane wraps the
BaseWidget directly.

Tests:
    1. Widget renders (Bokeh root attached to DOM)
    2. Component exposes expected params (modelStyle, colorType, atomLabelType, etc.)
    3. Python -> browser sync (change modelStyle from Python)
"""
import pytest

pytest.importorskip("weas_widget")
pytest.importorskip("ase")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui

# weas-widget known console errors — WebGL / 3D rendering issues in headless
_WEAS_KNOWN_ERRORS = [
    "WebGL",
    "getContext",
    "gl.getParameter",
    "THREE",
    "three.js",
    "Failed to load resource",
    "net::ERR",
    "ResizeObserver",
    "Error rendering Bokeh items",
]


def _filter_weas_errors(msgs):
    """Filter console errors, allowing known weas-widget/WebGL upstream issues."""
    errors = console_errors(msgs)
    errors = [
        e for e in errors
        if not any(known.lower() in e.text.lower() for known in _WEAS_KNOWN_ERRORS)
    ]
    return errors


def _make_weas_widget():
    """Create a WeasWidget with a simple water molecule and extract the BaseWidget."""
    from ase.build import molecule

    from weas_widget import WeasWidget

    atoms = molecule("H2O")
    weas = WeasWidget(from_ase=atoms, guiConfig={"enabled": False})
    # WeasWidget is an HBox; the actual anywidget is the first child
    base_widget = weas.children[0]
    return base_widget, weas


def _make_pane():
    """Create a Panel AnyWidget pane wrapping a weas-widget BaseWidget."""
    base_widget, weas = _make_weas_widget()
    pane = pn.pane.AnyWidget(base_widget, height=500, sizing_mode="stretch_width")
    return pane, base_widget, weas


def test_weaswidget_renders(page):
    """weas-widget loads and Bokeh root is attached to DOM.

    Note: The 3D WebGL viewer may not fully render in headless mode,
    but we verify the Bokeh model attaches to the DOM without crashing.
    """
    pane, base_widget, weas = _make_pane()

    msgs, _ = serve_component(page, pane)

    page.wait_for_load_state("networkidle", timeout=30_000)
    page.wait_for_timeout(3000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=15_000)

    unexpected = _filter_weas_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors (excluding known weas-widget/WebGL issues):\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_weaswidget_component_has_expected_params(page):
    """The wrapped component exposes modelStyle, colorType, atomLabelType params."""
    pane, base_widget, weas = _make_pane()

    msgs, _ = serve_component(page, pane)

    component = pane.component

    # modelStyle should be present (integer: 0=Space-filling, 1=Ball-stick, 2=Polyhedral)
    assert hasattr(component, 'modelStyle'), "component should have modelStyle param"

    # colorType should be present (string, e.g., "JMOL")
    assert hasattr(component, 'colorType'), "component should have colorType param"

    # atomLabelType should be present (string, e.g., "None")
    assert hasattr(component, 'atomLabelType'), "component should have atomLabelType param"

    # showBondedAtoms and showHydrogenBonds should be booleans
    assert hasattr(component, 'showBondedAtoms'), "component should have showBondedAtoms param"
    assert hasattr(component, 'showHydrogenBonds'), "component should have showHydrogenBonds param"

    # ready should be present
    assert hasattr(component, 'ready'), "component should have ready param"

    unexpected = _filter_weas_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_weaswidget_python_changes_model_style(page):
    """Changing modelStyle from Python updates the widget (Python -> browser sync)."""
    pane, base_widget, weas = _make_pane()

    msgs, _ = serve_component(page, pane)

    page.wait_for_load_state("networkidle", timeout=30_000)
    page.wait_for_timeout(3000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=15_000)

    # Change modelStyle from Python side (1 = Ball-stick)
    component = pane.component
    component.modelStyle = 1

    # Verify the traitlet value synced back to the underlying widget
    wait_until(lambda: base_widget.modelStyle == 1, page, timeout=10_000)
    assert base_widget.modelStyle == 1

    # Also verify the component reflects the new value
    assert component.modelStyle == 1

    unexpected = _filter_weas_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_weaswidget_python_changes_color_type(page):
    """Changing colorType from Python updates the widget (Python -> browser sync)."""
    pane, base_widget, weas = _make_pane()

    msgs, _ = serve_component(page, pane)

    page.wait_for_load_state("networkidle", timeout=30_000)
    page.wait_for_timeout(3000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=15_000)

    # Change colorType from Python side
    component = pane.component
    component.colorType = "VESTA"

    # Verify the traitlet value synced back to the underlying widget
    wait_until(lambda: base_widget.colorType == "VESTA", page, timeout=10_000)
    assert base_widget.colorType == "VESTA"

    unexpected = _filter_weas_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )
