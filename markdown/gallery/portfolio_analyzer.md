# Portfolio Analyzer

The Portfolio Analysis App demonstrates the powerful [Tabulator](../reference/widgets/Tabulator.md) table that ships with Panel.

This app is heavily inspired by the Dash AG Grid App [here](https://github.com/plotly/dash-ag-grid/blob/main/docs/demo_stock_portfolio.py). Having both enables you to compare [pros and cons of Panel w. Tabulator versus Dash w. AG Grid](https://github.com/holoviz/panel/issues/4341).

```python
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import panel as pn
import panel_material_ui as pmui

pn.extension('plotly', 'tabulator')
```

```python
ACCENT = "#BB2649"
RED = "#D94467"
GREEN = "#5AD534"

LINK_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-up-right-square" viewBox="0 0 16 16">
  <path fill-rule="evenodd" d="M15 2a1 1 0 0 0-1-1H2a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V2zM0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2zm5.854 8.803a.5.5 0 1 1-.708-.707L9.243 6H6.475a.5.5 0 1 1 0-1h3.975a.5.5 0 0 1 .5.5v3.975a.5.5 0 1 1-1 0V6.707l-4.096 4.096z"/>
</svg>
"""

CSV_URL = "https://datasets.holoviz.org/equities/v1/equities.csv"
```

Lets define our list of equities

```python
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
```

## Extract the data

We would be using *caching* (`pn.cache`) to improve the performance of the app if we where loading data from a live data source like `yfinance`.

```python
@pn.cache(ttl=600)
def get_historical_data(tickers=EQUITY_LIST, period="2y"):
    """Downloads the historical data from Yahoo Finance"""
    df = pd.read_csv(CSV_URL, index_col=[0, 1], parse_dates=['Date'])
    return df

historical_data = get_historical_data()
historical_data.head(3).round(2)
```

## Transform the data

Let us calculate the `summary_data` to show in the Table.

```python
def last_close(ticker, data=historical_data):
    """Returns the last close pricefor the given ticker"""
    return data.loc[ticker]["Close"].iloc[-1]

last_close("AAPL")
```

```python
summary_data_dict = {
    "ticker": EQUITY_LIST,
    "company": EQUITIES.values(),
    "info": [
        f"""[{LINK_SVG}](https://finance.yahoo.com/quote/{ticker})"""
        for ticker in EQUITIES
    ],
    "quantity": [75, 40, 100, 50, 40, 60, 20, 40],
    "price": [last_close(ticker) for ticker in EQUITIES],
    "value": None,
    "action": ["buy", "sell", "hold", "hold", "hold", "hold", "hold", "hold"],
    "notes": ["" for i in range(8)],
}

summary_data = pd.DataFrame(summary_data_dict)

def get_value_series(data=summary_data):
    """Returns the quantity * price series"""
    return data["quantity"] * data["price"]

summary_data["value"] = get_value_series()
summary_data.head(2)
```

## Define the *Summary Table*

We define the configuration of the Tabulator below.

```python
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
    "price": {"type": "money", "decimal": ".", "thousand": ",", "precision": 2},
    "value": {"type": "money", "decimal": ".", "thousand": ",", "precision": 0},
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
```

Here we define the `summary_table` *widget*.

```python
summary_table = pn.widgets.Tabulator(
    summary_data,
    editors=editors,
    formatters=formatters,
    frozen_columns=frozen_columns,
    layout="fit_data_table",
    selectable=1,
    show_index=False,
    text_align=text_align,
    titles=titles,
    widths=widths,
    configuration=base_configuration,
)
summary_table
```

Now lets *style* the table using the *Pandas styler* api.

```python
def style_of_action_cell(value, colors={'buy': GREEN, 'sell': RED}):
    """Returns the css to apply to an 'action' cell depending on the val"""
    return f'color: {colors[value]}' if value in colors else ''

summary_table.style.map(style_of_action_cell, subset=["action"]).set_properties(
    **{"background-color": "#444"}, subset=["quantity"]
)
```

For later we also need a function to handle when a user edits a cell in the table

```python
patches = pmui.IntInput(description="Used to raise an event when a cell value has changed")

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
```

## Define the plots

```python
def candlestick(selection=[], data=summary_data):
    """Returns a candlestick plot"""
    if not selection:
        ticker = "AAPL"
        company = "Apple"
    else:
        index = selection[0]
        ticker = data.loc[index, "ticker"]
        company = data.loc[index, "company"]

    dff_ticker_hist = historical_data.loc[ticker].reset_index()
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

pn.pane.Plotly(candlestick())
```

```python
def portfolio_distribution(patches=0):
    """Returns the distribution of the portfolio"""
    data = summary_table.value
    portfolio_total = data["value"].sum()

    fig = px.pie(
        data,
        values="value",
        names="ticker",
        hole=0.3,
        title=f"Portfolio Total $ {portfolio_total:,.0f}",
        template="plotly_dark",
    )
    fig.layout.autosize = True
    return fig

pn.pane.Plotly(portfolio_distribution())
```

## Bind the widgets and functions

We want the `candlestick` plot to depend on the selection in `summary_table`

```python
candlestick = pn.bind(candlestick, selection=summary_table.param.selection)
```

We want the `portfolio_distribution` to be updated when ever a cell value changes in the table

```python
summary_table.on_edit(handle_cell_edit)

portfolio_distribution = pn.bind(portfolio_distribution, patches=patches)
```

## Test the app

```python
pn.Column(
    pn.Row(
        pn.pane.Plotly(candlestick), 
        pn.pane.Plotly(portfolio_distribution)
    ),
    summary_table,
    height=600
)
```

## Layout the app in a nice template

We will use the `pmui.Page` with a `GridSpec` which provides a nice dashboard layout with Panels you can resize and move around interactively.

```python
grid = pn.GridSpec(sizing_mode="stretch_both", max_height=800)
```

Lets add the plots and table to the template

```python
grid[0:3, 0:8]  = pn.pane.Plotly(candlestick)
grid[0:3, 8:12] = pn.pane.Plotly(portfolio_distribution)
grid[3:5, :]    = summary_table

grid
```

The template does not display in a notebook so we only output it when in a *server* context.

### Served App

```python
if pn.state.served:
    pmui.Page(
        dark_theme=True,
        title="Portfolio Analysis",
        main=[grid],
        theme_config={
            "dark": {"palette": {"primary": {"main": ACCENT}}},
            "light": {"palette": {"primary": {"main": ACCENT}}},
        },
    ).servable()
```
