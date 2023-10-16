

import pytest

from panel.chat.interface import ChatInterface
from panel.layout import Row, Tabs
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
        assert len(chat_interface.value) == 1
        assert chat_interface.value[0].value == "Message"

    def test_click_undo(self, chat_interface):
        chat_interface.user = "User"
        chat_interface.send("Message 1")
        chat_interface.send("Message 2")
        chat_interface.send("Message 3", user="Assistant")
        expected = chat_interface.value[-2:].copy()
        chat_interface._click_undo(None)
        assert len(chat_interface.value) == 1
        assert chat_interface.value[0].value == "Message 1"
        assert chat_interface._button_data["undo"].objects == expected

        # revert
        chat_interface._click_undo(None)
        assert len(chat_interface.value) == 3
        assert chat_interface.value[0].value == "Message 1"
        assert chat_interface.value[1].value == "Message 2"
        assert chat_interface.value[2].value == "Message 3"

    def test_click_clear(self, chat_interface):
        chat_interface.send("Message 1")
        chat_interface.send("Message 2")
        chat_interface.send("Message 3")
        expected = chat_interface.value.copy()
        chat_interface._click_clear(None)
        assert len(chat_interface.value) == 0
        assert chat_interface._button_data["clear"].objects == expected

    def test_click_rerun(self, chat_interface):
        self.count = 0

        def callback(contents, user, instance):
            self.count += 1
            return self.count

        chat_interface.callback = callback
        chat_interface.send("Message 1")
        assert chat_interface.value[1].value == 1
        chat_interface._click_rerun(None)
        assert chat_interface.value[1].value == 2

    def test_click_rerun_null(self, chat_interface):
        chat_interface._click_rerun(None)
        assert len(chat_interface.value) == 0

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
        chat_interface._click_send(None)
        assert chat_interface.active_widget.value == ""

    def test_reset_on_send_text_area(self, chat_interface):
        chat_interface.widgets = TextAreaInput()
        chat_interface.active_widget.value = "Hello"
        chat_interface.reset_on_send = False
        chat_interface._click_send(None)
        assert chat_interface.active_widget.value == "Hello"

    def test_widgets_supports_list_and_widget(self, chat_interface):
        chat_interface.widgets = TextAreaInput()
        chat_interface.widgets = [TextAreaInput(), FileInput]

    def test_show_button_name_width(self, chat_interface):
        assert chat_interface.show_button_name
        assert chat_interface.width is None
        chat_interface.width = 200
        assert chat_interface.show_button_name

    def test_show_button_name_set(self, chat_interface):
        chat_interface.show_button_name = False
        chat_interface.width = 800
        assert not chat_interface.show_button_name

class TestChatInterfaceWidgetsSizingMode:
    def test_none(self):
        chat_interface = ChatInterface()
        assert chat_interface.sizing_mode is None
        assert chat_interface._chat_log.sizing_mode is None
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
