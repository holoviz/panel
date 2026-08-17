# Penguin Crossfilter

```python
import numpy as np
import pandas as pd
import panel as pn
import panel_material_ui as pmui

import holoviews as hv
import hvplot.pandas # noqa

pn.extension()
```

## Introduction

```python
welcome = "## Welcome and meet the Palmer penguins!"

penguins_art = pn.pane.PNG('https://raw.githubusercontent.com/allisonhorst/palmerpenguins/main/man/figures/palmerpenguins.png', height=160)

credit = "### Artwork by @allison_horst"

instructions = """
Use the box-select and lasso-select tools to select a subset of penguins
and reveal more information about the selected subgroup through the power
of cross-filtering.
"""

license = """
### License

Data are available by CC-0 license in accordance with the Palmer Station LTER Data Policy and the LTER Data Access Policy for Type I data."
"""

art = pn.Column(
    welcome, penguins_art, credit, instructions, license,
    sizing_mode='stretch_width'
)

art
```

## Building some plots

Let us first load the Palmer penguin dataset ([Gorman et al.](https://allisonhorst.github.io/palmerpenguins/)) which contains measurements about a number of penguin species:

```python
penguins = pd.read_csv('https://datasets.holoviz.org/penguins/v1/penguins.csv')
penguins = penguins[~penguins.sex.isnull()].reset_index().sort_values('species')

penguins.head()
```

Next we will set up a linked selections instance that will allow us to perform cross-filtering on the plots we will create in the next step:

```python
ls = hv.link_selections.instance()

def count(selected):
    return f"## {len(selected)}/{len(penguins)} penguins selected"

selected = pmui.Typography(
    pn.bind(count, ls.selection_param(penguins)),
    disable_anchors=True,
    sx={"color": "var(--mui-palette-primary-main);"},
    styles={"margin-left": "auto"}
)

selected
```

Now we can start plotting the data with hvPlot, which provides a familiar API to pandas `.plot` users but generates interactive plots and use the linked selections object to allow cross-filtering across the plots:

```python
colors = {
    'Adelie': '#1f77b4',
    'Gentoo': '#ff7f0e',
    'Chinstrap': '#2ca02c'
}

scatter = penguins.hvplot.points(
    'bill_length_mm', 'bill_depth_mm', c='species',
    cmap=colors, responsive=True, min_height=300
)

histogram = penguins.hvplot.hist(
    'body_mass_g', by='species', color=hv.dim('species').categorize(colors),
    legend=False, alpha=0.5, responsive=True, min_height=300
)

bars = penguins.hvplot.bar(
    'species', 'index', c='species', cmap=colors,
    responsive=True, min_height=300, ylabel=''
).aggregate(function=np.count_nonzero)

violin = penguins.hvplot.violin(
    'flipper_length_mm', by=['species', 'sex'], cmap='Category20',
    responsive=True, min_height=300, legend='bottom_right'
).opts(split='sex')

plots = pn.pane.HoloViews(
    ls(scatter.opts(show_legend=False) + bars + histogram + violin).opts(sizing_mode='stretch_both').cols(2)
)

plots
```

### Served App

```python
if pn.state.served:
    pmui.Page(
        header=[selected],
        main=[plots],
        sidebar=[art],
        logo='https://github.com/allisonhorst/palmerpenguins/raw/main/man/figures/logo.png',
        title="Palmer Penguins"
    ).servable()
```
