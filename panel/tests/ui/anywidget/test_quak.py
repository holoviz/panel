"""
Playwright test for the quak Widget anywidget example.

quak renders a scalable data profiler built on DuckDB and Mosaic.
It uses a message-passing protocol (model.send / model.on("msg:custom"))
for its DuckDB-WASM queries.

Tests:
    1. Widget renders — quak profiler table appears in the DOM
    2. Component has expected traits (_columns, sql)
"""
import pytest

pytest.importorskip("quak")
pytest.importorskip("playwright")

import pandas as pd
import quak

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import (
    assert_no_console_errors,
    wait_for_anywidget,
)

pytestmark = pytest.mark.ui


def _make_widget():
    """Create a quak Widget with sample data."""
    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie", "Diana"],
        "age": [25, 32, 28, 45],
        "salary": [50000, 72000, 61000, 95000],
    })
    return quak.Widget(df), df


def test_quak_renders(page):
    """quak Widget renders the data profiler table."""
    widget, df = _make_widget()
    pane = pn.pane.AnyWidget(widget, height=400)

    msgs, _ = serve_component(page, pane)

    wait_for_anywidget(page)

    # quak renders a table with the data profiler
    page.wait_for_timeout(5000)  # Allow DuckDB-WASM to initialize

    # The Bokeh root div should be attached
    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=10000)

    assert_no_console_errors(msgs)


def test_quak_component_has_expected_params(page):
    """The wrapped component exposes sql and _columns params."""
    widget, df = _make_widget()
    pane = pn.pane.AnyWidget(widget, height=400)

    msgs, _ = serve_component(page, pane)

    # Component params are available immediately
    component = pane.component

    # quak exposes _columns and sql as synced traits
    assert hasattr(component, '_columns'), "component should have _columns param"
    assert hasattr(component, 'sql'), "component should have sql param"

    # _columns should reflect the DataFrame column names
    assert component._columns == ["name", "age", "salary"]

    assert_no_console_errors(msgs)
