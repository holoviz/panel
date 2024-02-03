# Control the Size

In this tutorial we will discover how *sizing* works in Panel, explore the difference between *inherent sizing*, *fixed sizing* and *responsive sizing*. Finally we will touch upon the *fully responsive* layouts:

- `sizing_mode`: Allows toggling between fixed sizing and responsive sizing along vertical and/or horizontal dimensions.
- `width`/`height`:  Allows setting a fixed width or height
- `min_width`/`min_height`: Allows setting a minimum width or height, if responsive sizing is set along the corresponding dimension.
- `max_width`/`max_height` : Allows setting a maximum width or height, if responsive sizing is set along the corresponding dimension.

:::{note}
In the sections below, you may execute the code directly in the Panel documentation by using the green *run* button, in a notebook cell, or in a file named `app.py` served with `panel serve app.py --autoreload`.
:::

```{pyodide}
import panel as pn
pn.extension('tabulator')
```

## Inherent and absolute sizing

Many components you might want to display have an *inherent size*, e.g. take some text, based on the font-size and the content of the text it will take up a certain amount of space. When you render it it will fill the available space and wrap if necessary:

```{pyodide}
import panel as pn

pn.extension()

text = """A wind turbine is a renewable energy device that converts the kinetic energy from wind into electricity. It typically consists of a tall tower with large blades attached to a rotor. As the wind blows, it causes the rotor to spin, which in turn rotates a generator to produce electricity. Wind turbines are designed to harness the natural power of the wind and are used to generate clean, sustainable energy. They come in various sizes, from small residential turbines to massive commercial installations, and play a crucial role in reducing greenhouse gas emissions and meeting renewable energy goals."""

pn.panel(text).servable()
```

By restricting the width, we can force it to rewrap and it will have a different inherent height.

```{pyodide}
import panel as pn

pn.extension()

text = """A wind turbine is a renewable energy device that converts the kinetic energy from wind into electricity. It typically consists of a tall tower with large blades attached to a rotor. As the wind blows, it causes the rotor to spin, which in turn rotates a generator to produce electricity. Wind turbines are designed to harness the natural power of the wind and are used to generate clean, sustainable energy. They come in various sizes, from small residential turbines to massive commercial installations, and play a crucial role in reducing greenhouse gas emissions and meeting renewable energy goals."""

pn.panel(text, width=300).servable()
```

Explicitly setting both width and height will force the resulting display to scroll to ensure that it is not cut off:

```{pyodide}
import panel as pn

pn.extension()

text = """A wind turbine is a renewable energy device that converts the kinetic energy from wind into electricity. It typically consists of a tall tower with large blades attached to a rotor. As the wind blows, it causes the rotor to spin, which in turn rotates a generator to produce electricity. Wind turbines are designed to harness the natural power of the wind and are used to generate clean, sustainable energy. They come in various sizes, from small residential turbines to massive commercial installations, and play a crucial role in reducing greenhouse gas emissions and meeting renewable energy goals."""

pn.panel(text, width=300, height=100).servable()
```

## Sizing Mode

The `sizing_mode` option can be used to toggle responsiveness in the width or height dimension or both. To see the effect of this we will create a fixed size `Column` that we place the component into:

::::{tab-set}

:::{tab-item} Stretch Width

```{pyodide}
import panel as pn

pn.extension()

width_responsive = pn.Spacer(styles={'background': 'red'}, sizing_mode='stretch_width', height=200)

pn.Column(width_responsive, width=400, height=400, styles={'border': '1px solid black'}).servable()
```

:::

:::{tab-item} Stretch Height

```{pyodide}
import panel as pn

pn.extension()

height_responsive = pn.Spacer(styles={'background': 'green'}, sizing_mode='stretch_height', width=200)

pn.Column(height_responsive, width=400, height=400, styles={'border': '1px solid black'}).servable()
```

:::

:::{tab-item} Stretch Both

```{pyodide}
import panel as pn

pn.extension()

both_responsive = pn.Spacer(styles={'background': 'blue'}, sizing_mode='stretch_both')

pn.Column(both_responsive, width=400, height=400, styles={'border': '1px solid black'}).servable()
```

