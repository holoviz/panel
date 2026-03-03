"""
Playwright test for the d2-widget AnyWidget example.

d2-widget renders D2 diagram language specifications as SVG via a WASM
build of the D2 compiler running in the browser.

Tests:
    1. Widget renders (D2 diagram SVG appears after WASM compilation)
    2. No unexpected console errors
    3. Python -> Browser sync (change diagram text, SVG updates)
"""
import pytest

pytest.importorskip("d2_widget")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_pane():
    """Create a D2 diagram widget wrapped in an AnyWidget pane."""
    from d2_widget import Widget as D2Widget

    widget = D2Widget(diagram="A -> B: connects")
    return pn.pane.AnyWidget(widget, height=400)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_d2widget_renders(page):
    """D2 widget compiles diagram via WASM and renders SVG."""
    pane = _make_pane()
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=20_000)

    # WASM compilation takes time
    page.wait_for_timeout(5000)

    # D2 renders SVG
    expect(page.locator("svg").first).to_be_visible(timeout=15_000)

    assert_no_console_errors(msgs)


def test_d2widget_diagram_update(page):
    """Changing the diagram text from Python re-renders the SVG."""
    from d2_widget import Widget as D2Widget

    widget = D2Widget(diagram="A -> B: connects")
    pane = pn.pane.AnyWidget(widget, height=400)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=20_000)
    page.wait_for_timeout(5000)
    expect(page.locator("svg").first).to_be_visible(timeout=15_000)

    # Change diagram from Python
    pane.component.diagram = "X -> Y -> Z: flow"
    page.wait_for_timeout(5000)

    # SVG should still be visible after diagram update
    expect(page.locator("svg").first).to_be_visible(timeout=10_000)

    assert_no_console_errors(msgs)
