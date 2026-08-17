# Trend
---
```python
import numpy as np
import pandas as pd
import panel as pn

pn.extension()
```

The ``Trend`` is a value indicator providing a visual representation of a value along with an indicator of its recent trend. It supports streaming data to the plot component making it possible to provide performant live updates on the recent trends in some value.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``data``** (`dict(str, np.ndarray)` or `pd.DataFrame`): The plot data as a dictionary of arrays or a pandas DataFrame.
* **``layout``** (`str`, `default='column'`): The layout of the indicator, either 'column' or 'row'.
* **``plot_x``** (`str`, `default='y'`): The column in the data corresponding to x-values of the plot.
* **``plot_y``** (`str`, `default='x'`): The column in the data corresponding to y-values of the plot.
* **``plot_color``** (`str`, `default='#428bca'`): The color to use in the plot.
* **``plot_type``** (`str`, `default='bar'`): The plot type to render the plot data as, on of 'line', 'bar', 'step' or 'area'.
* **``pos_color``** (`str`, `default='#5cb85c'`): The color used to indicate a positive change.
* **``neg_color``** (`str`, `default='#d9534f'`): The color used to indicate a negative change.
* **``name``** (str): The name or a short description of the indicator.
* **``value``** (float or int or "auto", `default='auto'`): The primary value to be displayed.
* **``value_change``** (float or int or "auto", `default='auto'`): The change in the value expressed as a fraction.
___

The simplest form of a `Trend` just requires providing some `data` with x- and y-values, either declared as a dictionary or a `pandas.DataFrame`. The `value` and `value_change` values will then be automatically computed from the data:

```python
data = {'x': np.arange(50), 'y': np.random.randn(50).cumsum()}

trend = pn.indicators.Trend(
    label='Price', data=data, width=200, height=200
)
trend
```

### Streaming

The `Trend` indicator also provides a convenient method to stream new data, which supports a `rollover` argument to limit the amount of data displayed. We will register a periodic callback using `pn.state.add_periodic_callback` to update the plot:

```python
def stream_data():
    trend.stream({'x': [trend.data['x'][-1]+1], 'y': [trend.data['y'][-1]+np.random.randn()]}, rollover=50)

pn.state.add_periodic_callback(stream_data, period=250, count=100);
```

### Plot types

In addition to the default `plot_type` the stream indicator also supports several other options:

```python
pn.Row(*(trend.clone(plot_type=pt) for pt in trend.param.plot_type.objects))
```

## Controls

To get a feeling for the different parameters of the `Trend` indicator we will display a set of controls:

```python
trend = trend.clone()

pn.Row(trend.controls(), trend)
```

---
