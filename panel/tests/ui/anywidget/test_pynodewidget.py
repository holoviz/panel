"""
Playwright test for the pynodewidget CAVEATS banner.

pynodewidget's bundled ESM triggers a React error #185 inside Panel's
rendering context. The canvas mounts but React nodes may fail to render.
This test verifies the yellow caveat banner renders correctly.
"""
import pytest

pytest.importorskip("pynodewidget")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component

pytestmark = pytest.mark.ui


def test_pynodewidget_banner(page):
    """Verify the CAVEATS banner renders."""
    status = pn.pane.Markdown("""
<div style="background-color: #fff3cd; border: 2px solid #ffc107; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #856404; font-size: 20px; font-weight: bold; margin: 0;">
CAVEATS -- ReactFlow canvas renders but may show a blank area
</p>
<p style="color: #856404; font-size: 14px; margin: 8px 0 0 0;">
<strong>Upstream issue:</strong> pynodewidget's bundled ESM triggers a
React error #185 (<code>ReactDOM.render is no longer supported in React 18</code>)
inside Panel's rendering context. The canvas mounts but React nodes may fail
to render. This is a pynodewidget bundling issue, not a Panel bug.
</p>
</div>
""")

    msgs, _ = serve_component(page, pn.Column(status))
    page.wait_for_timeout(2000)
    expect(page.locator("text=CAVEATS")).to_be_visible(timeout=10_000)
