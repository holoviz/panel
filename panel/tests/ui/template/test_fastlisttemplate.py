import time

import pytest

try:
    from playwright.sync_api import expect
    pytestmark = pytest.mark.ui
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

from panel.io.server import serve
from panel.pane import Markdown
from panel.template import FastListTemplate


def test_fast_list_template_no_console_errors(page, port):
    tmpl = FastListTemplate()
    md = Markdown('Initial')

    tmpl.main.append(md)

    serve(tmpl, port=port, threaded=True, show=False)

    time.sleep(0.2)

    msgs = []
    page.on("console", lambda msg: msgs.append(msg))

    page.goto(f"http://localhost:{port}", timeout=40_000)

    known_messages = [
        "[bokeh] setting log level to: 'info'",
        "[bokeh] Websocket connection 0 is now open",
        "[bokeh] document idle at",
        "Bokeh items were rendered successfully"
    ]
    assert len([
        msg for msg in msgs if not any(msg.text.startswith(known) for known in known_messages)
    ]) == 0


def test_fast_list_template_updates(page, port):
    tmpl = FastListTemplate()
    md = Markdown('Initial')

    tmpl.main.append(md)

    serve(tmpl, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}", timeout=40_000)

    expect(page.locator(".markdown").locator("div")).to_have_text('Initial\n')
    md.object = 'Updated'
    expect(page.locator(".markdown").locator("div")).to_have_text('Updated\n')
