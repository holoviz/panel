# Templates

In this tutorial we will use *pre-made templates* to easily layout an app with a *header*, *sidebar* and *main* area:

- Templates are available in the `pn.template` namespace
- Templates can be found in the [Templates Section](../../reference/index.md#templates) of the [Component Gallery](../../reference/index.md).
- Templates are highly customizable

## A Hello World Template Example

Copy the code below to a file `app.py`.

```python
import panel as pn

pn.extension()

pn.template.FastListTemplate(
    title="Hello World",
    sidebar=["# Hello Sidebar", "This is text for the *sidebar*"],
    main=["# Hello Main", "This is text for the *main* area"],
).servable()
```

Serve the app with

```bash
panel serve app.py --autoreload
```

It should look like below

![Hello World FastListTemplate App](../../_static/images/templates_hello_world.png)

:::{admonition} Note
Panel ships with a large collection of built in templates. There is even a *Slides* template.
:::


Spend a couple of minutes checking out the [Templates Section](../../reference/index.md#templates) of the [Component Gallery](../../reference/index.md). Then return here.

[![Templates Section](../../_static/images/templates_section.png)](../../reference/index.md#templates)



## Don't display a Template in a Notebook

:::{admonition} Note
Currently *templates* do not display well in a notebook.
:::

Copy the two code cells below into a notebook.

```python
import panel as pn

pn.extension()
```

```
pn.template.FastListTemplate(
    title="Hello World",
    sidebar=["# Hello Sidebar", "This is text for the *sidebar*"],
    main=["# Hello Main", "This is text for the *main* area"],
).servable()
```

Add a `;` after `.servable()` to not display the template in the notebook.

*Preview* the app.

It should look like

![Hello World FastListTemplate App](../../_static/images/templates_hello_world_notebook.png)

## Templates are Highly Customizable

Copy the code below to a file `app.py`.

```python
import panel as pn
import pandas as pd
import altair as alt

pn.extension("vega")

ACCENT = "teal"

image = pn.pane.JPG("https://assets.holoviz.org/panel/tutorials/wind_turbines_sunset.png")

if pn.config.theme=="dark":
    alt.themes.enable("dark")
else:
    alt.themes.enable("default")

@pn.cache # Add caching to only download data once
def get_data():
    return pd.read_csv("https://assets.holoviz.org/panel/tutorials/turbines.csv.gz")

df = get_data()

top_manufacturers = (
    df.groupby("t_manu").p_cap.sum().sort_values().iloc[-10:].index.to_list()
)
df = df[df.t_manu.isin(top_manufacturers)]
fig = (
    alt.Chart(
        df.sample(5000),
        title="Capacity by Manufacturer",
    )
    .mark_circle(size=8)
    .encode(
        y="t_manu:N",
        x="p_cap:Q",
        yOffset="jitter:Q",
        color=alt.Color("t_manu:N").legend(None),
        tooltip=["t_manu", "p_cap"],
    )
    .transform_calculate(jitter="sqrt(-2*log(random()))*cos(2*PI*random())")
    .properties(
        height="container",
        width="container",
    )
)
plot = pn.pane.Vega(fig, sizing_mode="stretch_both", max_height=800, margin=20)

pn.template.FastListTemplate(
    title="Wind Turbine Manufacturers",
    sidebar=[image, "**Note**: Only the 10 Manufacturers with largest installed capacity are shown in the plot."],
    main=["# Installed Capacity", plot],
    accent=ACCENT,
    main_layout=None,
).servable()
```

Serve the app with

```bash
panel serve app.py --autoreload
```

It should look like below

![Customized FastListTemplate App](../../_static/images/templates_customized_default.png)

And in dark mode

![Customized FastListTemplate App](../../_static/images/templates_customized_dark.png)

## Recap

In this tutorial we have used *pre-made templates* to easily layout an app with a *header*, *sidebar* and *main* area:

- Templates are available in the `pn.template` namespace
- Templates can be found in the [Templates Section](../../reference/index.md#templates) of the [Component Gallery](../../reference/index.md).
- Templates are highly customizable

## References

### How-to

- [Arrange Components in a Template](../../how_to/templates/template_arrange.md)
- [Build a Custom Template](../../how_to/templates/template_custom.md)
- [Customize Template Theme](../../how_to/templates/template_theme.md)
- [Set a Template](../../how_to/templates/template_set.md)
- [Toggle Modal](../../how_to/templates/template_modal.md)

### Explanation

- [Templates](../../explanation/styling/templates_overview.md)
