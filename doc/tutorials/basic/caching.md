# Add Caching

Caching allows us to store and reuse valuable computations, reducing the energy required for calculations and making our apps run faster and smoother:

- Use `pn.cache` to *cache* function results.

:::{note}
When we ask to *run the code* in the sections below, we may execute the code directly in the Panel docs via the green *run* button, in a cell in a notebook, or in a file `app.py` that is served with `panel serve app.py --autoreload`.
:::

## Understand the Load

To understand why caching can be helpful and how to apply it, its important to understand how a Panel application executes code.

Create a file `external_module.py` containing the code below:

```python
print("running external_module.py")

# I'm defined once and shared between all sessions (i.e. between all users)
external_data={"__name__": __name__}
```

Create a file `app.py` containing the code below

```python
print("running app.py")
import panel as pn

from external_module import external_data

pn.extension()

# I'm defined each time the app loads and only shared within that session
data = {"__name__": __name__}

pn.Column(
    "## External Module", external_data, f"Object id: {id(external_data)}",
    "## App", data, f"Object id: {id(data)}",
).servable()
```

Run

```bash
panel serve app.py
```

Open the app in your browser and refresh it a few times.

It should look like

<video controls="" poster="https://assets.holoviz.org/panel/tutorials/page_load_end.png">
    <source src="https://assets.holoviz.org/panel/tutorials/page_load.mp4" type="video/mp4" style="max-height: 400px; max-width: 100%;">
    Your browser does not support the video tag.
</video>

Please note how the `__name__` and `id` does not change for the `external_module` when you refresh the page. Note that they do change for the served `app`.

:::{note}
Please note

- imported modules are run once the first time they are imported.
  - Objects defined in imported modules are shared between all user *sessions*
- the served `app.py` code is run every time the app is loaded.
  - Objects defined here are shared within the single user *session* only (unless they are cached).
- only *specific, bound functions* are rerun on user interactions. Not the entire `app.py` script.
:::

### Exercise: Add `--autoreload`

Try repeating the steps above with `--autoreload`

```bash
panel serve app.py --autoreload
```

What changes?

:::{dropdown}{Solution}
With `--autoreload` both files are run when the server starts and before the page is loaded the first time.

<img src="https://assets.holoviz.org/panel/tutorials/page_load_end_autoreload.png"></img>
:::

## Load Fast with Caching

Run the code below

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

Try refreshing the browser a few times.

Notice that it takes +2 seconds for the application to load and the timestamp is updated every time the app is reloaded.

### Exercise: Apply Caching

Now let's add caching to the `get_data` function by *annotating* it with `@pn.cache`.

Notice in the terminal that the `data` is loaded once when the server starts.

Try loading and refreshing the app several times. It's nice, right?

:::::{dropdown} Solution

::::{tab-set}

:::{tab-item} Annotation
:sync: annotation

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

:::

:::{tab-item} Function
:sync: function

If the `get_data` function is externally given, you can use `pn.cache` as a function instead.

```{pyodide}
from datetime import datetime
from time import sleep

import panel as pn

pn.extension()

def get_data():
    print("loading data ...")
    sleep(2)
    return {"last_update": str(datetime.now())}

get_data = pn.cache(get_data)

data = get_data()

pn.pane.JSON(data).servable()
```

:::

::::

:::::

## Reuse Function Results

Run the code below

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

Try dragging the slider. Notice how the app is initially responding slowly but as the cache is *populated* it starts responding instantly.

:::{hint}
You can learn to fine-tune `pn.cache` in the [Automatically Cache](../../how_to/caching/memoization.md) guide.
:::

## Recap

We have been speeding up our apps using caching.

- Use `pn.cache` to *cache* function results.

## Resources

### How-to

- [Automatically Cache](../../how_to/caching/memoization.md)
- [Manually Cache](../../how_to/caching/manual.md)
- [Migrate from Streamlit | Add Caching](../../how_to/streamlit_migration/caching.md)
