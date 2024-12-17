from typing import Any

from bokeh.core.properties import List, String
from bokeh.events import ModelEvent

from .layout import Column


class ScrollLatestEvent(ModelEvent):

    event_name = 'scroll_latest_event'

    def __init__(self, model, rerender=False):
        super().__init__(model=model)
        self.rerender = rerender

    def event_values(self) -> dict[str, Any]:
        return dict(super().event_values(), rerender=self.rerender)


class ScrollButtonClick(ModelEvent):

    event_name = 'scroll_button_click'

    def __init__(self, model, data=None):
        self.data = data
        super().__init__(model=model)


class Feed(Column):

    visible_children = List(String())
