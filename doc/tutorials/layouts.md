# Layouts

:::{note} Tutorial 5. **Layout**
:icon: false

#### Sizing and Responsiveness

Panel builds on Bokeh which has a CSS based layout engine, while you can fall back to using explicit CSS to lay out components, it has a higher-level abstraction that makes it possible to build both fixed size and responsive layouts easily.

The main sizing related options that you should know are:

`width`/`height`
: Allows setting a fixed width or height

`sizing_mode`
: Allows toggling between fixed sizing and responsive sizing along vertical and/or horizontal dimensions

`min_width`/`min_height`
: Allows setting a minimum width or height, if responsive sizing is set along the corresponding dimension.

`max_width`/`max_height`
: Allows setting a maximum width or height, if responsive sizing is set along the corresponding dimension.
:::

```{pyodide}
import panel as pn
pn.extension('tabulator')
```

## Inherent and absolute sizing

Many components you might want to display have an inherent size, e.g. take some text, based on the font-size and the content of the text it will take up a certain amount of space. When you render it it will fill the available space and wrap if necessary:

```{pyodide}
lorem_ipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

pn.panel(lorem_ipsum)
```

By restricting the width, we can force it to rewrap and it will have a different inherent height.

```{pyodide}
pn.panel(lorem_ipsum, width=300)
```

Explicitly setting both width and height will force the resulting display to scroll to ensure that it is not cut off:

```{pyodide}
pn.panel(lorem_ipsum, width=300, height=100)
```

## Responsive sizing

The `sizing_mode` option can be used to toggle responsiveness in the width or height dimension or both. To see the effect of this we will create a fixed size container that we place the components into:

```{pyodide}
width_responsive = pn.Spacer(styles={'background': 'red'}, sizing_mode='stretch_width', height=200)

pn.Column(width_responsive, width=400, height=400, styles={'border': '1px solid black'})
```

```{pyodide}
height_responsive = pn.Spacer(styles={'background': 'green'}, sizing_mode='stretch_height', width=200)

pn.Column(height_responsive, width=400, height=400, styles={'border': '1px solid black'})
```

```{pyodide}
both_responsive = pn.Spacer(styles={'background': 'blue'}, sizing_mode='stretch_both')

pn.Column(both_responsive, width=400, height=400, styles={'border': '1px solid black'})
```

### Exercise

Arrange the Markdown pane and Bokeh figure such that they fully fill the available space but also ensure that the text never shrinks below 200 pixels and never grows above 500 pixels in width.

```{pyodide}
import numpy as np

from bokeh.plotting import figure

md = pn.pane.Markdown(lorem_ipsum, ) # <-- Add options here
fig = figure() # <-- and here

xs = np.linspace(0, 10)
ys = np.sin(xs)

fig.line(xs, ys)

pn.Row(fig, md, height=500, sizing_mode='stretch_width')
```

## True Responsive Layouts

So far when we have talked about responsive layouts we have primarily focused on simple width/height responsiveness of individual components, i.e. whether they will grow and shrink to fill the available space. For a truly responsive experience however we will need responsive layouts that will reflow the content depending on the size of the screen, browser window or the container they are placed inside of, much like how text wraps when there is insufficient width to accommodate it:

Panel offers one such component out of the box, the `FlexBox` layout.

```{pyodide}
import random

pn.FlexBox(*(pn.Spacer(height=100, width=random.randint(1, 4)*100, styles={'background': 'indianred'}, margin=5) for _ in range(10)))
```

