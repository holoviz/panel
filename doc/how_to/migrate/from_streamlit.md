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

You *serve* the app with autoreload via

```bash
streamlit run app.py
```

### Panel Hello World Example

In Panel this looks like

```python
import panel as pn

pn.extension()

pn.panel("Hello World").servable()
```

You *serve* the app with autoreload via

```bash
panel serve app.py --autoreload --show
```

### Hello World Migration Steps

You can replace

- `st` with `pn` and
- `st.write` with `pn.panel`. Both functions can *magically* display
all kinds of python objects like (markdown) strings, dataframes, plots and more. Check out the `pn.panel` introduction. TODO: ADD LINK.

You will also have to add

- `pn.extension()` to configure your Panel application and
- `.servable()` to the Panel objects you want to include in your apps *template* when served as a web app.

Both `pn.extension` and `.servable` are needed to enable Panel to support more use cases than Streamlit. For example interactive data exploration in Jupyter Notebooks.

## Outputs

In Panel the objects that can display your Python objects are called *panes*. Let see how a migration to a Matplotlib pane works. TODO: INSERT LINK

## Streamlit Matplotlib Example

```python
import numpy as np
import streamlit as st

import matplotlib.pyplot as plt

arr = np.random.normal(1, 1, size=100)
fig, ax = plt.subplots()
ax.hist(arr, bins=20)

st.pyplot(fig)
```

## Panel Matplotlib Example

```python
import panel as pn
import numpy as np

from matplotlib.figure import Figure

pn.extension()

arr = np.random.normal(1, 1, size=100)
fig0 = Figure(figsize=(8, 6))
ax = fig0.subplots()
ax.hist(arr, bins=20)

pn.pane.Matplotlib(fig0, height=500).servable()
```

## Output Migration Steps

You should

- Identify the relevant Panes to migrate to in the [Gallery of Panes](). TODO: INSERT LINK
- Study the relevant Panes for the details. For example in the [Matplotlib Guide]() you will learn why we recommend using the `Figure` interface instead of the `matplotlib.pyplot` interface. TODO: INSERT LINKS
- Consider using some of the many new features that Panel provides. For example you can now react to events when you interact with plots and tables and interactively display big data with Datashader.

## Inputs

In Panel the objects that can provide you inputs are called *widgets*. Let see how the migration to an integer slider works.

### Streamlit Integer Slider Example

### Panel Integer Slider Example

## Templates

You might have noticed that Streamlit comes with a nice template out of the box. Panel on the other hand provides a clean template out of the box, many predefined templates and the opportunity to define your own.

You can add a template to the *Hello World* example via

```python
import panel as pn

pn.extension(template="bootstrap")

pn.panel("Hello World").servable()
```

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
