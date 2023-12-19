import pytest

pytest.importorskip("playwright")


from panel.chat import ChatReactionIcons
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui


def test_toggle_icon_click(page):
    icons = ChatReactionIcons(options={"like": "thumb-up", "dislike": "thumb-down"}, value=["dislike"])
    serve_component(page, icons)

    assert icons.value == ["dislike"]
    page.locator(".ti-thumb-up").click()
    wait_until(lambda: icons.value == ["dislike", "like"], page)

    page.locator(".ti-thumb-down-filled").click()
    wait_until(lambda: icons.value == ["like"], page)

    page.locator(".ti-thumb-up-filled").click()
    wait_until(lambda: icons.value == [], page)

    page.locator(".ti-thumb-up").click()
    wait_until(lambda: icons.value == ["like"], page)
