import datetime

from typing import List

import analytics_workspace as aw
import hvplot.pandas
import pandas as pd
import param

from diskcache import Cache

import panel as pn

aw.apps.panel.extension("ace", "tabulator", sizing_mode="stretch_width", notifications=True)

prep_db = aw.data.prep_db

DATA_COLUMNS = [
    "product_bid,"
    "price_provider_shortname,"
    "price_source_shortname,"
    "value_type_shortname,"
    "delivery_period_type_shortname,"
    "tickercode,"
    "delivery_start,"
    "delivery_end,"
    "price",
]

EMPTY_DATA = pd.DataFrame(columns=DATA_COLUMNS)

cache = Cache()

@cache.memoize(expire=60*15)
def read_sql(query):
    return prep_db.read_sql(query)

def to_product_bids_list(product_bids: str):
    product_bids = product_bids.replace(" ", "")
    return "'" + "','".join(product_bids.split(",")) + "'"    

def get_master_data_query(product_bids, notationtime):
    product_bids = to_product_bids_list(product_bids)
    return f"""
select distinct
product_name,
product_bid,
price_provider_shortname,
price_source_shortname,
value_type_shortname,
delivery_period_type_shortname,
tickercode
from dma_prep.DMA_PRICE_all_wv
where product_bid in({product_bids}) and notationtime=to_date('{notationtime.isoformat()}','yyyy-mm-dd')
order by
product_name,
product_bid,
price_provider_shortname,
price_source_shortname,
value_type_shortname,
delivery_period_type_shortname,
tickercode
"""

def to_where_list(row: dict):
    if not row:
        raise ValueError("The row provided is empty")
    
    result = ""
    for key, value in row.items():
        result += f"{key}='{value}' AND "
    return result[:-5]

def get_data_query(selection, notationtime):
    row_filter = "((" + ") OR (".join(map(to_where_list, selection)) + "))"
    return f"""
select
product_name,
product_bid,
price_provider_shortname,
price_source_shortname,
value_type_shortname,
delivery_period_type_shortname,
tickercode,
delivery_start,
delivery_end,
price
from dma_prep.DMA_PRICE_all_wv
where {row_filter} and notationtime=to_date('{notationtime.isoformat()}','yyyy-mm-dd')
order by tickercode, delivery_start
"""

def get_default_notationtime():
    today = datetime.datetime.today()
    return (today - pd.tseries.offsets.BDay(4)).date()

def get_series_name(data: pd.DataFrame)->pd.Series:
    return data.product_name + " (" + data.price_provider_shortname + ", " + data.price_source_shortname + ")"

class PREPPApp(param.Parameterized):
    product_bids = param.String(default="1580571, 1000060")
    notationtime = param.CalendarDate()
    
    get_master_data = param.Event()

    master_data_query = param.String()
    master_data = param.DataFrame()
    selection = param.List()

    get_data = param.Event()
    data_query = param.String()
    data = param.DataFrame()

    def __init__(self):
        super().__init__()

        self.notationtime = get_default_notationtime()
        self._master_data_table = pn.widgets.Tabulator(theme="fast", selectable='checkbox', show_index=False)

        self._panel = pn.Column(
            """The purpose of this tool is to enable you to **quickly identify the PREP series you need**.
            
Find the `product_bids` via the [PREP Price Repository | Product Report](https://app-prepp:7004/ords/prepp/f?p=100:100:16191376478769:::::). For example by filtering on *Commodity Group* and *Point*.""",
            self.param.product_bids,
            self.param.notationtime,
            self.param.get_master_data,
            pn.panel(self._read_master_data, loading_indicator=True,),
        )

    @property
    def selection(self):
        return self._master_data_table.selection

    @pn.depends("get_master_data")
    def _read_master_data(self):
        if not self.product_bids:
            return "Please specify a list of product_bids"
        query = get_master_data_query(self.product_bids, self.notationtime)
        self.master_data = read_sql(query)
        self._master_data_table.value = self.master_data
        self._master_data_table.selection=[]
        self.data = EMPTY_DATA
        master_data_tabs = pn.Tabs(
            ("Master Data", self._master_data_table),
            ("Query", pn.widgets.Ace(value=query)),
        )
        return pn.Column(
            master_data_tabs, self.param.get_data, pn.panel(self.data_tabs, loading_indicator=True,),)

    @pn.depends("get_data", watch=True)
    def _read_data(self):
        if not self.selection:
            self.data=EMPTY_DATA
        else:
            selected_df=self.master_data[self.master_data.index.isin(self.selection)]
            selected_list=selected_df.to_dict(orient='records')
            self.data_query =  get_data_query(selected_list, self.notationtime)
            data = read_sql(self.data_query)
            data["series"] = get_series_name(data)
            self.data = data

    @pn.depends("data")
    def data_tabs(self):
        if isinstance(self.data, pd.DataFrame) and self.data.empty:
            return "No Series Selected"
        elif not isinstance(self.data, pd.DataFrame) and not self.data:
            return "No Series Selected"
        plot = self.data.hvplot.line(x="delivery_start", y="price", by="series", color=aw.orsted.colors.COLOR_CYCLE, line_width=5)
        tabs = pn.Tabs(
            ("Data Plot", plot),
            ("Query", pn.widgets.Ace(value=self.data_query)),
        )
        return tabs

    def __panel__(self):
        return self._panel

app = PREPPApp()

pn.template.FastListTemplate(
    site="Market Trading", title="PREP Explorer POC",
    main=[pn.Column(app._panel)]
).servable()
