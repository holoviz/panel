# Layout Content

Welcome to our guide on layouting Python objects, including Panel components! Let's dive into arranging your content in a visually appealing and organized manner.

## Explore Layouts

In this guide, we'll explore the following aspects of layouts:

- **Layouts**: Accessible in the `pn` namespace.
- **Layout Techniques**: Utilize `pn.Column` and `pn.Row` to structure your content.
- **Reference Guides**: Explore detailed documentation for each layout in the [Layouts Section](../../reference/index.rst#layouts) of the [Component Gallery](../../reference/index.rst).

## Layout in a Column

Let's start by arranging objects vertically using the [Column](../../reference/layouts/Column.md) layout.

Run the code below:

```python
import pandas as pd
import panel as pn

pn.extension()

button = pn.widgets.Button(label="Refresh", icon="refresh", color="primary")

data = pd.DataFrame(
    [
        ("Monday", 7),
        ("Tuesday", 4),
        ("Wednesday", 9),
        ("Thursday", 4),
        ("Friday", 4),
        ("Saturday", 4),
        ("Sunday", 4),
    ],
    columns=["Day", "Wind Speed (m/s)"],
)

pn.Column("# Wind Speed", data, button).servable()
```

Click [this link](../../reference/layouts/Column.md) to access the `Column` *reference guide* and familiarize yourself with its functionality.

## Layout in a Row

Next, let's arrange objects horizontally using the `Row` layout.

Run the code below:

```python
import pandas as pd
import panel as pn
import hvplot.pandas

pn.extension()

data = pd.DataFrame(
    [
        ("Monday", 7),
        ("Tuesday", 4),
        ("Wednesday", 9),
        ("Thursday", 4),
        ("Friday", 4),
        ("Saturday", 4),
        ("Sunday", 4),
    ],
    columns=["Day", "Wind Speed (m/s)"],
)
plot = data.hvplot(x="Day", y="Wind Speed (m/s)", kind="bar", color="goldenrod", title="Wind Speed (m/s)")

pn.Row(plot, data).servable()
```

## Displays using `pn.panel`

Layouts automatically display objects using `pn.panel`.

Run the code below:

```python
import pandas as pd
import panel as pn

pn.extension()

data = pd.DataFrame(
    [
        ("Monday", 7),
        ("Tuesday", 4),
        ("Wednesday", 9),
        ("Thursday", 4),
        ("Friday", 4),
        ("Saturday", 4),
        ("Sunday", 4),
    ],
    columns=["Day", "Wind Speed (m/s)"],
)
button = pn.widgets.Button(label="Refresh", icon="refresh", color="primary")
component = pn.Column("# Wind Speed", data, button)
print(component)
component.servable()
```

The `print` statement will output something like:

```bash
Column
    [0] Markdown(str)
    [1] DataFrame(DataFrame)
    [2] Button(color='primary', icon='refresh', name='Refresh')
```

Under the hood, the `Column` layout uses `pn.panel` to determine how to best display Python objects.

Run the code below to see custom display:

```python
import pandas as pd
import panel as pn

pn.extension()

button = pn.widgets.Button(label="Refresh", icon="refresh", color="primary")

data = pd.DataFrame(
    [
        ("Monday", 7),
        ("Tuesday", 4),
        ("Wednesday", 9),
        ("Thursday", 4),
        ("Friday", 4),
        ("Saturday", 4),
        ("Sunday", 4),
    ],
    columns=["Day", "Wind Speed (m/s)"],
)

pn.Column(
    pn.pane.Str("# Wind Speed"), pn.panel(data, sizing_mode="stretch_width"), button
).servable()
```

## Works like a list

`Column`, `Row`, and many other layouts behave like lists.

Run the code below:

```python
import pandas as pd
import panel as pn

pn.extension()

button = pn.widgets.Button(label="Refresh", icon="refresh", color="primary")

data = pd.DataFrame(
    [
        ("Monday", 7),
        ("Tuesday", 4),
        ("Wednesday", 9),
        ("Thursday", 4),
        ("Friday", 4),
        ("Saturday", 4),
        ("Sunday", 4),
    ],
    columns=["Day", "Wind Speed (m/s)"],
)

component = pn.Column("# Wind Speed", data, button)
pn.Column(component[0], component[2], component[1]).servable()
```

## Combine Layouts

To create more complex layouts, we can combine and nest layouts.

Let's run the code below:

```python
import pandas as pd
import panel as pn
import hvplot.pandas

pn.extension()

button = pn.widgets.Button(label="Refresh", icon="refresh", color="primary")
data = pd.DataFrame(
    [
        ("Monday", 7),
        ("Tuesday", 4),
        ("Wednesday", 9),
        ("Thursday", 4),
        ("Friday", 4),
        ("Saturday", 4),
        ("Sunday", 4),
    ],
    columns=["Day", "Wind Speed (m/s)"],
)
plot = data.hvplot(
    x="Day",
    y="Wind Speed (m/s)",
    kind="bar",
    color="goldenrod",
    title="Wind Speed (m/s)",
)

pn.Column(
    "# Wind Speed",
    button,
    pn.Row(pn.panel(plot, sizing_mode="stretch_width"), pn.panel(data)),
).servable()
```

## Explore the Layouts

Panel provides a vast collection of layouts to suit your needs.

Click [this link](../../reference/index.rst#layouts) to explore available layouts and their detailed reference guides.

## Recap

In this guide, we have learned:

- **Layouts**: Available in the `pn` namespace.
- **Layout Techniques**: Utilize `pn.Column` and `pn.Row` to structure your content.
- **Automatic Display**: Layouts use `pn.panel` to determine the optimal display for Python objects.
- **List-like Behavior**: Layouts like `Column` and `Row` behave like lists, allowing for flexible manipulation.
- **Complex Layouts**: Combine and nest layouts for more intricate arrangements.

Now, you're equipped to create dynamic and visually appealing layouts for your Panel apps!

## References

### Tutorials

- [Display objects with `pn.panel`](pn_panel.md)
- [Display objects with Panes](panes.md)

### How-to

- [Align Components](../../how_to/layout/align.md)
- [Control Size](../../how_to/layout/size.md)
- [Customize Spacing](../../how_to/layout/spacing.md)
- [Migrate from Streamlit | Layout Objects](../../how_to/streamlit_migration/layouts.md)

### Explanation

- [Components Overview](../../explanation/components/components_overview.md)

### Component Gallery

- [Layouts](../../reference/index.rst#layouts)
