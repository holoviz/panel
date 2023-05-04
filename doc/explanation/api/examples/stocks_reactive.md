# Stock Explorer - Reactive API

Before launching into the application code we will first declare some components of the app that will be shared, including the title of the app, a set of stock tickers, a function to return a dataframe given the stock ``ticker`` and the rolling mean ``window_size``, and another function to return a plot given those same inputs:

```{pyodide}
import panel as pn
import pandas as pd
import altair as alt
import plotly.graph_objects as go

from bokeh.sampledata import stocks
from matplotlib.figure import Figure

pn.extension('plotly', 'vega', template='bootstrap')
import hvplot.pandas

tickers = ['AAPL', 'FB', 'GOOG', 'IBM', 'MSFT']

def get_df(ticker, window_size):
    df = pd.DataFrame(getattr(stocks, ticker))
    df['date'] = pd.to_datetime(df.date)
    return df.set_index('date').rolling(window=window_size).mean().reset_index()

def get_altair(ticker, window_size):
    df = get_df(ticker, window_size)
    return alt.Chart(df).mark_line().encode(x='date', y='close').properties(
        width="container", height=400
    )

def get_hvplot(ticker, window_size):
    df = get_df(ticker, window_size)
    return df.hvplot.line('date', 'close', grid=True, responsive=True, height=400)

def get_mpl(ticker, window_size):
    fig = Figure(figsize=(10, 6))
    ax = fig.subplots()
    df = get_df(ticker, window_size)
    df.plot.line('date', 'close', ax=ax)
    return fig

def get_plotly(ticker, window_size):
    df = get_df(ticker, window_size)
    return go.Scatter(x=df.date, y=df.close)

plot_fns = {
    'altair': get_altair,
	'hvplot': get_hvplot,
	'matplotlib': get_mpl,
	'plotly': get_plotly
}
```

This example demonstrates how APIs in Panel differ, to see the same app implemented using a different API visit:

- [Callback API](stocks_callbacks)
- [Declarative API](stocks_declarative)

The reactive programming model relies on the user (a) explicitly instantiating widgets, (b) declaring how those widgets relate to the function arguments (using the ``bind`` function), and (c) laying out the widgets and other components explicitly. In principle we could reuse the ``get_plot`` function from above here but for clarity we will repeat it:

```{pyodide}
backend = pn.widgets.Select(name='Backend', options=plot_fns)
ticker = pn.widgets.Select(name='Ticker', options=tickers)
window = pn.widgets.IntSlider(name='Window Size', value=6, start=1, end=51, step=5)

pn.Row(
    pn.Column(backend, ticker, window),
    pn.panel(pn.bind(backend, ticker, window), sizing_mode='stretch_width')
).servable()
```
