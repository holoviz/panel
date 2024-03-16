from bokeh.core.properties import Bool
from bokeh.events import ModelEvent

from .widgets import TextAreaInput


class ChatMessageEvent(ModelEvent):

    event_name = 'chat_message_event'

    def __init__(self, model, value=None):
        self.value = value
        super().__init__(model=model)


class ChatAreaInput(TextAreaInput):

    disabled_enter = Bool(default=False, help="""
        If True, the enter key will not submit the message (clear the value).""")
