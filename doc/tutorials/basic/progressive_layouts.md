# Update Progressively

In this tutorial, we will be running a slow *classifier* model and reporting progress and results as they arrive:

- Use [*generator functions*](https://realpython.com/introduction-to-python-generators/) (`yield`) to progressively return content and update the app.
- Use [*reactive expressions*](../../reference/panes/ReactiveExpr.ipynb) (`pn.rx`) to drive progressive updates to the app

:::{note}
When we ask to *run the code* in the sections below, we may execute the code directly in the Panel documentation by using the green *run* button, in a notebook cell, or in a file named `app.py` served with `panel serve app.py --autoreload`.
:::

## Replace Content Progressively

### Replace using a Generator

Run the code below:

```{pyodide}
import random
from time import sleep

import panel as pn

pn.extension()

OPTIONS = ["Wind Turbine", "Solar Panel", "Battery Storage"]


def classify(image):
    sleep(2)
    return random.choice(OPTIONS)


run = pn.widgets.Button(name="Submit", button_type="primary")

progress_message = pn.Row(
    pn.indicators.LoadingSpinner(
        value=True, width=25, height=25, align="center", margin=(5, 0, 5, 10)
    ),
    pn.panel("Running classifier ...", margin=0),
)


def get_prediction(running):
    if not running: # If the Button was not clicked
        yield "Click Submit" # Ask the user to Click Submit
        return

    yield progress_message # Yield the progress message
    prediction = classify(None)
    yield f"It's a {prediction}" # Yield the result

pn.Column(run, pn.bind(get_prediction, run)).servable()
```

Click the *Submit* `Button.`

#### Exercise: Disable the Button

Update the code to `disable` the `Button` while the classification is running.

:::::{dropdown} Solution(s)

::::{tab-set}

:::{tab-item} .disabled
:sync: disabled

```{pyodide}
import random
from time import sleep

import panel as pn

pn.extension()

OPTIONS = ["Wind Turbine", "Solar Panel", "Battery Storage"]


def classify(image):
    sleep(2)
    return random.choice(OPTIONS)


run = pn.widgets.Button(name="Submit", button_type="primary")

progress_message = pn.Row(
    pn.indicators.LoadingSpinner(
        value=True, width=25, height=25, align="center", margin=(5, 0, 5, 10)
    ),
    pn.panel("Running classifier ...", margin=0),
)


def get_prediction(running):
    if not running:
        yield "Click Submit"
        return

    run.disabled = True

    yield progress_message
    prediction = classify(None)
    yield f"It's a {prediction}"

    run.disabled = False


pn.Column(run, pn.bind(get_prediction, run)).servable()
```

:::

:::{tab-item} .param.update
:sync: param-update

```{pyodide}
import random
from time import sleep

import panel as pn

pn.extension()

OPTIONS = ["Wind Turbine", "Solar Panel", "Battery Storage"]


def classify(image):
    sleep(2)
    return random.choice(OPTIONS)


run = pn.widgets.Button(name="Submit", button_type="primary")

progress_message = pn.Row(
    pn.indicators.LoadingSpinner(
        value=True, width=25, height=25, align="center", margin=(5, 0, 5, 10)
    ),
    pn.panel("Running classifier ...", margin=0),
)


def get_prediction(running):
    if not running:
        yield "Click Submit"
        return

    with run.param.update(disabled=True):
        yield progress_message
        prediction = classify(None)
        yield f"It's a {prediction}"


pn.Column(run, pn.bind(get_prediction, run)).servable()
```

:::

::::

:::::

### Replace using Reactive Expressions

An alternative to a generator function is *reactive expressions* (`pn.rx`).

Run the code below.

```{pyodide}
import random
from time import sleep

import panel as pn

pn.extension()

OPTIONS = ["Wind Turbine", "Solar Panel", "Battery Storage"]

# State

result = pn.rx("")
is_running = pn.rx(False)

# Transformations


def classify(image):
    sleep(2)
    return random.choice(OPTIONS)


has_result = result.rx.pipe(bool)


def _show_submit_message(result, is_running):
    return not result and not is_running


show_submit_message = pn.rx(_show_submit_message)(result, is_running)


def run_classification(_):
    result.rx.value = ""
    is_running.rx.value = True
    prediction = classify(None)
    result.rx.value = f"It's a {prediction}"
    is_running.rx.value = False


# Inputs: Widgets

run = pn.widgets.Button(
    name="Submit", button_type="primary", on_click=run_classification
)

# Outputs: Views

click_submit = pn.pane.Markdown("Click Submit", visible=show_submit_message)
progress_message = pn.Row(
    pn.indicators.LoadingSpinner(
        value=True, width=25, height=25, align="center", margin=(5, 0, 5, 10)
    ),
    pn.panel("Running classifier ...", margin=0),
    visible=is_running,
)

# Layout
pn.Column(run, click_submit, result, progress_message).servable()
```

Click the *Submit* `Button`.

:::{note}
The generator (`yield`) approach and the state (`.rx`) approach are both powerful. They complement each other.

Changing component parameters on the fly is much easier to do and reason about when using the state (`.rx`) approach though.
:::

## Append Content Progressively

### Append using Generator

To append content progressively we can append to a `layout` like `Column` and yield the `layout`.

Run the code below

```{pyodide}
import panel as pn
from time import sleep
import random

pn.extension()

OPTIONS = ["Wind Turbine", "Solar Panel", "Battery Storage"]

def classify(image):
    sleep(2)
    return random.choice(OPTIONS)


run = pn.widgets.Button(name="Submit", button_type="primary")

progress_message = pn.Row(
    pn.indicators.LoadingSpinner(
        value=True, width=25, height=25, align="center", margin=(5, 0, 5, 10)
    ),
    pn.panel("Running classifier ...", margin=0),
)

layout = pn.Column("Click Submit")

def get_prediction(running):
    if not running:
        yield layout
        return

    layout.clear()
    for image in range(0,5):
        layout.append(progress_message)
        yield layout
        prediction = classify(None)
        result = f"Image {image} is a {prediction}"
        layout[-1]=result
        yield layout

pn.Column(run, pn.bind(get_prediction, run)).servable()
```

### Exercise: Replace the Generator with Reactive Expressions

Reimplement the app using *reactive expressions* (`pn.rx`). You are not allowed to use a generator function (`yield`).

:::{dropdown} Solution: pn.rx

```{pyodide}
import random
from time import sleep

import panel as pn

pn.extension()

OPTIONS = ["Wind Turbine", "Solar Panel", "Battery Storage"]

# State
results = pn.rx([])
is_running = pn.rx(False)

# Transformations

def classify(image):
    sleep(2)
    return random.choice(OPTIONS)

def classify_all(_):
    is_running.rx.value = True
    results.rx.value=[]

    for image in range(0, 5):
        prediction = classify(None)
        result = f"Image {image} is a {prediction}"
        results.rx.value = results.rx.value + [result]

        print(results_view.rx.value[0].object)

    is_running.rx.value = False

def _show_submit_message(results, is_running):
    return not results and not is_running

show_submit_message=pn.rx(_show_submit_message)(results, is_running)

# Inputs: Widgets

click_submit = pn.pane.Markdown("Click Submit", visible=show_submit_message)
run = pn.widgets.Button(
    name="Submit",
    button_type="primary",
    on_click=classify_all,
    disabled=is_running,
    loading=is_running,
)

# Outputs: Views

results_view = results.rx.pipe(lambda value: pn.Column(*value))

progress_message = pn.Row(
    pn.indicators.LoadingSpinner(
        value=True, width=25, height=25, align="center", margin=(5, 0, 5, 10)
    ),
    pn.panel("Running classifier ...", margin=0),
    visible=is_running
)

# Layout

pn.Column(run, click_submit, results_view, progress_message).servable()
```

:::

## Recap

In this tutorial, we have been running a slow *classifier* model and reported progress and results as they arrived:

- Use [*generator functions*](https://realpython.com/introduction-to-python-generators/) (`yield`) to progressively return content and update the app.
- Use [*reactive expressions*](../../reference/panes/ReactiveExpr.ipynb) (`pn.rx`) to drive progressive updates to the app

## Resources

### How to

- [Add interactivity with Generators](../../how_to/interactivity/bind_generators.md)
- [Migrate from Streamlit | Add Interactivity](../../how_to/streamlit_migration/interactivity.md)

### Component Gallery

- [ReactiveExpr](../../reference/panes/ReactiveExpr.md)
