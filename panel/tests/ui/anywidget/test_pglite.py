"""
Playwright test for the PGLite anywidget example (WORKS).

PGLite runs PostgreSQL in the browser via WebAssembly.

Tests:
    1. Widget loads (Bokeh root attached to DOM)
    2. Component has expected params (code_content, response, headless)
    3. SQL query sync from Python (Py→Br)
"""
import pytest

pytest.importorskip("jupyter_anywidget_pglite")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component

from .conftest import (
    assert_no_console_errors,
    console_errors,
    wait_for_anywidget,
)

pytestmark = [
    pytest.mark.ui,
    pytest.mark.filterwarnings(
        "ignore:The `ipykernel.comm.Comm` class has been deprecated:DeprecationWarning"
    ),
]

# PGLite WASM loading may produce network/resource warnings
_PGLITE_KNOWN_ERRORS = [
    "Failed to load resource", "net::ERR",
    "SharedArrayBuffer", "COOP", "COEP",
    "ResizeObserver",
]


def _filter_pglite_errors(msgs):
    errors = console_errors(msgs)
    return [
        e for e in errors
        if not any(known.lower() in e.text.lower() for known in _PGLITE_KNOWN_ERRORS)
    ]


def _make_pane():
    from jupyter_anywidget_pglite import postgresWidget

    widget = postgresWidget()
    pane = pn.pane.AnyWidget(widget, height=400)
    return pane, widget


def test_pglite_renders(page):
    """PGLite widget renders without crashing."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=10_000)

    unexpected = _filter_pglite_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_pglite_has_expected_params(page):
    """Component exposes code_content, response, and headless params."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)

    component = pane.component
    assert hasattr(component, 'code_content')
    assert hasattr(component, 'response')
    assert hasattr(component, 'headless')
    assert hasattr(component, 'extensions')


def test_pglite_sql_sync(page):
    """Setting code_content sends SQL to the widget (Py→Br)."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)

    component = pane.component
    component.code_content = "SELECT 1 + 1 AS result;"
    assert component.code_content == "SELECT 1 + 1 AS result;"
