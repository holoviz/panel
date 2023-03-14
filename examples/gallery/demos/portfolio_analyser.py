"""This app compares showcases Panel + Tabulator

Its inspired by the Dash + AG Grid here
https://github.com/plotly/dash-ag-grid/blob/dev/docs/demo_stock_portfolio.py

Having both its possible to compare them. See also
https://github.com/holoviz/panel/issues/4341
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import panel as pn

ACCENT = "#BB2649"
LINK_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-up-right-square" viewBox="0 0 16 16">
  <path fill-rule="evenodd" d="M15 2a1 1 0 0 0-1-1H2a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V2zM0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2zm5.854 8.803a.5.5 0 1 1-.708-.707L9.243 6H6.475a.5.5 0 1 1 0-1h3.975a.5.5 0 0 1 .5.5v3.975a.5.5 0 1 1-1 0V6.707l-4.096 4.096z"/>
</svg>
"""
CSS = """
.pnx-tabulator a {color: var(--neutral-foreground-rest);}
.pnx-tabulator a:hover {color: var(--neutral-foreground-hover);}
.tabulator-popup-container{position:absolute;display:inline-block;box-sizing:border-box;background:#666;border:1px solid #888;box-shadow:0 0 5px 0 rgba(0,0,0,.2);font-size:14px;overflow-y:auto;-webkit-overflow-scrolling:touch;z-index:10000}.tabulator-popup{padding:5px;border-radius:3px}.tabulator-tooltip{max-width:Min(500px,100%);padding:3px 5px;border-radius:2px;box-shadow:none;font-size:12px;pointer-events:none}.tabulator-menu .tabulator-menu-item{position:relative;box-sizing:border-box;padding:5px 10px;user-select:none}.tabulator-menu .tabulator-menu-item.tabulator-menu-item-disabled{opacity:.5}
.tabulator-edit-list{max-height:200px;font-size:14px;overflow-y:auto;-webkit-overflow-scrolling:touch}.tabulator-edit-list .tabulator-edit-list-item{padding:4px;color:#fff;outline:none}.tabulator-edit-list .tabulator-edit-list-item.active{color:#666;background:#999}.tabulator-edit-list .tabulator-edit-list-item.active.focused{outline:1px solid hsla(0,0%,40%,.5)}.tabulator-edit-list .tabulator-edit-list-item.focused{outline:1px solid #999}.tabulator-edit-list .tabulator-edit-list-item:hover{cursor:pointer;color:#666;background:#999}.tabulator-edit-list .tabulator-edit-list-placeholder{padding:4px;color:#fff;text-align:center}.tabulator-edit-list .tabulator-edit-list-group{border-bottom:1px solid #888;padding:6px 4px 4px;color:#fff;font-weight:700}.tabulator-edit-list .tabulator-edit-list-group.tabulator-edit-list-group-level-2,.tabulator-edit-list .tabulator-edit-list-item.tabulator-edit-list-group-level-2{padding-left:12px}.tabulator-edit-list .tabulator-edit-list-group.tabulator-edit-list-group-level-3,.tabulator-edit-list .tabulator-edit-list-item.tabulator-edit-list-group-level-3{padding-left:20px}.tabulator-edit-list .tabulator-edit-list-group.tabulator-edit-list-group-level-4,.tabulator-edit-list .tabulator-edit-list-item.tabulator-edit-list-group-level-4{padding-left:28px}.tabulator-edit-list .tabulator-edit-list-group.tabulator-edit-list-group-level-5,.tabulator-edit-list .tabulator-edit-list-item.tabulator-edit-list-group-level-5{padding-left:36px}
"""
RED = "#D94467"
GREEN = "#5AD534"

CSV_URL = "https://cdn.jsdelivr.net/gh/awesome-panel/awesome-panel-assets@master/data/portfolio_analyser.csv"
EQUITIES = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "GOOGL": "Alphabet",
    "TSLA": "Tesla",
    "BRK-B": "Berkshire Hathaway",
    "UNH": "United Health Group",
    "JNJ": "Johnson & Johnson",
}
EQUITY_LIST = tuple(EQUITIES.keys())

pn.extension("tabulator", sizing_mode="stretch_both", raw_css=[CSS])

# Extract Data



@pn.cache(ttl=600)
def get_historical_data(tickers=EQUITY_LIST, period="2y"):
    """Downloads the historical data from Yahoo Finance"""
    df = pd.read_csv(CSV_URL, header=[0,1], index_col=0, parse_dates=[])
    df.index = pd.to_datetime(df.index, utc=True)

    # import yfinance as yf
    # df =yf.download(tickers=tickers, period=period, group_by="ticker")
    # df.to_csv("portfolio_analyser.csv", index=True)

    return df


historical_data = get_historical_data()

# Transform Data


def last_close(
    ticker,
    data=historical_data,
):
    """Returns the last close pricefor the given ticker"""
    return data[ticker]["Close"].iloc[-1]


