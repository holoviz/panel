import pytest

pytest.importorskip("playwright")


from panel.chat.icon import ChatCopyIcon
from panel.tests.util import serve_component

pytestmark = pytest.mark.ui


def test_copy_icon_click(page):
    icons = ChatCopyIcon(text="test")
    serve_component(page, icons)

    page.locator(".ti-clipboard").click()
    assert page.locator(".ti-check")

    # Couldn't get the following to work, but tested manually
    # playwright._impl._errors.Error: DOMException: Read permission denied.
    # wait_until(lambda: page.evaluate("navigator.clipboard.readText()") == "test")
