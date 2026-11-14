# Theme Plotting Libraries

This guide shows how plots automatically follow the theme of a `panel.ui` app and how to generate color palettes and colormaps that match it.

---

When a plot is rendered inside a `panel.ui` app, e.g. in a [`Page`](../../reference/templates/Page), next to a [`ThemeToggle`](../../reference/templates/ThemeToggle) or inside any other `panel.ui` component at the root of your app, Panel applies the active theme to it. Plots pick up the font family, text and grid colors and background of the theme and switch along with it between light and dark mode, without any extra code.

How much of the theme is applied depends on the plotting library:

| Library | What is themed automatically |
| --- | --- |
| Bokeh, hvPlot and HoloViews | Background, fonts, text, axis, grid, legend, colorbar and hover tooltip styling, the active toolbar highlight in the primary color, and light/dark mode |
| Plotly | Background, fonts, text, axis and grid colors, and light/dark mode |
| Vega and Altair | Switches to the Vega `dark` theme in dark mode |
| ECharts | Gauge charts switch to the ECharts `dark` theme in dark mode |
| Matplotlib | Nothing, the plot is rendered as a static image |

This guide covers the automatic theming inside `panel.ui` apps. To style a plot yourself, e.g. with a library's own themes and templates, see the library-specific guides for [Altair](altair), [ECharts](echarts), [Matplotlib](matplotlib), [Plotly](plotly) and [Vega](vega).

## Theme Bokeh, hvPlot and HoloViews

Bokeh plots, including the ones created with hvPlot and HoloViews, adapt to the active theme, respecting the font family and toggling between dark and light mode. Use the toggle in the top right of the example to switch between the two:

```{pyodide}
import panel as pn
import pandas as pd
import hvplot.pandas

pn.extension()

df = pd.read_csv("https://datasets.holoviz.org/penguins/v1/penguins.csv")

toggle = pn.ui.ThemeToggle(styles={"margin-left": "auto"})

pn.ui.Container(
    toggle,
    df.hvplot.scatter(
        x="bill_length_mm", y="bill_depth_mm", by="species",
        height=400, responsive=True
    ),
    width_option="md"
).preview()
```

### Chart style

By default a minimal chart style is applied, which hides axis lines, tick marks and plot outlines for a cleaner look. You can switch to a different style by setting `chart_style` in the `theme_config`:

```{pyodide}
toggle = pn.ui.ThemeToggle(styles={"margin-left": "auto"})

pn.ui.Container(
    toggle,
    df.hvplot.scatter(
        x="bill_length_mm", y="bill_depth_mm", by="species",
        height=400, responsive=True
    ),
    theme_config={"chart_style": "classic"},
    width_option="md"
).preview()
```

There are three chart styles:

- `"minimal"` hides axis lines, tick marks, legend borders and plot outlines. It suits plots placed on the surfaces of an application.
- `"standard"` keeps the minimal look but adds a soft plot frame, axis lines with major ticks, a legend box and a bold title, so a plot holds together on its own.
- `"classic"` restores the full Bokeh look, with solid axis lines, major and minor ticks, legend borders, colorbar outlines and plot frames.

When `chart_style` is omitted, plots use `"minimal"` inside a `Page` and `"standard"` when rendered on their own, e.g. as a notebook output.

### Palettes and colormaps

The theme does not change the colors used to draw your data, so you control them with the usual `cmap` and `color` options. To keep your plots visually consistent with the rest of the app you can derive these colors from your theme's primary color.

