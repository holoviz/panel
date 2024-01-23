from bokeh.core.properties import List, String
from bokeh.events import ModelEvent

from .layout import Column


class ScrollButtonClick(ModelEvent):

    event_name = 'scroll_button_click'

    def __init__(self, model, data=None):
        self.data = data
        super().__init__(model=model)


class Feed(Column):

    visible_children = List(String())
