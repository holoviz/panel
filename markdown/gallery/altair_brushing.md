# Altair Brushing

```python
import altair as alt
import pandas as pd
import panel as pn
import panel_material_ui as pmui

pn.extension('vega')
```

This example demonstrates how to leverage the brushing/linked-selections support in the Vega pane to update a table.

```python
df = pd.read_json("https://raw.githubusercontent.com/vega/vega/master/docs/data/penguins.json")

brush = alt.selection_interval(name='brush')  # selection of type "interval"

chart = alt.Chart(df).mark_point().encode(
    x=alt.X('Beak Length (mm):Q', scale=alt.Scale(zero=False)),
    y=alt.Y('Beak Depth (mm):Q', scale=alt.Scale(zero=False)),
    color=alt.condition(brush, 'Species:N', alt.value('lightgray'))
).properties(
    width=300,
    height=300
).add_params(
    brush
)

vega_pane = pn.pane.Vega(chart, debounce=10)

def filtered_table(selection):
    if not selection:
        return df.iloc[:0]
    query = ' & '.join(
        f'{crange[0]:.3f} <= `{col}` <= {crange[1]:.3f}'
        for col, crange in selection.items()
    )
    return df.query(query)

description = pn.pane.Markdown(
    'Select points on the plot and watch the linked table update.',
    sizing_mode='stretch_width'
)

table = pn.pane.DataFrame(
    pn.bind(filtered_table, vega_pane.selection.param.brush),
    height=350,
    sizing_mode="stretch_width",
)

output = pn.Row(vega_pane, table)

output    
```

### Served App

```python
if pn.state.served:
    pmui.Page(
        main=[description, output],
        title="Altair Brushing"
    ).servable()
```
