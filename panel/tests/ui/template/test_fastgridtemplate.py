import time

import pytest

pytestmark = pytest.mark.ui

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

    assert page.text_content(".bk.markdown") == 'Initial'
    md.object = 'Updated'
    time.sleep(0.1)
    assert page.text_content(".bk.markdown") == 'Updated'
