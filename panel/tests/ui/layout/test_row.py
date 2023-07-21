import time

import pytest

from panel import Row, Spacer
from panel.io.server import serve

pytestmark = pytest.mark.ui

def test_row_scroll(page, port):
    col = Row(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=True, width=420
    )

    serve(col, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    row_el = page.locator(".bk-Row")
    bbox = row_el.bounding_box()

    assert bbox['width'] == 420
    assert bbox['height'] in (200, 215) # Ignore if browser hides empty scrollbar

    assert 'scrollable-horizontal' in row_el.get_attribute('class')