When visualizing categorical data, each color should be visibly distinct from all the other colors, rather than nearby in color space, so that each category is separately visible. You can find existing categorical colormaps in the [colorcet](https://colorcet.holoviz.org/user_guide/Categorical.html) and [HoloViews](https://holoviews.org/user_guide/Colormaps.html#categorical-colormaps) documentation.

#### Categorical

To create a categorical palette aligned with your theme, use the `pn.ui.theme.generate_palette` function. It takes a base color and the number of colors to generate (3 by default):

```{pyodide}
primary_color = "#6200ea"
colors = pn.ui.theme.generate_palette(primary_color, n_colors=3)
toggle = pn.ui.ThemeToggle(styles={"margin-left": "auto"})

pn.ui.Container(
    toggle,
    df.hvplot.scatter(
        x="bill_length_mm", y="bill_depth_mm", color="species",
        height=400, responsive=True, cmap=colors
    ),
    theme_config={"palette": {"primary": {"main": primary_color}}},
    width_option="md"
).preview()
```

#### Continuous

Similarly, you can use the `pn.ui.theme.linear_gradient` function to create a continuous colormap between two colors:

```{pyodide}
cmap = pn.ui.theme.linear_gradient("#ffffff", primary_color, n=256)
toggle = pn.ui.ThemeToggle(styles={"margin-left": "auto"})

plot = df.hvplot.scatter(
    x="bill_length_mm", y="flipper_length_mm", c="body_mass_g",
    cmap=cmap, colorbar=True, height=400, responsive=True
).opts(
    backend_opts={"plot.toolbar.autohide": True},
    toolbar="above"
)

pn.ui.Container(
    toggle,
    plot,
    theme_config={"palette": {"primary": {"main": primary_color}}},
    width_option="md"
).preview()
```

:::{tip}
A gradient starting at white fades the lowest values into the background in light mode but stands out in dark mode. If you want the colormap to blend into the background in both modes, start it from a dark color such as `"#222222"` when the app is in dark mode. The [Apply Branding](ui_branding) guide shows how to switch colormaps along with the theme.
:::

## Theme Plotly

Plotly figures are themed automatically as well. A light theme is applied by default:

```{pyodide}
import plotly.express as px

pn.extension("plotly")

iris = px.data.iris()

plot = px.scatter(
    iris, x="sepal_length", y="sepal_width", color="species",
    height=400
)

pn.ui.Container(plot, width_option="md").preview(height=500)
```

and the figure switches automatically in dark mode:

```{pyodide}
toggle = pn.ui.ThemeToggle(styles={"margin-left": "auto"}, value=True)

plot = px.scatter(
    iris, x="sepal_length", y="sepal_width", color="species",
    height=400
)

pn.ui.Container(
    toggle, plot, dark_theme=True, width_option="md"
).preview(height=500)
```

### Color palettes and scales

Plotly provides built-in [categorical color sequences](https://plotly.com/python/discrete-color/) and [continuous color scales](https://plotly.com/python/builtin-colorscales/). The `generate_palette` and `linear_gradient` functions shown above also work for Plotly, so you can align the plot colors with your theme.

#### Categorical colors

Generate a palette with `pn.ui.theme.generate_palette` and provide it as the `color_discrete_sequence`:

```{pyodide}
primary_color = "#4099da"

colors = pn.ui.theme.generate_palette(primary_color, n_colors=3)

plot = px.scatter(
    iris, x="sepal_length", y="sepal_width", color="species",
    height=400,
    color_discrete_sequence=colors
)

toggle = pn.ui.ThemeToggle(styles={"margin-left": "auto"}, value=False)

pn.ui.Container(
    toggle,
    plot,
    theme_config={"palette": {"primary": {"main": primary_color}}},
    width_option="md"
).preview(height=500)
```

:::{note}
When you create a Plotly `Figure` directly you can provide a discrete color sequence via the `colorway` of its `layout`, i.e.:

```python
go.Figure(layout={"colorway": colors})
```
:::

#### Continuous colors

Create continuous color scales with `pn.ui.theme.linear_gradient` and provide them as the `color_continuous_scale`:

```{pyodide}
colorscale = pn.ui.theme.linear_gradient("#ffffff", primary_color, n=256)

plot = px.scatter(
    iris, x="sepal_length", y="sepal_width", color="petal_length",
    height=400,
    color_continuous_scale=colorscale
)

toggle = pn.ui.ThemeToggle(styles={"margin-left": "auto"}, value=False)

pn.ui.Container(
    toggle,
    plot,
    theme_config={"palette": {"primary": {"main": primary_color}}},
    width_option="md"
).preview(height=500)
```

## Related Resources

- [Toggle Dark Mode](ui_dark_mode)
- [Customize the Palette](ui_palette)
- [Pick Colors](ui_pick_colors)
- [Apply Branding](ui_branding)
