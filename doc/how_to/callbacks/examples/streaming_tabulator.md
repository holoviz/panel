# Streaming Tabulator

```{pyodide}
import numpy as np
import pandas as pd
import panel as pn

pn.extension('tabulator', template='fast', sizing_mode="stretch_width")
```

This example demonstrates how to use `add_periodic_callback` to stream data to a `Tabulator` pane.

```{pyodide}
df = pd.DataFrame(np.random.randn(10, 4), columns=list('ABCD')).cumsum()

rollover = pn.widgets.IntInput(name='Rollover', value=15)
follow = pn.widgets.Checkbox(name='Follow', value=True, align='end')

tabulator = pn.widgets.Tabulator(df, height=450)

def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    color = 'red' if val < 0 else 'green'
    return 'color: %s' % color

tabulator.style.map(color_negative_red)

def stream():
    data = df.iloc[-1] + np.random.randn(4)
    tabulator.stream(data, rollover=rollover.value, follow=follow.value)

cb = pn.state.add_periodic_callback(stream, 200)

pn.Column(
    pn.Row(cb.param.period, rollover, follow, width=400),
    tabulator
).servable()
```
