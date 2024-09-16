# Run synchronous functions asynchronously

Running your bound, synchronous functions asynchronously can be an easy way to make your application responsive and scale to more users.

## Asyncify

This example will show how to make your app responsive by running a sync, cpu bound function asynchronously. We will be using [asyncer](https://asyncer.tiangolo.com) by Tiangolo. You can install the package via `pip install asyncer`.

```python
import numpy as np
import pandas as pd

from asyncer import asyncify
import panel as pn

widget = pn.widgets.IntSlider(value=5, start=0, end=10)

def do_sync_work(it, n):
    return sum(pd.DataFrame(np.random.rand(n,n)).sum().sum() for _ in range(it))

async def create_result():
    yield pn.indicators.LoadingSpinner(value=True, width=25, height=25)
    result = await asyncify(do_sync_work)(it=5, n=10000)
    yield f"Wow. That was slow.\n\nThe sum is **{result:.2f}**"

pn.Column(widget.rx() + 1, create_result).servable()
```

<video muted controls loop poster="../../_static/images/asyncify.png" style="max-height: 400px; max-width: 100%;">
    <source src="https://assets.holoviz.org/panel/how_to/concurrency/asyncify.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>

Without [`asyncify`](https://asyncer.tiangolo.com/tutorial/asyncify/) the app would have been unresponsive for 5-10 seconds while loading.

[`asyncify`](https://asyncer.tiangolo.com/tutorial/asyncify/) works well for IO bound functions as well as for CPU bound functions that releases the GIL.

## Dask

If you run many cpu bound functions you may consider offloading your functions asynchronously to an external compute engine like [Dask](https://www.dask.org/). See our [Dask how-to Guide](../concurrency/dask.md).
