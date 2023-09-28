import time

import pytest

from panel import Column, Spacer
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui

def test_column_scroll(page, port):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=True, height=420
    )
    serve_component(page, port, col)

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
    serve_component(page, port, col)

    column = page.locator(".bk-panel-models-layout-Column")

    bbox = column.bounding_box()

    assert bbox['width'] in (200, 215) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420

    assert 'scrollable-vertical' in column.get_attribute('class')
    assert column.evaluate('(el) => el.scrollTop') == 0

    # assert scroll location is still at top
    col.append(Spacer(styles=dict(background='yellow'), width=200, height=200))

    time.sleep(1)

    assert column.evaluate('(el) => el.scrollTop')  == 0

    # scroll to close to bottom
    column.evaluate('(el) => el.scrollTop = el.scrollHeight')

    # assert auto scroll works; i.e. distance from bottom is 0
    col.append(Spacer(styles=dict(background='yellow'), width=200, height=200))

    wait_until(lambda: column.evaluate(
        '(el) => el.scrollHeight - el.scrollTop - el.clientHeight'
    ) == 0, page, timeout=2000)


def test_column_auto_scroll_limit_disabled(page, port):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        auto_scroll_limit=0, height=420, scroll=True
    )
    serve_component(page, port, col)

    column = page.locator(".bk-panel-models-layout-Column")
    bbox = column.bounding_box()

    assert bbox['width'] in (200, 215) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420

    assert 'scrollable-vertical' in column.get_attribute('class')

    scroll_loc = column.evaluate('(el) => el.scrollTop')
    assert scroll_loc == 0

    # assert scroll location is still at top
    col.append(Spacer(styles=dict(background='yellow'), width=200, height=200))

    wait_until(lambda: column.evaluate('(el) => el.scrollTop') == scroll_loc, page)

def test_column_scroll_button_threshold(page, port):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll_button_threshold=10, height=420
    )
    serve_component(page, port, col)

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
    wait_until(lambda: (
        scroll_arrow.get_attribute('class') == 'scroll-button' and
        not scroll_arrow.is_visible()
    ), page)

    # assert scroll button is visible beyond threshold
    column.evaluate('(el) => el.scrollTop = 5')
    wait_until(lambda: (
        scroll_arrow.get_attribute('class') == 'scroll-button visible' and
        scroll_arrow.is_visible()
    ), page)


def test_column_scroll_button_threshold_disabled(page, port):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=True, scroll_button_threshold=0, height=420
    )
    serve_component(page, port, col)

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

    wait_until(lambda: (
        scroll_arrow.get_attribute('class') == 'scroll-button' and
        not scroll_arrow.is_visible()
    ), page)


def test_column_view_latest(page, port):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        view_latest=True, scroll=True, height=420
    )

    serve_component(page, port, col)

    # assert scroll location does not start at top
    column = page.locator(".bk-panel-models-layout-Column")
    bbox = column.bounding_box()

    assert bbox['width'] in (200, 215) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420
    assert 'scrollable-vertical' in column.get_attribute('class')
    wait_until(lambda: column.evaluate('(el) => el.scrollTop') != 0, page)


def test_column_scroll_position_init(page, port):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=True, scroll_position=100, height=420
    )

    serve_component(page, port, col)

    # assert scroll position can be used to initialize scroll location
    column = page.locator(".bk-panel-models-layout-Column")
    wait_until(lambda: column.evaluate('(el) => el.scrollTop') == 100, page)


def test_column_scroll_position_recorded(page, port):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=True, height=420
    )

    serve_component(page, port, col)

    column = page.locator(".bk-panel-models-layout-Column")

    # change scroll location thru scrolling
    column.evaluate('(el) => el.scrollTop = 150')

    # assert scroll position is synced and recorded at 150
    wait_until(lambda: col.scroll_position == 150, page)


def test_column_scroll_position_param_updated(page, port):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=True, height=420
    )

    serve_component(page, port, col)

    # change scroll location
    col.scroll_position = 175

    column = page.locator(".bk-panel-models-layout-Column")
    wait_until(lambda: column.evaluate('(el) => el.scrollTop') == 175, page)
