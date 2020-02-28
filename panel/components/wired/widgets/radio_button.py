"""Implementation of the wired RadioButton"""
import param

from panel.components.wired.models import RadioButton as _BkRadioButton
from panel.widgets.base import Widget


class RadioButton(Widget):
    """A Wired RadioButton"""

    _rename = {"title": None}
    _widget_type = _BkRadioButton

    html = param.String('<wired-radio checked id="1" checked>Radio Two</wired-radio>')


if __name__.startswith("bk"):
    import panel as pn

    js = """
<script src="https://unpkg.com/@webcomponents/webcomponentsjs@2.0.0/webcomponents-loader.js"></script>
<script type="module" src="https://unpkg.com/wired-elements@0.6.4/dist/wired-elements.bundled.js"></script>
"""


    radio_button = RadioButton()
    pn.config.sizing_mode="stretch_width"
    pn.Column(pn.pane.HTML(js), radio_button, pn.Param(radio_button.param.html)).servable()
