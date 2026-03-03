"""
Playwright test for the cosmograph-widget anywidget example.

Tests:
    1. Widget renders (Bokeh root attached to DOM)
    2. Component has expected params (point_color, point_size, etc.)
    3. Python -> browser sync (change point_color from Python)
"""
import pytest

pytest.importorskip("cosmograph_widget")
pytest.importorskip("playwright")

import pandas as pd
from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui

# Cosmograph uses WebGL for rendering — known errors in headless
_COSMO_KNOWN_ERRORS = [
    "WebGL",
    "getContext",
    "gl.getParameter",
    "Failed to load resource",
    "net::ERR",
    "ResizeObserver",
    "Error rendering Bokeh items",
]


def _filter_cosmo_errors(msgs):
    errors = console_errors(msgs)
    return [
        e for e in errors
        if not any(known.lower() in e.text.lower() for known in _COSMO_KNOWN_ERRORS)
    ]


def _make_pane():
    from cosmograph_widget import Cosmograph
    nodes = pd.DataFrame({
        "id": [f"n{i}" for i in range(5)],
        "label": [f"Node {i}" for i in range(5)],
    })
    edges = pd.DataFrame({
        "source": ["n0", "n1", "n2", "n3"],
        "target": ["n1", "n2", "n3", "n4"],
    })
    widget = Cosmograph(
        points=nodes,
        links=edges,
        point_color="#4a90d9",
        point_size=8,
        point_id_by="id",
        link_source_by="source",
        link_target_by="target",
        fit_view_on_init=True,
        background_color="#222222",
    )
    return pn.pane.AnyWidget(widget, height=400, sizing_mode="stretch_width"), widget


def test_cosmograph_renders(page):
    """Cosmograph widget loads without crashing."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)

    page.wait_for_load_state("networkidle", timeout=30_000)
    page.wait_for_timeout(3000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=15_000)

    unexpected = _filter_cosmo_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_cosmograph_component_has_expected_params(page):
    """The wrapped component exposes point_color, point_size, background_color."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)

    component = pane.component
    assert hasattr(component, 'point_color')
    assert hasattr(component, 'point_size')
    assert hasattr(component, 'background_color')
    assert component.point_color == "#4a90d9"
    assert component.point_size == 8

    unexpected = _filter_cosmo_errors(msgs)
    assert unexpected == []


def test_cosmograph_python_changes_point_color(page):
    """Changing point_color from Python updates the widget."""
    pane, widget = _make_pane()
    msgs, _ = serve_component(page, pane)

    page.wait_for_load_state("networkidle", timeout=30_000)
    page.wait_for_timeout(3000)

    pane.component.point_color = "#ff0000"
    wait_until(lambda: widget.point_color == "#ff0000", page, timeout=10_000)

    unexpected = _filter_cosmo_errors(msgs)
    assert unexpected == []
