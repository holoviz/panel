"""Implementation of the wired WebComponent"""
import param

from panel.models import WebComponent as _BkWebComponent
from panel.widgets.base import Widget
from typing import Set



class WebComponent(Widget):
    """A Wired WebComponent

    Use the WebComponent by inheriting from it. An example would be

    ```
    class RadioButton(WebComponent):
    html = param.String('<wired-radio>Radio Two</wired-radio>')

    checked = param.Boolean(default=False)
    ```

    Please make sure the `checked` parameter and the web component `checked` attribute is in sync.

    - For Boolean parameters they should just be there in the html string if True and not if False.
    """

    _rename = {"title": None, "html": "innerHTML"}
    _widget_type = _BkWebComponent

    html = param.String()

    def __init__(self, **params):
        for parameter in self._child_parameters():
            self._rename[parameter]=None

        super().__init__(**params)

    def _child_parameters(self) -> Set:
        """Returns a set of any new parameters added on self compared to WebComponent.

        """
        return set(self.param.objects())-set(WebComponent.param.objects())