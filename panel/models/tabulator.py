"""
Implementation of the Tabulator model.

See http://tabulator.info/
"""
from bokeh.core.properties import Any, Dict, Enum, Instance, List, String
from bokeh.models import ColumnDataSource
from bokeh.models.layouts import HTMLBox
from bokeh.models.widgets.tables import TableColumn


JS_SRC = "https://unpkg.com/tabulator-tables@4.7.2/dist/js/tabulator.min.js"
MOMENT_SRC = "https://unpkg.com/moment@2.27.0/moment.js"

CSS_HREFS = {
    "default": "https://unpkg.com/tabulator-tables@4.7.2/dist/css/tabulator.min.css",
    "site": "https://unpkg.com/tabulator-tables@4.7.2/dist/css/tabulator_site.min.css",
    "simple": "https://unpkg.com/tabulator-tables@4.7.2/dist/css/tabulator_simple.min.css",
    "midnight": "https://unpkg.com/tabulator-tables@4.7.2/dist/css/tabulator_midnight.min.css",
    "modern": "https://unpkg.com/tabulator-tables@4.7.2/dist/css/tabulator_modern.min.css",
    "bootstrap": "https://unpkg.com/tabulator-tables@4.7.2/dist/css/bootstrap/tabulator_bootstrap.min.css",
    "bootstrap4": "https://unpkg.com/tabulator-tables@4.7.2/dist/css/bootstrap/tabulator_bootstrap4.min.css",
    "semantic-ui": "https://unpkg.com/tabulator-tables@4.7.2/dist/css/semantic-ui/tabulator_semantic-ui.min.css",
    "bulma": "https://unpkg.com/tabulator-tables@4.7.2/dist/css/bulma/tabulator_bulma.min.css",
    "materialize": "https://unpkg.com/tabulator-tables@4.7.2/dist/css/materialize/tabulator_materialize.min.css",
}


class DataTabulator(HTMLBox):
    """A Bokeh Model that enables easy use of Tabulator tables
    See http://tabulator.info/
    """

    configuration = Dict(String, Any)

    columns = List(Instance(TableColumn), help="""
    The list of child column widgets.
    """)

    layout = Enum('fit_data', 'fit_data_fill', 'fit_data_stretch', 'fit_data_table', 'fit_columns')

    source = Instance(ColumnDataSource)

    __css__ = [CSS_HREFS["default"]]

    __javascript__ = [
        JS_SRC,
        MOMENT_SRC,
    ]

    __js_require__ = {
        'paths': {
            'tabulator': JS_SRC[:-3]
        },
        'exports': {'tabulator': 'Tabulator'}
    }
