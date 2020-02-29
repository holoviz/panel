"""Implementation of the wired WebComponent"""
import param

from panel.models import WebComponent as _BkWebComponent
from panel.widgets.base import Widget
from typing import Set, Dict, Optional

from html.parser import HTMLParser
class AttributeParser(HTMLParser):
    first_tag: bool = True
    attr_dict: Optional[Dict] = None
    def handle_starttag(self, tag, attrs):
        if self.first_tag:
            for attr in attrs:
                self.attr_dict[attr[0]]=attr[1]
            self.first_tag=False

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

    _rename = {"title": None, "html": "innerHTML", "attributes_to_sync": "attributesToSync"}
    _widget_type = _BkWebComponent

    html = param.String()
    attributes_to_sync = param.Dict()

    def __init__(self, **params):
        # Avoid AttributeError: unexpected attribute ...
        for parameter in self._child_parameters():
            self._rename[parameter]=None

        super().__init__(**params)

        self.parser: HTMLParser  = AttributeParser()

    def _child_parameters(self) -> Set:
        """Returns a set of any new parameters added on self compared to WebComponent.

        """
        return set(self.param.objects())-set(WebComponent.param.objects())

    def parse_html_to_dict(self, html):
        self.parser.attr_dict={}
        self.parser.first_tag = True
        self.parser.feed(html)
        return self.parser.attr_dict