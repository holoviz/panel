# Add interactivity with generators

This guide addresses how to use generators to build interactive components. This is done with the use of `pn.bind`, which binds a function or method to the value of a widget. Compared to simple reactive functions this allows for more complex interactivity.

---

```{pyodide}
import asyncio
import time

import panel as pn

pn.extension()
```

Let us say we have some action that is triggered by a widget, such as a button, and while we are computing the results we want to provide feedback to the user. Using imperative programming this involves writing callbacks that update the current state of our components. This is complex and really we prefer to write reactive components. This is where *generator functions* come in.

:::{important}
A *generator* function is a function that use `yield` to *return* results as they are produced during the execution. It is not allowed to `return` anything, but can use `return` to *break* the execution. For an introduction to *generator functions* check out [Real Python | Introduction to generator functions](https://realpython.com/introduction-to-python-generators/).
:::

In the example below we add a `Button` to trigger some calculation. Initially the calculation hasn't yet run, so we check the value provided by the `Button` indicating whether a calculation has been triggered and while it is `False` we `yield` some text and `return`. However, when the `Button` is clicked the function is called again with `run=True` and we kick off some calculation. As this calculation progresses we can `yield` updates and then once the calculation is successful we `yield` again with the final result:

```{pyodide}
run = pn.widgets.Button(name="Press to run calculation", align='center')

def runner(run):
    if not run:
        yield "Calculation did not run yet"
        return
    for i in range(101):
        time.sleep(0.01) # Some calculation
        yield pn.Column(
            f'Running ({i}/100%)', pn.indicators.Progress(value=i)
        )
    yield "Success ✅︎"
pn.Row(run, pn.bind(runner, run))
```

This provides a powerful mechanism for providing incrememental updates as we load some data, perform some data processing, etc.

This can also be combined with asynchronous processing, e.g. to dynamically stream in new data as it arrives:

```{pyodide}
import random

async def slideshow():
    index = 0
    while True:
        url = f"https://picsum.photos/800/300?image={index}"

        if pn.state._is_pyodide:
            from pyodide.http import pyfetch
            img, _ = await asyncio.gather(pyfetch(url), asyncio.sleep(1))
            yield pn.pane.JPG(await img.bytes())

        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                img, _ = await asyncio.gather(resp.read(), asyncio.sleep(1))
                yield pn.pane.JPG(img)
        index = (index + 1) % 10

pn.Row(slideshow)
```

## Related Resources

- Learn [how to use async callbacks to perform operations concurrently](../callbacks/async.md)
