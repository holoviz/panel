import pytest

pytest.importorskip("playwright")


from panel.chat.icon import ChatCopyIcon
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui


def test_copy_icon_click(page):
    icons = ChatCopyIcon(text="test")
    serve_component(page, icons)

    page.locator(".ti-clipboard").click()
    wait_until(lambda: page.evaluate("navigator.clipboard.readText()") == "test")
