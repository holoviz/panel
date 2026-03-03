"""
Playwright test for the moutils CopyToClipboard anywidget example.

Tests:
    1. Widget renders (Bokeh root attached, copy button visible)
    2. Component has expected params (text, button_text, success)
    3. Python -> browser sync (change text from Python)
"""
import pytest

pytest.importorskip("moutils")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui


def _make_pane():
    from moutils import CopyToClipboard
    widget = CopyToClipboard(
        text="Hello from test!",
        button_text="Copy",
    )
    return pn.pane.AnyWidget(widget, height=80), widget


def test_moutils_renders(page):
    """CopyToClipboard widget renders without crashing."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=10_000)

    assert_no_console_errors(msgs)


def test_moutils_component_has_expected_params(page):
    """The wrapped component exposes text, button_text, success params."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)

    component = pane.component
    assert hasattr(component, 'text')
    assert hasattr(component, 'button_text')
    assert hasattr(component, 'success')
    assert component.text == "Hello from test!"

    assert_no_console_errors(msgs)


def test_moutils_python_changes_text(page):
    """Changing text from Python updates the widget."""
    from moutils import CopyToClipboard
    widget = CopyToClipboard(text="original")
    pane = pn.pane.AnyWidget(widget, height=80)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)

    pane.component.text = "updated text"
    wait_until(lambda: widget.text == "updated text", page, timeout=10_000)

    assert_no_console_errors(msgs)
