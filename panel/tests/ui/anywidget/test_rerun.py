"""
Playwright test for the Rerun NOT COMPATIBLE banner.

rerun-notebook bundles a ~31 MiB WebAssembly binary. Panel serializes ESM
via WebSocket, so the payload kills the connection. This test verifies the
red banner renders correctly.
"""
import pytest

pytest.importorskip("rerun")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component

pytestmark = pytest.mark.ui


def test_rerun_banner(page):
    """Verify the DOES NOT RENDER banner renders."""
    status = pn.pane.Markdown("""
<div style="background-color: #f8d7da; border: 2px solid #dc3545; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #721c24; font-size: 20px; font-weight: bold; margin: 0;">
THIS WIDGET DOES NOT RENDER
</p>
<p style="color: #721c24; font-size: 15px; margin: 8px 0 0 0;">
<strong>Reason:</strong> rerun-notebook bundles a ~31 MiB WebAssembly binary.
Panel serializes ESM via WebSocket, so the payload kills the connection before
it arrives (<code>Error: Lost websocket connection, 1005</code>).
This page is documentation only.
</p>
</div>
""", sizing_mode="stretch_width")

    msgs, _ = serve_component(page, pn.Column(status))
    page.wait_for_timeout(2000)
    expect(page.locator("text=DOES NOT RENDER")).to_be_visible(timeout=10_000)
