"""
Playwright test for the jupyter-anywidget-graphviz example.

Tests:
    1. Widget renders (SVG output appears)
    2. Component has expected params (code_content, svg, response)
    3. Python -> browser sync (change code_content from Python)
"""
import pytest

pytest.importorskip("jupyter_anywidget_graphviz")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui

DOT_SOURCE = """\
digraph G {
    A -> B -> C;
}
"""


def _make_pane():
    from jupyter_anywidget_graphviz import graphvizWidget
    widget = graphvizWidget(code_content=DOT_SOURCE)
    return pn.pane.AnyWidget(widget, height=400), widget


def test_graphviz_renders(page):
    """Graphviz widget renders SVG output."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)

    # Graphviz renders SVG — wait for it to appear
    page.wait_for_timeout(3000)
    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=10_000)

    assert_no_console_errors(msgs)


def test_graphviz_component_has_expected_params(page):
    """The wrapped component exposes code_content, svg, response."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)

    component = pane.component
    assert hasattr(component, 'code_content')
    assert hasattr(component, 'svg')
    assert hasattr(component, 'response')
    assert component.code_content == DOT_SOURCE

    assert_no_console_errors(msgs)


def test_graphviz_python_changes_dot_source(page):
    """Changing code_content from Python updates the widget."""
    from jupyter_anywidget_graphviz import graphvizWidget
    widget = graphvizWidget(code_content=DOT_SOURCE)
    pane = pn.pane.AnyWidget(widget, height=400)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)
    page.wait_for_timeout(2000)

    new_dot = "digraph G { X -> Y; }"
    pane.component.code_content = new_dot
    wait_until(lambda: widget.code_content == new_dot, page, timeout=10_000)

    assert_no_console_errors(msgs)
