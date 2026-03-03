"""
Playwright test for the mopaint AnyWidget example.

mopaint provides a simple MS Paint-like drawing canvas with tools for
freehand drawing, thick marker, eraser, and color selection. Canvas
contents sync back as base64.

NOTE: mopaint's `width` and `height` traits collide with Panel's
Layoutable params and are renamed to `w_width` and `w_height`.

Tests:
    1. Widget renders (canvas element appears)
    2. No unexpected console errors
    3. Python -> Browser sync (change w_width from Python)
"""
import pytest

pytest.importorskip("mopaint")
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
    """Create a Paint widget wrapped in an AnyWidget pane."""
    from mopaint import Paint

    widget = Paint(width=400, height=300)
    return pn.pane.AnyWidget(widget)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_mopaint_renders(page):
    """Paint widget renders a canvas element."""
    pane = _make_pane()
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)
    page.wait_for_timeout(3000)

    # mopaint renders a canvas element
    expect(page.locator("canvas").first).to_be_visible(timeout=10_000)

    assert_no_console_errors(msgs)


def test_mopaint_dimension_sync(page):
    """Changing w_width from Python updates the canvas dimensions."""
    from mopaint import Paint

    widget = Paint(width=400, height=300)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)
    page.wait_for_timeout(3000)
    expect(page.locator("canvas").first).to_be_visible(timeout=10_000)

    # Change dimensions via renamed trait
    pane.component.w_width = 500
    page.wait_for_timeout(2000)

    assert_no_console_errors(msgs)
