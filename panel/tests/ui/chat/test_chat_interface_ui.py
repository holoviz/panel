import asyncio

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


def test_chat_interface_edit_message(page):
    def echo_callback(content, index, instance):
        return content

    def edit_callback(content, index, instance):
        instance.objects[index + 1].object = content

    chat_interface = ChatInterface(edit_callback=edit_callback, callback=echo_callback)
    chat_interface.send("Edit this")

    serve_component(page, chat_interface)

    # find the edit icon and click .ti.ti-edit
    # trict mode violation: locator(".ti-edit") resolved to 2 elements
    page.locator(".ti-edit").first.click()

    # find the input field and type new message
    chat_input = page.locator(".bk-input").first
    page.wait_for_timeout(200)
    chat_input.fill("Edited")

    # click enter
    chat_input.press("Enter")

    expect(page.locator(".message").first).to_have_text("Edited")
    for object in chat_interface.objects:
        assert object.object == "Edited"


def test_chat_interface_adaptive(page):
    async def echo_callback(content, user, instance):
        for i in range(3):
            await asyncio.sleep(0.1)
            instance.send(content + str(i), respond=False)

    chat_interface = ChatInterface(adaptive=True, callback=echo_callback)

    serve_component(page, chat_interface)

    chat_input = page.locator(".bk-input").first
    chat_input.fill("Hello")
    chat_input.press("Enter")
    expect(page.locator(".message").first).to_have_text("Hello")

    # wait for the first callback response
    page.wait_for_timeout(200)
    expect(page.locator(".message").nth(1)).to_have_text("Hello0")

    # Send another message while callback is still running
    chat_input.fill("World")
    chat_input.press("Enter")

    expect(page.locator(".message").nth(2)).to_have_text("World")

    # Wait for responses to complete
    page.wait_for_timeout(1000)

    # In adaptive mode, the second message interrupts the first callback
    # So we should have: Hello, Hello0, World, World0, World1, World2
    messages = page.locator(".message")
    expect(messages).to_have_count(6)  # 2 user messages + 4 callback responses (1 from first, 3 from second)

    # Verify the content of the messages
    expect(page.locator(".message").nth(0)).to_have_text("Hello")
    expect(page.locator(".message").nth(1)).to_have_text("Hello0")
    expect(page.locator(".message").nth(2)).to_have_text("World")
    expect(page.locator(".message").nth(3)).to_have_text("World0")
    expect(page.locator(".message").nth(4)).to_have_text("World1")
    expect(page.locator(".message").nth(5)).to_have_text("World2")


def test_chat_interface_adaptive_double_interruption(page):
    async def slow_callback(content, user, instance):
        for i in range(5):
            await asyncio.sleep(0.2)
            instance.send(f"{content} - step {i}", respond=False)

    chat_interface = ChatInterface(adaptive=True, callback=slow_callback)

    serve_component(page, chat_interface)

    chat_input = page.locator(".bk-input").first

    # Send first message
    chat_input.fill("First")
    chat_input.press("Enter")
    expect(page.locator(".message").first).to_have_text("First")

    # Wait for first response to start, then interrupt with second message
    page.wait_for_timeout(300)
    expect(page.locator(".message").nth(1)).to_have_text("First - step 0")

    chat_input.fill("Second")
    chat_input.press("Enter")
    expect(page.locator(".message").nth(2)).to_have_text("Second")

    # Wait for second response to start, then interrupt with third message
    page.wait_for_timeout(300)
    expect(page.locator(".message").nth(3)).to_have_text("Second - step 0")

    chat_input.fill("Third")
    chat_input.press("Enter")
    expect(page.locator(".message").nth(4)).to_have_text("Third")

    # Wait for the final response to complete without interruption
    page.wait_for_timeout(1200)

    # Verify final state: user messages + only the last callback responses
    expected_messages = [
        "First",
        "First - step 0",
        "Second",
        "Second - step 0",
        "Third",
        "Third - step 0",
        "Third - step 1",
        "Third - step 2",
        "Third - step 3",
        "Third - step 4"
    ]

    for i, expected_text in enumerate(expected_messages):
        expect(page.locator(".message").nth(i)).to_have_text(expected_text)

    # Verify the chat interface has the correct number of objects
    assert len(chat_interface.objects) == len(expected_messages)
