import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.chat import ChatMessage
from panel.tests.util import serve_component

pytestmark = pytest.mark.ui


def test_chat_message_dynamic_footer_objects(page):
    chat_msg = ChatMessage()
    serve_component(page, chat_msg)

    footer = page.get_by_text("It works!")
    expect(footer).to_have_count(0)

    chat_msg.footer_objects = ["It works!"]
    footer = page.get_by_text("It works!")
    expect(footer).to_have_count(1)


def test_chat_message_dynamic_header_objects(page):
    chat_msg = ChatMessage()
    serve_component(page, chat_msg)

    header = page.get_by_text("It works!")
    expect(header).to_have_count(0)

    chat_msg.header_objects = ["It works!"]
    header = page.get_by_text("It works!")
    expect(header).to_have_count(1)
