"""Implementation of the Tabulator pane.

See http://tabulator.info/
"""

from bokeh.core import properties
from bokeh.models import ColumnDataSource
from bokeh.models.layouts import HTMLBox

# pylint: disable=line-too-long

JS_SRC = "https://unpkg.com/tabulator-tables@4.7.2/dist/js/tabulator.min.js"
MOMENT_SRC = "https://unpkg.com/moment@2.27.0/moment.js"

TABULATOR_CSS_THEMES = {
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

# pylint: enable=line-too-long


class TabulatorModel(HTMLBox):
    """A Bokeh Model that enables easy use of Tabulator tables

    See http://tabulator.info/
    """

    __javascript__ = [
        MOMENT_SRC,
        JS_SRC,
    ]

    # I could not get Tabulator loaded in Notebook
    # I found a working solution using requirejs the notebook
    # I'm working on getting the below working.
    # See https://github.com/holoviz/panel/issues/1529
    __js_skip__ = {"Tabulator": __javascript__[1:]}

    __js_require__ = {
        "paths": {"tabulator": ["https://unpkg.com/tabulator-tables@4.7.2/dist/js/tabulator.min"]},
        "exports": {"tabulator": "Tabulator"},
    }

    # __css__ = [TABULATOR_CSS_THEMES["default"]]

    configuration = properties.Dict(properties.String, properties.Any)
    source = properties.Instance(ColumnDataSource)
    _cell_change = properties.Dict(properties.String, properties.Any)
