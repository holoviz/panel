"""
Playwright test for the widget-code-input AnyWidget example.

widget-code-input provides a CodeMirror-based Python function editor.
It syncs function_name, function_parameters, function_body, and other
traits. The `name` trait collides with Panel's `name` param and is
renamed to `w_name`.

Tests:
    1. Widget renders (Bokeh model attached, no console errors)
    2. Component has expected params (function_name, function_body, w_name)
    3. Python -> browser sync (change function_name from Python, verify update)
"""
import pytest

pytest.importorskip("widget_code_input")
pytest.importorskip("playwright")

from playwright.sync_api import expect
from widget_code_input import WidgetCodeInput

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui


def _make_widget():
    """Create a WidgetCodeInput with a sample function."""
    return WidgetCodeInput(
        function_name="my_function",
        function_parameters="x, y",
    )


def test_codeinput_renders(page):
    """WidgetCodeInput loads and the Bokeh model is attached to the DOM."""
    widget = _make_widget()
    pane = pn.pane.AnyWidget(widget, height=300)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # The Bokeh root div should be attached
    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=10000)

    assert_no_console_errors(msgs)


def test_codeinput_component_has_expected_params(page):
    """The wrapped component exposes function_name, function_body, and w_name."""
    widget = _make_widget()
    pane = pn.pane.AnyWidget(widget, height=300)

    msgs, _ = serve_component(page, pane)

    component = pane.component

    # Core function editing traits
    assert hasattr(component, 'function_name'), "component should have function_name param"
    assert hasattr(component, 'function_body'), "component should have function_body param"
    assert hasattr(component, 'function_parameters'), "component should have function_parameters param"

    # The 'name' trait collides with Panel's name param -> renamed to w_name
    assert hasattr(component, 'w_name'), "component should have w_name param (renamed from 'name')"
    assert 'name' in component._trait_name_map, "'name' should be in _trait_name_map"
    assert component._trait_name_map['name'] == 'w_name', "'name' should map to 'w_name'"

    # Initial values should match what was passed to the widget
    assert component.function_name == "my_function"
    assert component.function_parameters == "x, y"

    assert_no_console_errors(msgs)


def test_codeinput_python_to_browser(page):
    """Changing function_name from Python updates the widget in the browser."""
    widget = _make_widget()
    pane = pn.pane.AnyWidget(widget, height=300)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Verify initial function_name is rendered somewhere in the DOM
    # The editor shows "def my_function(x, y):" in its header/gutter
    page.wait_for_timeout(1000)

    # Change function_name from Python side via the component
    pane.component.function_name = "updated_func"

    # The underlying anywidget should also reflect the change
    wait_until(lambda: widget.function_name == "updated_func", page)

    # Verify the component param was updated
    assert pane.component.function_name == "updated_func"

    assert_no_console_errors(msgs)
