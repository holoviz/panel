"""
Implementation of the Tabulator model.

See http://tabulator.info/
"""
from bokeh.core.properties import (
    Any, Bool, Dict, Either, Enum, Instance, Int, List, Nullable,
    String, Tuple
)
from bokeh.models import ColumnDataSource
from bokeh.models.layouts import HTMLBox
from bokeh.models.widgets.tables import TableColumn

from ..io.resources import bundled_files
from ..util import classproperty

JS_SRC = "https://unpkg.com/tabulator-tables@4.9.3/dist/js/tabulator.js"
MOMENT_SRC = "https://unpkg.com/moment@2.27.0/moment.js"

THEME_PATH = "tabulator-tables@4.9.3/dist/css/"
THEME_URL = f"https://unpkg.com/{THEME_PATH}"
PANEL_CDN = f'https://cdn.jsdelivr.net/npm/@holoviz/panel/dist/bundled/{THEME_PATH}'
TABULATOR_THEMES = [
    'default', 'site', 'simple', 'midnight', 'modern', 'bootstrap',
    'bootstrap4', 'materialize', 'bulma', 'semantic-ui', 'fast'
]

def _get_theme_url(url, theme):
    if 'bootstrap' in theme:
        url += 'bootstrap/'
    elif 'materialize' in theme:
        url += 'materialize/'
    elif 'semantic-ui' in theme:
        url += 'semantic-ui/'
    elif 'bulma' in theme:
        url += 'bulma/'
    elif 'fast' in theme:
        if url.startswith(THEME_URL):
            url = url.replace(THEME_URL, PANEL_CDN)
        url += 'fast/'
    return url

CSS_URLS = []
for theme in TABULATOR_THEMES:
    _url = _get_theme_url(THEME_URL, theme)
    if theme == 'default':
        _url += 'tabulator.min.css'
    else:
        _url += f'tabulator_{theme}.min.css'
    CSS_URLS.append(_url)


class DataTabulator(HTMLBox):
    """A Bokeh Model that enables easy use of Tabulator tables
    See http://tabulator.info/
    """

    aggregators = Dict(String, String)

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

    indexes = List(String)

    layout = Enum('fit_data', 'fit_data_fill', 'fit_data_stretch', 'fit_data_table', 'fit_columns', default="fit_data")

    source = Instance(ColumnDataSource)

    styles = Dict(Int, Dict(Int, List(Either(String, Tuple(String, String)))))

    pagination = Nullable(String)

    page = Nullable(Int)

    page_size = Int()

    max_page = Int()

    sorters = List(Dict(String, String))

    select_mode = Any(default=True)

    selectable_rows = Nullable(List(Int))

    theme = Enum(*TABULATOR_THEMES, default="simple")

    theme_url = String(default=THEME_URL)

    __css_raw__ = CSS_URLS

    @classproperty
    def __css__(cls):
        cls.__css_raw__ = [
            url for url in cls.__css_raw__ if 'simple' in url or
            len(cls.__css_raw__) == 1
        ]
        return bundled_files(cls, 'css')

    __javascript_raw__ = [
        JS_SRC,
        MOMENT_SRC
    ]

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    @classproperty
    def __js_skip__(cls):
        return {'Tabulator': cls.__javascript__[:1], 'moment': cls.__javascript__[1:]}

    __js_require__ = {
        'paths': {
            'tabulator': JS_SRC[:-3],
            'moment': MOMENT_SRC[:-3]
        },
        'exports': {
            'tabulator': 'Tabulator',
            'moment': 'moment'
        }
    }

