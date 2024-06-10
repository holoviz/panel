# Add Interactivity with `pn.bind`

Both Streamlit and Panel are *reactive* frameworks that respond dynamically to user interactions within your application. However, their operational mechanics differ significantly:

**In Streamlit**:

- The script runs once when a user visits the page.
- The script reruns from the *top to bottom* upon any user interaction.

**In Panel**:

- The script runs once when a user visits the page.
- Only *specific, bound functions* are rerun based on user interactions.

Panel's interactivity architecture enables you to develop and maintain larger and more complex apps efficiently.

## Introduction

Panel's `pn.bind` function allows you to *bind* functions to widgets, creating what we refer to as *bound functions*.

To use `pn.bind`, follow these steps:

```python
# 1. Define your function(s)
def my_func(value):
    return ...
# 2. Define your widgets
slider = pn.widgets.IntSlider(...)
# 3. Bind your function to the widget(s)
my_bound_func = pn.bind(my_func, value=slider)
# 4. Layout and display your bound functions and widgets
pn.Column(slider, my_bound_func)
```

Once you've set up your functions and widgets as described, they will automatically update in response to user interactions.

## Migration Steps

Consider the following strategies for effective migration:

- Transition your core business logic into functions. This includes data loading, transformations, calculations, plot creations, complex computations like galaxy mass estimations, model training, and inference tasks.
- Enhance interactivity by using `pn.bind` to associate your functions with widgets.
  - For updates that occur multiple times during function execution, consider using generator functions (`yield`).
- Use visual feedback to indicate activity, as detailed in the [Show Activity Section](activity.md).

## Examples

### Basic Interactivity Example

Learn how to adapt your code for a straightforward result update that occurs once the execution completes.

#### Streamlit Basic Interactivity Example

```python
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from matplotlib.figure import Figure

data = np.random.normal(1, 1, size=100)
fig = Figure(figsize=(8,4))
ax = fig.subplots()
bins = st.slider(value=20, min_value=10, max_value=30, step=1, label="Bins")
ax.hist(data, bins=bins)

st.pyplot(fig)
```