summary_data_dict = {
    "ticker": EQUITY_LIST,
    "company": EQUITIES.values(),
    "info": [
        f"""<a href='https://finance.yahoo.com/quote/{ticker}' target='_blank'>
        <div title='Open in Yahoo'>{LINK_SVG}</div></a>"""
        for ticker in EQUITIES
    ],
    "quantity": [75, 40, 100, 50, 40, 60, 20, 40],
    "price": [last_close(ticker) for ticker in EQUITIES],
    "value": None,
    "action": ["buy", "sell", "hold", "hold", "hold", "hold", "hold", "hold"],
    "notes": ["" for i in range(8)],
}

summary_data = pd.DataFrame(summary_data_dict)
titles = {
    "ticker": "Stock Ticker",
    "company": "Company",
    "info": "Info",
    "quantity": "Shares",
    "price": "Last Close Price",
    "value": "Market Value",
    "action": "Action",
    "notes": "Notes",
}


def get_value_series(data=summary_data):
    """Returns the quantity * price series"""
    return data["quantity"] * data["price"]


summary_data["value"] = get_value_series()

# Configure the Summary table

frozen_columns = ["ticker", "company"]
editors = {
    "ticker": None,
    "company": None,
    "quantity": {"type": "number", "min": 0, "step": 1},
    "price": None,
    "value": None,
    "action": {
        "type": "list",
        "values": {"buy": "buy", "sell": "sell", "hold": "hold"},
    },
    "notes": {
        "type": "textarea",
        "elementAttributes": {"maxlength": "100"},
        "selectContents": True,
        "verticalNavigation": "editor",
        "shiftEnterSubmit": True,
    },
    "info": None,
}

widths = {"notes": 400}
formatters = {
    "price": {"type": "money", "decimal": ".", "thousand": ",", "precission": 2},
    "value": {"type": "money", "decimal": ".", "thousand": ",", "precission": 0},
    "info": {"type": "html", "field": "html"},
}

text_align = {
    "price": "right",
    "value": "right",
    "action": "center",
    "info": "center",
}
base_configuration = {
    "clipboard": "copy"
}
summary_table = pn.widgets.Tabulator(
    summary_data,
    editors=editors,
    formatters=formatters,
    frozen_columns=frozen_columns,
    layout="fit_data_table",
    selectable=1,
    show_index=False,
    text_align=text_align,
    theme="fast",
    titles=titles,
    widths=widths,
    configuration=base_configuration,
)


def style_of_action_cell(value):
    """Returns the css to apply to an 'action' cell depending on the val"""
    if value == "sell":
        return f"color: {RED}"
    if value == "buy":
        return f"color: {GREEN}"
    return ""


summary_table.style.applymap(style_of_action_cell, subset=["action"]).set_properties(
    **{"background-color": "#444"}, subset=["quantity"]
)

patches = pn.widgets.IntInput()

def handle_cell_edit(event, table=summary_table):
    """Updates the `value` cell when the `quantity` cell is updated"""
    row = event.row
    column = event.column
    if column == "quantity":
        quantity = event.value
        price = summary_table.value.loc[row, "price"]
        value = quantity * price
        table.patch({"value": [(row, value)]})

        patches.value +=1


# Define the plots


def candlestick(selection, data=summary_data):
    """Returns a candlestick plot"""
    if not selection:
        ticker = "AAPL"
        company = "Apple"
    else:
        index = selection[0]
        ticker = data.loc[index, "ticker"]
        company = data.loc[index, "company"]

    dff_ticker_hist = historical_data[ticker].reset_index()
    dff_ticker_hist["Date"] = pd.to_datetime(dff_ticker_hist["Date"])

    fig = go.Figure(
        go.Candlestick(
            x=dff_ticker_hist["Date"],
            open=dff_ticker_hist["Open"],
            high=dff_ticker_hist["High"],
            low=dff_ticker_hist["Low"],
            close=dff_ticker_hist["Close"],
        )
    )
    fig.update_layout(
        title_text=f"{ticker} {company} Daily Price",
        template="plotly_dark",
        autosize=True,
    )
    return fig


def portfolio_distribution(patches=0):
    """Returns the distribution of the portfolio"""
    data = summary_table.value
    portfolio_total = data["value"].sum()

    fig = px.pie(
        data,
        values="value",
        names="ticker",
        hole=0.3,
        title=f"Portfolio Total ${portfolio_total:,.0f}",
        template="plotly_dark",
    )
    fig.layout.autosize = True
    return fig


# Setup bindings

summary_table.on_edit(handle_cell_edit)

candlestick = pn.bind(candlestick, selection=summary_table.param.selection)
portfolio_distribution = pn.bind(portfolio_distribution, patches=patches)


# Layout it out in the FastGridTemplate

template = pn.template.FastGridTemplate(
    site="Panel",
    site_url="https://panel.holoviz.org",
    title="Portfolio Analysis",
    accent_base_color=ACCENT,
    header_background=ACCENT,
    prevent_collision=True,
    save_layout=True,
    theme_toggle=False,
    theme="dark",
)

template.main[0:3, 0:8] = pn.panel(
    candlestick,
    config={"responsive": True},
    sizing_mode="stretch_both",
    margin=(2, 0, 0, 0),
)
template.main[0:3, 8:12] = pn.Column(
    pn.panel(
        portfolio_distribution,
        sizing_mode="stretch_both",
    ),
    sizing_mode="stretch_both",
    margin=(0, 5, 5, 0),
)
template.main[3:5, 0:12] = summary_table
template.servable()
