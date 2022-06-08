import time

import pytest

pytestmark = pytest.mark.ui

from panel.io.server import serve
from panel.io.state import state
from panel.pane import Markdown


def test_on_load(page, port):
    def app():
        md = Markdown('Initial')

        def cb():
            md.object = 'Loaded'

        state.onload(cb)
        return md

    serve(app, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    time.sleep(0.2)

    assert page.text_content(".bk.markdown") == 'Loaded'
