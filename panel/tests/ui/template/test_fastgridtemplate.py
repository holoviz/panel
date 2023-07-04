import time

import pytest

try:
    from playwright.sync_api import expect
    pytestmark = pytest.mark.ui
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

from panel.io.server import serve
from panel.pane import Markdown
from panel.template import FastGridTemplate


def test_fast_grid_template_no_console_errors(page, port):
    tmpl = FastGridTemplate()
    md = Markdown('Initial')

    tmpl.main[0:3, 0:3] = md

    serve(tmpl, port=port, threaded=True, show=False)

    time.sleep(0.2)

    msgs = []
    page.on("console", lambda msg: msgs.append(msg))

    page.goto(f"http://localhost:{port}", timeout=40_000)

    expected = ['maxWidth', 'maxHeight']
    assert [
        msg for msg in msgs if msg.type == 'error' and not any(e in msg.text for e in expected)
    ] == []


def test_fast_grid_template_updates(page, port):
    tmpl = FastGridTemplate()
    md = Markdown('Initial')

    tmpl.main[0:3, 0:3] = md

    serve(tmpl, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}", timeout=40_000)

    expect(page.locator(".markdown").locator("div")).to_have_text('Initial\n')
    md.object = 'Updated'
    expect(page.locator(".markdown").locator("div")).to_have_text('Updated\n')
