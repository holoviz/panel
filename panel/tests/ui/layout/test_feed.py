import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel import Feed
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui

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

    wait_until(lambda: int(page.locator('pre').last.inner_text()) > 0.9 * ITEMS, page)

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
    import time
    time.sleep(5)

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
    wait_until(lambda: int(page.locator('pre').last.inner_text()) > 50, page)

def test_feed_dynamic_objects(page):
    feed = Feed(height=250, load_buffer=10)
    serve_component(page, feed)

    feed.objects = list(range(ITEMS))

    wait_until(lambda: expect(page.locator('pre').first).to_have_text('0'))
    wait_until(lambda: page.locator('pre').count() > 10, page)
