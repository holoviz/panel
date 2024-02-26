# Optimize Performance with Caching

Caching is a powerful technique that not only accelerates your applications but also conserves computational resources by storing and reusing valuable computations. Let's dive into how you can leverage caching in your Panel apps to enhance their speed and efficiency.

## Harness the Power of Caching

With `pn.cache`, you can effortlessly cache function results, unlocking a plethora of performance benefits for your Panel apps.

:::{note}
As you proceed through the sections below, feel free to execute the code directly in the Panel docs using the handy green *run* button, in a notebook cell, or within a Python file `app.py` served with `panel serve app.py --autoreload`.
:::

## Grasp Panel Application Execution

Before delving into caching, it's crucial to comprehend how Panel applications execute code. Let's gain some insights into this process.

Create a file named `external_module.py` with the following content:

```python
print("running external_module.py")

# This object is defined once and shared across all sessions (i.e., all users)
external_data = {"__name__": __name__}
```

Next, create a file named `app.py` with the following code:

```python
print("running app.py")
import panel as pn

from external_module import external_data

pn.extension()

# This object is defined each time the app loads and is shared only within that session
data = {"__name__": __name__}

pn.Column(
    "## External Module", external_data, f"Object id: {id(external_data)}",
    "## App", data, f"Object id: {id(data)}",
).servable()
```

Now, execute the following command in your terminal:

```bash
panel serve app.py
```

Open the app in your browser and refresh it a few times.

It should look like

<video controls="" poster="https://assets.holoviz.org/panel/tutorials/page_load_end.png">
    <source src="https://assets.holoviz.org/panel/tutorials/page_load.mp4" type="video/mp4" style="max-height: 400px; max-width: 100%;">
    Your browser does not support the video tag.
</video>

:::{note}

- Imported modules are executed once when they are first imported. Objects defined in these modules are shared across all user sessions.
- The `app.py` script is executed each time the app is loaded. Objects defined here are shared within the single user session only (unless cached).
- Only specific, bound functions are re-executed upon user interactions, not the entire `app.py` script.

:::

### Exercise: Enable `--autoreload`

Try repeating the aforementioned steps with `--autoreload`.

```bash
panel serve app.py --autoreload
```

Observe the changes.

:::{dropdown} Solution

With `--autoreload`, both files are executed when the server starts and before the page is loaded for the first time.

<img src="https://assets.holoviz.org/panel/tutorials/page_load_end_autoreload.png"></img>

:::

## Enhance Loading Speed with Caching

Now, let's explore how caching can dramatically improve the loading speed of your Panel apps.

Execute the code snippet below:

```{pyodide}
from datetime import datetime
from time import sleep

import panel as pn

pn.extension()


def get_data():
    print("loading data ...")
    sleep(2)
    return {"last_update": str(datetime.now())}


data = get_data()

pn.pane.JSON(data).servable()
```

Refresh the browser a few times and observe the loading time.

### Exercise: Implement Caching

Let's apply caching to the `get_data` function by decorating it with the `@pn.cache` decorator.

Observe in the terminal that the `data` is loaded only once when the server starts.

Try loading and refreshing the app several times to experience the improved performance.

:::::{dropdown} Solution

```{pyodide}
from datetime import datetime
from time import sleep

import panel as pn

pn.extension()

@pn.cache
def get_data():
    print("loading data ...")
    sleep(2)
    return {"last_update": str(datetime.now())}


data = get_data()

pn.pane.JSON(data).servable()
```

:::::

If the `get_data` function is provided externally, you can utilize `pn.cache` as a function instead.

Try using `pn.cache` as a function instead of a decorator.

:::::{dropdown} Solution

```{pyodide}
from datetime import datetime
from time import sleep

import panel as pn

pn.extension()

def get_data():
    print("loading data ...")
    sleep(2)
    return {"last_update": str(datetime.now())}

get_data_cached = pn.cache(get_data)

data = get_data_cached()

pn.pane.JSON(data).servable()
```

:::::

## Maximize Efficiency by Reusing Function Results

Execute the following code snippet:

```{pyodide}
from time import sleep

import panel as pn

pn.extension()

@pn.cache
def algo(value):
    print(f"calculating {value}")
    sleep(1)
    return value

slider = pn.widgets.IntSlider(name="Value", value=2, start=0, end=10)
pn.Column(
    slider, pn.bind(algo, slider)
).servable()
```

Drag the slider and notice the initial slow response of the app, which progressively becomes instantaneous as the cache is populated.

:::{tip}
For further optimization, explore fine-tuning options for `pn.cache` in the [Automatically Cache](../../how_to/caching/memoization.md) guide.
:::

## Recap

In this section, we've learned how to significantly enhance the performance of Panel apps through caching:

- Leveraged `pn.cache` to cache function results efficiently.

## Resources

### How-to Guides

- [Automatically Cache](../../how_to/caching/memoization.md)
- [Manually Cache](../../how_to/caching/manual.md)
- [Migration from Streamlit: Adding Caching](../../how_to/streamlit_migration/caching.md)

Keep exploring and optimizing your Panel apps for maximum efficiency! 🚀
