# Make interactive data workflows

This guide addresses how to bind interactive data pipelines to a component using the [Reactive Expressions of Param](https://param.holoviz.org/user_guide/Reactive_Expressions.html).

---

The `Param rx` object allows you to treat any object as a reactive expression. This is done by replacing the constant parameters in your pipeline with widgets (e.g., a number slider) that will trigger an output update on changes. With this approach, all your pipeline parameters are available in one place, and you get complete interactive control over the pipeline. For convenience, we could use `pn.rx` instead of `param.rx` when you `import panel as pn`.

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

Let's then use these to filter the data. We first wrap the `df` in `pn.rx` as `df_rx` and pass the `species_widget` as the `species` parameter and the `year_widget` as the `year` parameter. In our case, we want the year always to be greater than or equal to the widget's value.

```{pyodide}
import hvplot.pandas  # Enable interactive

df_rx = pn.rx(df)
df_rx = df_rx[(df_rx["species"] == species_widget) & (df_rx["year"] >= year_widget)]

df_rx.head()
```
Similarly we can use other pandas features in the same way.

```{pyodide}
head_widget = pn.widgets.IntSlider(name="Head", start=1, end=10)

df_rx.head(head_widget)
```

Because we've imported `hvplot.pandas`, we can utilize `.hvplot()` to render the widgets and plot the data easily:

```{pyodide}
df_rx.hvplot(kind="scatter", x="bill_length_mm", y="bill_depth_mm", by="sex")
```

We can leverage [`panel.ReactiveExpr`](../../reference/panes/ReactiveExpr) to assist in rendering `df_rx`. This allows us to include all widgets related to `df_rx`, while also offering the flexibility to customize the appearance of the widgets. For instance, we can specify `pn.Column` as the `widget_layout` parameter and `top` as the `widget_location` parameter, as shown below:

```{pyodide}
pn.ReactiveExpr(
    df_rx.head(),  # only show a few rows to save some space
    widget_layout=pn.Column,
    widget_location="top",
)
```

While `panel.ReactiveExpr` offers convenience, it's also common practice to bind the interactive pipeline we've constructed to a Panel component, such as a `Tabulator` widget:

```{pyodide}
table = pn.widgets.Tabulator(df_rx, page_size=10, pagination="remote")
pn.Column(species_widget, year_widget, table)
```

Notably, with this approach, we need to handle the layout of widgets ourselves.

For complex expressions involving many widgets, the `panel.ReactiveExpr` pane offers a `.widgets` attribute, returning a `ListPanel`, which helps us retrieve all the related widgets. Once we have access to the widgets, it becomes possible to reposition them or add custom widgets in the final layout.

```{pyodide}
widgets = pn.ReactiveExpr(df_rx).widgets

pn.Column(
    pn.WidgetBox(*reversed(widgets)),
    pn.Spacer(height=30),
    table,
)
```

Finally, if performance is critical, you might want to consider using [Reactive expressions as references](../../reference/panes/ReactiveExpr#reactive-expressions-as-references). For instance, you can try replacing `df_rx` with `df_rx.rx()` in this tutorial.

## Related Resources

* [Reactive Functions and Expressions of Param](https://param.holoviz.org/user_guide/Reactive_Expressions.html)
* [Reactive Expressions of Panel](../../tutorials/basic/pn_rx)
* [panel.ReactiveExpr documentation](../../reference/panes/ReactiveExpr)
