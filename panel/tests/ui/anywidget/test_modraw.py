"""
Playwright test for the modraw AnyWidget example.

modraw is a tldraw-based drawing widget that provides a full whiteboard /
infinite canvas. Unlike jupyter-tldraw, modraw exposes a `base64` trait
that syncs drawn content back to Python as a base64-encoded PNG.

NOTE: modraw's `width` and `height` traits collide with Panel's Layoutable
params and are renamed to `w_width` and `w_height`.

Tests:
    1. Widget renders (tldraw DOM appears inside the ESM container)
    2. No unexpected console errors
"""
import pytest

pytest.importorskip("modraw")
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
    """Create a Draw widget wrapped in an AnyWidget pane."""
    from modraw import Draw

    widget = Draw(width=400, height=300)
    return pn.pane.AnyWidget(widget)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_modraw_renders(page):
    """modraw widget renders its tldraw-based DOM inside the ESM container."""
    pane = _make_pane()
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=20_000)
    page.wait_for_timeout(5000)

    # modraw uses tldraw which renders complex DOM within the ReactiveESM container
    esm_el = page.locator(".bk-ReactiveESM")
    expect(esm_el.first).to_be_visible(timeout=15_000)

    assert_no_console_errors(msgs)
