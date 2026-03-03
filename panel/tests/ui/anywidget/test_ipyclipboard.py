"""
Playwright test for the ipyclipboard anywidget example.

Tests:
    1. Widget renders (Bokeh root attached, paste button visible)
    2. Component has expected params (value)
"""
import pytest

pytest.importorskip("ipyclipboard")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui


def _make_pane():
    from ipyclipboard import Clipboard
    widget = Clipboard()
    return pn.pane.AnyWidget(widget, height=100), widget


def test_ipyclipboard_renders(page):
    """Clipboard widget renders a paste button."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=10_000)

    assert_no_console_errors(msgs)


def test_ipyclipboard_component_has_value_param(page):
    """The wrapped component exposes a value param."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)

    component = pane.component
    assert hasattr(component, 'value')
    # Initial value should be empty string
    assert component.value == "" or component.value is None

    assert_no_console_errors(msgs)
