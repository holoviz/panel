# Build Animation

In this tutorial, we will create a *bar chart race* using the [Altair](https://altair-viz.github.io) plotting library and the [`Player`](../../reference/widgets/Player.ipynb) widget.

<video muted controls loop poster="https://assets.holoviz.org/panel/tutorials/bar_chart_race.png" style="max-height: 400px; max-width: 100%;">
    <source src="https://assets.holoviz.org/panel/tutorials/bar_chart_race.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>

:::{dropdown} Dependencies

```bash
altair panel
```

:::

:::{dropdown} Code

```python
import altair as alt
import pandas as pd
import panel as pn

pn.extension("vega") # load the vega/ Altair JavaScript dependencies

BY = "t_manu"  # t_state, t_county, or t_manu
VALUE = "p_cap"

## Extract the data

@pn.cache()  # use caching to only download data once
def get_data():
    return pd.read_csv("https://assets.holoviz.org/panel/tutorials/turbines.csv.gz")

## Transform the data

data = get_data()
min_year = int(data.p_year.min())
max_year = int(data.p_year.max())
max_capacity_by_manufacturer = data.groupby(BY)[VALUE].sum().max()


def get_group_sum(year):
    return (
        data[data.p_year <= year][[BY, VALUE]]
        .groupby(BY)
        .sum()
        .sort_values(by=VALUE, ascending=False)
        .reset_index()
        .head(10)
    )

# Plot the data

def get_plot(year):
    data = get_group_sum(year)
    base = (
        alt.Chart(data)
        .encode(
            x=alt.X(VALUE, scale=alt.Scale(domain=[0, max_capacity_by_manufacturer]), title="Capacity"),
            y=alt.Y(f"{BY}:O", sort=[BY], title="Manufacturer"),
            text=alt.Text(VALUE, format=",.0f"),
        )
        .properties(title=str(year), height=500, width="container")
    )
    return base.mark_bar() + base.mark_text(align="left", dx=2)

# Add widgets

year = pn.widgets.Player(
    value=max_year,
    start=min_year,
    end=max_year,
    name="Year",
    loop_policy="loop",
    interval=300,
    align="center",
)

def pause_player_at_max_year(value):
    if year.value==max_year:
        year.pause()

pn.bind(pause_player_at_max_year, year, watch=True) # Stops the player when max_year is reached.

# Bind the plot to the Player widget

plot = pn.pane.Vega(pn.bind(get_plot, year))

# Layout the components
pn.Column("# Wind Turbine Capacity 1982-2022", plot, year, sizing_mode="stretch_width").servable()
```

:::

## Install the dependencies

Please ensure that [Altair](https://altair-viz.github.io/) and [Panel](https://panel.holoviz.org) are installed.

::::{tab-set}

:::{tab-item} pip
:sync: pip

``` bash
pip install altair panel
```

:::

:::{tab-item} conda
:sync: conda

``` bash
conda install -y -c conda-forge altair panel
```

:::

::::

## Explanation

🚀 **Welcome to the Altair & Panel Bar Chart Race Tutorial!**

Let's embark on an adventure to visualize the dynamic evolution of wind turbine capacities over the years. 🌬️💨

```{pyodide}
import altair as alt
import pandas as pd
import panel as pn

pn.extension("vega")
```

First things first, we need to import our trusty companions: [Altair](https://altair-viz.github.io/) for stunning visualizations, [Pandas](https://pandas.pydata.org/) for data manipulation, and [Panel](https://panel.holoviz.org) for creating interactive web apps.

---

📊 **Step 1: Data Exploration and Extraction**

```{pyodide}
BY = "t_manu"
VALUE = "p_cap"

@pn.cache()
def get_data():
    return pd.read_csv("https://assets.holoviz.org/panel/tutorials/turbines.csv.gz")

data = get_data()
min_year = int(data.p_year.min())
max_year = int(data.p_year.max())
max_capacity_by_manufacturer = data.groupby(BY)[VALUE].sum().max()
```

We begin by defining our data source and understanding its bounds. We extract turbine data and identify the minimum and maximum years present in the dataset, along with the maximum capacity value aggregated by manufacturer.

---

🔄 **Step 2: Data Transformation and Grouping**

```{pyodide}
def get_group_sum(year):
    return (
        data[data.p_year <= year][[BY, VALUE]]
        .groupby(BY)
        .sum()
        .sort_values(by=VALUE, ascending=False)
        .reset_index()
        .head(10)
    )
```

We create a function to aggregate the turbine data up to a specified year, grouping by manufacturer and summing the capacity values. We then select the top 10 manufacturers based on capacity.

---

📈 **Step 3: Plotting Function**

```{pyodide}
def get_plot(year):
    data = get_group_sum(year)
    base = (
        alt.Chart(data)
        .encode(
            x=alt.X(VALUE, scale=alt.Scale(domain=[0, max_capacity_by_manufacturer]), title="Capacity"),
            y=alt.Y(f"{BY}:O", sort=[BY], title="Manufacturer"),
            text=alt.Text(VALUE, format=",.0f"),
        )
        .properties(title=str(year), height=500, width="container")
    )
    return base.mark_bar() + base.mark_text(align="left", dx=2)
```

Time to bring our visualization to life! This function generates an Altair chart based on the grouped data for a given year, encoding capacity on the x-axis, manufacturer on the y-axis, and displaying capacity as text within the bars.

---

⏩ **Step 4: Adding Interactive Controls**

```{pyodide}
year = pn.widgets.Player(
    value=max_year,
    start=min_year,
    end=max_year,
    name="Year",
    loop_policy="loop",
    interval=300,
    align="center",
)

def pause_player_at_max_year(value):
    if year.value==max_year:
        year.pause()

pn.bind(pause_player_at_max_year, year, watch=True)
```

Let's make it interactive! We introduce a [`Player`](../../reference/widgets/Player.ipynb) widget to loop continuously through the years.

---

🎨 **Step 5: Binding Plot to Widget**

```{pyodide}
plot = pn.pane.Vega(pn.bind(get_plot, year))
```

Now, let's bind our plot function to the selected year. Whenever the user changes the year, the plot dynamically updates to reflect the selected timeframe.

---

🖼️ **Step 6: Layout and Presentation**

```{pyodide}
pn.Column("# Wind Turbine Capacity 1982-2022", plot, year, sizing_mode="stretch_width").servable()
```

Lastly, we organize our components into a neat layout. A title sets the stage, followed by our interactive plot and the year selection widget. The layout adjusts to fill the available width.

---

Voilà! 🎉 You're now ready to run the code and witness the mesmerizing bar chart race showcasing the evolution of wind turbine capacities over the years. Happy exploring! 🌟

:::{hint}
You can create many types of animations using the object types that Panel can display. Not just bar chart races using Altair.
:::

## Serve the App

Now serve the app with:

::::{tab-set}

:::{tab-item} Script
:sync: script

```bash
panel serve app.py --autoreload
```

:::

:::{tab-item} Notebook
:sync: notebook

```bash
panel serve app.ipynb --autoreload
```

:::

::::

Open [http://localhost:5006/app](http://localhost:5006/app)

Press the *play* button.

It should resemble

<video muted controls loop poster="https://assets.holoviz.org/panel/tutorials/bar_chart_race.png" style="max-height: 400px; max-width: 100%;">
    <source src="https://assets.holoviz.org/panel/tutorials/bar_chart_race.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>

## Recap

In this tutorial, we built a *bar chart race* using the [Altair](https://altair-viz.github.io) plotting library and the [`Player`](../../reference/widgets/Player.ipynb) widget.
