import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.chat import ChatInterface
from panel.tests.util import serve_component

pytestmark = pytest.mark.ui


def test_chat_interface_help(page):
    chat_interface = ChatInterface(
        help_text="This is a test help text"
    )
    serve_component(page, chat_interface)

    expect(page.locator("p")).to_have_text("This is a test help text")


def test_chat_interface_custom_js(page):
    chat_interface = ChatInterface()
    chat_interface.button_properties={
        "help": {
            "icon": "help",
            "js_on_click": {
                "code": "console.log(`Typed: '${chat_input.value}'`)",
                "args": {"chat_input": chat_interface.active_widget},
            },
        },
    }
    serve_component(page, chat_interface)

    chat_input = page.locator(".bk-input")
    chat_input.fill("Hello")

    with page.expect_console_message() as msg_info:
        page.locator("button", has_text="help").click()
        msg = msg_info.value

    assert msg.args[0].json_value() == "Typed: 'Hello'"


def test_chat_interface_custom_js_string(page):
    chat_interface = ChatInterface()
    chat_interface.button_properties={
        "help": {
            "icon": "help",
            "js_on_click": "console.log(`Clicked`)",
        },
    }
    serve_component(page, chat_interface)

    chat_input = page.locator(".bk-input")
    chat_input.fill("Hello")

    with page.expect_console_message() as msg_info:
        page.locator("button", has_text="help").click()
        msg = msg_info.value

    assert msg.args[0].json_value() == "Clicked"



def test_chat_interface_show_button_tooltips(page):
    chat_interface = ChatInterface(show_button_tooltips=True)
    serve_component(page, chat_interface)

    help_button = page.locator("button", has_text="send")
    help_button.hover()

    expect(page.locator(".bk-Tooltip")).to_be_visible()
