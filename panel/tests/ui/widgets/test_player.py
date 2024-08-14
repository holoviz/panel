import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.tests.util import serve_component, wait_until
from panel.widgets import Player

pytestmark = pytest.mark.ui


def test_player_faster_click_shows_ms(page):
    player = Player()
    serve_component(page, player)

    faster_element = page.locator(".faster")
    faster_element.click()

    wait_until(lambda: player.interval == 350)
    assert faster_element.inner_text() == "2.9\nfps"

    wait_until(lambda: faster_element.inner_text() == "")


def test_player_slower_click_shows_ms(page):
    player = Player()
    serve_component(page, player)

    slower_element = page.locator(".slower")
    slower_element.click()

    wait_until(lambda: player.interval == 714)
    assert slower_element.inner_text() == "1.4\nfps"

    wait_until(lambda: slower_element.inner_text() == "")


def test_init(page):
    player = Player()
    serve_component(page, player)

    assert not page.is_visible('pn-player-value')
    assert page.query_selector('.pn-player-value') is None


def test_show_value(page):
    player = Player(show_value=True)
    serve_component(page, player)

    wait_until(lambda: page.query_selector('.pn-player-value') is not None)
    assert page.query_selector('.pn-player-value') is not None


def test_name(page):
    player = Player(name='test')
    serve_component(page, player)

    assert page.is_visible('label')
    assert page.query_selector('.pn-player-value') is None

    name = page.locator('.pn-player-title:has-text("test")')
    expect(name).to_have_count(1)


def test_value_align(page):
    player = Player(name='test', value_align='end')
    serve_component(page, player)

    name = page.locator('.pn-player-title:has-text("test")')
    expect(name).to_have_css("text-align", "right")


def test_name_and_show_value(page):
    player = Player(name='test', show_value=True)
    serve_component(page, player)

    assert page.is_visible('label')
    assert page.query_selector('.pn-player-value') is not None

    name = page.locator('.pn-player-title:has-text("test")')
    expect(name).to_have_count(1)
