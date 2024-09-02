import pytest

pytest.importorskip("playwright")

from panel import bind
from panel.chat import ChatAreaInput
from panel.pane import Markdown
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui


def test_chat_area_input_enter(page):
    def output(value):
        return value

    chat_area_input = ChatAreaInput()
    output_markdown = Markdown()
    output_markdown.object = bind(output, chat_area_input.param.value)
    serve_component(page, chat_area_input)

    # find chat area input and type a message
    textbox = page.locator(".bk-input")
    textbox.fill("Hello World!")
    wait_until(lambda: chat_area_input.value_input == "Hello World!", page)
    assert chat_area_input.value == ""
    assert output_markdown.object == ""

    # Click enter with textbox having focus
    textbox.press("Enter")
    wait_until(lambda: chat_area_input.value_input == "", page)
    assert chat_area_input.value == ""
    assert output_markdown.object == "Hello World!"

    textbox.fill("Try again now!")
    # lose focus and click enter
    page.keyboard.press("Tab")
    wait_until(lambda: chat_area_input.value_input == "Try again now!", page)
    assert chat_area_input.value == ""
    assert output_markdown.object == "Hello World!"
    page.keyboard.press("Enter")
    wait_until(lambda: chat_area_input.value_input == "Try again now!", page)
    textbox.press("Enter")
    wait_until(lambda: chat_area_input.value_input == "", page)
    assert chat_area_input.value == ""
    assert output_markdown.object == "Try again now!"


def test_chat_area_input_resets_to_row(page):

    chat_area_input = ChatAreaInput(rows=2)
    serve_component(page, chat_area_input)

    # find chat area input and type a message
    textbox = page.locator(".bk-input")
    textbox.fill("Hello World!")

    # click shift_enter 3 times
    textbox.press("Shift+Enter")
    textbox.press("Shift+Enter")
    textbox.press("Shift+Enter")
    wait_until(lambda: chat_area_input.value_input == "Hello World!\n\n\n", page)
    assert chat_area_input.value == ""
    textbox_rows = textbox.evaluate("el => el.rows")
    assert textbox_rows == 4

    # Click enter with textbox having focus
    textbox.press("Enter")
    wait_until(lambda: chat_area_input.value_input == "", page)
    assert chat_area_input.value == ""
    textbox_rows = textbox.evaluate("el => el.rows")
    assert textbox_rows == 2


def test_chat_area_enter_sends(page):

    chat_area_input = ChatAreaInput()
    serve_component(page, chat_area_input)

    # find chat area input
    textbox = page.locator(".bk-input")

    # Case enter_sends is True
    chat_area_input.enter_sends = True
    textbox.fill("enter_sends: True")
    wait_until(lambda: chat_area_input.value_input == "enter_sends: True", page)
    textbox.press("Shift+Enter")
    wait_until(lambda: chat_area_input.value_input == "enter_sends: True\n", page)
    textbox.press("Control+Enter")
    wait_until(lambda: chat_area_input.value_input == "enter_sends: True\n\n", page)
    textbox_rows = textbox.evaluate("el => el.rows")
    assert textbox_rows == 3

    textbox.press("Enter")
    wait_until(lambda: chat_area_input.value_input == "", page)
    assert chat_area_input.value == ""

    # Case enter_sends is False
    chat_area_input.enter_sends = False
    textbox.fill("enter_sends: False")
    wait_until(lambda: chat_area_input.value_input == "enter_sends: False", page)
    textbox.press("Enter")
    wait_until(lambda: chat_area_input.value_input == "enter_sends: False\n", page)
    textbox.press("Shift+Enter")
    wait_until(lambda: chat_area_input.value_input == "enter_sends: False\n\n", page)
    textbox_rows = textbox.evaluate("el => el.rows")
    assert textbox_rows == 3
    textbox.press("Control+Enter")
    wait_until(lambda: chat_area_input.value_input == "", page)
    assert chat_area_input.value == ""
