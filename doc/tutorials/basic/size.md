# Control the Size

Welcome to our tutorial on controlling the size of components in Panel! In this guide, we'll explore how sizing works, including inherent sizing, fixed sizing, and responsive sizing. We'll also delve into fully responsive layouts using the powerful [`FlexBox`](../../reference/layouts/FlexBox.ipynb) layout.

## Explore Sizing Modes

Panel provides various options to control the size of components:

- `sizing_mode`: Allows toggling between fixed sizing and responsive sizing along vertical and/or horizontal dimensions.
- `width`/`height`: Allows setting a fixed width or height.
- `min_width`/`min_height`: Allows setting a minimum width or height if responsive sizing is set along the corresponding dimension.
- `max_width`/`max_height`: Allows setting a maximum width or height if responsive sizing is set along the corresponding dimension.

:::{note}
Throughout this tutorial, you can execute the provided code directly in the Panel documentation using the green *run* button, in a notebook cell, or within a file named `app.py` served with `panel serve app.py --autoreload`.
:::

## Inherent and Absolute Sizing

Many components have inherent sizes. For instance, text will take up space based on its font size and content. Let's see how different sizing parameters affect the display:

```{pyodide}
import panel as pn

pn.extension()

text = """A wind turbine is a renewable energy device that converts the kinetic energy from wind into electricity. It typically consists of a tall tower with large blades attached to a rotor. As the wind blows, it causes the rotor to spin, which in turn rotates a generator to produce electricity. Wind turbines are designed to harness the natural power of the wind and are used to generate clean, sustainable energy. They come in various sizes, from small residential turbines to massive commercial installations, and play a crucial role in reducing greenhouse gas emissions and meeting renewable energy goals."""

pn.panel(text).servable()
```

By restricting the `width`, we can force the text to wrap:

```{pyodide}
import panel as pn

pn.extension()

text = """A wind turbine is a renewable energy device that converts the kinetic energy from wind into electricity. It typically consists of a tall tower with large blades attached to a rotor. As the wind blows, it causes the rotor to spin, which in turn rotates a generator to produce electricity. Wind turbines are designed to harness the natural power of the wind and are used to generate clean, sustainable energy. They come in various sizes, from small residential turbines to massive commercial installations, and play a crucial role in reducing greenhouse gas emissions and meeting renewable energy goals."""

pn.panel(text, width=300).servable()
```

Explicitly setting both `width` and `height` will force the display to scroll:

```{pyodide}
import panel as pn

pn.extension()

text = """A wind turbine is a renewable energy device that converts the kinetic energy from wind into electricity. It typically consists of a tall tower with large blades attached to a rotor. As the wind blows, it causes the rotor to spin, which in turn rotates a generator to produce electricity. Wind turbines are designed to harness the natural power of the wind and are used to generate clean, sustainable energy. They come in various sizes, from small residential turbines to massive commercial installations, and play a crucial role in reducing greenhouse gas emissions and meeting renewable energy goals."""

pn.panel(text, width=300, height=100).servable()
```

## Sizing Mode

The `sizing_mode` option toggles responsiveness. Let's create a fixed-size `Column` and observe its behavior:

::::{tab-set}

:::{tab-item} Stretch Width

```{pyodide}
import panel as pn

pn.extension()

layout = pn.Spacer(styles={'background': 'green'}, sizing_mode='stretch_width', height=200)

pn.Column(layout, width=400, height=400, styles={'border': '1px solid black'}).servable()
```

:::

:::{tab-item} Stretch Height

```{pyodide}
import panel as pn

pn.extension()

layout = pn.Spacer(styles={'background': 'green'}, sizing_mode='stretch_height', width=200)

pn.Column(layout, width=400, height=400, styles={'border': '1px solid black'}).servable()
```

:::

:::{tab-item} Stretch Both

```{pyodide}
import panel as pn

pn.extension()

layout = pn.Spacer(styles={'background': 'green'}, sizing_mode='stretch_both')

pn.Column(layout, width=400, height=400, styles={'border': '1px solid black'}).servable()
```

:::

::::

### Exercises

Let's dive in!

#### Configure the Sizing Mode

Rearrange the `Markdown` pane and Bokeh `figure` below such that they fully fill the available space but also ensure that the text never shrinks below 200 pixels and never grows above 500 pixels in width.

