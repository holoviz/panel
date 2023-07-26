import time

import pytest

from panel import Spacer, WidgetBox
from panel.io.server import serve

pytestmark = pytest.mark.ui

def test_widgetbox_vertical_scroll(page, port):
    col = WidgetBox(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=True, height=420
    )

    serve(col, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    bbox = page.locator(".bk-panel-models-layout-Column").bounding_box()

    assert bbox['width'] in (202, 217) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420

def test_widgetbox_horizontal_scroll(page, port):
    col = WidgetBox(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=True, width=420, horizontal=True
    )

    serve(col, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    bbox = page.locator(".bk-Row").bounding_box()

    assert bbox['width'] == 420
    assert bbox['height'] in (202, 217) # Ignore if browser hides empty scrollbar
