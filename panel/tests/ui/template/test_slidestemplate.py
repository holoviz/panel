import time

import pytest

pytestmark = pytest.mark.ui

from panel.io.server import serve
from panel.pane import Markdown
from panel.template import SlidesTemplate


def test_slides_template_no_console_errors(page, port):
    tmpl = SlidesTemplate()
    md = Markdown('Initial')

    tmpl.main.append(md)

    serve(tmpl, port=port, threaded=True, show=False)

    time.sleep(0.5)

    msgs = []
    page.on("console", lambda msg: msgs.append(msg))

    page.goto(f"http://localhost:{port}")

    assert [msg for msg in msgs if msg.type == 'error'] == []


def test_slides_template_updates(page, port):
    tmpl = SlidesTemplate()
    md = Markdown('Initial')

    tmpl.main.append(md)

    serve(tmpl, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    assert page.locator(".markdown").locator("div").text_content() == 'Initial\n'
    md.object = 'Updated'
    time.sleep(0.1)
    assert page.locator(".markdown").locator("div").text_content() == 'Updated\n'
