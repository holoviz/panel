import time

import pytest

pytestmark = pytest.mark.ui

from panel.io.server import serve
from panel.widgets import Button


def test_button_click(page, port):
    button = Button(name='Click')

    events = []
    def cb(event):
        events.append(event)
    button.on_click(cb)

    serve(button, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    page.click('.bk.bk-btn')

    time.sleep(0.1)

    assert len(events) == 1
