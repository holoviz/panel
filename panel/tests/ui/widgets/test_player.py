import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.tests.util import serve_component
from panel.widgets import Player

pytestmark = pytest.mark.ui


def test_init(page):
    player = Player()
    serve_component(page, player)

    assert not page.is_visible('label')
    assert page.query_selector('.pn-player-value') is None

def test_show_value(page):
    player = Player(show_value=True)
    serve_component(page, player)

    assert page.is_visible('label')
    assert page.query_selector('.pn-player-value') is not None


def test_name(page):
    player = Player(name='test')
    serve_component(page, player)

    assert page.is_visible('label')
    assert page.query_selector('.pn-player-value') is None

    name = page.locator('label:has-text("test")')
    expect(name).to_have_count(1)


def test_value_location(page):
    player = Player(name='test', value_location='top_right')
    serve_component(page, player)

    name = page.locator('label:has-text("test")')
    expect(name).to_have_css("text-align", "right")

def test_name_and_show_value(page):
    player = Player(name='test', show_value=True)
    serve_component(page, player)

    assert page.is_visible('label')
    assert page.query_selector('.pn-player-value') is not None

    name = page.locator('label:has-text("test")')
    expect(name).to_have_count(1)