![Streamlit Basic Interactivity Example](https://assets.holoviz.org/panel/gifs/streamlit_interactivity_example.gif)

In Streamlit, the entire script is rerun from top to bottom when the `bins` slider is adjusted.

#### Panel Basic Interactivity Example

```python
import panel as pn
import numpy as np

from matplotlib.figure import Figure

pn.extension(sizing_mode="stretch_width", template="bootstrap")

def plot(data, bins):
    fig = Figure(figsize=(8,4))
    ax = fig.subplots()
    ax.hist(data, bins=bins)
    return fig

data = np.random.normal(1, 1, size=100)
bins_input = pn.widgets.IntSlider(value=20, start=10, end=30, step=1, name="Bins")
bplot = pn.bind(plot, data=data, bins=bins_input)

pn.Column(bins_input, bplot).servable()
```

![Panel Basic Interactivity Example](https://assets.holoviz.org/panel/gifs/panel_interactivity_example.gif)

Panel updates more swiftly and smoothly by only rerunning the `plot` function when the `bins` slider is changed.

### Multiple Updates Example

Discover how to handle scenarios where a function needs to update the UI multiple times during its execution.

#### Streamlit Multiple Updates Example

```python
import random
import time

import streamlit as st

def calculation_a():
    time.sleep(1.5)
    return random.randint(0, 100)

def calculation_b():
    time.sleep(3.5)
    return random.randint(-100, 0)

st.write("# Calculation Runner")
option = st.radio("Which calculation would you like to perform?", ("A", "B"))
st.write("You chose: ", option)
if st.button("Press to run calculation"):
    with st.spinner("Running... Please wait!"):
        time_start = time.perf_counter()
        result = calculation_a() if option == "A" else calculation_b()
        time_end = time.perf_counter()
    st.write(f"""
Done!

Result: {result}

The function took {time_end - time_start:1.1f} seconds to complete
"""
    )
else:
    st.write(f"Calculation {option} did not run yet")
```

![Streamlit multiple updates example](https://assets.holoviz.org/panel/gifs/streamlit_runner_example.gif)

#### Panel Multiple Updates Example

In Panel, utilize a *generator function* to provide incremental updates during the function's execution.

```python
import time
import random

import panel as pn

pn.extension(sizing_mode="stretch_width", template="bootstrap")
pn.state.template.param.update(site="Panel", title="Calculation Runner")

def notify_choice(calculation):
    return f"You chose: {calculation}"

def calculation_a():
    time.sleep(2)
    return random.randint(0, 100)

def calculation_b():
    time.sleep(1)
    return random.randint(0, 100)

def run_calculation(running, calculation):
    if not running:
        yield "Calculation did not run yet"
        return # This will break the execution

    calc = calculation_a if calculation == "A" else calculation_b
    with run_input.param.update(loading=True):
        yield pn.indicators.LoadingSpinner(
            value=True, size=50, name='Running... Please Wait!'
        )
        time_start = time.perf_counter()
        result = calc()
        time_end = time.perf_counter()
        yield f"""
        Done!

        Result: {result}

        The function took {time_end - time_start:1.1f} seconds to complete
        """

calculation_input = pn.widgets.RadioBoxGroup(name="Calculation", options=["A", "B"])
run_input = pn.widgets.Button(
    name="Press to run calculation",
    icon="caret-right",
    button_type="primary",
    width=250,
)
pn.Column(
    "Which calculation would you like to perform?",
    calculation_input,
    pn.bind(notify_choice, calculation_input),
    run_input,
    pn.bind(run_calculation, run_input, calculation_input),
).servable()
```

![Panel Multiple Updates Example](https://assets.holoviz.org/panel/gifs/panel_runner_example.gif)

The use of `pn.indicators.LoadingSpinner` effectively signals ongoing activity during the calculation process.

#### Panel Multiple Updates Alternative Indicator Example

Instead of using a visual indicator, another approach involves modifying the `.disabled` and `.loading` parameters of the `calculation_input` and `run_input` to reflect the current state of the operation dynamically.

```python
import time
import random

import panel as pn

pn.extension(template="bootstrap")
pn.state.template.param.update(site="Panel", title="Calculation Runner")

def notify_choice(calculation):
    return f"You chose: {calculation}"

def calculation_a():
    time.sleep(2)
    return random.randint(0, 100)

def calculation_b():
    time.sleep(1)
    return random.randint(0, 100)

def run_calculation(running, calculation):
    if not running:
        return "Calculation did not run yet"

    calc = calculation_a if calculation == "A" else calculation_b
    with run_input.param.update(loading=True), calculation_input.param.update(disabled=True):
        time_start = time.perf_counter()
        result = calc()
        time_end = time.perf_counter()
        return f"""
        Done!

        Result: {result}

        The function took {time_end - time_start:1.1f} seconds to complete.
        """

calculation_input = pn.widgets.RadioBoxGroup(name="Calculation", options=["A", "B"])
run_input = pn.widgets.Button(
    name="Press to run calculation",
    icon="caret-right",
    button_type="primary",
    width=250,
)
pn.Column(
    "Which calculation would you like to perform?",
    calculation_input,
    pn.bind(notify_choice, calculation_input),
    run_input,
    pn.bind(run_calculation, run_input, calculation_input),
).servable()
```

![Panel Multiple Updates Alternative Example](https://assets.holoviz.org/panel/gifs/panel_generator_example.gif)

### Multiple Results Example

In some scenarios, such as with Large (AI) Language Models, you may need to output multiple results sequentially as they become available.

#### Streamlit Multiple Results Example

```python
import random
import time

import streamlit as st

run = st.button("Run model")

def model():
    time.sleep(1)
    return random.randint(0, 100)

if not run:
    st.write("The model has not run yet")
else:
    with st.spinner("Running..."):
        for i in range(10):
            result = model()
            st.write(f"Result {i}: {result}")
```

![Streamlit Multiple Results Example](https://assets.holoviz.org/panel/gifs/streamlit_multi_example.gif)

#### Panel Multiple Results Example

Panel utilizes a *generator function* to dynamically display multiple results from a single execution process as they become ready.

```python
import random
import time

import panel as pn

pn.extension(sizing_mode="stretch_width", template="bootstrap")

def model():
    time.sleep(1)
    return random.randint(0, 100)

def results(running):
    if not running:
        yield layout
        return

    layout.clear()
    for i in range(10):
        layout.append(loading)
        yield layout
        result = model()
        result = pn.panel(f"Result {i}: {result}")
        layout[-1] = result
        yield layout

run_input = pn.widgets.Button(name="Run model")
loading = pn.widgets.LoadingSpinner(value=True, size=50, name="Running... Please Wait!")
layout = pn.Column("Calculation did not run yet")

pn.Column(run_input, pn.bind(results, run_input)).servable()
```

![Panel Multiple Results Example](https://assets.holoviz.org/panel/gifs/panel_sync_multi_example.gif)
