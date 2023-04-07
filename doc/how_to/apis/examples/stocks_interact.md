# Stock Explorer - Interact API

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
- [Reactive API](stocks_reactive)

In the ``interact`` model the widgets are automatically generated from the arguments to the function or by providing additional hints to the ``interact`` call. This is a very convenient way to generate a simple app, particularly when first exploring some data.  However, because widgets are created implicitly based on introspecting the code, it is difficult to see how to modify the behavior.  Also, to compose the different components in a custom way it is necessary to unpack the layout returned by the ``interact`` call, as we do here:

```{pyodide}
def plot(backend, ticker, window_size):
    return backend(ticker, window_size)

interact = pn.interact(plot, ticker=tickers, window_size=(1, 51, 5), backend=plot_fns)

pn.Row(interact[0], interact[1]).servable()
```
