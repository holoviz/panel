import time

import pytest

pytestmark = pytest.mark.ui

from panel.io.server import serve
from panel.pane import Markdown
from panel.template import FastListTemplate


@pytest.mark.flaky(max_runs=3)
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

    assert page.text_content(".bk.markdown") == 'Initial'
    md.object = 'Updated'
    time.sleep(0.1)
    assert page.text_content(".bk.markdown") == 'Updated'
