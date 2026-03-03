"""
Playwright test for the ipymario anywidget example.

ipymario provides a Mario "?" block widget that plays a coin chime and
bounce animation on click. The widget has ``gain``, ``duration``, ``size``,
and ``animate`` traitlets.

Known limitations:
    - The canvas may appear invisible in headless Chromium (no GPU)
    - Browser-side clicks do NOT notify Python (ipymario's ESM doesn't
      call ``model.set()`` on click)
    - Custom messages (``widget.send({"type": "click"})``) trigger animation

Tests:
    1. Widget renders (Bokeh root attached to DOM)
    2. Component exposes expected params (size, gain, duration, animate)
    3. Python -> browser sync (change size from Python)
"""
import pytest

pytest.importorskip("ipymario")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui


def _make_widget():
    """Create an ipymario Widget with a visible size."""
    from ipymario import Widget
    return Widget(size=200)


def _make_pane():
    """Create a Panel AnyWidget pane wrapping an ipymario Widget."""
    widget = _make_widget()
    pane = pn.pane.AnyWidget(widget, width=400, height=400)
    return pane, widget


def test_ipymario_renders(page):
    """ipymario widget loads and Bokeh root is attached to DOM.

    Note: The Mario "?" block canvas may not be visually rendered in
    headless mode (no GPU), but the Bokeh model should still attach.
    """
    pane, widget = _make_pane()

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=15_000)

    assert_no_console_errors(msgs)


def test_ipymario_component_has_expected_params(page):
    """The wrapped component exposes size, gain, duration, and animate."""
    pane, widget = _make_pane()

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    component = pane.component

    # size should be present and match the initial value
    assert hasattr(component, 'size'), "component should have size param"
    assert component.size == 200

    # gain should be present (default 0.1)
    assert hasattr(component, 'gain'), "component should have gain param"

    # duration should be present (default 1.0)
    assert hasattr(component, 'duration'), "component should have duration param"

    # animate should be present (boolean)
    assert hasattr(component, 'animate'), "component should have animate param"

    assert_no_console_errors(msgs)


def test_ipymario_python_changes_size(page):
    """Changing size from Python updates the widget (Python -> browser sync)."""
    pane, widget = _make_pane()

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Change size from Python side
    component = pane.component
    component.size = 300

    # Verify the traitlet value synced back to the underlying widget
    wait_until(lambda: widget.size == 300, page, timeout=10_000)
    assert widget.size == 300

    # Also verify the component reflects the new value
    assert component.size == 300

    assert_no_console_errors(msgs)


def test_ipymario_python_changes_gain(page):
    """Changing gain from Python updates the widget (Python -> browser sync)."""
    pane, widget = _make_pane()

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Change gain from Python side
    component = pane.component
    component.gain = 0.5

    # Verify the traitlet value synced back to the underlying widget
    wait_until(lambda: widget.gain == 0.5, page, timeout=10_000)
    assert widget.gain == 0.5

    assert_no_console_errors(msgs)
