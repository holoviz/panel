"""
Playwright test for the ipyniivue anywidget example (WORKS WITH CAVEATS).

NiiVue renders a WebGL canvas. Scalar rendering params sync correctly, but
volume loading requires Jupyter's widget manager (IPY_MODEL_ references).

Tests:
    1. Widget loads (Bokeh root attached to DOM)
    2. Component has expected params (draw_opacity, w_height, overlay_alpha_shader)
    3. Python -> browser sync (change draw_opacity from Python)
"""
import pytest

pytest.importorskip("ipyniivue")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui

# NiiVue uses WebGL — known errors in headless
_NIIVUE_KNOWN_ERRORS = [
    "WebGL",
    "getContext",
    "gl.getParameter",
    "Failed to load resource",
    "net::ERR",
    "ResizeObserver",
    "Error rendering Bokeh items",
    "niivue",
]


def _filter_niivue_errors(msgs):
    errors = console_errors(msgs)
    return [
        e for e in errors
        if not any(known.lower() in e.text.lower() for known in _NIIVUE_KNOWN_ERRORS)
    ]


def _make_pane():
    from ipyniivue import NiiVue
    widget = NiiVue(height=300)
    return pn.pane.AnyWidget(widget, height=350, sizing_mode="stretch_width"), widget


def test_ipyniivue_renders(page):
    """NiiVue widget loads without crashing."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)

    page.wait_for_load_state("networkidle", timeout=30_000)
    page.wait_for_timeout(3000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=15_000)

    unexpected = _filter_niivue_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_ipyniivue_component_has_expected_params(page):
    """The wrapped component exposes draw_opacity, w_height, overlay_alpha_shader."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)

    component = pane.component
    assert hasattr(component, 'draw_opacity')
    assert hasattr(component, 'overlay_alpha_shader')
    # height is renamed to w_height due to collision with Panel
    assert hasattr(component, 'w_height')

    name_map = pane.trait_name_map
    assert name_map.get("height") == "w_height"

    unexpected = _filter_niivue_errors(msgs)
    assert unexpected == []


def test_ipyniivue_python_changes_draw_opacity(page):
    """Changing draw_opacity from Python updates the widget."""
    from ipyniivue import NiiVue
    widget = NiiVue(height=300)
    pane = pn.pane.AnyWidget(widget, height=350)

    msgs, _ = serve_component(page, pane)
    page.wait_for_load_state("networkidle", timeout=30_000)
    page.wait_for_timeout(3000)

    pane.component.draw_opacity = 0.5
    wait_until(lambda: widget.draw_opacity == 0.5, page, timeout=10_000)

    unexpected = _filter_niivue_errors(msgs)
    assert unexpected == []