:::

::::

### Exercises

Let the fun begin!

#### Configure the Sizing Mode

Arrange the `Markdown` pane and Bokeh `figure` such that they fully fill the available space but also ensure that the text never shrinks below 200 pixels and never grows above 500 pixels in width.

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
    y_axis_label="Wind Speed (m/s)", # <- insert argument here
)
fig.vbar(x=data["Day"], top=data["Wind Speed (m/s)"], width=0.5, color="navy", )

md = pn.pane.Markdown(
    text,  # <- insert arguments here
)
pn.Row(fig, md, height=500, sizing_mode="stretch_width").servable()
```

Test your solution by changing the window size of your browser. Notice how the `figure` and `text` stretches.

<video controls="" poster="https://assets.holoviz.org/panel/tutorials/exercise_configure_sizing_mode.png">
    <source src="https://assets.holoviz.org/panel/tutorials/exercise_configure_sizing_mode.mp4" type="video/mp4" style="max-height: 400px; max-width: 100%;">
    Your browser does not support the video tag.
</video>

:::{note}
**Hint**: To get get *content* to display correctly it sometimes requires a combination of arguments to 1) the underlying object to display and 2) The Panel component displaying it.
:::

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

#### Explore the Sizing Mode via Widgets

:::{note}
**Pro Tip**: When fine-tuning the `size_mode`, `height`, `width` and other parameters of your Panel component you can speed up the process by using widgets interactively instead of code. Panels `pn.Param` provides an easy way to create widgets to control your Panel component.
:::

Continue from the solution in the previous section.

Add the `settings` component below to your `Row`

```python
settings = pn.Param(md, parameters=["sizing_mode", "min_width", "max_width"])
```

Try changing the values of the `sizing_mode`, `min_height` and `max_height` widgets interactively. For each change in value, change the width of your browser window to see the effect(s).

:::{dropdown} Solution

```{pyodide}
import pandas as pd
import panel as pn
from bokeh.plotting import figure

pn.extension()
pn.config.sizing_mode="stretch_width"

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

#### Change the Default Sizing Mode

:::{admonition}
The default `sizing_mode` of Panel is `"fixed"`. You can change the default `sizing_mode` via `pn.extension(sizing_mode=...)` or `pn.config.sizing_mode=...`.
:::

Redo the initial `sizing_mode` exercise, but this time with a default `sizing_mode`  of `"stretch_width"`.

:::{dropdown} Solution

```python
import pandas as pd
import panel as pn
from bokeh.plotting import figure

pn.extension(sizing_mode="stretch_width")
# or
# pn.extension()
# pn.config.sizing_mode="stretch_width"

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

So far when we have talked about responsive layouts we have primarily focused on simple `width`/`height` responsiveness of individual components, i.e. whether they will grow and shrink to fill the available space. For a truly responsive experience however we will need responsive layouts that will reflow the content depending on the size of the screen, browser window or the container they are placed inside of, much like how text wraps when there is insufficient width to accommodate it:

Panel offers one such component out of the box, the [`FlexBox`](../../reference/layouts/FlexBox.ipynb) layout.

Lets try the `FlexBox`:

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

Try adjusting the width of your browser window.

:::{note}
We will explore the `FlexBox` in more detail in the [*intermediate* tutorial on sizing](../intermediate/size.md).
:::

## Recap

In this tutorial we have discovered how *sizing* works in Panel. We have explored the difference between *inherent sizing*, *fixed sizing* and *responsive sizing*. Finally we touched upon *fully responsive* layouts and the [`FlexBox`](../../reference/layouts/FlexBox.ipynb):

- `sizing_mode`: Allows toggling between fixed sizing and responsive sizing along vertical and/or horizontal dimensions.
- `width`/`height`:  Allows setting a fixed width or height
- `min_width`/`min_height`: Allows setting a minimum width or height, if responsive sizing is set along the corresponding dimension.
- `max_width`/`max_height` : Allows setting a maximum width or height, if responsive sizing is set along the corresponding dimension.

## Resources

### Tutorials

- [Control the Size (intermediate)](../intermediate/size.md)

### How-to

- [Control Size](../../how_to/layout/size.md)
