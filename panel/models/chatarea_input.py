from bokeh.events import ModelEvent

from .widgets import TextAreaInput


class ChatMessageEvent(ModelEvent):

    event_name = 'chat_message_event'

    def __init__(self, model, value=None):
        self.value = value
        super().__init__(model=model)


class ChatAreaInput(TextAreaInput):
    ...
