import time

import pytest

pytestmark = pytest.mark.ui

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

    page.goto(f"http://localhost:{port}")

    assert len(msgs) == 1
    assert msgs[0].text == "[bokeh] setting log level to: 'info'"