`FlexBox` is based on [CSS Flexbox](https://css-tricks.com/snippets/css/a-guide-to-flexbox/) and supports many of the same options, such as setting `flex_direction`, `flex-wrap`, `align_items` and `align_content`.

```{pyodide}
pn.FlexBox(*(pn.Spacer(height=random.randint(1, 2)*100, width=random.randint(1, 4)*100, styles={'background': 'indianred'}, margin=5) for _ in range(10)),
           align_items='center')
```

### Distributing proportions

To achieve more complex layouts, i.e. specific proportions between different components we can use the `flex` property on the children of our `FlexBox`, e.g. here we declare that the green Spacer should be three times as wide as the red and blue components.

```{pyodide}
red = pn.Spacer(height=200, styles={'background': 'red', 'flex': '1 1 auto'})
green = pn.Spacer(height=200, styles={'background': 'green', 'flex': '3 1 auto'})
blue = pn.Spacer(height=200, styles={'background': 'blue', 'flex': '1 1 auto'})

pn.FlexBox(red, green, blue)
```

To learn more about this read [this guide on controlling ratios of flex items](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_flexible_box_layout/Controlling_ratios_of_flex_items_along_the_main_axis).

#### Exercise

Using only the `flex` property inside `styles` of the two plots, distribute the two plots and the text such that the plots are both 3 times wider than the text, then center the text vertically.

```{pyodide}
xs = np.linspace(0, 10)

sin_fig = figure(height=400, width=None, styles={'flex': '3 1 auto'})
sin_fig.line(xs, np.sin(xs))

cos_fig = figure(height=400, width=None, styles={'flex': '3 1 auto'})
cos_fig.line(xs, np.cos(xs))

text = pn.pane.Markdown(lorem_ipsum, styles={'flex': '1 1 0'})

pn.FlexBox(sin_fig, text, cos_fig)
```

### Media queries

To achieve layouts depending on the overall screen/browser width, e.g. to have a different layout depending on whether we are working on a desktop or a mobile we can use media queries. Media queries allow us to apply different rules depending on a `min-width` or `max-width`, e.g. the example below will force the flexbow into a column layout when the viewport is below a size of 1200px:

```{pyodide}
red = pn.Spacer(height=200, width=400, styles={'background': 'red'})
green = pn.Spacer(height=200, width=400, styles={'background': 'green'})
blue = pn.Spacer(height=200, width=400, styles={'background': 'blue'})

media_query = """
@media screen and (max-width: 1200px) {
  div[id^="flexbox"] {
    flex-flow: column !important;
  }
}
"""

pn.FlexBox(red, green, blue, stylesheets=[media_query])
```

### Exercise

This exercise is a bit more free-form, the aim will be simply to generate a layout that is both responsive and visually pleasing. We'll start by declaring the data pipeline that will feed our components:

```{pyodide}
import holoviews as hv
import hvplot.pandas
import pandas as pd

data_url = 'https://datasets.holoviz.org/windturbines/v1/windturbines.parq'

df = pn.rx(pd.read_parquet(data_url))

CARD_STYLE = """
:host {
  box-shadow: rgba(50, 50, 93, 0.25) 0px 6px 12px -2px, rgba(0, 0, 0, 0.3) 0px 3px 7px -3px;
  padding: 5px 10px;
}"""

manufacturers = pn.widgets.MultiChoice(options=df.t_manu.unique().rx.pipe(list), name='Manufacturer')
year = pn.widgets.IntRangeSlider(start=df.p_year.min().rx.pipe(int), end=df.p_year.max().rx.pipe(int), name='Year')
columns = ['p_name', 't_state', 't_county', 'p_year', 't_manu', 'p_cap']

filtered = df[columns][df.t_manu.isin(manufacturers.rx.where(manufacturers, df.t_manu.unique())) & df.p_year.between(*year.rx())]
```

Now we'll declare all the individual components and put them in a column. Use everything you've learned to find a responsive and aesthetically pleasing layout:

```{pyodide}
count = pn.indicators.Number(name='Turbine Count', value=filtered.rx.len(), format='{value:,d} TWh', stylesheets=[CARD_STYLE])
total_cap = pn.indicators.Number(name='Total Capacity', value=filtered.p_cap.mean(), format='{value:.2f} TWh', stylesheets=[CARD_STYLE])
modal_year = pn.indicators.Number(name='Modal Year', value=filtered.p_year.mode().iloc[0], stylesheets=[CARD_STYLE])

widgets = pn.Column(manufacturers, year, stylesheets=[CARD_STYLE], margin=10)
table = pn.widgets.Tabulator(filtered, stylesheets=[CARD_STYLE], max_width=500)

year_hist = filtered.hvplot.hist(y='p_year', responsive=True, max_width=300, height=312)
cap_hist = filtered.hvplot.hist(y='p_cap', responsive=True, max_width=300, height=312)

plots = pn.Column(hv.DynamicMap(cap_hist), hv.DynamicMap(year_hist), stylesheets=[CARD_STYLE], max_width=400, margin=5)

pn.Column(count, total_cap, modal_year, widgets, table, plots)
```
