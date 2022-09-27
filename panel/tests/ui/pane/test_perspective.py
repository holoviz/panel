import time

import pandas as pd
import pytest

from panel.io.server import serve
from panel.pane import Perspective

pytestmark = pytest.mark.ui

def test_perspective_no_console_errors(page, port):
    perspective = Perspective(pd._testing.makeMixedDataFrame())
    serve(perspective, port=port, threaded=True, show=False)

    msgs = []
    page.on("console", lambda msg: msgs.append(msg))

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    time.sleep(1)

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []
