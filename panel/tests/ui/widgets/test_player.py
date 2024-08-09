import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.tests.util import serve_component, wait_until
from panel.widgets import Player

pytestmark = pytest.mark.ui


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
def test_player_visible_buttons(page):
    player = Player(visible_buttons=["play", "pause"])
    serve_component(page, player)

    assert page.is_visible(".play")
    assert page.is_visible(".pause")
    assert not page.is_visible(".reverse")
    assert not page.is_visible(".first")
    assert not page.is_visible(".previous")
    assert not page.is_visible(".next")
    assert not page.is_visible(".last")
    assert not page.is_visible(".slower")
    assert not page.is_visible(".faster")

    player.visible_buttons = ["first"]
    wait_until(lambda: page.is_visible(".first"))
    assert not page.is_visible(".play")
    assert not page.is_visible(".pause")


def test_player_visible_loop_options(page):
    player = Player(visible_loop_options=["loop", "once"])
    serve_component(page, player)

    assert page.is_visible(".loop")
    assert page.is_visible(".once")
    assert not page.is_visible(".reflect")

    player.visible_loop_options = ["reflect"]
    wait_until(lambda: page.is_visible(".reflect"))
    assert not page.is_visible(".loop")
    assert not page.is_visible(".once")


def test_player_scale_buttons(page):
    player = Player(scale_buttons=2)
    serve_component(page, player)

    expect(page.locator(".play")).to_have_attribute(
        "style",
        "text-align: center; flex-grow: 2; margin: 2px; transform: scale(2); max-width: 50px;",
    )
