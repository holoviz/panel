# Build Crossfiltering Dashboard

*Crossfiltering* is a dynamic method of data visualization that allows users to interactively filter and explore large datasets across multiple dimensions simultaneously. It's particularly useful in dashboards and data analysis applications where understanding relationships between different data facets is essential. By enabling the selection of specific criteria in one data visualization, crossfiltering instantly updates all other visualizations on the dashboard to reflect the filtered data. This real-time interaction provides deeper insights and a more intuitive way to navigate complex datasets, making it an invaluable tool for data scientists, analysts, and anyone looking to make informed decisions based on data trends and patterns.

In this tutorial, we'll guide you through constructing a dashboard with crossfiltering capabilities using [HoloViews](https://holoviews.org/) and [Panel](https://panel.holoviz.org/). This approach will showcase how to link multiple data visualizations so that interactions with one plot automatically update others. We'll be working with a dataset on wind turbines to illustrate how crossfiltering can unveil patterns and trends that might not be immediately apparent, enhancing your data exploration and analysis capabilities.

<video muted controls loop poster="../../_static/images/panel_crossfilter_dashboard.png" style="max-height: 400px; max-width: 100%;">
    <source src="https://assets.holoviz.org/panel/tutorials/panel_crossfilter_dashboard.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>

:::::{dropdown} Dependencies

```bash
holoviews panel
```

:::::

:::::{dropdown} Code

```python
import holoviews as hv
import numpy as np
import pandas as pd
import panel as pn
from bokeh.models.formatters import NumeralTickFormatter

pn.extension(sizing_mode="stretch_width")

ACCENT = "teal"

SHORT_NAMES = {
    "Changzhou Railcar Propulsion Engineering Research and Development Center": "Changzhou",
    "Siemens Gamesa Renewable Energy": "Siemens Gamesa",
}


@pn.cache()
def get_data():
    data = pd.read_csv("https://assets.holoviz.org/panel/tutorials/turbines.csv.gz")

    mask = data.t_manu.isin(list(SHORT_NAMES))
    data.loc[mask, "t_manu"] = data.loc[mask, "t_manu"].map(SHORT_NAMES)
    data.t_cap = data.t_cap / 10**6 # Convert capacity to gigawatts for readability
    return data

@pn.cache
def get_plots():
    data = get_data()

    # Define shared dataset
    ds = hv.Dataset(data, ["t_manu", "p_year", "t_cap"], "t_cap")

    # Create plots
    ds_by_year = ds.aggregate("p_year", function=np.sum).sort("p_year")[1995:]
    ds_by_manufacturer = ds.aggregate("t_manu", function=np.sum).sort(
        "t_cap", reverse=True
    ).iloc[:20]
    formatter = NumeralTickFormatter(format="0,0")
    plot_by_year = hv.Bars(
        ds_by_year, ("p_year", "Year"), ("t_cap", "Capacity (GW)")
    ).opts(
        responsive=True,
        min_height=300,
        yformatter=formatter,
        color=ACCENT,
        tools=["hover"],
        active_tools=["box_select"],
    )
    plot_by_manufacturer = hv.Bars(
        ds_by_manufacturer, ("t_manu", "Manufacturer"), ("t_cap", "Capacity (GW)")
    ).opts(
        responsive=True,
        min_height=300,
        xrotation=90,
        yformatter=formatter,
        color=ACCENT,
        tools=["hover"],
        active_tools=["box_select"],
    )

    return (plot_by_year + plot_by_manufacturer).cols(1)

crossfilter_plots = hv.link_selections(get_plots()).opts(shared_axes=False)

pn.template.FastListTemplate(
    title="Windturbine Dashboard with Crossfiltering",
    main=[crossfilter_plots],
    main_layout=None,
    accent=ACCENT,
).servable()
```

:::::

## Detailed Explanation

The following code snippets demonstrates how to set up a crossfiltering dashboard. We'll use a dataset on wind turbines, focusing on two key aspects: the production year and the manufacturer. The goal is to explore the total capacity of turbines produced each year and the contribution of different manufacturers to this capacity.

### Setting Up the Environment

The initial setup involves importing necessary libraries and configuring the Panel extension to ensure our dashboard is responsive and visually consistent.

```python
import holoviews as hv
import numpy as np
import pandas as pd
import panel as pn
from bokeh.models.formatters import NumeralTickFormatter

pn.extension(sizing_mode="stretch_width")

ACCENT = "teal"

SHORT_NAMES = {
    "Changzhou Railcar Propulsion Engineering Research and Development Center": "Changzhou",
    "Siemens Gamesa Renewable Energy": "Siemens Gamesa",
}
```

Here, we import HoloViews (`hv`) for creating interactive plots, NumPy (`np`) and Pandas (`pd`) for data manipulation, and Panel (`pn`) for dashboard creation. The `NumeralTickFormatter` from Bokeh is used to format numerical values on the plot axes for better readability.

### Data Preparation

