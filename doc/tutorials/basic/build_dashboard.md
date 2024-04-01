# Build a Dashboard

Welcome to our tutorial on building an interactive dashboard showcasing essential metrics from wind turbine manufacturers.

We'll demonstrate how to leverage a variety of components such as sliders, dropdowns, plots, indicators, tables and layouts to craft a visually stunning and functional application.

By following along, you'll gain insights into how these components can be seamlessly combined to present data in a meaningful way.

Our objective is to empower you to replicate this process for your own datasets and use cases, enabling you to create impactful dashboards tailored to your specific needs.

<iframe src="https://panel-org-build-dashboard.hf.space" frameborder="0" style="width: 100%;height:1000px"></iframe>

Click the dropdowns below to see the requirements or the full code.

:::::{dropdown} Requirements

::::{tab-set}

:::{tab-item} pip
:sync: pip

```bash
pip install hvplot pandas panel
```

:::

:::{tab-item} conda
:sync: conda

```bash
conda install -y -c conda-forge hvplot pandas panel
```

:::

::::

:::::

:::{dropdown} Code

```python
import hvplot.pandas
import pandas as pd
import panel as pn

pn.extension("tabulator")

ACCENT = "teal"

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
    ylabel="Capacity (GW)",
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
        name="Avg. Capacity (GW)",
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

## Explanation

### Importing Libraries

```{pyodide}
import hvplot.pandas
import pandas as pd
import panel as pn
```

- `hvplot.pandas`: This library provides a high-level plotting interface for Pandas DataFrames using [HoloViews](https://holoviews.holoviz.org/).
- `pandas`: This library is used for data manipulation and analysis.
- `panel`: This is the [Panel](https://panel.holoviz.org/) library used for creating interactive dashboards and apps.

### Extension

```{pyodide}
pn.extension("tabulator")
```

- `pn.extension("tabulator")`: This line enables the Tabulator widget, which provides a high-performance interactive table widget in Panel.

### Styles

```{pyodide}
ACCENT = "teal"

styles = {
    "box-shadow": "rgba(50, 50, 93, 0.25) 0px 6px 12px -2px, rgba(0, 0, 0, 0.3) 0px 3px 7px -3px",
    "border-radius": "4px",
    "padding": "10px",
}
```

- `ACCENT`: This variable stores the color teal, which will be used as the accent color throughout the dashboard.
- `styles`: This dictionary contains CSS styles to be applied to various components in the dashboard for consistent styling, including box shadow, border radius, and padding.

### Data Extraction

```{pyodide}
@pn.cache()
def get_data():
    return pd.read_csv("https://assets.holoviz.org/panel/tutorials/turbines.csv.gz")

source_data = get_data()
```

- `get_data()`: This function is decorated with `@pn.cache()`, which ensures that the data is only downloaded once, improving performance by caching the result.
- `source_data`: This variable stores the downloaded CSV data as a Pandas DataFrame.

### Data Transformation

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

- `min_year`, `max_year`: These variables store the minimum and maximum values of the "p_year" column in the DataFrame, representing the earliest and latest years.
- `top_manufacturers`: This variable stores the top 10 manufacturers based on the sum of their turbine capacities.
- `filter_data()`: This function filters the source data based on the selected manufacturer and year.

### Widgets

```{pyodide}
t_manu = pn.widgets.Select(
    name="Manufacturer",
    value="Vestas",
    options=sorted(top_manufacturers),
    description="The name of the manufacturer",
)
p_year = pn.widgets.IntSlider(name="Year", value=max_year, start=min_year, end=max_year)
```

- `t_manu`: This widget is a select dropdown for choosing the manufacturer.
- `p_year`: This widget is an integer slider for selecting the year.

### Data Transformation 2

```{pyodide}
df = pn.rx(filter_data)(t_manu=t_manu, year=p_year)
count = df.rx.len()
total_capacity = df.t_cap.sum()
avg_capacity = df.t_cap.mean()
avg_rotor_diameter = df.t_rd.mean()
```

- `df`: This variable stores the filtered DataFrame based on the selected manufacturer and year.
- `count`, `total_capacity`, `avg_capacity`, `avg_rotor_diameter`: These variables calculate various statistics from the filtered DataFrame, such as count, total capacity, average capacity, and average rotor diameter.

### Plotting Data

```{pyodide}
fig = (
    df[["p_year", "t_cap"]].groupby("p_year").sum() / 10**6
).hvplot.bar(
    title="Capacity Change",
    rot=90,
    ylabel="Capacity (GW)",
    xlabel="Year",
    xlim=(min_year, max_year),
    color=ACCENT,
)
```

- `fig`: This variable stores a bar plot of the total turbine capacity over the years.

### Displaying Data

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
```

- `image`: This variable stores an image pane displaying a background image for the dashboard.
- `indicators`: This variable stores a collection of indicator widgets displaying various statistics.

### Creating Components

```{pyodide}
plot = pn.pane.HoloViews(fig, sizing_mode="stretch_both", name="Plot")
table = pn.widgets.Tabulator(df, sizing_mode="stretch_both", name="Table")
```

- `plot`: This variable stores a HoloViews plot pane displaying the bar plot.
- `table`: This variable stores a Tabulator widget displaying the filtered DataFrame as a table.

### Layout

```{pyodide}
tabs = pn.Tabs(
    plot, table, styles=styles, sizing_mode="stretch_width", height=500, margin=10
)
```

- `tabs`: This variable stores a Tabs widget containing the plot and table, allowing users to switch between them.

### Creating the Dashboard

```python
pn.template.FastListTemplate(
    title="Wind Turbine Dashboard",
    sidebar=[image, t_manu, p_year],
    main=[pn.Column(indicators, tabs, sizing_mode="stretch_both")],
    main_layout=None,
    accent=ACCENT,
).servable()
```

- This code creates a `FastListTemplate` dashboard with a sidebar containing the image, manufacturer select dropdown, and year slider, and a main section containing the indicators and tabs.

### Conclusion

This code sets up a dynamic dashboard for exploring wind turbine data, including filtering, data transformation, visualization, and statistics display. It leverages various Panel widgets, HoloViews plots, and CSS styling to create an interactive and informative dashboard.
