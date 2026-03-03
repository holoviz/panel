"""
Playwright test for the pylifemap anywidget example (WORKS WITH CAVEATS).

pylifemap.Lifemap is NOT an anywidget itself — the internal widget is
extracted via _to_widget(). This test verifies the widget renders.

Tests:
    1. Widget loads (Bokeh root attached to DOM)
    2. Component has expected params (options, w_height, w_width)
"""
import pytest

pytest.importorskip("pylifemap")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component

from .conftest import console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui

# pylifemap loads Leaflet tiles — network errors expected in CI
_LIFEMAP_KNOWN_ERRORS = [
    "Failed to load resource",
    "net::ERR",
    "tile",
    "lifemap",
    "Error rendering Bokeh items",
    "ResizeObserver",
]


def _filter_lifemap_errors(msgs):
    errors = console_errors(msgs)
    return [
        e for e in errors
        if not any(known.lower() in e.text.lower() for known in _LIFEMAP_KNOWN_ERRORS)
    ]


def _make_pane():
    from pylifemap import Lifemap
    lm = Lifemap(width=600, height=400, theme="dark", zoom=5)
    widget = lm._to_widget()
    return pn.pane.AnyWidget(widget, height=450, sizing_mode="stretch_width"), widget


def test_pylifemap_renders(page):
    """pylifemap widget loads without crashing."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)

    page.wait_for_load_state("networkidle", timeout=30_000)
    page.wait_for_timeout(3000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=15_000)

    unexpected = _filter_lifemap_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_pylifemap_component_has_expected_params(page):
    """The wrapped component exposes options, w_height, w_width."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)

    component = pane.component
    assert hasattr(component, 'options')
    # height and width are renamed due to collision with Panel
    assert hasattr(component, 'w_height')
    assert hasattr(component, 'w_width')

    name_map = pane.trait_name_map
    assert name_map.get("height") == "w_height"
    assert name_map.get("width") == "w_width"

    unexpected = _filter_lifemap_errors(msgs)
    assert unexpected == []
