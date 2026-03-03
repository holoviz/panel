"""
Playwright tests for the widget-periodictable anywidget component.

widget-periodictable renders an interactive periodic table where elements
can be clicked to cycle through selection states.

Key traitlets:
    - selected_elements (Dict): Maps element symbols to selection state index
    - states (Int): Number of selection states
    - disabled (Bool): Whether the widget is disabled
    - disabled_elements (List): Elements that cannot be selected
    - selected_colors (List): Colors for each selection state
    - width (Unicode): Element cell width (renamed to w_width due to Panel collision)

Tests:
    1. Widget renders (periodic table DOM elements appear)
    2. No unexpected console errors
    3. Component has expected params (selected_elements, states, disabled, w_width)
    4. Python -> Browser sync (set selected_elements from Python, verify on widget)
"""
import pytest

pytest.importorskip("widget_periodictable")
pytest.importorskip("playwright")

from widget_periodictable import PTableWidget

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui


def _make_widget(**kwargs):
    """Create a PTableWidget with sensible defaults for testing."""
    defaults = dict(
        states=3,
        selected_colors=[
            "rgb(100,180,255)",
            "rgb(100,220,100)",
            "rgb(255,160,80)",
        ],
    )
    defaults.update(kwargs)
    return PTableWidget(**defaults)


# ---------------------------------------------------------------------------
# 1. Renders
# ---------------------------------------------------------------------------

def test_periodictable_renders(page):
    """PTableWidget renders and the periodic table DOM is attached."""
    widget = _make_widget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # The periodic table renders element cells with class 'periodic-table-entry'
    # Wait for at least one element cell to appear
    page.wait_for_timeout(2000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_visible()

    # The widget should render periodic table entry divs
    entries = page.locator(".periodic-table-entry")
    expect(entries.first).to_be_visible(timeout=10000)

    # There should be many element entries (118 elements in periodic table)
    count = entries.count()
    assert count > 50, f"Expected many periodic table entries, got {count}"

    assert_no_console_errors(msgs)


# ---------------------------------------------------------------------------
# 2. Component params
# ---------------------------------------------------------------------------

def test_periodictable_component_has_expected_params(page):
    """The wrapped component exposes the expected params."""
    widget = _make_widget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)

    component = pane.component

    # Core traitlets should be available as params
    assert hasattr(component, 'selected_elements'), \
        "component should have selected_elements param"
    assert hasattr(component, 'states'), \
        "component should have states param"
    assert hasattr(component, 'disabled'), \
        "component should have disabled param"
    assert hasattr(component, 'disabled_elements'), \
        "component should have disabled_elements param"
    assert hasattr(component, 'selected_colors'), \
        "component should have selected_colors param"

    # 'width' collides with Panel's width param, so it should be renamed
    assert hasattr(component, 'w_width'), \
        "component should have w_width param (renamed from width)"

    # Verify default values
    assert component.selected_elements == {}
    assert component.states == 3  # We set states=3 in _make_widget
    assert component.disabled is False
    assert component.disabled_elements == []

    assert_no_console_errors(msgs)


# ---------------------------------------------------------------------------
# 3. Python -> Browser sync
# ---------------------------------------------------------------------------

def test_periodictable_python_to_browser(page):
    """Setting selected_elements from Python updates the widget's traitlet."""
    widget = _make_widget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)
    page.wait_for_timeout(2000)

    component = pane.component

    # Initially no elements are selected
    assert component.selected_elements == {}
    assert widget.selected_elements == {}

    # Select some elements from Python
    new_selection = {"Fe": 0, "Au": 1, "Ag": 2}
    component.selected_elements = new_selection

    # Verify the traitlet on the original widget is updated
    wait_until(lambda: widget.selected_elements == new_selection, page)
    assert widget.selected_elements == new_selection

    # Now clear the selection
    component.selected_elements = {}
    wait_until(lambda: widget.selected_elements == {}, page)
    assert widget.selected_elements == {}

    assert_no_console_errors(msgs)
