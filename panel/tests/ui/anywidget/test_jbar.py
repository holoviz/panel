"""
Playwright test for the jbar NOT COMPATIBLE banner.

jbar's ESM uses d3.select("#my_dataviz"), a document-level CSS selector
query, which cannot penetrate Panel's Shadow DOM. The SVG bar chart is
never created. This test verifies the red banner renders correctly.
"""
import pytest

pytest.importorskip("jbar")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component

pytestmark = pytest.mark.ui


def test_jbar_banner(page):
    """Verify the DOES NOT RENDER banner renders."""
    status = pn.pane.Markdown("""
<div style="background-color: #f8d7da; border: 2px solid #dc3545; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #721c24; font-size: 20px; font-weight: bold; margin: 0;">
DOES NOT RENDER
</p>
<p style="color: #721c24; font-size: 15px; margin: 8px 0 0 0;">
<strong>Root cause:</strong> jbar's ESM uses <code>d3.select("#my_dataviz")</code>,
a document-level CSS selector query, to locate its container div. Panel renders
AnyWidget components inside a <strong>Shadow DOM</strong>, and
<code>document.querySelector()</code> cannot penetrate shadow DOM boundaries.
D3 returns an empty selection, so the SVG bar chart is never created.
</p>
</div>
""", sizing_mode="stretch_width")

    msgs, _ = serve_component(page, pn.Column(status))
    page.wait_for_timeout(2000)
    expect(page.locator("text=DOES NOT RENDER")).to_be_visible(timeout=10_000)
