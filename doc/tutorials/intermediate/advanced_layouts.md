# Advanced Layouts

## Responsive Layouts with FlexBox

So far when we have talked about responsive layouts we have primarily focused on simple `width`/`height` responsiveness of individual components, i.e. whether they will grow and shrink to fill the available space. For a truly responsive experience however we will need responsive layouts that will reflow the content depending on the size of the screen, browser window or the container they are placed inside of, much like how text wraps when there is insufficient width to accommodate it:

Panel offers one such component out of the box, the [`FlexBox`](../../reference/layouts/FlexBox.md) layout.

```{pyodide}
import panel as pn
pn.extension('tabulator')
```

```{pyodide}
import panel as pn
import random

pn.extension()

def create_random_spacer():
    return pn.ui.Spacer(
        height=100,
        width=random.randint(1, 4) * 100,
        styles={"background": "teal"},
        margin=5,
    )
spacers = [create_random_spacer() for _ in range(10)]

pn.ui.FlexBox(*spacers).servable()
```

`FlexBox` is based on [CSS Flexbox](https://css-tricks.com/snippets/css/a-guide-to-flexbox/) and supports many of the same options, such as setting `flex_direction`, `flex-wrap`, `align_items` and `align_content`.

```{pyodide}
import panel as pn
import random

pn.extension()

def create_random_spacer():
    return pn.ui.Spacer(
        height=random.randint(1, 2) * 100,
        width=random.randint(1, 4) * 100,
        styles={"background": "teal"},
        margin=5,
    )
spacers = [create_random_spacer() for _ in range(10)]

pn.ui.FlexBox(*spacers, align_items="center").servable()
```

### Distributing proportions

To achieve more complex layouts, i.e. specific proportions between different components we can use the `flex` property on the children of our `FlexBox`, e.g. here we declare that the green Spacer should be three times as wide as the red and blue components.

```{pyodide}
import panel as pn

pn.extension()

red = pn.ui.Spacer(height=200, styles={'background': 'red', 'flex': '1 1 auto'})
green = pn.ui.Spacer(height=200, styles={'background': 'green', 'flex': '3 1 auto'})
blue = pn.ui.Spacer(height=200, styles={'background': 'blue', 'flex': '1 1 auto'})

pn.ui.FlexBox(red, green, blue).servable()
```

To learn more about this read [this guide on controlling ratios of flex items](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_flexible_box_layout/Controlling_ratios_of_flex_items_along_the_main_axis).

### Exercise

Using only the `styles` of the components, distribute the two `dataframe`s and the `markdown` such that the `dataframe`s are both 3 times wider than the `markdown`, then center the `markdown` vertically.

You might find inspiration in [this guide on aligning items in a flex container](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_flexible_box_layout/Aligning_items_in_a_flex_container).

```{pyodide}
import pandas as pd
import panel as pn

pn.extension()

text = """A *wind turbine* is a renewable energy device that converts the kinetic energy from wind into electricity."""
wind_speed = pd.DataFrame(
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

dataframe_1 = pn.ui.DataFrame(wind_speed, styles={'flex': '3 1 auto'})
markdown = pn.ui.Markdown(text, styles={'flex': '3 1 auto'})
dataframe_2 = pn.ui.DataFrame(wind_speed, styles={'flex': '3 1 auto'})

pn.ui.FlexBox(dataframe_1, markdown, dataframe_2).servable()
```

:::{dropdown} Solution

```{pyodide}
import pandas as pd
import panel as pn

pn.extension()

text = """A *wind turbine* is a renewable energy device that converts the kinetic energy from wind into electricity."""
wind_speed = pd.DataFrame(
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

dataframe_1 = pn.ui.DataFrame(wind_speed, styles={'flex': '3 1 auto'})
markdown = pn.ui.Markdown(text, styles={'flex': '1 1 0', "align-self": "center"})
dataframe_2 = pn.ui.DataFrame(wind_speed, styles={'flex': '3 1 auto'})

pn.ui.FlexBox(dataframe_1, markdown, dataframe_2).servable()
```

:::

:::{note}
Getting the `FlexBox` `styles` right can be tricky. If you need help try posting a [minimum, reproducible example](https://stackoverflow.com/help/minimal-reproducible-example) on [Discourse](https://discourse.holoviz.org/).
:::

### Media queries

To achieve layouts depending on the overall screen/browser width, e.g. to have a different layout depending on whether we are working on a desktop or a mobile we can use *media queries*. Media queries allow us to apply different rules depending on a `min-width` or `max-width`. The `pn.ui.FlexBox` accepts them as part of its `sx` styling dictionary, e.g. the example below will force the flexbox into a column layout when the viewport is below a size of 1200px:

```{pyodide}
import panel as pn

pn.extension()


red = pn.ui.Spacer(height=200, width=400, styles={'background': 'red'})
green = pn.ui.Spacer(height=200, width=400, styles={'background': 'green'})
blue = pn.ui.Spacer(height=200, width=400, styles={'background': 'blue'})

media_query = {
    "@media (max-width: 1200px)": {"flexDirection": "column"}
}

pn.ui.FlexBox(red, green, blue, sx=media_query).servable()
```

Try changing your browser width to see how the layout changes from row based to column based.

### Exercise: Challenge

This exercise is a bit more free-form and can be solved in many ways.

Please generate a layout that is both responsive and visually pleasing starting from the below code.

```{pyodide}
import panel as pn
import holoviews as hv
import hvplot.pandas
import pandas as pd

pn.extension('tabulator', throttled=True)

data_url = 'https://assets.holoviz.org/panel/tutorials/turbines.csv.gz'

@pn.cache
def get_data():
    return pd.read_csv(data_url)

df = pn.rx(get_data())

CARD_STYLE = """
:host {
  box-shadow: rgba(50, 50, 93, 0.25) 0px 6px 12px -2px, rgba(0, 0, 0, 0.3) 0px 3px 7px -3px;
  padding: 5px 10px;
}"""

manufacturers = pn.ui.MultiChoice(options=df.t_manu.unique().rx.pipe(list), label='Manufacturer')
year = pn.ui.IntRangeSlider(start=df.p_year.min().rx.pipe(int), end=df.p_year.max().rx.pipe(int), label='Year')
columns = ['p_name', 't_state', 't_county', 'p_year', 't_manu', 'p_cap', 't_cap']

filtered = df[columns][df.t_manu.isin(manufacturers.rx.where(manufacturers, df.t_manu.unique())) & df.p_year.between(*year.rx())]

count = pn.ui.Number(label='Turbine Count', value=filtered.rx.len(), format='{value:,d}', stylesheets=[CARD_STYLE])
total_cap = pn.ui.Number(label='Total Capacity', value=filtered.t_cap.sum() / 1e6, format='{value:,.2f} GW', stylesheets=[CARD_STYLE])
modal_year = pn.ui.Number(label='Modal Year', value=filtered.p_year.mode().iloc[0], format='{value:.0f}', stylesheets=[CARD_STYLE])

widgets = pn.ui.Column(manufacturers, year, stylesheets=[CARD_STYLE], margin=10)
table = pn.ui.Tabulator(filtered, stylesheets=[CARD_STYLE], max_width=500)

year_hist = filtered.hvplot.hist(y='p_year', responsive=True, max_width=300, height=312)
cap_hist = filtered.hvplot.hist(y='p_cap', responsive=True, max_width=300, height=312)

plots = pn.ui.Column(hv.DynamicMap(cap_hist), hv.DynamicMap(year_hist), stylesheets=[CARD_STYLE], max_width=400, margin=5)

pn.ui.Column(count, total_cap, modal_year, widgets, table, plots).servable()
```

:::{dropdown} Solution

This is just an example solution. The exercise can be solved in many ways.

Here we use a `pn.ui.Grid`, which arranges its items in a 12 column grid. The `size` of each item declares how many columns it spans at a given breakpoint (`xs`, `sm`, `md`, `lg` and `xl`), so the filters and indicators share a row on wide screens and stack on narrow ones, while the table and the plots sit side by side only on large screens.

```{pyodide}
import panel as pn
import holoviews as hv
import hvplot.pandas
import pandas as pd

pn.extension('tabulator', throttled=True)

data_url = 'https://assets.holoviz.org/panel/tutorials/turbines.csv.gz'

@pn.cache
def get_data():
    return pd.read_csv(data_url)

df = pn.rx(get_data())

CARD_STYLE = """
:host {
  box-shadow: rgba(50, 50, 93, 0.25) 0px 6px 12px -2px, rgba(0, 0, 0, 0.3) 0px 3px 7px -3px;
  padding: 5px 10px;
}"""

manufacturers = pn.ui.MultiChoice(options=df.t_manu.unique().rx.pipe(list), label='Manufacturer')
year = pn.ui.IntRangeSlider(start=df.p_year.min().rx.pipe(int), end=df.p_year.max().rx.pipe(int), label='Year')
columns = ['p_name', 't_state', 't_county', 'p_year', 't_manu', 'p_cap', 't_cap']

filtered = df[columns][df.t_manu.isin(manufacturers.rx.where(manufacturers, df.t_manu.unique())) & df.p_year.between(*year.rx())]

count = pn.ui.Number(label='Turbine Count', value=filtered.rx.len(), format='{value:,d}', font_size='28pt', stylesheets=[CARD_STYLE], sizing_mode='stretch_width')
total_cap = pn.ui.Number(label='Total Capacity', value=filtered.t_cap.sum() / 1e6, format='{value:,.2f} GW', font_size='28pt', stylesheets=[CARD_STYLE], sizing_mode='stretch_width')
modal_year = pn.ui.Number(label='Modal Year', value=filtered.p_year.mode().iloc[0], format='{value:.0f}', font_size='28pt', stylesheets=[CARD_STYLE], sizing_mode='stretch_width')

widgets = pn.ui.Column(manufacturers, year, stylesheets=[CARD_STYLE], sizing_mode='stretch_width')
table = pn.ui.Tabulator(filtered, pagination='remote', page_size=10, stylesheets=[CARD_STYLE], sizing_mode='stretch_width')

year_hist = filtered.hvplot.hist(y='p_year', responsive=True, height=300)
cap_hist = filtered.hvplot.hist(y='p_cap', responsive=True, height=300)

plots = pn.ui.Column(hv.DynamicMap(cap_hist), hv.DynamicMap(year_hist), stylesheets=[CARD_STYLE], sizing_mode='stretch_width')

pn.ui.Grid(
    pn.ui.Grid(widgets, size={'xs': 12, 'md': 3}),
    pn.ui.Grid(count, size={'xs': 12, 'sm': 4, 'md': 3}),
    pn.ui.Grid(total_cap, size={'xs': 12, 'sm': 4, 'md': 3}),
    pn.ui.Grid(modal_year, size={'xs': 12, 'sm': 4, 'md': 3}),
    pn.ui.Grid(table, size={'xs': 12, 'lg': 7}),
    pn.ui.Grid(plots, size={'xs': 12, 'lg': 5}),
    container=True,
    spacing=2,
    sizing_mode='stretch_width',
).servable()
```

:::
