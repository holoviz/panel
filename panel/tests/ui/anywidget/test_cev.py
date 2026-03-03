"""
Playwright test for the CEV NOT COMPATIBLE banner.

CEV's EmbeddingComparisonWidget extends ipywidgets.VBox, NOT
anywidget.AnyWidget. It has no _esm attribute and cannot be rendered
by Panel's AnyWidget pane. This test verifies the red banner renders
correctly.
"""
import pytest

pytest.importorskip("cev")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component

pytestmark = pytest.mark.ui


def test_cev_banner(page):
    """Verify the NOT COMPATIBLE banner renders."""
    status = pn.pane.Markdown("""
<div style="background-color: #f8d7da; border: 2px solid #dc3545; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #721c24; font-size: 20px; font-weight: bold; margin: 0;">
NOT COMPATIBLE — NOT AN ANYWIDGET
</p>
<p style="color: #721c24; font-size: 15px; margin: 8px 0 0 0;">
<strong>Reason:</strong> CEV's <code>EmbeddingComparisonWidget</code> extends
<code>ipywidgets.VBox</code>, NOT <code>anywidget.AnyWidget</code>.
It has no <code>_esm</code> attribute and cannot be rendered by Panel's AnyWidget pane.
This page is documentation only.
</p>
</div>
""", sizing_mode="stretch_width")

    msgs, _ = serve_component(page, pn.Column(status))
    page.wait_for_timeout(2000)
    expect(page.locator("text=NOT COMPATIBLE")).to_be_visible(timeout=10_000)
