# Migrate from Streamlit

This guide addresses how to migrate from Streamlit to Panel via examples.

This how-to guide can also be used as

- an alternative *introduction to Panel* guide if you are already familiar with Streamlit.
- a means of comparing Streamlit and Panel.

---

## Hello World

Lets start by converting a *Hello World* application.

### Streamlit Hello World Example

In Streamlit a *Hello World* application looks like

```python
import streamlit as st

st.write("Hello World")
```

You *serve* and *show* the app with *autoreload* via

```bash
streamlit run app.py
```

### Panel Hello World Example

In Panel this looks like

```python
import panel as pn

pn.extension(sizing_mode="stretch_width", template="bootstrap")

pn.panel("Hello World").servable()
```

We use `pn.extension` to configure your application.

- We set the `sizing_mode` to `stretch_width` to get the *responsive* behaviour you expect from
Streamlit apps.
- We set the `template` to `bootstrap` to wrap your application in a nice template as you expect
from Streamlit apps. If you don't set a template you will get a blank template to add your
components to. You can see the available templates in the
[Templates Section](https://panel.holoviz.org/reference/index.html#templates) of the
[Component Gallery](https://panel.holoviz.org/reference/index.html).

We use `pn.panel` similarly to `st.write` to *magically* display
Python objects like (markdown) strings, dataframes, plots and more. Check out the
[`pn.panel` API Reference](https://panel.holoviz.org/api/panel.pane.html#panel.pane.panel) for the
details.

We use `.servable` to specify the Panel objects we want to add the Panel *template* when
served as a web app.

You *serve* and *show* the app with *autoreload* via

```bash
panel serve app.py --autoreload --show
```

See the [Command Line Guide](https://panel.holoviz.org/how_to/server/commandline.html) for more
command line options.

### Hello World Migration Steps

You can replace

- `import streamlit as st` with `import panel as pn` and
- `st.write` with `pn.panel`.

You will also have to

- add `pn.extension(...)` to configure your Panel application.
- add `.servable()` to the Panel objects you want to include in your apps *template* when served as
a web app.

For production you will also have to

- Migrate some of your app configuration to `panel serve` command line options or environment
variables.

You won't have to

- Provide your email or
- opt out of telemetry data collection.

We have never collected or had plans to collect telemetry data from our users apps.

## Outputs

In Panel the objects that can display your Python objects are called *panes*.

With Panels *panes* you will be able to

- get notifications about interactions like click events on your plots and tables and react to them.
- also access data visualization ecosystems like HoloViz, ipywidgets and VTK.

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
fig, ax = plt.subplots()
ax.hist(data, bins=20)

st.pyplot(fig)
```

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

pn.pane.Matplotlib(fig).servable()
```

We use Matplotlibs `Figure` interface instead of the `pyplot` interface to
avoid memory leaks if you forget to close the figure. Check out the
[Matplotlib Guide](https://panel.holoviz.org/reference/panes/Matplotlib.html) for the details.

### Output Migration Steps

You should

- replace your Streamlit `st.output_me` function with the corresponding Panel `pn.pane.OutputMe`
class.

You can identify the corresponding Panel *panes* in the
[Panes Section](https://panel.holoviz.org/reference/index.html#panes) of the
[Component Gallery](https://panel.holoviz.org/reference/index.html).

## Inputs

In Panel the objects that can provide you with input values from users are called *widgets*.

Panel provides widgets similar to the ones you know from Streamlit and some unique ones.

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

### Panel Integer Slider Example

You will find Panels input *widgets* in `pn.widgets` module.

```python
import panel as pn

pn.extension(sizing_mode="stretch_width", template="bootstrap")

bins = pn.widgets.IntSlider(value=20, start=10, end=30, step=1, name="Bins").servable()

pn.pane.Str(bins).servable()
```

If you debug and inspect the code your will notice a big difference. Streamlits `bins` value is an
`integer` while Panels `bins` value is an `IntSlider`. This is the first real indication that
Streamlit and Panel works in very different ways.

For more info about the `IntSlider` check out the
[`IntSlider` Guide](https://panel.holoviz.org/reference/widgets/IntSlider.html).

### Input Migration Steps

You should

- replace your Streamlit `st.input_widget` function with the corresponding Panel
`pn.widgets.InputWidget` class.

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
    st.write("# The powerful data exploration & web app framework for Python")

with col2:
    st.image("https://panel.holoviz.org/_images/logo_horizontal_light_theme.png")
    st.write("# A faster way to build and share data apps")
```

TODO: Find and replace with the square Panel logo

### Panel Layout Example

You will find Panels *layouts* in the `pn` module.

```python
import panel as pn

pn.extension(sizing_mode="stretch_width", template="bootstrap")

col1 = pn.Column(
    pn.pane.Image("https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png"),
    pn.panel("# A faster way to build and share data apps")
)
col2 = pn.Column(
    pn.pane.Image("https://panel.holoviz.org/_images/logo_horizontal_light_theme.png"),
    pn.panel("# The powerful data exploration & web app framework for Python"),
)

pn.Row(col1, col2).servable()
```

TODO: Find and replace with the square Panel logo

Panels `Column` and `Row` are *list like* objects. So you can use familiar methods like `.append`,
`.pop` and `[]` indexing when you work with them. For the details check out the
[`Column` Guide](https://panel.holoviz.org/reference/layouts/Column.html) and
the [`Row` Guide](https://panel.holoviz.org/reference/layouts/Row.html).

### Layout Migration Steps

You should

- replace your Streamlit `st.some_layout` function with the corresponding Panel
`pn.SomeLayout` class.

You can identify the relevant layout to migrate to in the
[Layouts Section](https://panel.holoviz.org/reference/index.html#layouts) of the
[Component Gallery](https://panel.holoviz.org/reference/index.html).

### Interactivity

Both Streamlit and Panel are *reactive* frameworks that *react* when you interact with your
application. But they work very differently:

- Streamlit executes the whole script *top to bottom* on user interactions.
- Panel executes specific *bound* functions on user interactions.

Panel supports reacting to many more interactions than Streamlit. For example interactions with
tables and plots.

With Panels interactivity architecture you will be able to develop and maintain larger and more
complex apps to support more cases.

### Basic Interactivity Example

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
    ax.hist(data, bins=20)
    return fig

data = np.random.normal(1, 1, size=100)
bins = pn.widgets.IntSlider(value=20, start=10, end=30, step=1, name="Bins")
bplot = pn.bind(plot, bins, data)

pn.Column(bins, bplot).servable()
```

Only the `plot` function is rerun when you change the `bins` slider. You specify that
by *binding* the `plot` function to the `bins` widget using `pn.bind`.

### Advanced Interactivity Example

#### Streamlit Advanced Interactivity Example

```python
import time

import streamlit as st


def calculation_a():
    time.sleep(1.5)


def calculation_b():
    time.sleep(1.5)


st.write("# Calculation Runner")

option = st.radio("Which calculation would you like to perform?", ("A", "B"))

st.write("You chose: ", option)
if option == "A":
    if st.button("Press to run calculation"):
        with st.spinner("running... Please wait!"):
            time_start = time.perf_counter()
            calculation_a()
            st.write("Done!")
            time_end = time.perf_counter()
            st.write(f"The function took {time_end - time_start:1.1f} seconds to complete")

    else:
        st.write("Calculation A did not run yet")

elif option == "B":
    if st.button("Press to run calculation"):
        with st.spinner("running... Please wait!"):
            time_start = time.perf_counter()
            calculation_b()
            st.write("Done!")
            time_end = time.perf_counter()
            st.write(f"The function took {time_end - time_start:1.1f} seconds to complete")
    else:
        st.write("Calculation B did not run yet")
```

### Interactivity Migration Steps

You should

- Move your business logic to functions. Business logic can be code to load data,
create plots, do inference using a machinelearning model etc.
- Use `pn.bind` to specify which functions are bound to which widgets.

## Caching

One of the key concepts in Streamlit is *caching*. In Streamlit your entire script is rerun
*top to bottom* on user interactions. Without caching you would be
reconnecting to your database, reloading your dataset and rerunning your expensive calculation every
time a user clicks a `Button` or changes a `slider` value. This would make your application very
slow.

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

@st.cache_resources
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
- replace `st.cache_resources` with `pn.state.as_cached` to migrate your *global caching*
  - You only need to cache expensive, *bound functions* and objects you want to share across user
  sessions

In the process consider separating your business logic and caching logic
(when and how to apply caching) to get more maintainable and reusable code.

## Multiple Steps

```python
import time

import streamlit as st


def calculation_a():
    time.sleep(1.5)


def calculation_b():
    time.sleep(1.5)


st.write("# Calculation Runner")

option = st.radio("Which Calculation would you like to perform?", ("A", "B"))

st.write("You chose: ", option)
if option == "A":
    if st.button("Press to run calculation"):
        with st.spinner("running... Please wait!"):
            time_start = time.perf_counter()
            calculation_a()
            st.write("Done!")
            time_end = time.perf_counter()
            st.write(f"The function took {time_end - time_start:1.1f} seconds to complete")

    else:
        st.write("Calculation A did not run yet")

elif option == "B":
    if st.button("Press to run calculation"):
        with st.spinner("running... Please wait!"):
            time_start = time.perf_counter()
            calculation_b()
            st.write("Done!")
            time_end = time.perf_counter()
            st.write(f"The function took {time_end - time_start:1.1f} seconds to complete")
    else:
        st.write("Calculation B did not run yet")
```

TODO: MAKE LINKS RELATIVE
