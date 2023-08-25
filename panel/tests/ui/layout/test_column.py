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


def test_column_auto_scroll_limit(page, port):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        auto_scroll_limit=100, height=420
    )

    serve(col, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    column = page.locator(".bk-panel-models-layout-Column")
    bbox = column.bounding_box()

    assert bbox['width'] in (200, 215) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420

    assert 'scrollable-vertical' in column.get_attribute('class')

    scroll_loc = column.evaluate('(el) => el.scrollTop')
    assert scroll_loc == 0

    # assert scroll location is still at top
    col.append(Spacer(styles=dict(background='yellow'), width=200, height=200))
    time.sleep(1)
    new_scroll_loc = column.evaluate('(el) => el.scrollTop')
    assert new_scroll_loc == scroll_loc

    # scroll to close to bottom
    column.evaluate('(el) => el.scrollTop = el.scrollHeight')

    # assert auto scroll works; i.e. distance from bottom is 0
    col.append(Spacer(styles=dict(background='yellow'), width=200, height=200))
    time.sleep(1)
    distance_from_bottom = column.evaluate(
        '(el) => el.scrollHeight - el.scrollTop - el.clientHeight'
    )
    assert distance_from_bottom == 0


def test_column_auto_scroll_limit_disabled(page, port):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        auto_scroll_limit=0, height=420, scroll=True
    )

    serve(col, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    column = page.locator(".bk-panel-models-layout-Column")
    bbox = column.bounding_box()

    assert bbox['width'] in (200, 215) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420

    assert 'scrollable-vertical' in column.get_attribute('class')

    scroll_loc = column.evaluate('(el) => el.scrollTop')
    assert scroll_loc == 0

    # assert scroll location is still at top
    col.append(Spacer(styles=dict(background='yellow'), width=200, height=200))
    time.sleep(1)
    new_scroll_loc = column.evaluate('(el) => el.scrollTop')
    assert new_scroll_loc == scroll_loc


def test_column_scroll_button_threshold(page, port):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll_button_threshold=10, height=420
    )

    serve(col, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    column = page.locator(".bk-panel-models-layout-Column")
    bbox = column.bounding_box()

    assert bbox['width'] in (200, 215) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420

    assert 'scrollable-vertical' in column.get_attribute('class')

    # assert scroll button is visible on render
    scroll_arrow = page.locator(".scroll-button")
    assert scroll_arrow.get_attribute('class') == 'scroll-button visible'
    assert scroll_arrow.is_visible()

    # assert scroll button is invisible at bottom of page
    column.evaluate('(el) => el.scrollTop = el.scrollHeight')
    time.sleep(0.5)
    assert scroll_arrow.get_attribute('class') == 'scroll-button'
    assert not scroll_arrow.is_visible()

    # assert scroll button is visible beyond threshold
    column.evaluate('(el) => el.scrollTop = 5')
    time.sleep(0.5)
    assert scroll_arrow.get_attribute('class') == 'scroll-button visible'
    assert scroll_arrow.is_visible()


def test_column_scroll_button_threshold_disabled(page, port):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=True, scroll_button_threshold=0, height=420
    )

    serve(col, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    column = page.locator(".bk-panel-models-layout-Column")
    bbox = column.bounding_box()

    assert bbox['width'] in (200, 215) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420

    assert 'scrollable-vertical' in column.get_attribute('class')

    # assert scroll button is invisible on render
    scroll_arrow = page.locator(".scroll-button")
    assert scroll_arrow.get_attribute('class') == 'scroll-button'
    assert not scroll_arrow.is_visible()

    # assert scroll button is visible beyond threshold
    column.evaluate('(el) => el.scrollTop = 5')
    time.sleep(0.5)
    assert scroll_arrow.get_attribute('class') == 'scroll-button'
    assert not scroll_arrow.is_visible()


def test_column_view_latest(page, port):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        view_latest=True, scroll=True, height=420
    )

    serve(col, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    column = page.locator(".bk-panel-models-layout-Column")
    bbox = column.bounding_box()

    assert bbox['width'] in (200, 215) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420

    assert 'scrollable-vertical' in column.get_attribute('class')

    # assert scroll location does not start at top
    scroll_loc = column.evaluate('(el) => el.scrollTop')
    assert scroll_loc != 0

def test_column_scroll_position_init(page, port):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=True, scroll_position=100, height=420
    )

    serve(col, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    column = page.locator(".bk-panel-models-layout-Column")

    # assert scroll position can be used to initialize scroll location
    scroll_loc = column.evaluate('(el) => el.scrollTop')
    assert scroll_loc == 100


def test_column_scroll_position_recorded(page, port):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=True, height=420
    )

    serve(col, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    column = page.locator(".bk-panel-models-layout-Column")

    # change scroll location thru scrolling
    column.evaluate('(el) => el.scrollTop = 150')
    time.sleep(0.5)

    # assert scroll position is synced and recorded at 150
    assert col.scroll_position == 150


def test_column_scroll_position_param_updated(page, port):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=True, height=420
    )

    serve(col, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    column = page.locator(".bk-panel-models-layout-Column")

    # change scroll location thru param
    col.scroll_position = 175
    time.sleep(0.5)

    # assert scroll location is synced and recorded at 175
    scroll_loc = column.evaluate('(el) => el.scrollTop')
    assert scroll_loc == 175
