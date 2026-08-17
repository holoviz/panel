# Windturbines

```python
import holoviews as hv
import panel as pn
import panel_material_ui as pmui
import pandas as pd

pn.extension('vizzu', 'tabulator')
import hvplot.pandas
```

## Load data

```python
windturbines = pn.state.as_cached(
    'windturbines',
    pd.read_parquet,
    path='https://datasets.holoviz.org/windturbines/v1/windturbines.parq'
)

windturbines.head()
```

## Plot data

```python
def data(df, groupby, quant):
    if quant == 'Count':
        return df.value_counts(groupby).to_frame(name='Count').sort_index().reset_index().iloc[:50]
    else:
        return df.groupby(groupby)[quant].sum().reset_index().iloc[:50]

def config(chart_type, groupby, quant):
    if chart_type == 'Bubble':
        return {
            "channels": {
                "x": None,
                "y": None,
                "color": groupby,
                "label": groupby,
                "size": quant
            },
            'geometry': 'circle'
        }
    else:
        return {
            "channels": {
                "x": groupby,
                "y": quant,
                "color": None,
                "label": None,
                "size": None
            },
            'geometry': 'rectangle'
        }
    
ls = hv.link_selections.instance()

geo = ls(windturbines.hvplot.points(
    'easting', 'northing', xaxis=None, yaxis=None, rasterize=True,
    tiles='CartoLight', responsive=True, dynspread=True,
    height=500, cnorm='log', cmap='plasma', xlim=(-14000000, -8000000),
    ylim=(3000000, 6500000)
))
    
groupby = pmui.RadioButtonGroup(
    options={'State': 't_state', 'Year': 'p_year', 'Manufacturer': 't_manu'}, align='center', margin=0
)
chart_type = pmui.RadioButtonGroup(
    options=['Bar', 'Bubble'], align='center', margin=0
)
quant = pmui.RadioButtonGroup(
    options={'Count': 'Count', 'Capacity': 'p_cap'}, align='center', margin=0
)
lsdata = ls.selection_param(windturbines)

vizzu = pn.pane.Vizzu(
    pn.bind(data, lsdata, groupby, quant),
    config=pn.bind(config, chart_type, groupby, quant),
    column_types={'p_year': 'dimension'},
    style={
        "plot": {
            "xAxis": {
                "label": {
                    "angle": "-45deg"
                }
            }
        }
    },
    sizing_mode='stretch_both'
)

def format_df(df):
    df = df[['t_state', 't_county', 'p_name', 'p_year', 't_manu', 't_cap']]
    return df.rename(
        columns={col: col.split('_')[1].title() for col in df.columns}
    )

table = pn.widgets.Tabulator(
    pn.bind(format_df, lsdata), page_size=8, pagination='remote',
    show_index=False,
)

format_header = lambda text: (
    pmui.Typography(
        text, disable_anchors=True, sx={"color": "var(--mui-palette-primary-main);"}
    )
)

header = pmui.Row(
    quant,
    format_header("# by"),
    groupby,
    format_header("# as a"),
    chart_type,
    format_header("# chart"),
    margin=(0, 0, 0, 10)
)

main = pn.Column(
    pn.Row(geo, table),
    vizzu, min_height=1000,
    sizing_mode='stretch_both'
)

pn.Column(header, main)
```

### Served App

```python
if pn.state.served:
    pmui.Page(
        header=[header],
        main=[main],
        title="Windturbines"
    ).servable()
```
