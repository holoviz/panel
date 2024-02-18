# Build Animation

In this tutorial we will build a *bar chart race* animation using the [Altair](https://altair-viz.github.io) plotting library and the [`Player`](../../reference/widgets/Player.ipynb) widget.

:::{note}
When we ask to *run the code* in the sections below, we may either execute the code directly in the Panel docs via the green *run* button, in a cell in a notebook, or in a file `app.py` that is served with `panel serve app.py --autoreload`.
:::

```{pyodide}
import panel as pn

pn.extension("vega")
```

## Install the dependencies

Please make sure [Altair](https://altair-viz.github.io/) is installed.

::::{tab-set}

:::{tab-item} conda
:sync: conda

``` bash
conda install -y -c conda-forge altair
```

:::

:::{tab-item} pip
:sync: pip

``` bash
pip install altair
```

:::

::::

## Create a Bar Chart Race

Run the code below

```{pyodide}
import altair as alt
import pandas as pd
import panel as pn

pn.extension("vega") # load the vega/ Altair JavaScript dependencies

BY = "t_manu"  # t_state, t_county or t_manu
VALUE = "p_cap"

## Extract the data

@pn.cache()  # use caching to only download data once
def get_data():
    print("Downloading data ...")
    return pd.read_csv("https://assets.holoviz.org/panel/tutorials/turbines.csv.gz")

## Transform the data

data = get_data()
min_year = int(data.p_year.min())
max_year = int(data.p_year.max())
max_group_value = data.groupby(BY)[VALUE].sum().max()


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
            x=alt.X(VALUE, scale=alt.Scale(domain=[0, max_group_value])),
            y=alt.Y(f"{BY}:O", sort=[BY]),
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
pn.Column("# Manufacturer Capacity 1982-2022", plot, year, sizing_mode="stretch_width").servable()
```

Press the *play* button.

It will take a little bit of time to run `get_data` the first time the code is run.

You should see how the top 10 manufacturer capacity has developed since the beginning of the 80's via a *bar chart race*.

:::{note}
The code refers to

- `get_plot`: A function returning a bar chart for the given year.
- `year`: The Panel `Player` widget. Its value starts at `min_year` and ends at `max_year`.
- `pn.bind(pause_player_at_max_year, year, watch=True)`: Stops the player when the `max_year` is reached.
- `plot`: Binds `get_plot` to the `year` Player widget.

:::

## Recap

In this tutorial we built a *bar chart race* animation using the [Altair](https://altair-viz.github.io) plotting library and the [`Player`](../../reference/widgets/Player.ipynb) widget.

We could have created an animation using any object type that Panel can display including your favorite plotting library.
