# Style Altair Plots

This guide addresses how to style Altair plots displayed using the [Vega pane](../../../examples/reference/panes/Vega.ipynb).

You can select the theme of Altair plots using [`altair.themes.enable`](https://altair-viz.github.io/user_guide/customization.html#changing-the-theme) and an accent color using the `configure_mark` method.

The gif below displays an example of what can be achieved with a little styling of the Altair plot and the `FastListTemplate`.

![VegaAltairStyle.gif](https://assets.holoviews.org/panel/thumbnails/gallery/styles/vega-styles.gif)

## An Altair plot with dark theme and accent color

In this example we will give the Altair Plot a dark theme and a custom accent color.

```{pyodide}
import altair as alt
import panel as pn

from vega_datasets import data

pn.extension("vega")

ALTAIR_ACCENT_COLOR = "#F08080"
ALTAIR_THEME = "dark" # "default", "opaque"

plot = (
    alt.Chart(data.cars())
    .mark_circle(size=200)
    .encode(
        x='Horsepower:Q',
        y='Miles_per_Gallon:Q',
        tooltip=["Name", "Origin", "Horsepower", "Miles_per_Gallon"],
    )
    .configure_mark(
        color=ALTAIR_ACCENT_COLOR
    )
    .properties(
        height="container",
        width="container",
    )
    .interactive()
)

alt.themes.enable(ALTAIR_THEME)
pn.pane.Vega(plot, max_height=500, sizing_mode="stretch_width").servable()
```

If you do not wish to apply the `"dark"` theme to other Altair plots, you should reset the
theme to `"default"` after the `pn.pane.Vega(..)` line.

```{pyodide}
alt.themes.enable("default")
```
