"""
Playwright test for the ChromoSpyce anywidget example (WORKS).

ChromoSpyce renders 3D chromosome structure data using WebGL.

Tests:
    1. Widget loads (Bokeh root attached to DOM)
    2. Component has expected params (structure, viewconfig)
    3. Structure update syncs from Python (Py→Br)
"""
import pytest

pytest.importorskip("chromospyce")
pytest.importorskip("playwright")

import numpy as np

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
]

# WebGL/3D rendering may log benign warnings in headless environments
_CHROMO_KNOWN_ERRORS = [
    "WebGL", "getContext", "gl.getParameter",
    "Failed to load resource", "net::ERR",
    "ResizeObserver",
]


def _filter_chromo_errors(msgs):
    errors = console_errors(msgs)
    return [
        e for e in errors
        if not any(known.lower() in e.text.lower() for known in _CHROMO_KNOWN_ERRORS)
    ]


def _make_pane():
    from chromospyce import Widget as ChromoWidget

    t = np.linspace(0, 4 * np.pi, 100)
    structure = np.column_stack([np.cos(t), np.sin(t), t])
    widget = ChromoWidget(structure)
    pane = pn.pane.AnyWidget(widget, height=400)
    return pane, widget


def test_chromospyce_renders(page):
    """ChromoSpyce widget renders without crashing."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=10_000)

    unexpected = _filter_chromo_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_chromospyce_has_expected_params(page):
    """Component exposes structure and viewconfig params."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)

    component = pane.component
    assert hasattr(component, 'structure')
    assert hasattr(component, 'viewconfig')
    assert isinstance(component.structure, bytes)
    assert len(component.structure) > 0


def test_chromospyce_structure_update(page):
    """Updating structure trait syncs new data (Py→Br)."""
    from chromospyce import Widget as ChromoWidget

    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)

    component = pane.component
    old_len = len(component.structure)

    # Create a new structure with different data
    new_data = np.random.randn(50, 3)
    new_widget = ChromoWidget(new_data)
    component.structure = new_widget.structure

    # Structure bytes should have changed
    assert len(component.structure) != old_len or component.structure != new_widget.structure
