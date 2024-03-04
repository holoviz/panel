from panel.chat.input import ChatAreaInput


class TestChatAreaInput:

    def test_chat_area_input(self):
        chat_area_input = ChatAreaInput()
        assert chat_area_input.auto_grow
        assert chat_area_input.max_rows == 10
        assert chat_area_input.resizable == "height"
