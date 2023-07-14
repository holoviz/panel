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

    col_el = page.locator(".bk-panel-models-layout-Column")
    bbox = col_el.bounding_box()

    assert bbox['width'] in (200, 215) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420

    assert 'scrollable-vertical' in col_el.get_attribute('class')


def test_column_auto_scroll(page, port):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        auto_scroll=True, height=420
    )

    serve(col, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    column = page.locator(".bk-panel-models-layout-Column")
    bbox = column.bounding_box()

    assert bbox['width'] in (200, 215) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420

    assert 'scrollable-vertical' in column.get_attribute('class')

    scroll_loc = column.scrollTop
    assert scroll_loc == 0

    col.append(Spacer(styles=dict(background='yellow'), width=200, height=200))
    new_scroll_loc = column.scrollTop
    assert new_scroll_loc > scroll_loc


def test_column_scroll_button_threshold(page, port):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll_button_threshold=0.5, height=420
    )

    serve(col, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    column = page.locator(".bk-panel-models-layout-Column")
    bbox = column.bounding_box()

    assert bbox['width'] in (200, 215) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420

    assert 'scrollable-vertical' in column.get_attribute('class')

    # trigger scroll event
    column.scrollTop = 1
    scroll_arrow = page.locator(".scroll-button")
    assert scroll_arrow.get_attribute('class') == 'scroll-button'
    assert scroll_arrow.is_visible()
