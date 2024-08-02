import pytest

pytest.importorskip("playwright")


from panel.tests.util import serve_component, wait_until
from panel.widgets import Player

pytestmark = pytest.mark.ui


def test_player_faster_click_shows_ms(page):
    player = Player()
    serve_component(page, player)

    faster_element = page.locator(".faster")
    faster_element.click()

    wait_until(lambda: player.interval == 350)
    assert faster_element.inner_text() == "350ms"

    wait_until(lambda: faster_element.inner_text() == "")


def test_player_slower_click_shows_ms(page):
    player = Player()
    serve_component(page, player)

    slower_element = page.locator(".slower")
    slower_element.click()

    wait_until(lambda: player.interval == 714)
    assert slower_element.inner_text() == "714ms"

    wait_until(lambda: slower_element.inner_text() == "")
