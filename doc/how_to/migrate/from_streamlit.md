# Migrate from Streamlit

This guide addresses how to migrate from Streamlit to Panel.

This guide can also be used as

- an alternative *Introduction to Panel* guide if you are already familiar with Streamlit.
- a means of comparing Streamlit and Panel on a more detailed level. You won't see the unique
features that Panel provides though.

---

## The Basics

Lets start by converting a *Hello World* application.

### Streamlit Hello World Example

```python
import streamlit as st

st.write("Hello World")
```

You *run* and *show* the app with *autoreload* via

```bash
streamlit run app.py
```

The application looks like

![Streamlit Hello World Example](https://user-images.githubusercontent.com/42288570/243343663-63c4c22b-ca56-4d50-95f7-3de6be69a372.png)

### Panel Hello World Example

```python
import panel as pn

pn.extension(sizing_mode="stretch_width", template="bootstrap")

pn.panel("Hello World").servable()
```

You use `pn.extension` to configure the application.

- You set the `sizing_mode` to `stretch_width` to get the *responsive* behaviour you expect from
Streamlit apps.
- You set the `template` to `bootstrap` to wrap your application in a nice looking template as you
expect from Streamlit apps. If you don't set a template you will get a blank template to add your
components to. You can see the available templates in the
[Templates Section](https://panel.holoviz.org/reference/index.html#templates) of the
[Component Gallery](https://panel.holoviz.org/reference/index.html).

You use `pn.panel` similarly to `st.write` to *magically* display
Python objects like (markdown) strings, dataframes, plots and more. Check out the
[`pn.panel` API Reference](https://panel.holoviz.org/api/panel.pane.html#panel.pane.panel) for the
details.

You use `.servable` to specify the Panel objects you want to add the Panel *template* when
served as a web app.

You *serve* and *show* the app with *autoreload* via

```bash
panel serve app.py --autoreload --show
```

See the [Command Line Guide](https://panel.holoviz.org/how_to/server/commandline.html) for more
command line options.

The application looks like

![Panel Hello World Example](https://user-images.githubusercontent.com/42288570/243343688-e6212faa-7b05-4686-b113-b67cd21e1063.png)

### Basic Migration Steps

You should replace

- `import streamlit as st` with `import panel as pn` and
- `st.write` with `pn.panel`.

You will also have to

- add `pn.extension` to configure your Panel application via arguments like `sizing_mode` and `template`.
- add `.servable` to the Panel objects you want to include in your apps *template* when served as
a web app.

For production you will also have to

- Migrate some of your app configuration to `panel serve` command line options or environment
variables.

You won't have to

- Provide your email or
- opt out of telemetry data collection.

We have never collected or had plans to collect telemetry data from our users apps.

## Displaying Content

In Panel the objects that can display your Python objects are called *panes*. With Panels *panes*
you will be able to

- get notifications about interactions like click events on your plots and tables and react to them.
- use unique data visualization ecosystems like HoloViz, ipywidgets and VTK.

Check out the
[Panes Section](https://panel.holoviz.org/reference/index.html#panes) of
the [Component Gallery](https://panel.holoviz.org/reference/index.html) for the full list of
*panes*.

### Streamlit Matplotlib Example

```python
import numpy as np
import streamlit as st

import matplotlib.pyplot as plt

data = np.random.normal(1, 1, size=100)
fig, ax = plt.subplots(figsize=(8,4))
ax.hist(data, bins=20)

st.pyplot(fig)
```

The app looks like

![Streamlit Matplotlib Example](https://user-images.githubusercontent.com/42288570/243348167-4d2a3c36-59dc-4df5-b266-84dd1837f2b6.png)

### Panel Matplotlib Example

You will find Panels output *panes* in `pn.pane` module.

```python
import panel as pn
import numpy as np

from matplotlib.figure import Figure

pn.extension(sizing_mode="stretch_width", template="bootstrap")

data = np.random.normal(1, 1, size=100)
fig = Figure(figsize=(8,4))
ax = fig.subplots()
ax.hist(data, bins=20)

pn.pane.Matplotlib(fig, format='svg', sizing_mode='scale_both').servable()
```

We use Matplotlibs `Figure` interface instead of the `pyplot` interface to
avoid memory leaks if you forget to close the figure. This is all described in the
[Matplotlib Guide](https://panel.holoviz.org/reference/panes/Matplotlib.html).

The app looks like

![Panel Matplotlib Example](https://user-images.githubusercontent.com/42288570/243348449-233d1dcc-fdd3-4907-9085-50bf0772065f.png)

### Output Migration Steps

You should

- replace your Streamlit `st.some_object` function with the corresponding Panel
`pn.pane.SomeObject` class.

You can identify the corresponding Panel *pane* in the
[Panes Section](https://panel.holoviz.org/reference/index.html#panes) of the
[Component Gallery](https://panel.holoviz.org/reference/index.html).

## Inputs

In Panel the objects that can accept user inputs are called *widgets*.

Panel provides widgets similar to the ones you know from Streamlit and some unique ones in addition.

Check out the
[Widgets Section](https://panel.holoviz.org/reference/index.html#widgets) of
the [Component Gallery](https://panel.holoviz.org/reference/index.html) for the full list of
*widgets*.

### Streamlit Integer Slider Example

```python
import streamlit as st

bins = st.slider(value=20, min_value=10, max_value=30, step=1, label="Bins")

st.write(bins)
```

The app looks like

![Streamlit Widgets Example](https://user-images.githubusercontent.com/42288570/243349378-a27fa7bd-b8dc-4b30-85f0-684a74ec40cf.png)

### Panel Integer Slider Example

You will find Panels input *widgets* in `pn.widgets` module.

```python
import panel as pn

pn.extension(sizing_mode="stretch_width", template="bootstrap")

bins = pn.widgets.IntSlider(value=20, start=10, end=30, step=1, name="Bins")

pn.Column(bins, pn.pane.Str(bins)).servable()
```

If you check the type of the variables, you will notice a key difference. Streamlit's `bins` returns the value of the slider as an `integer` while Panel's `bins` returns an `IntSlider`!

To access the value of the slider in Panel, you would need to call `bins.value`.

For more info about the `IntSlider` check out the
[`IntSlider` Guide](https://panel.holoviz.org/reference/widgets/IntSlider.html).

The app looks like

![Panel Widgets Example](https://user-images.githubusercontent.com/42288570/243349394-084dfd83-a9fd-404e-9408-78831c2ca2e5.png)

### Input Migration Steps

You should

- replace your Streamlit `st.some_widget` function with the corresponding Panel
`pn.widgets.SomeWidget` class.

You can identify the corresponding widget via the
[Widgets Section](https://panel.holoviz.org/reference/index.html#widgets) of the
[Component Gallery](https://panel.holoviz.org/reference/index.html).

## Layouts

*Layouts* helps you organize your *panes* and *widgets*.

Panel provides layouts similar to the ones you know from Streamlit and some unique ones.

Check out the [Layouts Section](https://panel.holoviz.org/reference/index.html#layouts) of the
[Component Gallery](https://panel.holoviz.org/reference/index.html) for the full list of *layouts*.

### Streamlit Layout Example

```python
import streamlit as st

col1, col2 = st.columns(2)

with col1:
    st.image("https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png")
    st.write("# A faster way to build and share data apps")

with col2:
    st.image("https://panel.holoviz.org/_images/logo_horizontal_light_theme.png")
    st.write("# The powerful data exploration & web app framework for Python")
```

The app looks like

![Streamlit Layout Example](https://user-images.githubusercontent.com/42288570/243353648-add1e7af-26ba-428b-ba47-2f602ff3ce93.png)

I would love to align the images (and texts) but I could not find functionality like *row*, *margin* or *spacing* to do this.

### Panel Layout Example

You will find Panels *layouts* in the `pn` module.

```python
import panel as pn

pn.extension(sizing_mode="stretch_width", template="bootstrap")

col1 = pn.Column(
    pn.pane.Image("https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png"),
   "# A faster way to build and share data apps"
)
col2 = pn.Column(
    pn.pane.Image("https://panel.holoviz.org/_images/logo_horizontal_light_theme.png"),
    pn.panel("# The powerful data exploration & web app framework for Python"),
)

pn.Row(col1, col2).servable()
```

Panels `Column` and `Row` are *list like* objects. So you can use familiar methods like `.append`,
`.pop` and `[]` indexing when you work with them. For the details check out the
[`Column` Guide](https://panel.holoviz.org/reference/layouts/Column.html) and
the [`Row` Guide](https://panel.holoviz.org/reference/layouts/Row.html).

The app looks like

![Panel Layout Example](https://user-images.githubusercontent.com/42288570/243362603-45ba78a4-d67b-43bc-b3c2-386105fe6ed8.png)

### Layout Migration Steps

You should

- replace your Streamlit `st.some_layout` function with the corresponding Panel
`pn.SomeLayout` class.

You can identify the relevant layout to migrate to in the
[Layouts Section](https://panel.holoviz.org/reference/index.html#layouts) of the
[Component Gallery](https://panel.holoviz.org/reference/index.html).

### Template Migration Steps

When migrating you first have to choose which template to use

- None (default)
- A built in like *vanilla*, *bootstrap*, *material* or *fast*. See the
[Templates Section](../../reference/index#templates) of the
[Components Guide](../../reference/index).
- A custom template

Then you have to configure it.

#### Panel Template Example

Here is an example with the [`FastListTemplate`](https://panel.holoviz.org/reference/templates/FastListTemplate.html) for illustration.

```python
import panel as pn
from datetime import datetime
from asyncio import sleep
import panel as pn
from asyncio import sleep

pn.extension(sizing_mode="stretch_width", template="fast", theme="dark")

pn.Column(
    "# 📖 Info",
    """This app is an example of a built in template with a
*sidebar*, *header* and *main* area.

We have

- set the *header* background, site and title parameters
- set the default *theme* to `dark`

The app streams the current date and time using an *async generator function*.
""",
).servable(target="sidebar")


async def stream():
    for i in range(0, 100):
        await sleep(0.25)
        yield datetime.now()


pn.Column("The current date and time:", *(stream for i in range(5))).servable(
    target="main"
)

pn.state.template.param.update(
    site="Panel",
    title="Template Example",
    header_background="#E91E63",
    accent_base_color="#E91E63",
)
```

The app looks like

![Panel Template Example](https://user-images.githubusercontent.com/42288570/243438919-edce17a0-48b6-451d-9be3-d86eff5cc166.gif)

## Show Activity

Panel supports two ways of indicating activity

- Indicators. See the [Indicators Section](https://panel.holoviz.org/reference/index.html#indicators)
of the [Component Gallery](https://panel.holoviz.org/reference/index.html).
- `disabled`/ `loading` parameters on Panel components

We will show you how to migrate your Streamlit activity indicators to Panel in the
[Interactivity Section](#interactivity) just below.

## Interactivity

Both Streamlit and Panel are *reactive* frameworks that *react* when you interact with your
application. But they work very differently:

- Streamlit executes the whole script *top to bottom* on user interactions.
- Panel executes specific *bound* functions on user interactions.

Panel supports reacting to many more interactions than Streamlit. For example interactions with
tables and plots.

Panels `pn.bind` provides the functionality to *bind* functions to widgets. We call the resulting
functions *bound functions*.

With Panels interactivity architecture you will be able to develop and maintain larger and more
complex apps to support more use cases.

### Basic Interactivity Example

This example will show you how to migrate code that produces a single result
and only updates the UI once the code execution has completed.

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

The app looks like

![Streamlit Basic Interactivity Example](https://user-images.githubusercontent.com/42288570/243358295-c26e90c2-0053-4441-9b98-2426d6d1a8e1.gif)

The entire script is rerun *top to bottom* when you change the `bins` slider.

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

pn.Column(bins, bplot).servable()
```

Only the `plot` function is rerun when you change the `bins` slider. You specify that
by *binding* the `plot` function to the `bins` widget using `pn.bind`.

The app looks like

![Panel Basic Interactivity Example](https://user-images.githubusercontent.com/42288570/243358311-04ed5189-1a79-4932-97ea-00898c27f283.gif)

You might notice that the Panel app updates much quicker and more smoothly than the Streamlit app.
This is due to fundamental differences in architectures. With Panel you will be able to
develop very smooth and performant apps.

### Multiple Updates Example

This example will show you how to migrate code that produces a single result
and updates the UI multiple times during the code execution.

#### Streamlit Multiple Updates Example

```python
import random
import time

import streamlit as st


def calculation_a():
    time.sleep(1.5)
    return random.randint(0, 100)


def calculation_b():
    time.sleep(1.5)
    return random.randint(0, 100)


st.write("# Calculation Runner")

option = st.radio("Which calculation would you like to perform?", ("A", "B"))

st.write("You chose: ", option)
if option == "A":
    if st.button("Press to run calculation"):
        with st.spinner("Running... Please wait!"):
            time_start = time.perf_counter()
            result = calculation_a()
            time_end = time.perf_counter()
            st.write(f"""Done!

Result: {result}

The function took {time_end - time_start:1.1f} seconds to complete""")

    else:
        st.write("Calculation A did not run yet")

elif option == "B":
    if st.button("Press to run calculation"):
        with st.spinner("Running... Please wait!"):
            time_start = time.perf_counter()
            result = calculation_b()
            time_end = time.perf_counter()
            st.write(f"""Done!

Result: {result}

The function took {time_end - time_start:1.1f} seconds to complete""")
    else:
        st.write("Calculation B did not run yet")
```

The app looks like

![Streamlit multiple updates example](https://user-images.githubusercontent.com/42288570/243399616-4f172e4b-ace9-4761-b19a-757a532bafbc.gif)

#### Panel Multiple Updates Example

With Panel you will use a *generator function* to update a component multiple times during code execution.

```python
import time
import random
from textwrap import dedent

import panel as pn

pn.extension(sizing_mode="stretch_width", template="bootstrap")
pn.state.template.param.update(site="Panel", title="Calculation Runner")


def notify_choice(calculation):
    return f"You chose: {calculation}"


def calculation_a():
    time.sleep(1.5)
    return random.randint(0, 100)


def calculation_b():
    time.sleep(1.5)
    return random.randint(0, 100)


def run_calculation(running, calculation):
    if not running:
        yield "Calculation did not run yet"
        return  # This will break the execution
    yield pn.Row(
        pn.indicators.LoadingSpinner(value=True, width=50, height=50, align="center"),
        "Running... Please wait!",
        align="center",
    )
    if calculation == "A":
        func = calculation_a
    else:
        func = calculation_b
    time_start = time.perf_counter()
    result = func()
    time_end = time.perf_counter()
    yield dedent(
        f"""
        Done!
        Result: {result}
        The function took {time_end - time_start:1.1f} seconds to complete
        """
    )


calculation_input = pn.widgets.RadioBoxGroup(name="Calculation", options=["A", "B"])
run_input = pn.widgets.Button(
    name="Press to run calculation",
    icon="caret-right",
    button_type="primary",
    sizing_mode="fixed",
    width=250,
)
pn.Column(
    "Which calculation would you like to perform?",
    calculation_input,
    pn.bind(notify_choice, calculation_input),
    run_input,
    pn.bind(run_calculation, run_input, calculation_input),
).servable()
).servable()
```

We use the `pn.indicators.LoadingSpinner` to indicate the activity. You find the full list of indicators in the [Indicators Section](https://panel.holoviz.org/reference/index.html#indicators) of the [Component Gallery](https://panel.holoviz.org/reference/index.html).

The app looks like

![Panel Multiple Updates Examples](https://user-images.githubusercontent.com/42288570/243399714-04345c38-44a8-4bc0-b111-a8d26f03484b.gif)

#### Panel Multiple Updates Alternative Indicator Example

An alternative to using an *indicator* would be to change the `.disabled` and `.loading` parameters of the `calculation_input` and `run_input`.

```python
import time
import random
from textwrap import dedent

import panel as pn

pn.extension(sizing_mode="stretch_width", template="bootstrap")
pn.state.template.param.update(site="Panel", title="Calculation Runner")


def notify_choice(calculation):
    return f"You chose: {calculation}"


def calculation_a():
    time.sleep(1.5)
    return random.randint(0, 100)


def calculation_b():
    time.sleep(1.5)
    return random.randint(0, 100)


def run_calculation(running, calculation):
    if not running:
        yield "Calculation did not run yet"
        return  # This will break the execution
    try:
        calculation_input.loading = True
        run_input.loading = True
        yield pn.Row(
            pn.indicators.LoadingSpinner(value=True, width=50, height=50, align="center"),
            "Running... Please wait!",
            align="center",
        )
        if calculation == "A":
            func = calculation_a
        else:
            func = calculation_b
        time_start = time.perf_counter()
        result = func()
        time_end = time.perf_counter()
        yield dedent(
            f"""
            Done!
            Result: {result}
            The function took {time_end - time_start:1.1f} seconds to complete
            """
        )
    finally:
        calculation_input.loading = False
        run_input.loading = False


calculation_input = pn.widgets.RadioBoxGroup(name="Calculation", options=["A", "B"])
run_input = pn.widgets.Button(
    name="Press to run calculation",
    icon="caret-right",
    button_type="primary",
    sizing_mode="fixed",
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

The app looks like

![Panel Multiple Updates Alternative Example](https://user-images.githubusercontent.com/42288570/243402005-0e520ed0-a41f-4339-a854-14ff31cb04ce.gif)

### Multiple Results Example

Sometimes you want to output multiple results individually as soon as they are ready.

This is for example the case for Large (AI) Language Models that generates one token after the other.

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
        for i in range(0,10):
            result = model()
            st.write(f"Result {i}: {result}")
```

The app looks like

![Streamlit Multiple Results Example](https://user-images.githubusercontent.com/42288570/243421817-bcd0d8d4-89af-4ef4-8924-f20a8d7a8d33.gif)

#### Panel Multiple Results Example

With Panel you will use a *generator function* to display multiple results from code execution as soon as they are ready.

```python
import random
import time

import panel as pn

pn.extension(sizing_mode="stretch_width", template="bootstrap")

run_input = pn.widgets.Button(name="Run model")

def model():
    time.sleep(1)
    return random.randint(0, 100)

def results(running):
    if not running:
        yield "Calculation did not run yet"
        return # This will break the execution

    run_input.disabled=True
    loading_indicator = pn.Row(pn.indicators.LoadingSpinner(value=True, width=50, height=50, align="center"), "Running... Please wait!", align="center")
    layout = pn.Column(loading_indicator)
    yield layout # This will display the layout

    for i in range(0,10):
        result = model()
        message = f"Result {i}: {result}"
        layout.append(message)
        yield layout # This will force the UI to update

    layout.pop(0)
    run_input.disabled=False
    yield layout # This will force the UI to update


pn.Column(run_input, pn.bind(results, run_input)).servable()
```

![Panel Multiple Results Example](https://user-images.githubusercontent.com/42288570/243421842-b6c29bb0-b814-4d96-9918-946deea807ff.gif)

### Interactivity Migration Steps

You should

- Move your business logic to functions. Business logic can be code to load data,
create plots, calculate the mass of the milky way, train models, do inference etc.
- Use `pn.bind` to specify which functions are bound to which widgets.
- Use generator functions (`yield`) if you want to update the UI multiple times during the
  code execution.
- Indicate activity if needed. You can use one of
[Panels Indicators](https://panel.holoviz.org/reference/index.html#indicators) and/ or
the `.disabled`+`.loading` parameter on Panels components.

## Caching

One of the key concepts in Streamlit is *caching*. In Streamlit your entire script is rerun
*top to bottom* on user interactions. Without caching you would be
reconnecting to your database, reloading your dataset and rerunning your expensive calculation
every time a user clicks a `Button` or changes a `slider` value. This would make your application
very slow.

In Panel only your *bound functions* are rerun on user interactions.

In Panel you would use the

- *session cache* (`pn.cache`) to speed up expensive, bound functions for a user session
- *global cache* (`pn.state.as_cached`) to speed up expensive, bound functions or to share
Python objects globally. I.e. across user sessions.

Check out the [Cache How-To Guides](https://panel.holoviz.org/how_to/caching/index.html) for the
details.

### Session Cache Example

This session will show you how to cache for a user session.

#### Streamlit Session Cache Example

```python
from time import sleep

import numpy as np
import streamlit as st
from matplotlib.figure import Figure

@st.cache_data
def get_data():
    print("get_data func")
    sleep(1.0)
    return np.random.normal(1, 1, size=100)

@st.cache_data(hash_funcs={Figure: lambda _: None})
def plot(data, bins):
    print("plot func", bins)
    sleep(0.25)
    fig = Figure(figsize=(8,4))
    ax = fig.subplots()
    ax.hist(data, bins=bins)
    return fig

data = get_data()
bins = st.slider(value=20, min_value=10, max_value=30, step=1, label="Bins")
st.pyplot(plot(data, bins))
```

I've added

- `sleep` statements to make the functions more *expensive*.
- `print` statements to show you that the functions are only runs once for a specific set of
arguments.

#### Panel Session Cache Example

```python
from time import sleep

import numpy as np
import panel as pn
from matplotlib.figure import Figure


def get_data():
    print("get_data func")
    sleep(1.0)
    return np.random.normal(1, 1, size=100)

def plot(data, bins):
    print("plot func", bins)
    sleep(0.25)
    fig = Figure(figsize=(8,4))
    ax = fig.subplots()
    ax.hist(data, bins=bins)
    return fig

pn.extension(sizing_mode="stretch_width", template="bootstrap")

data = get_data()
bins = pn.widgets.IntSlider(value=20, start=10, end=30, step=1)
cplot = pn.cache(plot)
bplot = pn.bind(cplot, data, bins)
pn.Column(bins, bplot).servable()
```

You can also use `pn.cache` as an annotation similar to `st.cache_data`. I.e. as

```python
@pn.cache
def plot(data, bins):
    ...
```

Be aware the the annotation approach has a tendency to mix up your business logic
(`data` and `plot` function) and your caching logic (when and how to apply caching). This can make
your code harder to maintain and reuse for other use cases.

### Global Cache Example

This session will show you how to cache globally, i.e. across user sessions

#### Streamlit Global Cache Example

```python
from time import sleep

import numpy as np
import streamlit as st
from matplotlib.figure import Figure

@st.cache_resource
def get_data():
    print("get_data func")
    sleep(1.0)
    return np.random.normal(1, 1, size=100)

@st.cache_data(hash_funcs={Figure: lambda _: None})
def plot(data, bins):
    print("plot func", bins)
    sleep(0.25)
    fig = Figure(figsize=(8,4))
    ax = fig.subplots()
    ax.hist(data, bins=bins)
    return fig

data = get_data()
bins = st.slider(value=20, min_value=10, max_value=30, step=1, label="Bins")
st.pyplot(plot(data, bins))
```

The global cache `st.cache_resource` is used on the `get_data` function to only load the data once
across all users sessions.

#### Panel Global Cache Example

```python
from time import sleep

import numpy as np
import panel as pn
from matplotlib.figure import Figure


def get_data():
    print("data func")
    sleep(1.0)
    return np.random.normal(1, 1, size=100)

def plot(data, bins):
    print("plot func", bins)
    sleep(0.25)
    fig = Figure(figsize=(8,4))
    ax = fig.subplots()
    ax.hist(data, bins=bins)
    return fig

pn.extension(sizing_mode="stretch_width", template="bootstrap")

data = pn.state.as_cached(key="data", fn=get_data) # Global Cache
bins = pn.widgets.IntSlider(value=20, start=10, end=30, step=1)
cplot = pn.cache(plot) # Session Cache
bplot = pn.bind(cplot, data, bins)
pn.Column(bins, bplot).servable()
```

The global cache `pn.state.as_cached` is used on the `get_data` function to only load the data once
across all users sessions.

### Cache Migration Steps

To migrate

- replace `st.cache_data` with `pn.cache` to migrate your *session caching*
  - You only need to cache expensive, *bound functions*.
- replace `st.cache_resource` with `pn.state.as_cached` to migrate your *global caching*
  - You only need to cache expensive, *bound functions* and objects you want to share across user
  sessions

In the process consider separating your business logic and caching logic
(when and how to apply caching) to get more maintainable and reusable code.

## Multi Page Apps

Migrating your Streamlit multi page app to Panel is simple. In Panel each page is simply a file
that you *serve*

```bash
panel serve home.py page1.py page2.ipynb
```

You can specify the *home* page with the `--index` flag.

```bash
panel serve home.py page1.py page2.ipynb --index=home
```

## Migration Support

We hope you will have fun with the Panel framework. If you have usage questions you can post them
on [Discourse](https://discourse.holoviz.org/). If you experience issues or have requests for
features please post them on [Github](https://github.com/holoviz/panel).

If you want to support Panel please

- give a ⭐ on [Github](https://github.com/holoviz/panel) or
- donate to [HoloViz](https://holoviz.org/) via [Numfocus](https://numfocus.org/support#donate)
