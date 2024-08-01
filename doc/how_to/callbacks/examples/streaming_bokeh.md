# Streaming Bokeh

```{pyodide}
import numpy as np
import panel as pn

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource

pn.extension(template='fast')
```

This example demonstrates how to use `add_periodic_callback` to stream data to a Bokeh plot.

```{pyodide}
p = figure(sizing_mode='stretch_width', title='Bokeh streaming example')

xs = np.arange(1000)
ys = np.random.randn(1000).cumsum()
x, y = xs[-1], ys[-1]

cds = ColumnDataSource(data={'x': xs, 'y': ys})

p.line('x', 'y', source=cds)

def stream():
    global x, y
    x += 1
    y += np.random.randn()
    cds.stream({'x': [x], 'y': [y]})
    pn.io.push_notebook(bk_pane) # Only needed when running in notebook context

cb = pn.state.add_periodic_callback(stream, 100)

bk_pane = pn.pane.Bokeh(p)

pn.Column(
	pn.Row(
        cb.param.period,
	    pn.widgets.Toggle.from_param(cb.param.running, align='end')
    ),
	bk_pane
).servable()
```
