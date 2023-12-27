import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel import Log
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui


def test_log_load_entries(page):
    log = Log(*list(range(1000)), height=250)
    serve_component(page, log)

    log_el = page.locator(".bk-panel-models-layout-Log")

    bbox = log_el.bounding_box()
    assert bbox["height"] == 250

    expect(log_el).to_have_class("bk-panel-models-layout-Log scrollable-vertical")

    children_count = log_el.evaluate(
        '(element) => element.shadowRoot.querySelectorAll(".bk-panel-models-markup-HTML").length'
    )
    assert children_count == 20

    # Assert scroll is not at 0 (view_latest)
    assert log_el.evaluate('(el) => el.scrollTop') > 0

    # Now scroll to somewhere below threshold
    log_el.evaluate('(el) => el.scrollTo({top: 100})')
    children_count = log_el.evaluate(
        '(element) => element.shadowRoot.querySelectorAll(".bk-panel-models-markup-HTML").length'
    )
    assert children_count == 20

    # Now scroll to top
    log_el.evaluate('(el) => el.scrollTo({top: 0})')
    wait_until(
        lambda: log_el.evaluate(
            '(element) => element.shadowRoot.querySelectorAll(".bk-panel-models-markup-HTML").length'
        )
        == 40
    )
