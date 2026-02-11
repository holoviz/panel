import numpy as np

from bokeh.plotting import figure

import panel as pn

pn.extension(sizing_mode="stretch_width")

n_points = pn.widgets.IntSlider(name="Points", start=10, end=500, value=100)
spread = pn.widgets.FloatSlider(name="Spread", start=0.1, end=5.0, step=0.1, value=1.0)

def make_plot(n, s):
    np.random.seed(42)
    x = np.random.randn(n)
    y = x * 0.5 + np.random.randn(n) * s
    colors = ["#3b82f6" if v > 0 else "#ef4444" for v in y]
    p = figure(title=f"{n} points (spread={s:.1f})", height=350, tools="pan,wheel_zoom,reset")
    p.scatter(x, y, size=6, color=colors, alpha=0.7)
    return p

pn.Column(
    "# Interactive Scatter Plot",
    pn.Row(n_points, spread),
    pn.pane.Bokeh(pn.bind(make_plot, n_points, spread)),
).servable()
