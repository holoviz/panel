"""Implementation of the Predix App Navigation Widget

See https://www.predix-ui.com/#/elements/px-app-nav"""

from bokeh.core import properties
from bokeh.models.layouts import HTMLBox

class WebComponent(HTMLBox):
    """A Predix App Navigation Widget

    See https://www.predix-ui.com/#/elements/px-app-nav"""
    innerHTML = properties.String('')
    attributesToWatch = properties.Dict(properties.String, properties.Any)