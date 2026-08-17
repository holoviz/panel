# Streamz
---
```python
import panel as pn

from streamz import Stream

pn.extension('vega')
```

The ``Streamz`` pane renders [Streamz](https://streamz.readthedocs.io/en/latest/) Stream objects emitting arbitrary objects, unlike the ``DataFrame`` pane which specifically handles streamz DataFrame and Series objects and exposes various formatting objects.

If you are not already a user of the Streamz library, we recommend using functionality from the Param and Panel ecosystem, such as [reactive expressions](https://param.holoviz.org/user_guide/Reactive_Expressions.html), [generator functions](https://param.holoviz.org/user_guide/Generators.html) and/ or *periodic callbacks*. We find these features to be more robustly supported.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``always_watch``** (boolean, default=False): Whether to watch the stream even when not displayed.
* **``object``** (streamz.Stream): The streamz.Stream object being watched
* **``rate_limit``** (float, default=0.1): The minimum interval between events in seconds.

___

The `Streamz` pane uses the default panel resolution to figure out the appropriate way to render the object returned by a Stream. By default the pane will only watch the ``Stream`` if it is displayed, we can tell it to watch the stream as soon as it is created by setting `always_watch=True`.

```python
def increment(x):
    return x + 1

source = Stream()

streamz_pane = pn.pane.Streamz(source.map(increment), always_watch=True)

# Note: To ensure that a static render of the stream displays anything
#       we set always_watch=True and emit an event before displaying
source.emit(1)

streamz_pane
```

We can now define a periodic callback which emits an increasing count on the `Stream`:

```python
count = 1 

def emit_count():
    global count
    count += 1
    source.emit(count)

pn.state.add_periodic_callback(emit_count, period=100, count=9);
```

Lets reset the pane

```python
source.emit(1)
```

The `Streamz` stream can be used to stream any kind of data, e.g. we can create a streamz DataFrame, accumulate the data into a sliding window and then map it to a altair `line_plot` function

```python
import numpy as np
import altair as alt
import pandas as pd
from datetime import datetime
from streamz.dataframe import DataFrame as sDataFrame

df = sDataFrame(example=pd.DataFrame({'y': []}, index=pd.DatetimeIndex([])))

def line_plot(data):
    return alt.Chart(pd.concat(data).reset_index()).mark_line().encode(
        x='index',
        y='y',
    ).properties(width="container")

altair_stream = df.cumsum().stream.sliding_window(50).map(line_plot)

altair_pane = pn.pane.Streamz(altair_stream, height=350, sizing_mode="stretch_width", always_watch=True)

for i in range(100):
    df.emit(pd.DataFrame({'y': [np.random.randn()]}, index=pd.DatetimeIndex([datetime.now()])))

altair_pane
```

Now we can emit additional data on the DataFrame and watch the plot update:

```python
def emit():
    df.emit(pd.DataFrame({'y': [np.random.randn()]}, index=pd.DatetimeIndex([datetime.now()])))

pn.state.add_periodic_callback(emit, period=100, count=50);
```

---
