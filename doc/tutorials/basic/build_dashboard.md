# Build a Dashboard

In this tutorial we will build a beautiful dashboard showing key metrics of wind turbine manufacturers.

<iframe src="https://awesome-panel-build-dashboard.hf.space" frameborder="0" style="width: 100%;height:1000px"></iframe>

Click the dropdowns below to see the requirements or full code.

:::::{dropdown} Requirements

::::{tab-set}

:::{tab-item} conda
:sync: conda

```bash
conda install -y -c conda-forge hvplot panel pandas
```

:::

:::{tab-item} pip
:sync: pip

```bash
pip install hvplot panel pandas
```

:::

::::

:::::

:::{dropdown} Code

```python
import panel as pn
import pandas as pd
import hvplot.pandas

pn.extension("tabulator")

ACCENT="teal"

styles = {
    "box-shadow": "rgba(50, 50, 93, 0.25) 0px 6px 12px -2px, rgba(0, 0, 0, 0.3) 0px 3px 7px -3px",
    "border-radius": "4px",
    "padding": "10px",
}

# Extract Data

@pn.cache()  # only download data once
def get_data():
    return pd.read_csv("https://assets.holoviz.org/panel/tutorials/turbines.csv.gz")

source_data = get_data()

# Transform Data

min_year = int(source_data["p_year"].min())
max_year = int(source_data["p_year"].max())
top_manufacturers = (
    source_data.groupby("t_manu").p_cap.sum().sort_values().iloc[-10:].index.to_list()
)

def filter_data(t_manu, year):
    data = source_data[(source_data.t_manu == t_manu) & (source_data.p_year <= year)]
    return data

# Filters

t_manu = pn.widgets.Select(
    name="Manufacturer",
    value="Vestas",
    options=sorted(top_manufacturers),
    description="The name of the manufacturer",
)
p_year = pn.widgets.IntSlider(name="Year", value=max_year, start=min_year, end=max_year)

# Transform Data 2

df = pn.rx(filter_data)(t_manu=t_manu, year=p_year)
count = df.rx.len()
total_capacity = df.t_cap.sum()
avg_capacity = df.t_cap.mean()
avg_rotor_diameter = df.t_rd.mean()

# Plot Data

fig = (
    df[["p_year", "t_cap"]].groupby("p_year").sum() / 10**6
).hvplot.bar(
    title="Capacity Change",
    rot=90,
    ylabel="Capacity (MW)",
    xlabel="Year",
    xlim=(min_year, max_year),
    color=ACCENT,
)

# Display Data

image = pn.pane.JPG("https://assets.holoviz.org/panel/tutorials/wind_turbines_sunset.png")

indicators = pn.FlexBox(
    pn.indicators.Number(
        value=count, name="Count", format="{value:,.0f}", styles=styles
    ),
    pn.indicators.Number(
        value=total_capacity / 1e6,
        name="Total Capacity (TW)",
        format="{value:,.1f}",
        styles=styles,
    ),
    pn.indicators.Number(
        value=avg_capacity/1e3,
        name="Avg. Capacity (MW)",
        format="{value:,.1f}",
        styles=styles,
    ),
    pn.indicators.Number(
        value=avg_rotor_diameter,
        name="Avg. Rotor Diameter (m)",
        format="{value:,.1f}",
        styles=styles,
    ),
)

plot = pn.pane.HoloViews(fig, sizing_mode="stretch_both", name="Plot")
table = pn.widgets.Tabulator(df, sizing_mode="stretch_both", name="Table")

# Layout Data

tabs = pn.Tabs(
    plot, table, styles=styles, sizing_mode="stretch_width", height=500, margin=10
)

pn.template.FastListTemplate(
    title="Wind Turbine Dashboard",
    sidebar=[image, t_manu, p_year],
    main=[pn.Column(indicators, tabs, sizing_mode="stretch_both")],
    main_layout=None,
    accent=ACCENT,
).servable()
```

:::

```{pyodide}
import panel as pn

pn.extension("tabulator")
```

