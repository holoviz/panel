# Streaming Perspective

```{pyodide}
import numpy as np
import pandas as pd
import panel as pn

pn.extension('perspective', template='fast', sizing_mode='stretch_width')
```

This example demonstrates how to use `add_periodic_callback` to stream data to a `Perspective` pane.

```{pyodide}
df = pd.DataFrame(np.random.randn(10, 4), columns=list('ABCD')).cumsum()

rollover = pn.widgets.IntInput(name='Rollover', value=15)

perspective = pn.pane.Perspective(df, height=400)

def stream():
    data = df.iloc[-1] + np.random.randn(4)
    perspective.stream(data, rollover=rollover.value)

cb = pn.state.add_periodic_callback(stream, 50)

pn.Column(
    pn.Row(cb.param.period, rollover, perspective.param.theme),
    perspective
).servable()
```
