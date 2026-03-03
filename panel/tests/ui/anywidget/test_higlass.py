"""
Playwright test for the HiGlass NOT COMPATIBLE banner.

HiGlass's ESM requires Jupyter's widget model manager which Panel does not
implement. The widget does not render. This test verifies the red banner
renders correctly.
"""
import pytest

pytest.importorskip("higlass")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component

pytestmark = pytest.mark.ui


def test_higlass_banner(page):
    """Verify the DOES NOT RENDER banner renders."""
    status = pn.pane.Markdown("""
<div style="background-color: #f8d7da; border: 2px solid #dc3545; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #721c24; font-size: 20px; font-weight: bold; margin: 0;">
THIS WIDGET DOES NOT RENDER
</p>
<p style="color: #721c24; font-size: 15px; margin: 8px 0 0 0;">
<strong>Reason:</strong> HiGlass's ESM requires Jupyter's widget model manager
(<code>model.widget_manager.get_model()</code>) to register its data fetcher.
Panel does not implement this Jupyter protocol.
</p>
</div>
""", sizing_mode="stretch_width")

    msgs, _ = serve_component(page, pn.Column(status))
    page.wait_for_timeout(2000)
    expect(page.locator("text=DOES NOT RENDER")).to_be_visible(timeout=10_000)