## Explanation

Lets start by importing the packages

```{pyodide}
import panel as pn
import pandas as pd
import hvplot.pandas
```

To later use the [Tabulator](../../reference/widgets/Tabulator.ipynb) widget we need to add it to `pn.extension`.

```{pyodide}
pn.extension("tabulator")
```

We define an `ACCENT` color and `styles` we will be using later.

```{pyodide}

ACCENT="teal"

styles = {
    "box-shadow": "rgba(50, 50, 93, 0.25) 0px 6px 12px -2px, rgba(0, 0, 0, 0.3) 0px 3px 7px -3px",
    "border-radius": "4px",
    "padding": "10px",
}
```

We extract the data and *cache* it.

```{pyodide}
@pn.cache()  # only download data once
def get_data():
    return pd.read_csv("https://assets.holoviz.org/panel/tutorials/turbines.csv.gz")

source_data = get_data()
```

We transform the data

```{pyodide}

min_year = int(source_data["p_year"].min())
max_year = int(source_data["p_year"].max())
top_manufacturers = (
    source_data.groupby("t_manu").p_cap.sum().sort_values().iloc[-10:].index.to_list()
)

def filter_data(t_manu, year):
    data = source_data[(source_data.t_manu == t_manu) & (source_data.p_year <= year)]
    return data
```

Lets define a couple of widgets to filter the data

```{pyodide}
t_manu = pn.widgets.Select(
    name="Manufacturer",
    value="Vestas",
    options=sorted(top_manufacturers),
    description="The name of the manufacturer",
)
p_year = pn.widgets.IntSlider(name="Year", value=max_year, start=min_year, end=max_year)
pn.Column(t_manu, p_year)
```

Lets continue to filter and transform the data. We will be using `pn.rx` to make the transformations
*depend* on the widgets.

```{pyodide}
df = pn.rx(filter_data)(t_manu=t_manu, year=p_year)
count = df.rx.len()
total_capacity = df.t_cap.sum()
avg_capacity = df.t_cap.mean()
avg_rotor_diameter = df.t_rd.mean()
```

Now its time to plot the data

```{pyodide}
fig = (
    df[["p_year", "t_cap"]].groupby("p_year").sum() / 10**6
).hvplot.bar(
    title="Capacity Change",
    rot=90,
    ylabel="Capacity (MW)",
    xlabel="Year",
    xlim=(min_year, max_year),
    color=ACCENT,
)
```

Lets display the data

```{pyodide}
image = pn.pane.JPG("https://assets.holoviz.org/panel/tutorials/wind_turbines_sunset.png")

indicators = pn.FlexBox(
    pn.indicators.Number(
        value=count, name="Count", format="{value:,.0f}", styles=styles
    ),
    pn.indicators.Number(
        value=total_capacity / 1e6,
        name="Total Capacity (TW)",
        format="{value:,.1f}",
        styles=styles,
    ),
    pn.indicators.Number(
        value=avg_capacity/1e3,
        name="Avg. Capacity (MW)",
        format="{value:,.1f}",
        styles=styles,
    ),
    pn.indicators.Number(
        value=avg_rotor_diameter,
        name="Avg. Rotor Diameter (m)",
        format="{value:,.1f}",
        styles=styles,
    ),
)

plot = pn.pane.HoloViews(fig, sizing_mode="stretch_both", name="Plot")
table = pn.widgets.Tabulator(df, sizing_mode="stretch_both", name="Table")
```

Lets layout the components

```{pyodide}
tabs = pn.Tabs(
    plot, table, styles=styles, sizing_mode="stretch_width", height=500, margin=10
)

main = pn.Column(indicators, tabs, sizing_mode="stretch_both")
main
```

Finally lets style and layout via the `FastListTemplate`.

```python
pn.template.FastListTemplate(
    title="Wind Turbine Dashboard",
    sidebar=[image, t_manu, p_year],
    main=[main],
    main_layout=None,
    accent=ACCENT,
).servable()
```
