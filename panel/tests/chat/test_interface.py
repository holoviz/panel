import asyncio

from io import BytesIO

import pytest
import requests

from panel.chat.input import ChatAreaInput
from panel.chat.interface import ChatInterface
from panel.chat.message import ChatMessage
from panel.layout import Row, Tabs
from panel.pane import Image
from panel.tests.util import async_wait_until, wait_until
from panel.widgets.button import Button
from panel.widgets.input import FileInput, TextAreaInput, TextInput
from panel.widgets.select import RadioButtonGroup

ChatInterface.callback_exception = "raise"  # type: ignore


class TestChatInterface:
    @pytest.fixture
    def chat_interface(self):
        return ChatInterface()

    def test_init(self, chat_interface):
        assert len(chat_interface._button_data) == 5
        assert len(chat_interface._widgets) == 1
        assert isinstance(chat_interface._input_layout, Row)
        assert isinstance(chat_interface._widgets["ChatAreaInput"], ChatAreaInput)

        assert chat_interface.active == -1

        # Buttons added to input layout
        inputs = chat_interface._input_layout
        for index, button_data in enumerate(chat_interface._button_data.values()):
            widget = inputs[index + 1]
            assert isinstance(widget, Button)
            assert widget.name == button_data.name.title()

    def test_init_avatar_image(self, chat_interface):
        chat_interface.avatar = Image("https://panel.holoviz.org/_static/logo_horizontal.png")
        assert chat_interface.avatar.object == "https://panel.holoviz.org/_static/logo_horizontal.png"

    @pytest.mark.internet
    @pytest.mark.parametrize("type_", [bytes, BytesIO])
    def test_init_avatar_bytes(self, type_, chat_interface):
        with requests.get("https://panel.holoviz.org/_static/logo_horizontal.png") as resp:
            chat_interface.avatar = type_(resp.content)
        assert isinstance(chat_interface.avatar, type_)

    def test_init_custom_widgets(self):
        widgets = [TextInput(name="Text"), FileInput()]
        chat_interface = ChatInterface(widgets=widgets)
        assert len(chat_interface._widgets) == 2
        assert isinstance(chat_interface._input_layout, Tabs)
        assert isinstance(chat_interface._widgets["Text"], TextInput)
        assert isinstance(chat_interface._widgets["FileInput"], FileInput)
        assert chat_interface.active == 0

    def test_active_in_constructor(self):
        widgets = [TextInput(name="Text"), FileInput()]
        chat_interface = ChatInterface(widgets=widgets, active=1)
        assert chat_interface.active == 1

    def test_file_input_only(self):
        ChatInterface(widgets=[FileInput(name="CSV File", accept=".csv")])

    def test_active_widget(self, chat_interface):
        active_widget = chat_interface.active_widget
        assert isinstance(active_widget, ChatAreaInput)

    def test_active(self):
        widget = TextInput(name="input")
        chat_interface = ChatInterface(widgets=[widget])
        assert chat_interface.active == -1

    def test_active_multiple_widgets(self, chat_interface):
        widget1 = TextInput(name="input1")
        widget2 = TextInput(name="input2")
        chat_interface.widgets = [widget1, widget2]
        assert chat_interface.active == 0

        chat_interface.active = 1
        assert chat_interface.active == 1
        assert isinstance(chat_interface.active_widget, TextInput)

    async def test_click_send(self, chat_interface: ChatInterface):
        chat_interface.widgets = [TextAreaInput()]
        chat_interface.active_widget.value = "Message"
        # since it's TextAreaInput and NOT TextInput, need to manually send
        assert len(chat_interface.objects) == 0
        chat_interface._click_send(None)
        assert len(chat_interface.objects) == 1

    async def test_click_send_with_no_value_input(self, chat_interface: ChatInterface):
        chat_interface.widgets = [RadioButtonGroup(options=["A", "B"])]
        chat_interface.active_widget.value = "A"
        chat_interface._click_send(None)
        assert chat_interface.objects[0].object == "A"

    async def test_show_stop_disabled(self, chat_interface: ChatInterface):
        async def callback(msg, user, instance):
            yield "A"
            send_button = instance._buttons["send"]
            stop_button = instance._buttons["stop"]
            wait_until(lambda: send_button.visible)
            wait_until(lambda: send_button.disabled) #  should be disabled while callback is running
            assert not stop_button.visible
            yield "B"  # should not stream this

        chat_interface.callback = callback
        chat_interface.show_stop = False
        chat_interface.send("Message", respond=True)
        send_button = chat_interface._input_layout[1]
        stop_button = chat_interface._input_layout[2]
        assert send_button.name == "Send"
        assert stop_button.name == "Stop"
        assert send_button.visible
        assert not send_button.disabled
        assert not stop_button.visible

    async def test_show_stop_for_async(self, chat_interface: ChatInterface):
        async def callback(msg, user, instance):
            send_button = instance._buttons["send"]
            stop_button = instance._buttons["stop"]
            await async_wait_until(lambda: stop_button.visible)
            await async_wait_until(lambda: not send_button.visible)

        chat_interface.callback = callback
        chat_interface.send("Message", respond=True)
        send_button = chat_interface._input_layout[1]
        assert not send_button.disabled

    async def test_show_stop_for_async_generator(self, chat_interface: ChatInterface):
        async def callback(msg, user, instance):
            send_button = instance._buttons["send"]
            stop_button = instance._buttons["stop"]
            await async_wait_until(lambda: stop_button.visible)
            await async_wait_until(lambda: not send_button.visible)
            yield "Hello"

        chat_interface.callback = callback
        chat_interface.send("Message", respond=True)
        send_button = chat_interface._input_layout[1]
        assert not send_button.disabled

    async def test_show_stop_for_sync_generator(self, chat_interface: ChatInterface):
        def callback(msg, user, instance):
            send_button = instance._buttons["send"]
            stop_button = instance._buttons["stop"]
            wait_until(lambda: stop_button.visible)
            wait_until(lambda: not send_button.visible)
            yield "Hello"

        chat_interface.callback = callback
        chat_interface.send("Message", respond=True)
        send_button = chat_interface._input_layout[1]
        assert not send_button.disabled

    async def test_click_stop(self, chat_interface: ChatInterface):
        async def callback(msg, user, instance):
            send_button = instance._buttons["send"]
            stop_button = instance._buttons["stop"]
            await async_wait_until(lambda: stop_button.visible)
            await async_wait_until(lambda: not send_button.visible)
            instance._click_stop(None)

        chat_interface.callback = callback
        chat_interface.placeholder_threshold = 0.001
        try:
            chat_interface.send("Message", respond=True)
        except asyncio.exceptions.CancelledError:
            pass
        await async_wait_until(lambda: not chat_interface._buttons["send"].disabled)
        await async_wait_until(lambda: chat_interface._buttons["send"].visible)
        await async_wait_until(lambda: not chat_interface._buttons["stop"].visible)

    @pytest.mark.parametrize("widget", [TextInput(), TextAreaInput()])
    async def test_auto_send_types(self, chat_interface: ChatInterface, widget):
        chat_interface.auto_send_types = [TextAreaInput]
        chat_interface.widgets = [widget]
        chat_interface.active_widget.value = "Message"
        assert len(chat_interface.objects) == 1
        assert chat_interface.objects[0].object == "Message"

    async def test_click_undo(self, chat_interface):
        chat_interface.user = "User"
        chat_interface.send("Message 1")
        chat_interface.send("Message 2")
        chat_interface.send("Message 3", user="Assistant")
        expected = chat_interface.objects[-2:].copy()
        chat_interface._click_undo(None)
        assert len(chat_interface.objects) == 1
        assert chat_interface.objects[0].object == "Message 1"
        assert chat_interface._button_data["undo"].objects == expected

        # revert
        chat_interface._click_undo(None)
        assert len(chat_interface.objects) == 3
        assert chat_interface.objects[0].object == "Message 1"
        assert chat_interface.objects[1].object == "Message 2"
        assert chat_interface.objects[2].object == "Message 3"

    async def test_click_clear(self, chat_interface):
        chat_interface.send("Message 1")
        chat_interface.send("Message 2")
        chat_interface.send("Message 3")
        expected = chat_interface.objects.copy()
        chat_interface._click_clear(None)
        assert len(chat_interface.objects) == 0
        assert chat_interface._button_data["clear"].objects == expected

    async def test_click_rerun(self, chat_interface):
        self.count = 0

        def callback(contents, user, instance):
            self.count += 1
            return self.count

        chat_interface.callback = callback
        chat_interface.send("Message 1")
        await async_wait_until(lambda: len(chat_interface.objects) >= 2)
        await async_wait_until(lambda: chat_interface.objects[1].object == 1)
        chat_interface._click_rerun(None)
        await async_wait_until(lambda: len(chat_interface.objects) == 2 and chat_interface.objects[1].object == 2)

    async def test_click_rerun_null(self, chat_interface):
        chat_interface._click_rerun(None)
        assert len(chat_interface.objects) == 0

    def test_replace_widgets(self, chat_interface):
        assert isinstance(chat_interface._input_layout, Row)

        chat_interface.widgets = [TextAreaInput(), FileInput()]
        assert len(chat_interface._widgets) == 2
        assert isinstance(chat_interface._input_layout, Tabs)
        assert isinstance(chat_interface._widgets["TextAreaInput"], TextAreaInput)
        assert isinstance(chat_interface._widgets["FileInput"], FileInput)

    async def test_reset_on_send(self, chat_interface):
        chat_interface.active_widget.value = "Hello"
        chat_interface.reset_on_send = True
        assert chat_interface.active_widget.value == ""

    async def test_reset_on_send_text_area(self, chat_interface):
        chat_interface.widgets = TextAreaInput()
        chat_interface.reset_on_send = False
        chat_interface.active_widget.value = "Hello"
        assert chat_interface.active_widget.value == "Hello"

    def test_widgets_supports_list_and_widget(self, chat_interface):
        chat_interface.widgets = TextAreaInput()
        chat_interface.widgets = [TextAreaInput(), FileInput]

    def test_show_button_name_width(self, chat_interface):
        assert chat_interface.show_button_name
        assert chat_interface.width is None
        chat_interface.width = 200
        assert chat_interface.show_button_name
        assert chat_interface._input_layout[1].name == "Send"

    def test_show_button_name_set(self, chat_interface):
        chat_interface.show_button_name = False
        chat_interface.width = 800
        assert not chat_interface.show_button_name
        assert chat_interface._input_layout[1].name == ""

    def test_show_send_interactive(self, chat_interface):
        send_button = chat_interface._input_layout[1]
        assert chat_interface.show_send
        assert send_button.visible
        chat_interface.show_send = False
        assert not chat_interface.show_send
        assert not send_button.visible

    @pytest.mark.parametrize("key", ["callback", "post_callback"])
    async def test_button_properties_new_button(self, chat_interface, key):
        def callback(instance, event):
            instance.send("Checking if this works", respond=False)

        chat_interface.widgets = TextAreaInput()
        chat_interface.button_properties = {
            "check": {"icon": "check", key: callback},
        }
        chat_interface.active_widget.value = "This comes second"
        check_button = chat_interface._input_layout[-1]
        assert check_button.icon == "check"
        check_button.param.trigger("clicks")
        assert chat_interface.objects[0].object == "Checking if this works"

    async def test_button_properties_new_callback_and_post_callback(self, chat_interface):
        def pre_callback(instance, event):
            instance.send("1", respond=False)

        def post_callback(instance, event):
            instance.send("2", respond=False)

        chat_interface.widgets = TextAreaInput()
        chat_interface.button_properties = {
            "check": {"callback": pre_callback, "post_callback": post_callback},
        }
        check_button = chat_interface._input_layout[-1]
        check_button.param.trigger("clicks")
        assert chat_interface.objects[0].object == "1"
        assert chat_interface.objects[1].object == "2"

    async def test_button_properties_default_callback_and_post_callback(self, chat_interface):
        def post_callback(instance, event):
            instance.send("This should show", respond=False)

        chat_interface.button_properties = {
            "clear": {"post_callback": post_callback},
        }
        clear_button = chat_interface._input_layout[-1]
        chat_interface.send("This shouldn't show up!", respond=False)
        clear_button.param.trigger("clicks")
        assert chat_interface.objects[0].object == "This should show"

    async def test_button_properties_send_with_callback_no_duplicate(self, chat_interface):
        def post_callback(instance, event):
            instance.send("This should show", respond=False)

        chat_interface.widgets = TextAreaInput()
        chat_interface.button_properties = {
            "send": {"post_callback": post_callback},
        }
        chat_interface.active_widget.value = "This is it!"
        send_button = chat_interface._input_layout[1]
        send_button.param.trigger("clicks")
        assert chat_interface.objects[0].object == "This is it!"
        assert chat_interface.objects[1].object == "This should show"
        assert len(chat_interface.objects) == 2

    def test_button_properties_new_button_missing_callback(self, chat_interface):
        chat_interface.widgets = TextAreaInput()
        with pytest.raises(ValueError, match="A 'callback' key is required for"):
            chat_interface.button_properties = {
                "check": {"icon": "check"},
            }

    async def test_button_properties_update_default(self, chat_interface):
        def callback(instance, event):
            instance.send("This comes first", respond=False)

        chat_interface.widgets = TextAreaInput()
        chat_interface.button_properties = {
            "send": {"icon": "check", "callback": callback},
        }
        chat_interface.active_widget.value = "This comes second"
        send_button = chat_interface._input_layout[1]
        assert send_button.icon == "check"
        send_button.param.trigger("clicks")
        assert chat_interface.objects[0].object == "This comes first"
        assert chat_interface.objects[1].object == "This comes second"

    async def test_button_properties_update_default_icon(self, chat_interface):
        chat_interface.widgets = TextAreaInput()
        chat_interface.button_properties = {
            "send": {"icon": "check"},
        }
        chat_interface.active_widget.value = "Test test"
        send_button = chat_interface._input_layout[1]
        assert send_button.icon == "check"
        send_button.param.trigger("clicks")
        assert chat_interface.objects[0].object == "Test test"

    async def test_button_properties_update_callback_and_post_callback(self, chat_interface):
        def pre_callback(instance, event):
            instance.send("1", respond=False)

        def post_callback(instance, event):
            instance.send("3", respond=False)

        chat_interface.widgets = TextAreaInput()
        chat_interface.active_widget.value = "2"
        chat_interface.button_properties = {
            "send": {"callback": pre_callback, "post_callback": post_callback},
        }
        send_button = chat_interface._input_layout[1]
        send_button.param.trigger("clicks")
        assert chat_interface.objects[0].object == "1"
        assert chat_interface.objects[1].object == "2"
        assert chat_interface.objects[2].object == "3"

    def test_custom_js_no_code(self):
        chat_interface = ChatInterface()
        with pytest.raises(ValueError, match="A 'code' key is required for"):
            chat_interface.button_properties = {
                "help": {
                    "icon": "help",
                    "js_on_click": {
                        "args": {"chat_input": chat_interface.active_widget},
                    },
                },
            }

    async def test_manual_user(self):
        chat_interface = ChatInterface(user="New User")
        assert chat_interface.user == "New User"
        chat_interface.send("Test")
        assert chat_interface.objects[0].user == "New User"

    async def test_stream_chat_message(self, chat_interface):
        chat_interface.stream(ChatMessage("testeroo", user="useroo", avatar="avataroo"))
        chat_message = chat_interface.objects[0]
        assert chat_message.user == "useroo"
        assert chat_message.avatar == "avataroo"
        assert chat_message.object == "testeroo"

    def test_stream_chat_message_error_passed_user(self, chat_interface):
        with pytest.raises(ValueError, match="Cannot set user or avatar"):
            chat_interface.stream(ChatMessage(
                "testeroo", user="useroo", avatar="avataroo",
            ), user="newuser")

    def test_stream_chat_message_error_passed_avatar(self, chat_interface):
        with pytest.raises(ValueError, match="Cannot set user or avatar"):
            chat_interface.stream(ChatMessage(
                "testeroo", user="useroo", avatar="avataroo",
            ), avatar="newavatar")

    async def test_nested_disabled(self, chat_interface):
        PERSON_1 = "Happy User"
        PERSON_2 = "Excited User"
        PERSON_3 = "Passionate User"

        async def callback(contents: str, user: str, instance: ChatInterface):
            await asyncio.sleep(0.1)
            if user == "User":
                instance.send(
                    f"Hey, {PERSON_2}! Did you hear the user?",
                    user=PERSON_1,
                    avatar="😊",
                    respond=True,  # This is the default, but it's here for clarity
                )
            elif user == PERSON_1:
                user_message = instance.objects[-2]
                user_contents = user_message.object
                yield ChatMessage(
                    f'Yeah, they said "{user_contents}"! Did you also hear {PERSON_3}?',
                    user=PERSON_2,
                    avatar="😄",
                )
                instance.respond()
            elif user == PERSON_2:
                instance.send(
                    'Yup, I heard!',
                    user=PERSON_3,
                    avatar="😆",
                    respond=False,
                )

        chat_interface.callback = callback
        chat_interface.send("Hello")
        await async_wait_until(lambda: chat_interface.objects[-1].object == "Hey, Excited User! Did you hear the user?")
        assert chat_interface.disabled
        await async_wait_until(lambda: chat_interface.objects[-1].object == "Yup, I heard!")
        await asyncio.sleep(0.2)  # give a little time for enabling
        assert not chat_interface.disabled

    async def test_prevent_stream_override_message_user_avatar(self, chat_interface):
        msg = chat_interface.send("Hello", user="Welcoming User", avatar="👋")
        chat_interface.stream("New Hello", message=msg)
        assert msg.user == "Welcoming User"
        assert msg.avatar == "👋"

