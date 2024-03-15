import pytest

pytest.importorskip("playwright")

from panel.chat import ChatInterface
from panel.tests.util import serve_component

pytestmark = pytest.mark.ui


def test_chat_interface_help(page):
    chat_interface = ChatInterface(
        help_text="This is a test help text"
    )
    serve_component(page, chat_interface)
    message = page.locator("p")
    message_text = message.inner_text()
    assert message_text == "This is a test help text"
