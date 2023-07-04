import time

import pytest

try:
    from playwright.sync_api import expect
    pytestmark = pytest.mark.ui
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

from panel.io.server import serve
from panel.pane import Markdown
from panel.template import BootstrapTemplate


def test_bootstrap_template_no_console_errors(page, port):
    tmpl = BootstrapTemplate()
    md = Markdown('Initial')

    tmpl.main.append(md)

    serve(tmpl, port=port, threaded=True, show=False)

    time.sleep(0.2)

    msgs = []
    page.on("console", lambda msg: msgs.append(msg))

    page.goto(f"http://localhost:{port}")

    assert [msg for msg in msgs if msg.type == 'error'] == []


def test_bootstrap_template_raw_css_on_config(page, port):
    tmpl = BootstrapTemplate()

    tmpl.config.raw_css = ['.markdown { color: rgb(255, 0, 0); }']

    md = Markdown('Initial')

    tmpl.main.append(md)

    serve(tmpl, port=port, threaded=True, show=False)

    time.sleep(1)

    msgs = []
    page.on("console", lambda msg: msgs.append(msg))

    page.goto(f"http://localhost:{port}")

    expect(page.locator('.markdown')).to_have_css('color', 'rgb(255, 0, 0)')

    assert [msg for msg in msgs if msg.type == 'error'] == []


def test_bootstrap_template_updates(page, port):
    tmpl = BootstrapTemplate()
    md = Markdown('Initial')

    tmpl.main.append(md)

    serve(tmpl, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expect(page.locator(".markdown").locator("div")).to_have_text('Initial\n')
    md.object = 'Updated'
    expect(page.locator(".markdown").locator("div")).to_have_text('Updated\n')
