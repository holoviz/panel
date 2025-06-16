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
            await asyncio.sleep(0.5)
            instance.send(content + str(i), respond=False)

    chat_interface = ChatInterface(adaptive=True, callback=echo_callback)

    serve_component(page, chat_interface)

    chat_input = page.locator(".bk-input").first
    chat_input.fill("Hello")
    chat_input.press("Enter")
    expect(page.locator(".message").first).to_have_text("Hello")

    # Wait for the first callback response to appear
    expect(page.locator(".message").nth(1)).to_have_text("Hello0", timeout=5000)

    # Send another message while callback is still running
    chat_input.fill("World")
    chat_input.press("Enter")

    page.wait_for_timeout(1000)

    # If not in expected positions, check all messages
    world_found = False
    for i in range(4):
        messages = page.locator(".message")
        try:
            expect(messages.nth(i)).to_contain_text("World", timeout=1000)
            world_found = True
            break
        except Exception:
            # If the message is not found in this position, try the next one
            continue
    assert world_found, "Expected to find 'World' message after interruption"

    # Wait for responses to complete
    page.wait_for_timeout(1000)

    # In adaptive mode, the second message interrupts the first callback
    # So we should have fewer messages than if both callbacks completed fully
    messages = page.locator(".message")  # Re-query to get final count
    message_count = messages.count()
    assert message_count < 8, f"Expected less than 8 messages, got {message_count}"


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

    # Wait for first response to appear
    expect(page.locator(".message").nth(1)).to_have_text("First - step 0", timeout=5000)

    # Send second message while first callback is still running
    chat_input.fill("Second")
    chat_input.press("Enter")

    # If not in expected positions, check all messages
    second_found = False
    for i in range(2, 6):
        messages = page.locator(".message")
        try:
            expect(messages.nth(i)).to_contain_text("Second", timeout=1000)
            second_found = True
            break
        except Exception:
            # If the message is not found in this position, try the next one
            continue
    assert second_found, "Expected to find 'Second' message after interruption"

    # Send third message while both callbacks are running
    chat_input.fill("Third")
    chat_input.press("Enter")

    # If not in expected positions, check all messages
    third_found = False
    for i in range(2, 6):
        messages = page.locator(".message")
        try:
            expect(messages.nth(i)).to_contain_text("Third", timeout=1000)
            third_found = True
            break
        except Exception:
            # If the message is not found in this position, try the next one
            continue
    assert third_found, "Expected to find 'Third' message after second interruption"

    # Wait for responses to complete
    page.wait_for_timeout(1000)
    messages = page.locator(".message")  # Re-query to get final count
    message_count = messages.count()
    assert message_count < 10, f"Expected less than 10 messages, got {message_count}"
