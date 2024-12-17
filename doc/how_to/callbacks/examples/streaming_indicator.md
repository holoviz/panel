# Streaming Indicator

```{pyodide}
import numpy as np
import panel as pn

pn.extension(template='fast')
```

This example demonstrates how to use `add_periodic_callback` to stream data to the `Trend` indicator.

```{pyodide}
layout = pn.layout.FlexBox(*(
    pn.indicators.Trend(
        data={'x': list(range(10)), 'y': np.random.randn(10).cumsum()},
        width=150,
        height=100,
        plot_type=pn.indicators.Trend.param.plot_type.objects[i%4]
    ) for i in range(32)
))

def stream():
    for trend in layout:
        trend.stream({'x': [trend.data['x'][-1]+1], 'y': [trend.data['y'][-1]+np.random.randn()]}, rollover=20)

cb = pn.state.add_periodic_callback(stream, 500)

pn.Column(
  pn.Row(
      cb.param.period,
	  pn.widgets.Toggle.from_param(cb.param.running, align='end')
  ),
  layout
).servable()
```