The `get_data` function fetches the wind turbine dataset from a URL and preprocesses it by shortening the names of certain manufacturers for clarity in the visualizations.

```python
@pn.cache()
def get_data():
    data = pd.read_csv("https://assets.holoviz.org/panel/tutorials/turbines.csv.gz")

    mask = data.t_manu.isin(list(SHORT_NAMES))
    data.loc[mask, "t_manu"] = data.loc[mask, "t_manu"].map(SHORT_NAMES)
    data.t_cap = data.t_cap / 10**6 # Convert capacity to gigawatts for readability
    return data
```

`@pn.cache()` decorates the function to cache its output, reducing loading times by avoiding repeated data fetching and processing.

### Creating the Crossfiltering Plot

The core of the dashboard is the `get_plots` function, which generates two interactive bar charts: one displaying the total capacity of wind turbines by year and another by manufacturer.

```python
@pn.cache
def get_plots():
    data = get_data()

    # Define shared dataset
    ds = hv.Dataset(data, ["t_manu", "p_year", "t_cap"], "t_cap")

    ... # continues in next section
```

The function starts by calling `get_data()` to retrieve the preprocessed dataset. It then uses HoloViews to define a dataset (`ds`) that encapsulates our data, specifying columns for manufacturers (`t_manu`), production year (`p_year`), and turbine capacity (`t_cap`).

:::{note}

In order for [HoloViews linked brushing](https://holoviews.org/user_guide/Linked_Brushing.html) (crossfiltering) to work the plots need to be generated from a shared dataset.

:::

#### Visualizing Data by Year and Manufacturer

Next, we aggregate the data by year and manufacturer to create two separate plots. The plots are formatted to be responsive and use an accent color for consistency.

```python
@pn.cache
def get_plots():
    ... # continues from previous section

    # Create plots
    ds_by_year = ds.aggregate("p_year", function=np.sum).sort("p_year")[1995:]
    ds_by_manufacturer = ds.aggregate("t_manu", function=np.sum).sort(
        "t_cap", reverse=True
    ).iloc[:20]
    formatter = NumeralTickFormatter(format="0,0")
    plot_by_year = hv.Bars(
        ds_by_year, ("p_year", "Year"), ("t_cap", "Capacity (GW)")
    ).opts(
        responsive=True,
        min_height=300,
        yformatter=formatter,
        color=ACCENT,
        tools=["hover"],
        active_tools=["box_select"],
    )
    plot_by_manufacturer = hv.Bars(
        ds_by_manufacturer, ("t_manu", "Manufacturer"), ("t_cap", "Capacity (GW)")
    ).opts(
        responsive=True,
        min_height=300,
        xrotation=90,
        yformatter=formatter,
        color=ACCENT,
        tools=["hover"],
        active_tools=["box_select"],
    )

    return (plot_by_year + plot_by_manufacturer).cols(1)
```

The `hv.Bars` method creates bar charts, which are then customized with options (`opts`) for responsiveness, rotation of the x-axis labels, formatting of the y-axis values, and color styling.

#### Linking the Selections

The crossfiltering capability is enabled by linking the selections across the two plots. This means that interacting with one plot (e.g., selecting a range of years) will dynamically filter the data in the other plot to match the selection criteria.

```python
crossfilter_plots = hv.link_selections(get_plots()).opts(shared_axes=False)
```

The `hv.link_selections` function wraps our layout of plots, enabling interactive filtering across them. This crossfilter mechanism is what makes our dashboard powerful for data exploration.

:::{note}

Please note we create a `crossfilter_plots` object for every user session because sessions cannot share `link_selections` objects.

:::

### Serving the Dashboard

Finally, the plots are incorporated into a Panel template, which is then made servable. This step prepares our dashboard for deployment, allowing users to interact with the visualizations through a web interface.

```python
pn.template.FastListTemplate(
    title="Windturbine Dashboard with Crossfiltering",
    main=[crossfilter_plots],
    main_layout=None,
    accent=ACCENT,
).servable()
```

The [`FastListTemplate`](https://panel.holoviz.org/reference/templates/FastListTemplate.html) is a pre-built Panel template that provides a clean and modern layout for our dashboard. It takes our crossfiltering plot and other configurations as input, creating a cohesive and interactive web application.

Now serve the app with `panel serve app.py --autoreload`. It should look like

<video muted controls loop poster="../../_static/images/panel_crossfilter_dashboard.png" style="max-height: 400px; max-width: 100%;">
    <source src="https://assets.holoviz.org/panel/tutorials/panel_crossfilter_dashboard.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>

## References

### App Gallery

- [Glaciers Dashboard](https://panel.holoviz.org/gallery/glaciers.html)
- [Penguin Dashboard](https://panel.holoviz.org/gallery/penguin_crossfilter.html)
- [Windturbines Dashboard](https://panel.holoviz.org/gallery/windturbines.html)

### External

- [HoloViews Linked Brushing](https://holoviews.org/user_guide/Linked_Brushing.html)
