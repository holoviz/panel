import time

import pytest

pytestmark = pytest.mark.ui

from panel.io.server import serve
from panel.pane import panel


def test_param_defer_load(page, port):
    def defer_load():
        time.sleep(0.5)
        return 'I render after load!'

    component = panel(defer_load, defer_load=True)

    serve(component, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    assert page.locator(".pn-loading")

    time.sleep(0.5)

    assert page.locator(".markdown").locator("div").text_content() == 'I render after load!\n'
