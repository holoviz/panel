# Migrate from Streamlit

This guide addresses how to migrate from Streamlit to Panel via examples

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

You *serve* and *show* the app with *autoreload* via

```bash
panel serve app.py --autoreload --show
```

We set the `sizing_mode` to `stretch_width` to get the *responsive* behaviour you expect from
Streamlit apps.

We set the `template` to `bootstrap` to wrap your application in a nice template as you expect from Streamlit apps. If you don't set a template you will get a blank page to add your components to.
You can see the available templates in the [Templates Section](https://panel.holoviz.org/reference/index.html#templates) of the [Component Gallery](https://panel.holoviz.org/reference/index.html).

### Hello World Migration Steps

You can replace

- `import streamlit as st` with `import panel as pn` and
- `st.write` with `pn.panel`. Both functions can *magically* display
all kinds of python objects like (markdown) strings, dataframes, plots and more. Check out the `pn.panel` introduction. TODO: ADD LINK.

You will also have to

- add `pn.extension` to configure your Panel application. Learn more about `pn.extension` here TODO: Add link.
- add `.servable()` to the Panel objects you want to include in your apps *template* when served as a web app.

Both `pn.extension` and `.servable` helps enable new workflows and use cases that Streamlit does not support. For example interactive data exploration in Jupyter Notebooks.

For production you will also have to

- Migrate some of your app configuration to `panel serve` command line flags or environment variables. See TODO: Insert link

You won't have to

- Provide your email or
- opt out of telemetry collection.

We have never collected or had plans to collect telemetry data from our users apps.

## Outputs

In Panel the objects that can display your Python objects are called *panes*.

With Panels *panes* you will be able to use additional data visualization ecosystems like
HoloViz, ipywidgets and VTK.

### Streamlit Matplotlib Example

```python
import numpy as np
import streamlit as st

import matplotlib.pyplot as plt

arr = np.random.normal(1, 1, size=100)
fig, ax = plt.subplots()
ax.hist(arr, bins=20)

st.pyplot(fig)
```

### Panel Matplotlib Example

You will find Panels output *panes* in `pn.pane` module.

```python
import panel as pn
import numpy as np

from matplotlib.figure import Figure

pn.extension(sizing_mode="stretch_width", template="bootstrap")

arr = np.random.normal(1, 1, size=100)
fig = Figure(figsize=(8,4))
ax = fig.subplots()
ax.hist(arr, bins=20)

pn.pane.Matplotlib(fig).servable()
```

Please note that we use the `Figure` interface instead of the `matplotlib.pyplot` interface to
avoid memory leaks if you forget to close the figure.

### Output Migration Steps

You should

- Identify the relevant Panes to migrate to in the [Components Gallery](https://panel.holoviz.org/reference/index.html#panes).
- Study the relevant guides for the details. For example the [Matplotlib Guide](https://panel.holoviz.org/reference/panes/Matplotlib.html).

## Inputs

In Panel the objects that can provide you inputs are called *widgets*. Let see how the migration of an integer slider widget works.

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

If you debug and inspect the code your will notice a big difference. Streamlits `bins` value is an `integer` while Panels `bins` value is an `IntSlider`. This is the first real indication that Streamlit and Panel works in very different ways.

### Input Migration Steps

- Identify the relevant widgets to migrate to in the [Components Gallery](). TODO: INSERT LINK.
- Study the relevant widget guides for the details. For example the [IntSlider]() guide. TODO: INSERT LINKS

## Layouts

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

Panels `Column` and `Row` are *list like* objects. So you can use familiar methods like `.append`,
`.pop` and `[]` indexing when you work with them.

### Layout Migration Steps

- Identify the relevant layouts to migrate to in the [Components Gallery](). TODO: INSERT LINK.
- Study the relevant layout guides for the details. For example the [Column]() or [Row]() guides. TODO: INSERT LINKS

### Reactivity

Both Streamlit and Panel are *reactive* frameworks that *react* when you interact with your widgets.
But they work very differently:

- Streamlit executes the whole script *top to bottom* on user interactions.
- Panel executes specific scripts on user interactions.

Furthermore Panel supports reacting to many more events. For example from interactions with
tables and plots.

With Panels reactivity architecture you will be able to develop larger and more complex
apps. For example Streaming Applications.

### Streamlit Reactivity Example

```python
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

bins = st.slider(value=20, min_value=10, max_value=30, step=1, label="Bins")

arr = np.random.normal(1, 1, size=100)
fig, ax = plt.subplots()
ax.hist(arr, bins=bins)

st.pyplot(fig)
```

For Streamlit the entire script is rerun *top to bottom* when you change the `bins` slider.

### Panel Reactivity Example

```python
import panel as pn
import numpy as np

from matplotlib.figure import Figure

pn.extension(sizing_mode="stretch_width", template="bootstrap")

arr = np.random.normal(1, 1, size=100)

def plot(bins, arr):
    fig = Figure(figsize=(8,4))
    ax = fig.subplots()
    ax.hist(arr, bins=20)
    return fig

bins = pn.widgets.IntSlider(value=20, start=10, end=30, step=1, name="Bins")
bplot = pn.bind(plot, bins, arr)

pn.Column(bins, bplot).servable()
```

For Panel only the `plot` function is rerun when you change the `bins` slider. You specify that
by *binding* the `plot` function to the `bins` widget using `pn.bind`.

### Reactivity Migration Steps


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
