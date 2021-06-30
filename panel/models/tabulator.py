"""
Implementation of the Tabulator model.

See http://tabulator.info/
"""
from bokeh.core.properties import (
    Any, Bool, Dict, Enum, Instance, Int, List, Nullable, String
)
from bokeh.models import ColumnDataSource
from bokeh.models.layouts import HTMLBox
from bokeh.models.widgets.tables import TableColumn

from ..io.resources import bundled_files
from ..util import classproperty

JS_SRC = "https://unpkg.com/tabulator-tables@4.9.3/dist/js/tabulator.js"
MOMENT_SRC = "https://unpkg.com/moment@2.27.0/moment.js"

THEME_URL = "https://unpkg.com/tabulator-tables@4.9.3/dist/css/"
TABULATOR_THEMES = [
    'default', 'site', 'simple', 'midnight', 'modern', 'bootstrap',
    'bootstrap4', 'materialize', 'bulma', 'semantic-ui'
]

class DataTabulator(HTMLBox):
    """A Bokeh Model that enables easy use of Tabulator tables
    See http://tabulator.info/
    """

    configuration = Dict(String, Any)

    columns = List(Instance(TableColumn), help="""
    The list of child column widgets.
    """)

    download = Bool(default=False)

    editable = Bool(default=True)

    filename = String(default="table.csv")

    follow = Bool(True)

    frozen_rows = List(Int)

    groupby = List(String)

    hidden_columns = List(String)

    layout = Enum('fit_data', 'fit_data_fill', 'fit_data_stretch', 'fit_data_table', 'fit_columns', default="fit_data")

    source = Instance(ColumnDataSource)

    styles = Dict(Int, Dict(Int, List(String)))

    pagination = Nullable(String)

    page = Nullable(Int)

    page_size = Int()

    max_page = Int()

    sorters = List(Dict(String, String))

    select_mode = Any(default=True)

    selectable_rows = Nullable(List(Int))

    theme = Enum(*TABULATOR_THEMES, default="simple")

    theme_url = String(default=THEME_URL)

    __css_raw__ = [
        f'{THEME_URL}tabulator.min.css' if theme == 'default' else f'{THEME_URL}tabulator_{theme}.min.css'
        for theme in TABULATOR_THEMES
    ]

    @classproperty
    def __css__(cls):
        cls.__css_raw__ = [url for url in cls.__css_raw__ if 'simple' in url]
        return bundled_files(cls)

    __javascript_raw__ = [
        JS_SRC,
        MOMENT_SRC
    ]

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    @classproperty
    def __js_skip__(cls):
        return {'Tabulator': cls.__javascript__[:1]}

    __js_require__ = {
        'paths': {
            'tabulator': JS_SRC[:-3]
        },
        'exports': {'tabulator': 'Tabulator'}
    }
