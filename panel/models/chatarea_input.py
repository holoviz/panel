from bokeh.events import ModelEvent

from .widgets import TextAreaInput


class ShiftEnterKeyDown(ModelEvent):

    event_name = 'shift_enter_key_down'

    def __init__(self, model, data=None):
        self.data = data
        super().__init__(model=model)


class ChatAreaInput(TextAreaInput):
    ...