```{pyodide}
import pandas as pd
import panel as pn
from bokeh.plotting import figure

pn.extension()

text = """A *wind turbine* is a renewable energy device that converts the kinetic energy from wind into electricity. It typically consists of a tall tower with large blades attached to a rotor. As the wind blows, it causes the rotor to spin, which in turn rotates a generator to produce electricity. Wind turbines are designed to harness the natural power of the wind and are used to generate clean, sustainable energy. They come in various sizes, from small residential turbines to massive commercial installations, and play a crucial role in reducing greenhouse gas emissions and meeting renewable energy goals."""
data = pd.DataFrame(
    [
        ("Monday", 7),
        ("Tuesday", 4),
        ("Wednesday", 9),
        ("Thursday", 4),
        ("Friday", 4),
        ("Saturday", 5),
        ("Sunday", 4),
    ],
    columns=["Day", "Wind Speed (m/s)"],
)

fig = figure(
    x_range=data["Day"],
    title="Wind Speed by Day",
    y_axis_label="Wind Speed (m/s)",
    # <- insert argument here
)
fig.vbar(x=data["Day"], top=data["Wind Speed (m/s)"], width=0.5, color="navy", )

md = pn.pane.Markdown(
    text,  # <- insert arguments here
)
pn.Row(fig, md, height=500, sizing_mode="stretch_width").servable()
```

:::{hint}
**Hint 1**: Use `min_width`, `max_width`, and `sizing_mode` arguments.

**Hint 2**: To ensure the content displays correctly, you may need to adjust both the underlying object's settings and the Panel component displaying it.
:::

Test your solution by changing the window size of your browser. It should look like below.

<video controls="" poster="https://assets.holoviz.org/panel/tutorials/exercise_configure_sizing_mode.png" style="max-height: 400px; max-width: 100%;">
    <source src="https://assets.holoviz.org/panel/tutorials/exercise_configure_sizing_mode.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>

:::{dropdown} Solution

```{pyodide}
import pandas as pd
import panel as pn
from bokeh.plotting import figure

pn.extension()

text = """A *wind turbine* is a renewable energy device that converts the kinetic energy from wind into electricity. It typically consists of a tall tower with large blades attached to a rotor. As the wind blows, it causes the rotor to spin, which in turn rotates a generator to produce electricity. Wind turbines are designed to harness the natural power of the wind and are used to generate clean, sustainable energy. They come in various sizes, from small residential turbines to massive commercial installations, and play a crucial role in reducing greenhouse gas emissions and meeting renewable energy goals."""
data = pd.DataFrame(
    [
        ("Monday", 7),
        ("Tuesday", 4),
        ("Wednesday", 9),
        ("Thursday", 4),
        ("Friday", 4),
        ("Saturday", 5),
        ("Sunday", 4),
    ],
    columns=["Day", "Wind Speed (m/s)"],
)

fig = figure(
    x_range=data["Day"],
    title="Wind Speed by Day",
    y_axis_label="Wind Speed (m/s)",
    sizing_mode='stretch_both',
)
fig.vbar(x=data["Day"], top=data["Wind Speed (m/s)"], width=0.5, color="navy", )

md = pn.pane.Markdown(
    text,  sizing_mode="stretch_width", min_width=200, max_width=500,
)
pn.Row(fig, md, height=500, sizing_mode="stretch_width").servable()
```

:::

#### Finetune with Widgets

:::{tip}
**Pro Tip**: Speed up the process of fine-tuning by using interactive widgets instead of code. Panel's `pn.Param` provides an easy way to create widgets to control your Panel component.
:::

Continue from the previous exercise solution. Add the `settings` component below your `Row`:

```python
settings = pn.Param(md, parameters=["sizing_mode", "min_width", "max_width"])
```

Try changing the values of the `sizing_mode`, `min_height`, and `max_height` widgets interactively. Observe the effect on the component's display as you adjust the values.

:::{dropdown} Solution

