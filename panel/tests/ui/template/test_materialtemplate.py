import time

import pytest

try:
    from playwright.sync_api import expect
    pytestmark = pytest.mark.ui
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

from panel.io.server import serve
from panel.pane import Markdown
from panel.template import MaterialTemplate


def test_material_template_no_console_errors(page, port):
    tmpl = MaterialTemplate()
    md = Markdown('Initial')

    tmpl.main.append(md)

    serve(tmpl, port=port, threaded=True, show=False)

    time.sleep(0.2)

    msgs = []
    page.on("console", lambda msg: msgs.append(msg))

    page.goto(f"http://localhost:{port}")

    assert [msg for msg in msgs if msg.type == 'error'] == []


def test_material_template_updates(page, port):
    tmpl = MaterialTemplate()
    md = Markdown('Initial')

    tmpl.main.append(md)

    serve(tmpl, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expect(page.locator(".markdown").locator("div")).to_have_text('Initial\n')
    md.object = 'Updated'
    expect(page.locator(".markdown").locator("div")).to_have_text('Updated\n')
