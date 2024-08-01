# Stock Explorer - Callback API

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

- [Declarative API](stocks_declarative)
- [Reactive API](stocks_reactive)

Other APIs in Panel are all reactive in some way, triggering actions whenever manipulating a widget causes a parameter to change, without users writing code to trigger callbacks explicitly. The callback based API on the other allows complete low-level control of precisely how the different components of the app are updated, but they can quickly become unmaintainable because the complexity increases dramatically as more callbacks are added. The approach works by defining callbacks using the ``.param.watch`` API that either updates or replaces	 the already rendered components when a watched parameter changes:

```{pyodide}
backend = pn.widgets.Select(name='Backend', options=plot_fns)
ticker = pn.widgets.Select(name='Ticker', options=['AAPL', 'FB', 'GOOG', 'IBM', 'MSFT'])
window = pn.widgets.IntSlider(name='Window', value=6, start=1, end=21)

def update(event):
    row[1] = pn.panel(backend.value(ticker.value, window.value), sizing_mode='stretch_width')

backend.param.watch(update, 'value')
ticker.param.watch(update, 'value')
window.param.watch(update, 'value')

row = pn.Row(
    pn.Column(backend, ticker, window),
    pn.panel(backend.value(ticker.options[0], window.value))
)

row.servable()
```
