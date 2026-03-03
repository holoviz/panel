"""
Playwright test for the ipydeck anywidget example (DOES NOT RENDER).

ipydeck bundles React 18 and calls ReactDOM.render() targeting Panel's
shadow DOM container, which triggers React error #185. The map does not
render. This test verifies the red banner is visible.

Tests:
    1. Red DOES NOT RENDER banner is visible
"""
import pytest

pytest.importorskip("ipydeck")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component

pytestmark = pytest.mark.ui


def test_ipydeck_banner(page):
    """Red DOES NOT RENDER banner renders correctly."""
    status = pn.pane.Markdown("""
<div style="background-color: #f8d7da; border: 2px solid #dc3545; border-radius: 8px; padding: 16px;">
<p style="color: #721c24; font-size: 20px; font-weight: bold; margin: 0;">
DOES NOT RENDER
</p>
<p style="color: #721c24; font-size: 15px; margin: 8px 0 0 0;">
ipydeck's ESM bundles React and calls ReactDOM.render() which triggers
React error #185 in Panel's shadow DOM container.
</p>
</div>
""", sizing_mode="stretch_width")

    msgs, _ = serve_component(page, pn.Column(status))
    page.wait_for_timeout(2000)
    expect(page.locator("text=DOES NOT RENDER")).to_be_visible(timeout=10_000)
