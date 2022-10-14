"""
Implementation of the Tabulator model.

See http://tabulator.info/
"""
from bokeh.core.properties import (
    Any, Bool, Dict, Either, Enum, Instance, Int, List, Nullable, String,
    Tuple,
)
from bokeh.events import ModelEvent
from bokeh.models import ColumnDataSource, LayoutDOM
from bokeh.models.layouts import HTMLBox
from bokeh.models.widgets.tables import TableColumn

from ..config import config
from ..io.resources import JS_VERSION, bundled_files
from ..util import classproperty

TABULATOR_VERSION = "5.3.2"

JS_SRC = f"{config.npm_cdn}/tabulator-tables@{TABULATOR_VERSION}/dist/js/tabulator.js"
MOMENT_SRC = f"{config.npm_cdn}/luxon/build/global/luxon.min.js"

THEME_PATH = f"tabulator-tables@{TABULATOR_VERSION}/dist/css/"
THEME_URL = f"{config.npm_cdn}/{THEME_PATH}"
PANEL_CDN = f"{config.npm_cdn}/@holoviz/panel@{JS_VERSION}/dist/bundled/datatabulator/{THEME_PATH}"
TABULATOR_THEMES = [
    'default', 'site', 'simple', 'midnight', 'modern', 'bootstrap',
    'bootstrap4', 'materialize', 'bulma', 'semantic-ui', 'fast'
]
# Theme names were renamed in Tabulator 5.0.
_TABULATOR_THEMES_MAPPING = {
    'bootstrap': 'bootstrap3',
    'semantic-ui': 'semanticui',
}

class TableEditEvent(ModelEvent):

    event_name = 'table-edit'

    def __init__(self, model, column, row, pre=False, value=None, old=None):
        self.column = column
        self.row = row
        self.value = value
        self.old = old
        self.pre = pre
        super().__init__(model=model)

    def __repr__(self):
        return (
            f'{type(self).__name__}(column={self.column}, row={self.row}, '
            f'value={self.value}, old={self.old})'
        )

class CellClickEvent(ModelEvent):

    event_name = 'cell-click'

    def __init__(self, model, column, row, value=None):
        self.column = column
        self.row = row
        self.value = value
        super().__init__(model=model)

    def __repr__(self):
        return (
            f'{type(self).__name__}(column={self.column}, row={self.row}, '
            f'value={self.value})'
        )

def _get_theme_url(url, theme):
    if 'fast' in theme:
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
        theme = _TABULATOR_THEMES_MAPPING.get(theme, theme)
        _url += f'tabulator_{theme}.min.css'
    CSS_URLS.append(_url)


class DataTabulator(HTMLBox):
    """A Bokeh Model that enables easy use of Tabulator tables
    See http://tabulator.info/
    """

    aggregators = Dict(String, String)

    buttons = Dict(String, String)

    configuration = Dict(String, Any)

    columns = List(Instance(TableColumn), help="""
    The list of child column widgets.
    """)

    download = Bool(default=False)

    children = Dict(Int, Instance(LayoutDOM))

    editable = Bool(default=True)

    expanded = List(Int)

    filename = String(default="table.csv")

    filters = List(Any)

    follow = Bool(True)

    frozen_rows = List(Int)

    groupby = List(String)

    hidden_columns = List(String)

    indexes = List(String)

    layout = Enum('fit_data', 'fit_data_fill', 'fit_data_stretch', 'fit_data_table', 'fit_columns', default="fit_data")

    source = Instance(ColumnDataSource)

    styles = Dict(String, Either(String, Dict(Int, Dict(Int, List(Either(String, Tuple(String, String)))))))

    pagination = Nullable(String)

    page = Nullable(Int)

    page_size = Int()

    max_page = Int()

    sorters = List(Dict(String, String))

    select_mode = Any()

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
