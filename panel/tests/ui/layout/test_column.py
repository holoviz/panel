import time

import pytest

from panel import Column, Spacer
from panel.io.server import serve

pytestmark = pytest.mark.ui

def test_column_scroll(page, port):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=True, height=420
    )

    serve(col, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    bbox = page.locator(".bk-Column").bounding_box()

    assert bbox['width'] in (200, 215) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420