class TestChatInterfaceWidgetsSizingMode:
    def test_none(self):
        chat_interface = ChatInterface()
        assert chat_interface.sizing_mode == "stretch_width"
        assert chat_interface._chat_log.sizing_mode == "stretch_width"
        assert chat_interface._input_layout.sizing_mode == "stretch_width"
        assert chat_interface._input_layout[0].sizing_mode == "stretch_width"

    def test_fixed(self):
        chat_interface = ChatInterface(sizing_mode="fixed")
        assert chat_interface.sizing_mode == "fixed"
        assert chat_interface._chat_log.sizing_mode == "fixed"
        assert chat_interface._input_layout.sizing_mode == "stretch_width"
        assert chat_interface._input_layout[0].sizing_mode == "stretch_width"

    def test_stretch_both(self):
        chat_interface = ChatInterface(sizing_mode="stretch_both")
        assert chat_interface.sizing_mode == "stretch_both"
        assert chat_interface._chat_log.sizing_mode == "stretch_both"
        assert chat_interface._input_layout.sizing_mode == "stretch_width"
        assert chat_interface._input_layout[0].sizing_mode == "stretch_width"

    def test_stretch_width(self):
        chat_interface = ChatInterface(sizing_mode="stretch_width")
        assert chat_interface.sizing_mode == "stretch_width"
        assert chat_interface._chat_log.sizing_mode == "stretch_width"
        assert chat_interface._input_layout.sizing_mode == "stretch_width"
        assert chat_interface._input_layout[0].sizing_mode == "stretch_width"

    def test_stretch_height(self):
        chat_interface = ChatInterface(sizing_mode="stretch_height")
        assert chat_interface.sizing_mode == "stretch_height"
        assert chat_interface._chat_log.sizing_mode == "stretch_height"
        assert chat_interface._input_layout.sizing_mode == "stretch_width"
        assert chat_interface._input_layout[0].sizing_mode == "stretch_width"

    def test_scale_both(self):
        chat_interface = ChatInterface(sizing_mode="scale_both")
        assert chat_interface.sizing_mode == "scale_both"
        assert chat_interface._chat_log.sizing_mode == "scale_both"
        assert chat_interface._input_layout.sizing_mode == "stretch_width"
        assert chat_interface._input_layout[0].sizing_mode == "stretch_width"

    def test_scale_width(self):
        chat_interface = ChatInterface(sizing_mode="scale_width")
        assert chat_interface.sizing_mode == "scale_width"
        assert chat_interface._chat_log.sizing_mode == "scale_width"
        assert chat_interface._input_layout.sizing_mode == "stretch_width"
        assert chat_interface._input_layout[0].sizing_mode == "stretch_width"

    def test_scale_height(self):
        chat_interface = ChatInterface(sizing_mode="scale_height")
        assert chat_interface.sizing_mode == "scale_height"
        assert chat_interface._chat_log.sizing_mode == "scale_height"
        assert chat_interface._input_layout.sizing_mode == "stretch_width"
        assert chat_interface._input_layout[0].sizing_mode == "stretch_width"


@pytest.mark.xdist_group("chat")
class TestChatInterfaceEditCallback:

    @pytest.fixture
    def chat_interface(self):
        return ChatInterface()

    @pytest.mark.parametrize("method", ["send", "stream"])
    async def test_show_edit_icon_user(self, chat_interface, method):
        chat_interface.edit_callback = lambda content, index, instance: ""
        getattr(chat_interface, method)("Hello", user="User")
        assert chat_interface[0].show_edit_icon

    @pytest.mark.parametrize("method", ["send", "stream"])
    @pytest.mark.parametrize("user", ["admin", "Assistant", "Help"])
    async def test_not_show_edit_icon_user(self, chat_interface, user, method):
        chat_interface.edit_callback = lambda content, index, instance: ""
        getattr(chat_interface, method)("Hello", user=user)
        assert not chat_interface[0].show_edit_icon
