"""
Playwright test for the ipymidi anywidget example (WORKS WITH CAVEATS).

ipymidi's MIDIInterface is a headless widget (_view_name = None) — it renders
no visible DOM element. This test verifies the Bokeh root attaches and the
component exposes the expected params.

Tests:
    1. Widget loads (Bokeh root attached to DOM)
    2. Component has expected params (enabled)
"""
import pytest

pytest.importorskip("ipymidi")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component

from .conftest import wait_for_anywidget

pytestmark = pytest.mark.ui


def _make_pane():
    from ipymidi import get_interface
    widget = get_interface()
    return pn.pane.AnyWidget(widget, height=50), widget


def test_ipymidi_renders(page):
    """ipymidi headless widget loads without crashing."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)

    page.wait_for_load_state("networkidle", timeout=15_000)
    page.wait_for_timeout(2000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=10_000)


def test_ipymidi_component_has_enabled_param(page):
    """The wrapped component exposes the enabled param."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)

    component = pane.component
    assert hasattr(component, 'enabled')
    # Initially False (MIDI access not yet granted)
    assert component.enabled is False
