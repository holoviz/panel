# Binding on components

This guide addresses how to bind parameters and bound functions on components.

---

## Binding parameters on components

The power to binding parameters to components can be used with all of Panel's widgets and panes, which makes it easy to create powerful components. An example is by binding a parameter to the `page_size` of the [Tabulator](../../reference/widgets/Tabulator) widget. This will allow you to change the page size of the table with the slider.

```{pyodide}
import pandas as pd
import panel as pn
pn.extension("tabulator")

df = pd.read_csv("https://datasets.holoviz.org/penguins/v1/penguins.csv")

slider = pn.widgets.IntSlider(value=5, start=1, end=10)
tabulator = pn.widgets.Tabulator(df, page_size=slider, pagination="remote")

pn.Row(slider, tabulator)
```

# Binding bound function on components

```{admonition} Prerequisites
1. Read the [How to > Make your functions interactive](./bind_function) guide to learn how to bind functions.
```

Binding a parameter to a component is a powerful way to make your component interactive. However, binding a parameter to a component is not always possible. For example, if there is no ideal parameter for the component or the component depends on multiple parameters. In these cases, you can bind a function to a component instead with the use of `pn.bind`.

Let's say we have a function that outputs a string, which depends both on a slider but also a select widget.
This select widget has the option of using either ⭐ or 🐘.

```{pyodide}

def object_creator(number, object):
    return object * number


slider = pn.widgets.IntSlider(value=5, start=1, end=10)
select = pn.widgets.Select(value="⭐", options=["⭐", "🐘"])

pn.Row(slider, select)
```

We can now bind this function to the slider and the select widget to create an interactive string. Try changing the slider and the select widget and see the output change.

```{pyodide}
pn.pane.Markdown(pn.bind(object_creator, slider, select))
```
