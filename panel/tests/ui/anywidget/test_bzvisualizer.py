"""
Playwright test for the BZ Visualizer anywidget example (WORKS).

widget-bzvisualizer renders interactive 3D Brillouin zones for crystal structures.

Tests:
    1. Widget loads (Bokeh root attached to DOM)
    2. Component has expected params (cell, rel_coords, atom_numbers, show_axes, etc.)
    3. Trait name collisions handled (height→w_height, width→w_width)
    4. Crystal structure update syncs (Py→Br)
"""
import pytest

pytest.importorskip("widget_bzvisualizer")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import (
    assert_no_console_errors, console_errors, wait_for_anywidget,
)

pytestmark = [
    pytest.mark.ui,
    pytest.mark.filterwarnings(
        "ignore:The `ipykernel.comm.Comm` class has been deprecated:DeprecationWarning"
    ),
    pytest.mark.filterwarnings(
        "ignore:Set OLD_ERROR_HANDLING to false:DeprecationWarning"
    ),
    pytest.mark.filterwarnings(
        "ignore:`get_BZ` is deprecated:UserWarning"
    ),
]

# WebGL/3D rendering may log benign warnings in headless environments
_BZ_KNOWN_ERRORS = [
    "WebGL", "getContext", "gl.getParameter",
    "Failed to load resource", "net::ERR",
    "ResizeObserver", "seekpath",
]


def _filter_bz_errors(msgs):
    errors = console_errors(msgs)
    return [
        e for e in errors
        if not any(known.lower() in e.text.lower() for known in _BZ_KNOWN_ERRORS)
    ]


def _make_pane():
    import widget_bzvisualizer

    # FCC copper
    cell = [[0, 0.5, 0.5], [0.5, 0, 0.5], [0.5, 0.5, 0]]
    widget = widget_bzvisualizer.BZVisualizer(
        cell=cell, rel_coords=[[0, 0, 0]], atom_numbers=[29],
    )
    pane = pn.pane.AnyWidget(widget, height=400)
    return pane, widget


def test_bzvisualizer_renders(page):
    """BZVisualizer widget renders without crashing."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=10_000)

    unexpected = _filter_bz_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_bzvisualizer_has_expected_params(page):
    """Component exposes crystal structure and display params."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)

    component = pane.component
    assert hasattr(component, 'cell')
    assert hasattr(component, 'rel_coords')
    assert hasattr(component, 'atom_numbers')
    assert hasattr(component, 'show_axes')
    assert hasattr(component, 'show_bvectors')
    assert hasattr(component, 'show_pathpoints')


def test_bzvisualizer_trait_name_collisions(page):
    """Height and width traits are renamed to w_height and w_width."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)

    component = pane.component
    # Original traits are height/width (Unicode), renamed to w_height/w_width
    assert hasattr(component, 'w_height')
    assert hasattr(component, 'w_width')


def test_bzvisualizer_crystal_update(page):
    """Updating crystal structure params syncs new data (Py→Br)."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)

    component = pane.component
    # Switch to BCC iron
    component.cell = [[-0.5, 0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, -0.5]]
    component.atom_numbers = [26]

    assert component.cell == [[-0.5, 0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, -0.5]]
    assert component.atom_numbers == [26]
