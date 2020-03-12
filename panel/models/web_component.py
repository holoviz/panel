"""Implementation of the Predix App Navigation Widget

See https://www.predix-ui.com/#/elements/px-app-nav"""

from bokeh.core import properties
from bokeh.models.layouts import HTMLBox
from bokeh.models import ColumnDataSource

class WebComponent(HTMLBox):
    """A Bokeh Model that enables easily creating new Panel components from web components

    See https://www.predix-ui.com/#/elements/px-app-nav"""
    innerHTML = properties.String('')
    attributesToWatch = properties.Dict(properties.String, properties.Any)
    attributesLastChange = properties.Dict(properties.String, properties.Any)
    propertiesToWatch = properties.Dict(properties.String, properties.Any)
    propertiesLastChange = properties.Dict(properties.String, properties.Any)
    eventsToWatch = properties.Dict(properties.String, properties.Any)
    eventsCountLastChange = properties.Dict(properties.String, properties.Int)
    columnDataSource = properties.Instance(ColumnDataSource)
    columnDataSourceOrient = properties.String()
    columnDataSourceLoadFunction = properties.String()