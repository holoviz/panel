# Use Asynchronous Callbacks

This guide addresses how to leverage asynchronous callbacks to run I/O bound tasks in parallel.

```{admonition} Prerequisites
1. Python has natively supported asynchronous functions since version 3.5, for a quick overview of some of the concepts involved see [the Python documentation](https://docs.python.org/3/library/asyncio-task.html).
```
---

## `.param.watch`

One of the major benefits of leveraging async functions is that it is simple to write callbacks which will perform some longer running IO tasks in the background. Below we simulate this by creating a `Button` which will update some text when it starts and finishes running a long-running background task (here simulated using `asyncio.sleep`. If you are running this in the notebook you will note that you can start multiple tasks and it will update the text immediately but continue in the background:

```{pyodide}
import panel as pn
import asyncio

pn.extension()

button = pn.widgets.Button(name='Click me!')
text = pn.widgets.StaticText()

async def run_async(event):
    text.value = f'Running {event.new}'
    await asyncio.sleep(2)
    text.value = f'Finished {event.new}'

button.on_click(run_async)

pn.Row(button, text)
```

Note that `on_click` is simple one way of registering an asynchronous callback, but the more flexible `.param.watch` is also supported. Scheduling asynchronous periodic callbacks can be done with `pn.state.add_periodic_callback`.

It is important to note that asynchronous callbacks operate without locking the underlying Bokeh Document, which means Bokeh models cannot be safely modified by default. Usually this is not an issue because modifying Panel components appropriately schedules updates to underlying Bokeh models, however in cases where we want to modify a Bokeh model directly, e.g. when embedding and updating a Bokeh plot in a Panel application we explicitly have to decorate the asynchronous callback with `pn.io.with_lock`.

```{pyodide}
import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource

button = pn.widgets.Button(name='Click me!')

p = figure(width=500, height=300)
cds = ColumnDataSource(data={'x': [0], 'y': [0]})
p.line(x='x', y='y', source=cds)
pane = pn.pane.Bokeh(p)

@pn.io.with_lock
async def stream(event):
    await asyncio.sleep(1)
    x, y = cds.data['x'][-1], cds.data['y'][-1]
    cds.stream({'x': list(range(x+1, x+6)), 'y': y+np.random.randn(5).cumsum()})
    pane.param.trigger('object')

# Equivalent to `.on_click` but shown
button.param.watch(stream, 'clicks')

pn.Row(button, pane)
```

## `pn.bind`

```{pyodide}
widget = pn.widgets.IntSlider(start=0, end=10)

async def get_img(index):
    url = f"https://picsum.photos/800/300?image={index}"
    if pn.state._is_pyodide:
        from pyodide.http import pyfetch
        return pn.pane.JPG(await (await pyfetch(url)).bytes())

    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return pn.pane.JPG(await resp.read())

pn.Column(widget, pn.bind(get_img, widget))
```

In this example Panel will invoke the function and update the output when the function returns while leaving the process unblocked for the duration of the `aiohttp` request.

The equivalent can be written using `.param.watch` as:

```{pyodide}
widget = pn.widgets.IntSlider(start=0, end=10)

image = pn.pane.JPG()

async def update_img(event):
    url = f"https://picsum.photos/800/300?image={event.new}"
    if pn.state._is_pyodide:
        from pyodide.http import pyfetch
        image.object = await (await pyfetch(url)).bytes()
        return

    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            image.object = await resp.read()

widget.param.watch(update_img, 'value')
widget.param.trigger('value')

pn.Column(widget, image)
```

In this example Param will await the asynchronous function and the image will be updated when the request completes.

## Related Resources

- See the related [How-to > Link Parameters with Callbacks API](../links/index.md) guides, including [How to > Create Low-Level Python Links Using `.watch`](../links/watchers.md).
