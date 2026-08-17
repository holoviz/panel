# Glaciers

```python
import numpy as np
import pandas as pd
import holoviews as hv
import panel as pn
import panel_material_ui as pmui

from colorcet import bmy

pn.extension('tabulator')
import hvplot.pandas
```

## Create intro

```python
instruction = pn.pane.Markdown("""
This dashboard visualizes all global glaciers and allows exploring the relationships
between their locations and variables such as their elevation, temperature and annual
precipitation.<br><br>Box- or lasso-select on each plot to subselect and hit the 
"Clear selection" button to reset. See the notebook source code for how to build apps
like this!""", width=600)

panel_logo = pn.pane.PNG(
    'https://panel.holoviz.org/_static/logo_stacked.png',
    link_url='https://panel.holoviz.org', height=95, align='center'
)

oggm_logo = pn.pane.PNG(
    'https://raw.githubusercontent.com/OGGM/oggm/master/docs/_static/logos/oggm_s_alpha.png',
    link_url='https://oggm.org/', height=100, align='center'
)

intro = pn.Row(
    oggm_logo,
    instruction,
    pn.layout.HSpacer(),
    panel_logo,
    sizing_mode='stretch_width'
)

intro
```

### Load and cache data

```python
from holoviews.element.tiles import lon_lat_to_easting_northing

@pn.cache
def load_data():
    df = pd.read_parquet('https://datasets.holoviz.org/oggm_glaciers/v1/oggm_glaciers.parq')
    df['latdeg'] = df.cenlat
    df['x'], df['y'] = lon_lat_to_easting_northing(df.cenlon, df.cenlat)
    return df

df = load_data()

df.tail()
```

### Set up linked selections

```python
ls = hv.link_selections.instance()

def clear_selections(event):
    ls.selection_expr = None

clear_button = pmui.Button(label='Clear selection', align='center')

clear_button.param.watch(clear_selections, 'clicks');

total_area = df.area_km2.sum()

def count(data):
    selected_area  = np.sum(data['area_km2'])
    selected_percentage = selected_area / total_area * 100
    return f'## Glaciers selected: {len(data)} | Area: {selected_area:.0f} km² ({selected_percentage:.1f}%)</font>'

header = pn.Row(
    pmui.Typography(
        pn.bind(count, ls.selection_param(df)),
        align='center',
        sizing_mode="stretch_width",
        sx={"color": "var(--mui-palette-primary-main);"}
    ),
    clear_button
)

header
```

### Create plots

```python
geo = df.hvplot.points(
    'x', 'y', rasterize=True, tools=['hover'], tiles='ESRI', cmap=bmy, logz=True, colorbar=True,
    xaxis=None, yaxis=False, ylim=(-7452837.583633271, 6349198.00989753), min_height=400, responsive=True
).opts('Tiles', alpha=0.8)

scatter = df.hvplot.scatter(
    'avg_prcp', 'mean_elev', rasterize=True, fontscale=1.2, grid=True,
    xlabel='Avg. Precipitation', ylabel='Elevation', responsive=True, min_height=400
)

temp = df.hvplot.hist(
    'avg_temp_at_mean_elev', fontscale=1.2, responsive=True, min_height=350, fill_color='#85c1e9'
)

precipitation = df.hvplot.hist(
    'avg_prcp', fontscale=1.2, responsive=True, min_height=350, fill_color='#f1948a'
)

plots = pn.pane.HoloViews(ls(geo + scatter + temp + precipitation).cols(2).opts(sizing_mode='stretch_both'))
plots
```

## Served App

```python
if pn.state.served:
    pmui.Page(
        header=[header],
        main=[intro, plots],
        title="OGGM"
    ).servable()
```
