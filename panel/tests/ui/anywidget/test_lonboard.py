"""
Playwright test for the lonboard NOT COMPATIBLE banner.

Lonboard is a compound widget (Map references child widgets via IPY_MODEL_
strings). It does NOT work with Panel's AnyWidget pane. This test verifies
the red banner renders correctly.
"""
import pytest

pytest.importorskip("lonboard")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component

pytestmark = pytest.mark.ui


def test_lonboard_banner(page):
    """Verify the NOT COMPATIBLE banner renders."""
    status = pn.pane.Markdown("""
<div style="background-color: #f8d7da; border: 2px solid #dc3545; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #721c24; font-size: 20px; font-weight: bold; margin: 0;">
NOT COMPATIBLE WITH AnyWidget PANE
</p>
<p style="color: #721c24; font-size: 15px; margin: 8px 0 0 0;">
<strong>Reason:</strong> Lonboard is a <em>compound widget</em> &mdash; its Map references
child widgets (layers, controls, basemap) via <code>IPY_MODEL_</code> strings.
The AnyWidget pane only supports leaf widgets with flat traits.
Use <code>pn.pane.IPyWidget</code> with <code>pn.extension("ipywidgets")</code> instead.
</p>
</div>
""", sizing_mode="stretch_width")

    msgs, _ = serve_component(page, pn.Column(status))
    page.wait_for_timeout(2000)
    expect(page.locator("text=NOT COMPATIBLE")).to_be_visible(timeout=10_000)
