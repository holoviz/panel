# Periodically Run Callbacks

This guide addresses how to set up per-session callbacks that run periodically.

---

Periodic callbacks allow periodically updating your application with new data. Below we will create a simple Bokeh plot and display it with Panel:

```{pyodide}
import numpy as np
import panel as pn

from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

pn.extension()

source = ColumnDataSource({"x": np.arange(10), "y": np.arange(10)})
p = figure()
p.line(x="x", y="y", source=source)

bokeh_pane = pn.pane.Bokeh(p)
bokeh_pane.servable()
```

Now we will define a callback that updates the data on the `ColumnDataSource` and use the `pn.state.add_periodic_callback` method to schedule updates every 200 ms. We will also set a timeout of 5 seconds after which the callback will automatically stop.

```{warning}
The dynamic callbacks may not function properly in the online documentation. Please use them in a notebook or script.
```

```{pyodide}
def update():
    data = np.random.randint(0, 2 ** 31, 10)
    source.data.update({"y": data})
    bokeh_pane.param.trigger('object') # Only needed in notebook

cb = pn.state.add_periodic_callback(update, 200, timeout=5000)
```

In a notebook or bokeh server context we should now see the plot update periodically. The other nice thing about this is that `pn.state.add_periodic_callback` returns `PeriodicCallback` we can call `.stop()` and `.start()` on if we want to stop or pause the periodic execution. Additionally we can also dynamically adjust the period by setting the `timeout` parameter to speed up or slow down the callback.

Other nice features on a periodic callback are the ability to check the number of executions using the `cb.counter` property and the ability to toggle the callback on and off simply by setting the `running` parameter. This makes it possible to link a widget to the running state:

```{pyodide}
toggle = pn.widgets.Toggle(name='Toggle callback', value=True)

toggle.link(cb, bidirectional=True, value='running')
toggle
```

Note that when starting a server dynamically with `pn.serve` you cannot start a periodic callback before the application is actually being served. Therefore you should create the application and start the callback in a wrapping function:

```python
from functools import partial

import numpy as np
import panel as pn

from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

def update(source):
    data = np.random.randint(0, 2 ** 31, 10)
    source.data.update({"y": data})

def panel_app():
    source = ColumnDataSource({"x": np.arange(10), "y": np.arange(10)})
    p = figure()
    p.line(x="x", y="y", source=source)
    cb = pn.state.add_periodic_callback(partial(update, source), 200, timeout=5000)
    toggle = pn.widgets.Toggle(name='Toggle callback', value=True)
    toggle.link(cb, bidirectional=True, value='running')
    return pn.Column(pn.pane.Bokeh(p), toggle)

pn.serve(panel_app)
```

## Related Resources
- See the related [How-to > Link Parameters with Callbacks API](../links/index) guides, including [How to > Create High-Level Python Links with `.link`](../links/links).
