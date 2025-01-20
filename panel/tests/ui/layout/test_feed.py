import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel import Feed
from panel.layout.spacer import Spacer
from panel.tests.util import serve_component, wait_until

pytestmark = [pytest.mark.ui, pytest.mark.flaky(max_runs=3)]

ITEMS = 100  # 1000 items make the CI flaky

def test_feed_load_entries(page):
    feed = Feed(*list(range(ITEMS)), height=250)
    serve_component(page, feed)

    feed_el = page.locator(".bk-panel-models-feed-Feed")

    bbox = feed_el.bounding_box()
    assert bbox["height"] == 250

    expect(feed_el).to_have_class("bk-panel-models-feed-Feed scroll-vertical")

    children_count = feed_el.locator('.bk-panel-models-markup-HTML').count()
    assert 50 <= children_count <= 65

    # Now scroll to somewhere down
    feed_el.evaluate('(el) => el.scrollTo({top: 100})')
    children_count = feed_el.locator('.bk-panel-models-markup-HTML').count()
    assert 50 <= children_count <= 65

    # Now scroll to top
    feed_el.evaluate('(el) => el.scrollTo({top: 0})')
    wait_until(lambda: feed_el.locator('.bk-panel-models-markup-HTML').count() >= 50, page)

def test_feed_view_latest(page):
    feed = Feed(*list(range(ITEMS)), height=250, view_latest=True)
    serve_component(page, feed)

    feed_el = page.locator(".bk-panel-models-feed-Feed")

    bbox = feed_el.bounding_box()
    assert bbox["height"] == 250

    expect(feed_el).to_have_class("bk-panel-models-feed-Feed scroll-vertical")

    # Assert scroll is not at 0 (view_latest)
    wait_until(lambda: feed_el.evaluate('(el) => el.scrollTop') > 0, page)

    wait_until(lambda: int(page.locator('pre').last.inner_text() or 0) > 0.9 * ITEMS, page)


def test_feed_view_scroll_to_latest(page):
    feed = Feed(*list(range(ITEMS)), height=250)
    serve_component(page, feed)

    feed_el = page.locator(".bk-panel-models-feed-Feed")

    bbox = feed_el.bounding_box()
    assert bbox["height"] == 250

    expect(feed_el).to_have_class("bk-panel-models-feed-Feed scroll-vertical")

    # Assert scroll is not at 0 (view_latest)
    wait_until(lambda: feed_el.evaluate('(el) => el.scrollTop') == 0, page)

    feed.scroll_to_latest()

    wait_until(lambda: int(page.locator('pre').last.inner_text() or 0) > 0.9 * ITEMS, page)


def test_feed_scroll_to_latest_disabled_when_limit_zero(page):
    """Test that scroll_to_latest is disabled when scroll_limit = 0"""
    feed = Feed(*list(range(ITEMS)), height=250)
    serve_component(page, feed)

    feed_el = page.locator(".bk-panel-models-feed-Feed")
    initial_scroll = feed_el.evaluate('(el) => el.scrollTop')

    # Try to scroll to latest
    feed.scroll_to_latest(scroll_limit=0)

    # Verify scroll position hasn't changed
    final_scroll = feed_el.evaluate('(el) => el.scrollTop')
    assert initial_scroll == final_scroll, "Scroll position should not change when limit is 0"


def test_feed_scroll_to_latest_always_when_limit_null(page):
    """Test that scroll_to_latest always triggers when scroll_limit is null"""
    feed = Feed(*list(range(ITEMS)), height=250)
    serve_component(page, feed)

    wait_until(lambda: int(page.locator('pre').last.inner_text() or 0) < 0.9 * ITEMS, page)
    feed.scroll_to_latest(scroll_limit=None)
    wait_until(lambda: int(page.locator('pre').last.inner_text() or 0) > 0.9 * ITEMS, page)


def test_feed_scroll_to_latest_within_limit(page):
    """Test that scroll_to_latest only triggers within the specified limit"""
    feed = Feed(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        auto_scroll_limit=0, height=420
    )
    serve_component(page, feed)

    feed_el = page.locator(".bk-panel-models-feed-Feed")

    expect(feed_el).to_have_js_property('scrollTop', 0)

    feed.scroll_to_latest(scroll_limit=100)

    feed.append(Spacer(styles=dict(background='yellow'), width=200, height=200))

    # assert scroll location is still at top
    expect(feed_el.locator('div')).to_have_count(5)
    expect(feed_el).to_have_js_property('scrollTop', 0)

    # scroll to close to bottom
    feed_el.evaluate('(el) => el.scrollTo({top: 200})')
    expect(feed_el).to_have_js_property('scrollTop', 200)

    # assert auto scroll works; i.e. distance from bottom is 0
    feed.append(Spacer(styles=dict(background='yellow'), width=200, height=200))
    feed.scroll_to_latest(scroll_limit=1000)

    def assert_at_bottom():
        assert feed_el.evaluate(
            '(el) => el.scrollHeight - el.scrollTop - el.clientHeight'
        ) == 0
    wait_until(assert_at_bottom, page)


def test_feed_view_scroll_button(page):
    feed = Feed(*list(range(ITEMS)), height=250, scroll_button_threshold=50)
    serve_component(page, feed)

    feed_el = page.locator(".bk-panel-models-feed-Feed")

    # assert scroll button is visible on render
    scroll_arrow = page.locator(".scroll-button")
    expect(scroll_arrow).to_have_class('scroll-button visible')
    expect(scroll_arrow).to_be_visible()

    # click on scroll arrow
    scroll_arrow.click()

    # Assert scroll is not at 0 (view_latest)
    wait_until(lambda: feed_el.evaluate('(el) => el.scrollTop') > 0, page)
    wait_until(lambda: int(page.locator('pre').last.inner_text() or 0) > 50, page)

def test_feed_dynamic_objects(page):
    feed = Feed(height=250, load_buffer=10)
    serve_component(page, feed)

    feed.objects = list(range(ITEMS))

    wait_until(lambda: expect(page.locator('pre').first).to_have_text('0'))
    wait_until(lambda: page.locator('pre').count() > 10, page)
