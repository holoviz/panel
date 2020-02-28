"""Implementation of the Predix App Navigation Widget

See https://www.predix-ui.com/#/elements/px-app-nav"""
import pathlib

from bokeh.core import properties
from bokeh.models.layouts import HTMLBox

WEBCOMPONENT_TS_PATH = pathlib.Path(__file__).parent / "web_component.ts"
WEBCOMPONENT_TS_STR = str(WEBCOMPONENT_TS_PATH.resolve())


class WebComponent(HTMLBox):
    """A Predix App Navigation Widget

    See https://www.predix-ui.com/#/elements/px-app-nav"""

    __implementation__ = WEBCOMPONENT_TS_STR

    innerHTML = properties.String('')
