# Make interactive data workflows

This guide addresses how to bind interactive data pipelines to a component using `hvplot.interactive`. This is done by combining Panels widgets with [hvplot](https://hvplot.holoviz.org/).

---

`hvplot.interactive` is a tool to get better control over your data pipelines. This is done by replacing the constant parameters in your pipeline with widgets (e.g., a number slider) that will automatically get displayed next to your pipeline output and trigger an output update on changes. With this approach, all your pipeline parameters are available in one place, and you get complete interactive control over the pipeline. For more information, check out the [hvPlot documentation](https://hvplot.holoviz.org/user_guide/Interactive.html).

Let's start by fetching some data:

```{pyodide}
import pandas as pd

df = pd.read_csv('https://datasets.holoviz.org/penguins/v1/penguins.csv')
df.head()
```

We now want to create select widgets for the column `species` and a slider for `year`. We can do this with Panel's widgets:

```{pyodide}
import panel as pn

pn.extension('tabulator')

species_widget = pn.widgets.Select(name="species", options=["Adelie", "Gentoo", "Chinstrap"])
year_widget = pn.widgets.IntSlider(name="year", start=2007, end=2009)
```

Let's then use these to filter the data. We can do this by using `hvplot.interactive` and passing the `species_widget` as the `species` parameter and the `year_widget` as the `year` parameter. In our case, we want the year always to be greater than the widget's value.

```{pyodide}
import hvplot.pandas  # Enable interactive

idf = df.interactive()
idf = idf[(idf["species"] == species_widget) & (idf["year"] > year_widget)]

idf.head()
```

Because we are already using `hvplot`, we can use the other powerful API of plotting the data with `hvplot`:

```{pyodide}
idf.hvplot(kind="scatter", x="bill_length_mm", y="bill_depth_mm", by="sex")
```

However we can also use bind the interactive pipeline we have built to a Panel component, e.g. a `Tabulator` widget:

```{pyodide}
pn.Row(
    idf.widgets(),
    pn.widgets.Tabulator(idf, page_size=10, pagination='remote'),
)
```

## Related Resources
