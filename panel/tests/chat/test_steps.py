import pytest

from panel.chat.steps import ChatStep, ChatSteps
from panel.pane.markup import Markdown


class TestChatSteps:
    def test_append_step(self):
        chat_steps = ChatSteps()
        chat_step = chat_steps.append_step("Hello World")
        assert isinstance(chat_step, ChatStep)
        assert len(chat_steps.objects) == 1
        assert chat_steps.objects[0] == chat_step
        assert isinstance(chat_steps.objects[0].objects[0], Markdown)
        assert chat_steps.objects[0].objects[0].object == "Hello World"

    def test_append_step_to_inactive(self):
        chat_steps = ChatSteps()
        with chat_steps:
            pass
        with pytest.raises(ValueError):
            chat_steps.append_step("Hello World")

    def test_validate_steps_with_invalid_step(self):
        chat_steps = ChatSteps()
        with pytest.raises(ValueError):
            chat_steps.append("Not a ChatStep")

    def test_active_state_management(self):
        chat_steps = ChatSteps()
        with chat_steps:
            assert chat_steps.active is True
        assert chat_steps.active is False

    def test_serialization(self):
        chat_steps = ChatSteps()
        chat_steps.append_step("Test Serialization")
        serialized_data = chat_steps.serialize()
        assert "Test Serialization" in serialized_data
