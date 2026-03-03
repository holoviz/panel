"""
Playwright test for the navio_jupyter anywidget example.

Tests:
    1. Widget renders (Bokeh root attached to DOM)
    2. Component has expected params (data, height, selected)
    3. Python -> browser sync (change data from Python)
"""
import pytest

pytest.importorskip("navio_jupyter")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui


SAMPLE_DATA = [
    {"Name": "Alice", "Age": 25, "Salary": 55000},
    {"Name": "Bob", "Age": 30, "Salary": 72000},
    {"Name": "Charlie", "Age": 35, "Salary": 68000},
    {"Name": "Diana", "Age": 28, "Salary": 61000},
    {"Name": "Eve", "Age": 32, "Salary": 80000},
]


def _make_pane():
    from navio_jupyter import navio
    widget = navio(data=SAMPLE_DATA, height=300)
    return pn.pane.AnyWidget(widget, sizing_mode="stretch_width"), widget


def test_navio_renders(page):
    """navio widget renders without crashing."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=10_000)

    assert_no_console_errors(msgs)


def test_navio_component_has_expected_params(page):
    """The wrapped component exposes data, height, selected params."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)

    component = pane.component
    assert hasattr(component, 'data')
    assert hasattr(component, 'height')
    assert hasattr(component, 'selected')
    assert len(component.data) == 5

    assert_no_console_errors(msgs)


def test_navio_python_changes_data(page):
    """Changing data from Python updates the widget."""
    from navio_jupyter import navio
    widget = navio(data=SAMPLE_DATA, height=300)
    pane = pn.pane.AnyWidget(widget, sizing_mode="stretch_width")

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)

    new_data = [
        {"Fruit": "Apple", "Calories": 95},
        {"Fruit": "Banana", "Calories": 105},
    ]
    pane.component.data = new_data
    wait_until(lambda: len(widget.data) == 2, page, timeout=10_000)

    assert_no_console_errors(msgs)
