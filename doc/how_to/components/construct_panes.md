# Construct Panes

This guide addresses how to construct Pane objects for displaying visible components.

---

There are two main ways to construct a pane - explicitly or automatically.

To explicitly construct a pane, use one of the pane types listed in the [component gallery](../../reference/index#panes). For example, you can create a Markdown pane as follows:

```{pyodide}
import panel as pn
pn.extension() # for notebook

pn.pane.Markdown('''
# H1
## H2
### H3
''')
```

Alternatively, you can create a pane using the `pn.panel()` utility to automatically infer the pane type from the object being passed as the argument:

```{pyodide}
png = pn.panel('https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png', width=500)

png
```
## Using `pn.panel`

The `pn.panel` function is one of the most important entry points in Panel. It converts many different Python objects into Panel components that can be displayed in layouts or served in applications.

### Basic usage

`pn.panel` automatically converts Python objects into appropriate Panel panes.

```python
import panel as pn
pn.extension()

pn.panel("Hello Panel!")
```

### Converting different objects

#### Strings

```python
pn.panel("Hello world")
```

#### Functions

Functions can be wrapped and displayed dynamically.

```python
import panel as pn
pn.extension()

def greet(name):
    return f"Hello {name}"

pn.panel(greet)
```

#### DataFrames

```python
import pandas as pd
import panel as pn

pn.extension()

df = pd.DataFrame({
    "A": [1,2,3],
    "B": [4,5,6]
})

pn.panel(df)
```

#### Plots

Many plotting libraries can be passed directly.

```python
import matplotlib.pyplot as plt
import panel as pn

pn.extension()

fig, ax = plt.subplots()
ax.plot([1,2,3], [4,5,6])

pn.panel(fig)
```

### Why `pn.panel` is powerful

`pn.panel` automatically selects the correct Pane type depending on the object you provide. This makes it easy to build dashboards quickly without manually selecting Pane classes.
---

## Related Resources

- Learn more about Panes in [Explanation > Components](../../explanation/components/components_overview.md#panes).
