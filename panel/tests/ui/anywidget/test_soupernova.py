"""
Playwright test for the soupernova NOT COMPATIBLE banner.

soupernova.SouperNova is an ipywidgets.VBox (compound widget), not a
direct anywidget.AnyWidget. This test verifies the red banner renders
correctly.
"""
import pytest

pytest.importorskip("soupernova")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component

pytestmark = pytest.mark.ui


def test_soupernova_banner(page):
    """Verify the NOT COMPATIBLE banner renders."""
    status = pn.pane.Markdown("""
<div style="background-color: #f8d7da; border: 2px solid #dc3545; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #721c24; font-size: 20px; font-weight: bold; margin: 0;">
NOT COMPATIBLE with pn.pane.AnyWidget
</p>
<p style="color: #721c24; font-size: 14px; margin: 8px 0 0 0;">
<strong>soupernova.SouperNova</strong> is an <code>ipywidgets.VBox</code>
(compound widget), not a direct <code>anywidget.AnyWidget</code>.
Use <code>pn.pane.IPyWidget</code> with <code>ipywidgets_bokeh</code> instead.
</p>
</div>
""", sizing_mode="stretch_width")

    msgs, _ = serve_component(page, pn.Column(status))
    page.wait_for_timeout(2000)
    expect(page.locator("text=NOT COMPATIBLE")).to_be_visible(timeout=10_000)
