from datetime import datetime, timedelta

import numpy as np

from bokeh.models import NumeralTickFormatter
from bokeh.plotting import figure

import panel as pn

pn.extension(sizing_mode="stretch_width")

ticker = pn.widgets.Select(name="Ticker", options=["ACME", "GLOBEX", "INITECH", "HOOLI"], value="ACME")

def make_chart(symbol):
    np.random.seed(hash(symbol) % 2**31)
    days = 90
    dates = [datetime(2025, 1, 1) + timedelta(days=i) for i in range(days)]
    returns = np.random.randn(days) * 0.02
    price = 100 * np.exp(np.cumsum(returns))
    base = np.full(days, price.min() * 0.98)

    p = figure(title=f"{symbol} — 90 Day Price", x_axis_type="datetime", height=350, tools="pan,wheel_zoom,reset")
    p.varea(x=dates, y1=base, y2=price, fill_alpha=0.25, fill_color="#3b82f6")
    p.line(dates, price, line_width=2, color="#3b82f6")
    p.yaxis.formatter = NumeralTickFormatter(format="$0.00")
    return p

pn.Column(
    "# Stock Ticker",
    ticker,
    pn.pane.Bokeh(pn.bind(make_chart, ticker)),
).servable()
