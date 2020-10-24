"""Implementation of the [Pivot Table JS]\
(https://pivottable.js.org/examples/).
"""

from bokeh.core import properties
from bokeh.models import ColumnDataSource
from bokeh.models.layouts import HTMLBox


class PivotTable(HTMLBox):
    """A Bokeh Model that enables easy use of pivot-table widget
    """

    # pylint: disable=line-too-long
    __javascript__ = [
        "https://code.jquery.com/jquery-3.5.1.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.11.4/jquery-ui.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/pivottable/2.13.0/pivot.min.js",
    ]

    __js_skip__ = {
        "pivottable": __javascript__[2:3],
    }

    __js_require__ = {
        "paths": {
            "pivottable": "https://cdnjs.cloudflare.com/ajax/libs/pivottable/2.13.0/pivot.min",
        },
        "exports": {"pivottable": "PivotTable",},
    }

    __css__ = ["https://cdnjs.cloudflare.com/ajax/libs/pivottable/2.13.0/pivot.min.css"]

    # pylint: enable=line-too-long

    source = properties.Instance(ColumnDataSource)
    source_stream = properties.Instance(ColumnDataSource)
    source_patch = properties.Instance(ColumnDataSource)
