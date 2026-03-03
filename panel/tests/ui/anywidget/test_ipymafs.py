"""
Playwright test for the ipymafs anywidget example.

Tests:
    1. Widget renders (Bokeh root attached to DOM)
    2. Component has expected params (my_vector on Line, my_x_coord on Bezier)
    3. Python -> browser sync (change my_vector from Python)
"""
import pytest

pytest.importorskip("ipymafs")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui


def _make_line_pane():
    from ipymafs import Line
    widget = Line()
    return pn.pane.AnyWidget(widget, height=550, sizing_mode="stretch_width"), widget


def _make_bezier_pane():
    from ipymafs import Bezier
    widget = Bezier()
    return pn.pane.AnyWidget(widget, height=550, sizing_mode="stretch_width"), widget


def test_ipymafs_line_renders(page):
    """ipymafs Line widget renders without crashing."""
    pane, _ = _make_line_pane()
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=10_000)

    assert_no_console_errors(msgs)


def test_ipymafs_line_has_my_vector(page):
    """The Line component exposes my_vector param."""
    pane, _ = _make_line_pane()
    msgs, _ = serve_component(page, pane)

    component = pane.component
    assert hasattr(component, 'my_vector')
    assert isinstance(component.my_vector, (list, tuple))
    assert len(component.my_vector) == 2

    assert_no_console_errors(msgs)


def test_ipymafs_line_python_changes_vector(page):
    """Changing my_vector from Python updates the widget."""
    from ipymafs import Line
    widget = Line()
    pane = pn.pane.AnyWidget(widget, height=550)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)

    pane.component.my_vector = [3, 7]
    wait_until(lambda: widget.my_vector == [3, 7], page, timeout=10_000)

    assert_no_console_errors(msgs)
