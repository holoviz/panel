import time

import pytest

from panel import FloatPanel, Spacer
from panel.io.server import serve

pytestmark = pytest.mark.ui

def test_float_panel_closed_status(page, port):
    float_panel = FloatPanel(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
    )

    serve(float_panel, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    page.locator('.jsPanel-btn-close').click()

    time.sleep(0.2)

    assert float_panel.status == 'closed'
