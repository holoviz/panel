# Loading Indicator

```{pyodide}
import time
import panel as pn
import holoviews as hv
import numpy as np
import holoviews.plotting.bokeh

pn.extension(loading_spinner='dots', loading_color='#00aa41', template='bootstrap')
hv.extension('bokeh')
```

Every pane, widget and layout provides the **`loading` parameter**. When set to `True` a spinner will overlay the panel and indicate that the panel is currently loading. When you set `loading` to false the spinner is removed.

Using the `pn.extension` or by setting the equivalent parameters on `pn.config` we can select between different visual styles and colors for the loading indicator.

```python
pn.extension(loading_spinner='dots', loading_color='#00aa41')
```

We can enable the loading indicator for reactive functions annotated with `depends` or `bind` globally using:

```python
pn.param.ParamMethod.loading_indicator = True
```

Alternatively we can enable it for a specific function by passing the `loading_indicator=True` argument to `pn.panel` or directly to the underlying  `ParamMethod`/`ParamFunction` object:

```{pyodide}
button = pn.widgets.Button(name="UPDATE", button_type="primary", sizing_mode='stretch_width')

def random_plot(event):
    if event: time.sleep(5)
    return hv.Points(np.random.rand(100, 2)).opts(
        responsive=True, height=400, size=8, color="green")

pn.Column(
    button,
    pn.param.ParamFunction(pn.bind(random_plot, button), loading_indicator=True)
).servable()
```