```{pyodide}
import pandas as pd
import panel as pn
from bokeh.plotting import figure

pn.extension()

text = """A *wind turbine* is a renewable energy device that converts the kinetic energy from wind into electricity. It typically consists of a tall tower with large blades attached to a rotor. As the wind blows, it causes the rotor to spin, which in turn rotates a generator to produce electricity. Wind turbines are designed to harness the natural power of the wind and are used to generate clean, sustainable energy. They come in various sizes, from small residential turbines to massive commercial installations, and play a crucial role in reducing greenhouse gas emissions and meeting renewable energy goals."""
data = pd.DataFrame(
    [
        ("Monday", 7),
        ("Tuesday", 4),
        ("Wednesday", 9),
        ("Thursday", 4),
        ("Friday", 4),
        ("Saturday", 5),
        ("Sunday", 4),
    ],
    columns=["Day", "Wind Speed (m/s)"],
)

fig = figure(
    x_range=data["Day"],
    title="Wind Speed by Day",
    y_axis_label="Wind Speed (m/s)",
    sizing_mode='stretch_both',
)
fig.vbar(x=data["Day"], top=data["Wind Speed (m/s)"], width=0.5, color="navy", )

md = pn.pane.Markdown(
    text,  min_width=200, max_width=500,
)
settings = pn.Param(md, parameters=["sizing_mode", "min_width", "max_width"])
pn.Row(fig, md, settings, height=500,).servable()
```

:::

#### Change the Defaults

:::{note}
The default `sizing_mode` of Panel is `"fixed"`. We can change the default `sizing_mode` via `pn.extension(sizing_mode=...)` or `pn.config.sizing_mode=...`.
:::

Let's redo the initial `sizing_mode` exercise, but this time with a default `sizing_mode` of `"stretch_width"`.

:::{dropdown} Solution

```{pyodide}
import pandas as pd
import panel as pn
from bokeh.plotting import figure

pn.extension(sizing_mode="stretch_width")

text = """A *wind turbine* is a renewable energy device that converts the kinetic energy from wind into electricity. It typically consists of a tall tower with large blades attached to a rotor. As the wind blows, it causes the rotor to spin, which in turn rotates a generator to produce electricity. Wind turbines are designed to harness the natural power of the wind and are used to generate clean, sustainable energy. They come in various sizes, from small residential turbines to massive commercial installations, and play a crucial role in reducing greenhouse gas emissions and meeting renewable energy goals."""
data = pd.DataFrame(
    [
        ("Monday", 7),
        ("Tuesday", 4),
        ("Wednesday", 9),
        ("Thursday", 4),
        ("Friday", 4),
        ("Saturday", 5),
        ("Sunday", 4),
    ],
    columns=["Day", "Wind Speed (m/s)"],
)

fig = figure(
    x_range=data["Day"],
    title="Wind Speed by Day",
    y_axis_label="Wind Speed (m/s)",
    sizing_mode='stretch_both',
)
fig.vbar(x=data["Day"], top=data["Wind Speed (m/s)"], width=0.5, color="navy", )

md = pn.pane.Markdown(
    text,  min_width=200, max_width=500,
)
pn.Row(fig, md, height=500,).servable()
```

:::

## Responsive Layouts with FlexBox

Responsive layouts are essential for adapting to various screen sizes. Panel's `FlexBox` layout provides this functionality out of the box.

Let's try out `FlexBox`:

```{pyodide}
import panel as pn
import random

pn.extension()

def create_random_spacer():
    return pn.Spacer(
        height=100,
        width=random.randint(1, 4) * 100,
        styles={"background": "teal"},
        margin=5,
    )
spacers = [create_random_spacer() for _ in range(10)]

pn.FlexBox(*spacers).servable()
```

Adjust the width of your browser window to observe the layout's responsiveness.

:::{note}
We'll explore `FlexBox` in more detail in the [Control the Size (intermediate)](../intermediate/size.md) tutorial.
:::

## Recap

In this tutorial, we've explored various aspects of controlling component size in Panel. We've covered inherent sizing, fixed sizing, and responsive sizing, along with the powerful [`FlexBox`](../../reference/layouts/FlexBox.ipynb) layout:

- `sizing_mode`: Allows toggling between fixed sizing and responsive sizing along vertical and/or horizontal dimensions.
- `width`/`height`: Allows setting a fixed width or height.
- `min_width`/`min_height`: Allows setting a minimum width or height if responsive sizing is set along the corresponding dimension.
- `max_width`/`max_height`: Allows setting a maximum width or height if responsive sizing is set along the corresponding dimension.

## Resources

### Tutorials

- [Control the Size (intermediate)](../intermediate/size.md)

### How-to

- [Control Size](../../how_to/layout/size.md)
