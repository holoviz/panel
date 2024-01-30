# Explore the Data

In this section we will use the [Swipe](../../reference/layouts/Swipe.ipynb) *layout* to understand how the global mean surface temperature has risen from 1945 to 2015 and the [Perspective](../../reference/panes/Perspective.ipynb) *pane* to slice and dice the wind `turbines` dataset.

This will barely scratch the surface of what Panel has to offer for exploratory data analysis (EDA) workflow. That is why we say that *Panel is **the powerful data exploration** and web app **framework***.

:::{admonition} Note
When I ask you to *run the code* in the sections below, you may either execute the code directly in the Panel docs via the green *run* button, in a cell in a notebook or in a file `app.py` that is served with `panel serve app.py --autoreload`.
:::

```{pydodide}
import panel as pn

pn.extension("perspective)
```

## Compare Temperatures with Swipe

Lets understand why we need renewable energy and wind turbines by comparing the global mean surface temperatures of the periods 1945-49 and 2015-2019.

Run the code below:

```{pyodide}
import panel as pn

pn.extension()

gis_1945 = 'https://earthobservatory.nasa.gov/ContentWOC/images/globaltemp/global_gis_1945-1949.png'
gis_2015 = 'https://earthobservatory.nasa.gov/ContentWOC/images/globaltemp/global_gis_2015-2019.png'

pn.Swipe(gis_1945, gis_2015).servable()
```

Try dragging the *slider* to compare the periods.

## Slice and dice with Perspective

Throughout these tutorials we will be using the wind `turbines` dataset. Let us take a first look.

Run the code below.

```{pyodide}
import pandas as pd
import panel as pn

pn.extension("perspective")

df = pd.read_csv("https://assets.holoviz.org/panel/tutorials/turbines.csv.gz")

pn.pane.Perspective(df, sizing_mode="stretch_width", height=600).servable()
```

:::{admonition} Note
The code refers to

- `pn.extension("perspective")`: We instruct Panel to load the javascript dependencies of [Perspective](../../reference/panes/Perspective.ipynb) into the notebook or server app.
- `pn.pane.Perspective(df, sizing_mode="stretch_width", height=600)`: Display the dataframe `df` with the [Perspective](../../reference/panes/Perspective.ipynb) *pane*. Stretch the width as much as possible and use a `height` of 600 pixels. You will learn much more about this later.
:::

:::{admonition} Note
You can use the pivoting capabilities of [Perspective](../../reference/panes/Perspective.ipynb) to explore the data. You can *drag* columns and *drop* them into the `Group By`, `Split By`, `Order By` and `Where` input areas. You can *CTRL drag* if a column must be used in multiple places.
:::

Find the Manufacturers (`t_manu`) with the highest installed capacity (`p_cap`):

- *Group By* `t_manu`
- *Display* and *Order By* `p_cap`

<details><summary>Solution: Capacity by Manufactorer Table</summary>

![Perspective Table](../../_static/images/explore_data_perspective_table.png)
</details>

Change the visualization from a `Datagrid` to an `X Bar` chart.

<details><summary>Solution: Capacity by Manufactorer Chart</summary>

![Perspective Chart](../../_static/images/explore_data_perspective_chart.png)
</details>

## Recap

We have used the [Swipe](../../reference/layouts/Swipe.ipynb) *layout* to understand how the global mean surface temperature has risen from 1945 to 2015 and the [Perspective](../../reference/panes/Perspective.ipynb) *pane* to slice and dice the wind `turbines` dataset.

We have barely scratched the surface of how Panel can improve your exploratory data analysis (EDA) workflow. That is why we say *Panel is **the powerful data exploration** and web app framework*.
