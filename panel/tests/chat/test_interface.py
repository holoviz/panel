

from io import BytesIO

import pytest
import requests

from panel.chat.interface import ChatInterface
from panel.layout import Row, Tabs
from panel.pane import Image
from panel.widgets.button import Button
from panel.widgets.input import FileInput, TextAreaInput, TextInput


class TestChatInterface:
    @pytest.fixture
    def chat_interface(self):
        return ChatInterface()

    def test_init(self, chat_interface):
        assert len(chat_interface._button_data) == 4
        assert len(chat_interface._widgets) == 1
        assert isinstance(chat_interface._input_layout, Row)
        assert isinstance(chat_interface._widgets["TextInput"], TextInput)

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
        assert isinstance(active_widget, TextInput)

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

    def test_click_send(self, chat_interface: ChatInterface):
        chat_interface.widgets = [TextAreaInput()]
        chat_interface.active_widget.value = "Message"
        # since it's TextAreaInput and NOT TextInput, need to manually send
        assert len(chat_interface.objects) == 0
        chat_interface._click_send(None)
        assert len(chat_interface.objects) == 1
        assert chat_interface.objects[0].object == "Message"

    @pytest.mark.parametrize("widget", [TextInput(), TextAreaInput()])
    def test_auto_send_types(self, chat_interface: ChatInterface, widget):
        chat_interface.auto_send_types = [TextAreaInput]
        chat_interface.widgets = [widget]
        chat_interface.active_widget.value = "Message"
        assert len(chat_interface.objects) == 1
        assert chat_interface.objects[0].object == "Message"

    def test_click_undo(self, chat_interface):
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

    def test_click_clear(self, chat_interface):
        chat_interface.send("Message 1")
        chat_interface.send("Message 2")
        chat_interface.send("Message 3")
        expected = chat_interface.objects.copy()
        chat_interface._click_clear(None)
        assert len(chat_interface.objects) == 0
        assert chat_interface._button_data["clear"].objects == expected

    def test_click_rerun(self, chat_interface):
        self.count = 0

        def callback(contents, user, instance):
            self.count += 1
            return self.count

        chat_interface.callback = callback
        chat_interface.send("Message 1")
        assert chat_interface.objects[1].object == 1
        chat_interface._click_rerun(None)
        assert chat_interface.objects[1].object == 2

    def test_click_rerun_null(self, chat_interface):
        chat_interface._click_rerun(None)
        assert len(chat_interface.objects) == 0

    def test_replace_widgets(self, chat_interface):
        assert isinstance(chat_interface._input_layout, Row)

        chat_interface.widgets = [TextAreaInput(), FileInput()]
        assert len(chat_interface._widgets) == 2
        assert isinstance(chat_interface._input_layout, Tabs)
        assert isinstance(chat_interface._widgets["TextAreaInput"], TextAreaInput)
        assert isinstance(chat_interface._widgets["FileInput"], FileInput)

    def test_reset_on_send(self, chat_interface):
        chat_interface.active_widget.value = "Hello"
        chat_interface.reset_on_send = True
        assert chat_interface.active_widget.value == ""

    def test_reset_on_send_text_area(self, chat_interface):
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
    def test_button_properties_new_button(self, chat_interface, key):
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

    def test_button_properties_new_callback_and_post_callback(self, chat_interface):
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

    def test_button_properties_new_button_missing_callback(self, chat_interface):
        chat_interface.widgets = TextAreaInput()
        with pytest.raises(ValueError, match="A 'callback' key is required for"):
            chat_interface.button_properties = {
                "check": {"icon": "check"},
            }

    def test_button_properties_update_default(self, chat_interface):
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

    def test_button_properties_update_default_icon(self, chat_interface):
        chat_interface.widgets = TextAreaInput()
        chat_interface.button_properties = {
            "send": {"icon": "check"},
        }
        chat_interface.active_widget.value = "Test test"
        send_button = chat_interface._input_layout[1]
        assert send_button.icon == "check"
        send_button.param.trigger("clicks")
        assert chat_interface.objects[0].object == "Test test"

    def test_button_properties_update_callback_and_post_callback(self, chat_interface):
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
