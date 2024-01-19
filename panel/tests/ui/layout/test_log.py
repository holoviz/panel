import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel import Log
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui


def test_log_load_entries(page):
    log = Log(*list(range(1000)), height=250)
    serve_component(page, log)

    log_el = page.locator(".bk-panel-models-log-Log")

    bbox = log_el.bounding_box()
    assert bbox["height"] == 250

    expect(log_el).to_have_class("bk-panel-models-log-Log scrollable-vertical")

    children_count = log_el.evaluate(
        '(element) => element.shadowRoot.querySelectorAll(".bk-panel-models-markup-HTML").length'
    )
    assert children_count == 50

    # Now scroll to somewhere down
    log_el.evaluate('(el) => el.scrollTo({top: 100})')
    children_count = log_el.evaluate(
        '(element) => element.shadowRoot.querySelectorAll(".bk-panel-models-markup-HTML").length'
    )
    assert children_count == 50

    # Now scroll to top
    log_el.evaluate('(el) => el.scrollTo({top: 0})')
    wait_until(
        lambda: log_el.evaluate(
            '(element) => element.shadowRoot.querySelectorAll(".bk-panel-models-markup-HTML").length'
        )
        == 50
    )


def test_log_view_latest(page):
    log = Log(*list(range(1000)), height=250, view_latest=True)
    serve_component(page, log)

    log_el = page.locator(".bk-panel-models-log-Log")

    bbox = log_el.bounding_box()
    assert bbox["height"] == 250

    expect(log_el).to_have_class("bk-panel-models-log-Log scrollable-vertical")

    # Assert scroll is not at 0 (view_latest)
    assert log_el.evaluate('(el) => el.scrollTop') > 0

    # playwright get the last <pre> element
    last_pre_element = page.query_selector_all('pre')[-1]
    assert last_pre_element.inner_text() == "999"


def test_log_view_scroll_button(page):
    log = Log(*list(range(1000)), height=250, scroll_button_threshold=50)
    serve_component(page, log)

    log_el = page.locator(".bk-panel-models-log-Log")

    # assert scroll button is visible on render
    scroll_arrow = page.locator(".scroll-button")
    expect(scroll_arrow).to_have_class('scroll-button visible')
    expect(scroll_arrow).to_be_visible()

    # click on scroll arrow
    scroll_arrow.click()

    # Assert scroll is not at 0 (view_latest)
    assert log_el.evaluate('(el) => el.scrollTop') > 0
    wait_until(
        lambda: int(page.query_selector_all('pre')[-1].inner_text()) > 50
    )
