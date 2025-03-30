import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.layout.base import _SCROLL_MAPPING, Column
from panel.layout.spacer import Spacer
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui


def test_column_scroll(page):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=True, height=420
    )
    serve_component(page, col)

    col_el = page.locator(".bk-panel-models-layout-Column")
    bbox = col_el.bounding_box()

    assert bbox['width'] in (200, 215) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420
    expect(col_el).to_have_class('bk-panel-models-layout-Column scrollable-vertical')


@pytest.mark.parametrize('scroll', _SCROLL_MAPPING.keys())
def test_column_scroll_string(page, scroll):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=scroll, height=420
    )
    serve_component(page, col)

    col_el = page.locator(".bk-panel-models-layout-Column")
    bbox = col_el.bounding_box()

    assert bbox['width'] in (200, 215) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420
    expect(col_el).to_have_class(f'bk-panel-models-layout-Column {_SCROLL_MAPPING[scroll]}')


def test_column_auto_scroll_limit(page):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        auto_scroll_limit=100, height=420
    )
    serve_component(page, col)

    column = page.locator(".bk-panel-models-layout-Column")

    bbox = column.bounding_box()
    assert bbox['width'] in (200, 215) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420

    expect(column.locator('div')).to_have_count(4)
    expect(column).to_have_class('bk-panel-models-layout-Column scrollable-vertical')
    expect(column).to_have_js_property('scrollTop', 0)

    # assert scroll location is still at top
    col.append(Spacer(styles=dict(background='yellow'), width=200, height=200))

    page.wait_for_timeout(500)

    expect(column.locator('div')).to_have_count(5)
    expect(column).to_have_js_property('scrollTop', 0)

    # scroll to close to bottom
    column.evaluate('(el) => el.scrollTo({top: el.scrollHeight})')

    # assert auto scroll works; i.e. distance from bottom is 0
    col.append(Spacer(styles=dict(background='yellow'), width=200, height=200))

    wait_until(lambda: column.evaluate(
        '(el) => el.scrollHeight - el.scrollTop - el.clientHeight'
    ) == 0, page)


def test_column_auto_scroll_limit_disabled(page):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        auto_scroll_limit=0, height=420, scroll=True
    )
    serve_component(page, col)

    column = page.locator(".bk-panel-models-layout-Column")

    bbox = column.bounding_box()
    assert bbox['width'] in (200, 215) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420

    expect(column).to_have_class('bk-panel-models-layout-Column scrollable-vertical')
    expect(column).to_have_js_property('scrollTop', 0)

    # assert scroll location is still at top
    col.append(Spacer(styles=dict(background='yellow'), width=200, height=200))
    expect(column).to_have_js_property('scrollTop', 0)


def test_column_scroll_button_threshold(page):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll_button_threshold=10, height=420
    )
    serve_component(page, col)

    column = page.locator(".bk-panel-models-layout-Column")
    bbox = column.bounding_box()

    assert bbox['width'] in (200, 215) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420

    expect(column).to_have_class('bk-panel-models-layout-Column scrollable-vertical')

    # assert scroll button is visible on render
    scroll_arrow = page.locator(".scroll-button")
    expect(scroll_arrow).to_have_class('scroll-button visible')
    expect(scroll_arrow).to_be_visible()

    # assert scroll button is invisible at bottom of page
    column.evaluate('(el) => el.scrollTo({top: el.scrollHeight})')
    expect(scroll_arrow).to_have_class('scroll-button')
    expect(scroll_arrow).not_to_be_visible()

    # assert scroll button is visible beyond threshold
    column.evaluate('(el) => el.scrollTo({top: 5})')
    expect(scroll_arrow).to_have_class('scroll-button visible')
    expect(scroll_arrow).to_be_visible()


def test_column_scroll_button_threshold_disabled(page):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=True, scroll_button_threshold=0, height=420
    )
    serve_component(page, col)

    column = page.locator(".bk-panel-models-layout-Column")
    bbox = column.bounding_box()

    assert bbox['width'] in (200, 215) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420

    expect(column).to_have_class('bk-panel-models-layout-Column scrollable-vertical')

    # assert scroll button is invisible on render
    scroll_arrow = page.locator(".scroll-button")
    expect(scroll_arrow).to_have_class('scroll-button')
    expect(scroll_arrow).not_to_be_visible()

    # assert scroll button is visible beyond threshold
    column.evaluate('(el) => el.scrollTo({top: 5})')
    expect(scroll_arrow).to_have_class('scroll-button')
    expect(scroll_arrow).not_to_be_visible()


def test_column_view_latest(page):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        view_latest=True, scroll=True, height=420
    )

    serve_component(page, col)

    # assert scroll location does not start at top
    column = page.locator(".bk-panel-models-layout-Column")
    bbox = column.bounding_box()

    assert bbox['width'] in (200, 215) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420

    expect(column).to_have_class('bk-panel-models-layout-Column scrollable-vertical')
    expect(column).not_to_have_js_property('scrollTop', '0')


def test_column_scroll_position_init(page):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=True, scroll_position=100, height=420
    )

    serve_component(page, col)

    # assert scroll position can be used to initialize scroll location
    column = page.locator('.bk-panel-models-layout-Column')
    expect(column).to_have_js_property('scrollTop', 100)


def test_column_scroll_position_recorded(page):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=True, height=420
    )

    serve_component(page, col)

    column = page.locator(".bk-panel-models-layout-Column")

    column.evaluate('(el) => el.scrollTop = 150')
    expect(column).to_have_js_property('scrollTop', 150)


def test_column_scroll_position_param_updated(page):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=True, height=420
    )

    serve_component(page, col)

    page.wait_for_timeout(200)

    col.scroll_position = 175

    column = page.locator(".bk-panel-models-layout-Column")
    expect(column).to_have_js_property('scrollTop', 175)


@pytest.mark.flaky(reruns=3)
def test_column_scroll_to(page):
    col = Column(
        *list(range(100)),
        height=300,
        sizing_mode="fixed",
        scroll=True,
    )

    serve_component(page, col)

    page.wait_for_timeout(200)

    # start at 0
    column_el = page.locator(".bk-panel-models-layout-Column")
    expect(column_el).to_have_js_property('scrollTop', 0)

    # scroll to 50
    col.scroll_to(50)
    expect(column_el).to_have_js_property('scrollTop', 1362)

    # scroll away using mouse wheel
    column_el.evaluate('(el) => el.scrollTo({top: 1000})')
    expect(column_el).to_have_js_property('scrollTop', 1000)

    # scroll to 50 again
    col.scroll_to(50)
    expect(column_el).to_have_js_property('scrollTop', 1362)
