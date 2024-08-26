# Update Progressively

Welcome to the "Update Progressively" tutorial! Here, we'll explore an exciting aspect of HoloViz Panel: progressively updating content while running a slow classifier model.

In this tutorial, we'll:

- Utilize generator functions (`yield`) to progressively return content and update the app.
- Harness the power of reactive expressions (`pn.rx`) to facilitate dynamic updates to the app.

:::{note}
When instructed to run the code, you can execute it directly in the Panel documentation using the green *run* button, in a notebook cell, or in a file named `app.py` served with `panel serve app.py --autoreload`.
:::

## Replace Content Progressively

### Replace using a Generator

Let's kick off by replacing content progressively with the help of a generator function.

```{pyodide}
import random
from time import sleep
import panel as pn

pn.extension()

OPTIONS = ["Wind Turbine", "Solar Panel", "Battery Storage"]

# Classifier function
def classify(image):
    sleep(2)
    return random.choice(OPTIONS)

# Components
run = pn.widgets.Button(name="Submit", button_type="primary")

progress_message = pn.Row(
    pn.indicators.LoadingSpinner(
        value=True, width=25, height=25, align="center", margin=(5, 0, 5, 10)
    ),
    pn.panel("Running classifier ...", margin=0),
)

# Generator function
def get_prediction(running):
    if not running:
        yield "Click Submit"
        return

    yield progress_message
    prediction = classify(None)
    yield f"It's a {prediction}"

# Display
pn.Column(run, pn.bind(get_prediction, run)).servable()
```

Click the *Submit* `Button` to see it in action!

#### Exercise: Disable the Button

Now, let's enhance our app by disabling the button while the classification is running.

:::::{dropdown} Solution

```{pyodide}
import random
from time import sleep
import panel as pn

pn.extension()

OPTIONS = ["Wind Turbine", "Solar Panel", "Battery Storage"]

# Classifier function
def classify(image):
    sleep(2)
    return random.choice(OPTIONS)

# Components
run = pn.widgets.Button(name="Submit", button_type="primary")

progress_message = pn.Row(
    pn.indicators.LoadingSpinner(
        value=True, width=25, height=25, align="center", margin=(5, 0, 5, 10)
    ),
    pn.panel("Running classifier ...", margin=0),
)

# Generator function
def get_prediction(running):
    if not running:
        yield "Click Submit"
        return

    run.disabled = True
    yield progress_message
    prediction = classify(None)
    yield f"It's a {prediction}"
    run.disabled = False

# Display
pn.Column(run, pn.bind(get_prediction, run)).servable()
```

:::::

### Replace using Reactive Expressions

Another approach to achieve the same functionality is by using reactive expressions (`pn.rx`).

```{pyodide}
import random
from time import sleep
import panel as pn

pn.extension()

OPTIONS = ["Wind Turbine", "Solar Panel", "Battery Storage"]

# State
result = pn.rx("")
is_running = pn.rx(False)

# Classifier function
def classify(image):
    sleep(2)
    return random.choice(OPTIONS)

# Reactive expressions
def _show_submit_message(result, is_running):
    return not result and not is_running

show_submit_message = pn.rx(_show_submit_message)(result, is_running)

def run_classification(_):
    result.rx.value = ""
    is_running.rx.value = True
    prediction = classify(None)
    result.rx.value = f"It's a {prediction}"
    is_running.rx.value = False

# Components
click_submit = pn.pane.Markdown("Click Submit", visible=show_submit_message)
run = pn.widgets.Button(
    name="Submit", button_type="primary", on_click=run_classification
)
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

Click the *Submit* `Button` to observe the magic!

## Append Content Progressively

### Append using Generator

Now, let's explore how to append content progressively using a generator.

```{pyodide}
import panel as pn
from time import sleep
import random

pn.extension()

OPTIONS = ["Wind Turbine", "Solar Panel", "Battery Storage"]

# Classifier function
def classify(image):
    sleep(2)
    return random.choice(OPTIONS)

# Components
run = pn.widgets.Button(name="Submit", button_type="primary")

progress_message = pn.Row(
    pn.indicators.LoadingSpinner(
        value=True, width=25, height=25, align="center", margin=(5, 0, 5, 10)
    ),
    pn.panel("Running classifier ...", margin=0),
)

layout = pn.Column("Click Submit")

# Generator function
def get_prediction(running):
    if not running:
        yield layout
        return

    layout.clear()
    for image in range(0, 5):
        layout.append(progress_message)
        yield layout
        prediction = classify(None)
        result = f"Image {image} is a {prediction}"
        layout[-1] = result
        yield layout

# Display
pn.Column(run, pn.bind(get_prediction, run)).servable()
```

### Exercise: Replace the Generator with Reactive Expressions

Let's reimplement the app using reactive expressions (`pn.rx`), without using a generator function (`yield`).

:::::{dropdown} Solution

```{pyodide}
import random
from time import sleep

import panel as pn

pn.extension()

OPTIONS = ["Wind Turbine", "Solar Panel", "Battery Storage"]

# State
results = pn.rx([])
is_running = pn.rx(False)

# Classifier function
def classify(image):
    sleep(2)
    return random.choice(OPTIONS)

# Reactive expressions
def _show_submit_message(results, is_running):
    return not results and not is_running

show_submit_message = pn.rx(_show_submit_message)(results, is_running)

def classify_all(_):
    is_running.rx.value = True
    results.rx.value = []

    for image in range(0, 5):
        prediction = classify(None)
        result = f"Image {image} is a {prediction}"
        results.rx.value = results.rx.value + [result]

    is_running.rx.value = False

# Components
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
    visible=is_running,
)

# Layout
pn.Column(run, click_submit, results_view, progress_message).servable()
```

:::::

## Recap

In this tutorial, we've explored how to progressively update content in a Panel app:

- We learned how to utilize generator functions (`yield`) for progressive updates.
- We also explored the usage of reactive expressions (`pn.rx`) for dynamic content updates.

Keep experimenting and building with Panel! 🚀

## Resources

### How to

- [Add interactivity with Generators](../../how_to/interactivity/bind_generators.md)
- [Migrate from Streamlit | Add Interactivity](../../how_to/streamlit_migration/interactivity.md)

### Component Gallery

- [ReactiveExpr](../../reference/panes/ReactiveExpr.md)

Feel free to reach out on [Discord](https://discord.gg/rb6gPXbdAr) if you have any questions or need further assistance!
