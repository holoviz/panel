# Stock Explorer - Declarative API

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
- [Reactive API](stocks_reactive)

The declarative API expresses the app entirely as a single ``Parameterized`` class with parameters to declare the inputs, rather than explicit widgets. The parameters are independent of any GUI code, which can be important for maintaining large codebases, with parameters and functionality defined separately from any GUI or panel code. Once again the ``depends`` decorator is used to express the dependencies, but in this case the dependencies are expressed as strings referencing class parameters, not parameters of widgets. The parameters and the ``plot`` method can then be laid out independently, with Panel used only for this very last step.

```{pyodide}
import param

class StockExplorer(param.Parameterized):

    backend = param.Selector(objects=plot_fns)

    ticker = param.Selector(objects=tickers)

    window_size = param.Integer(default=6, bounds=(1, 21))

    @param.depends('backend', 'ticker', 'window_size')
    def plot(self):
        return self.backend(self.ticker, self.window_size)

explorer = StockExplorer()

pn.Row(
    pn.Column(explorer.param),
    pn.panel(explorer.plot, sizing_mode='stretch_width'),
).servable()
```
