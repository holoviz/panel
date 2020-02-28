"""Implementation of the Predix App Navigation Widget

See https://www.predix-ui.com/#/elements/px-app-nav"""
import pathlib

from bokeh.core import properties
from bokeh.models.layouts import HTMLBox

RADIOBUTTON_TS_PATH = pathlib.Path(__file__).parent / "radio_button.ts"
RADIOBUTTON_TS_STR = str(RADIOBUTTON_TS_PATH.resolve())


class RadioButton(HTMLBox):
    """A Predix App Navigation Widget

    See https://www.predix-ui.com/#/elements/px-app-nav"""

    __implementation__ = RADIOBUTTON_TS_STR

    html = properties.String('{"label":"Home","id":"home","icon":"px-fea:home"}')
