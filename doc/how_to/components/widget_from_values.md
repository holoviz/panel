# Construct Widgets from Data

This guide discusses how to automatically generate widget from data.

---

When working with data, be it in the form of lists, arrays or DataFrames it is common to want to filter that data. Manually computing the `start` and `end` values of a slider or the unique values of a dropdown can be an annoyance so widgets have a `classmethod` called `from_values` to help with this.

```{pyodide}
import pandas as pd
import panel as pn
pn.extension() # for notebook

df = pd.read_csv("https://datasets.holoviz.org/penguins/v1/penguins.csv")

species = pn.widgets.MultiSelect.from_values(df.species)

species
```

As we can see the special constructor automatically inferred both the `option` and the `name` for the widget.

Similarly we can also use this to infer the values of a numeric column:

```{pyodide}
body_mass = pn.widgets.RangeSlider.from_values(df.body_mass_g)

body_mass
```

---

## Related Resources

- Learn about building interactive data pipelines [How-To > Interactivity -> ](../how_to/interactivity/hvplot_interactive.md).
