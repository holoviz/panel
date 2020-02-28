"""Implementation of the wired WebComponent"""
import param

from panel.models import WebComponent as _BkWebComponent
from panel.widgets.base import Widget


class WebComponent(Widget):
    """A Wired WebComponent"""

    _rename = {"title": None, "html": "innerHTML"}
    _widget_type = _BkWebComponent

    html = param.String('<wired-radio checked id="1" checked>Radio Two</wired-radio>')