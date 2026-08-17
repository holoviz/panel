# Vega
---
```python
import pandas as pd
import panel as pn

pn.extension('vega')
```

The ``Vega`` pane renders Vega-based plots (including those from Altair) inside a panel. It optimizes plot rendering by using binary serialization for any array data found in the Vega/Altair object, providing significant speedups over the standard JSON serialization employed by Vega natively. Note that to use the ``Vega`` pane in the notebook, the Panel extension must be loaded with 'vega' as an argument to ensure that vega.js is initialized.

#### Parameters:

For details on other options for customizing the component, see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``debounce``** (int or dict): The debounce timeout to apply to selection events, either specified as a single integer value (in milliseconds) or a dictionary that declares a debounce value per event. Debouncing ensures that events are only dispatched N milliseconds after a user is done interacting with the plot.
* **``object``** (dict or altair Chart): Either a dictionary containing a Vega or Vega-Lite plot specification, or an Altair Chart.
* **``show_actions``** (boolean): Whether to show the chart actions menu, such as save, edit, etc.
* **``theme``** (str): A theme to apply to the plot. Must be one of 'excel', 'ggplot2', 'quartz', 'vox', 'fivethirtyeight', 'dark', 'latimes', 'urbaninstitute', 'googlecharts', 'powerbi', 'carbonwhite', 'carbong10', 'carbong90', or 'carbong100'.

Readonly parameters:

* **``selection``** (Selection): The Selection object exposes parameters that reflect the selections declared on the plot into Python.

___

The ``Vega`` pane supports both `vega` and `vega-lite` specifications, which may be provided in raw form (i.e., a dictionary) or by defining an ``altair`` plot.

---

### Vega and Vega-lite

To display ``vega`` and ``vega-lite`` specification simply construct a ``Vega`` pane directly or pass it to ``pn.panel``:

```python
vegalite = {
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {"url": "https://raw.githubusercontent.com/vega/vega/master/docs/data/barley.json"},
  "mark": "bar",
  "encoding": {
    "x": {"aggregate": "sum", "field": "yield", "type": "quantitative"},
    "y": {"field": "variety", "type": "nominal"},
    "color": {"field": "site", "type": "nominal"}
  }
}
vgl_pane = pn.pane.Vega(vegalite, height=240)
vgl_pane
```

Like all other panes, the ``Vega`` pane ``object`` can be updated, either in place and triggering an update:

```python
vegalite['mark'] = 'area'
vgl_pane.param.trigger('object')
```

or by replacing the ``object`` entirely:

```python
vega_disasters = {
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {
    "url": "https://raw.githubusercontent.com/vega/vega/master/docs/data/disasters.csv"
  },
  "width": 600,
  "height": 400,
  "transform": [
    {"filter": "datum.Entity !== 'All natural disasters'"}
  ],
  "mark": {
    "type": "circle",
    "opacity": 0.8,
    "stroke": "black",
    "strokeWidth": 1
  },
  "encoding": {
    "x": {
        "field": "Year",
        "type": "quantitative",
        "axis": {"labelAngle": 90},
        "scale": {"zero": False}
    },
    "y": {
        "field": "Entity",
        "type": "nominal",
        "axis": {"title": ""}
    },
    "size": {
      "field": "Deaths",
      "type": "quantitative",
      "legend": {"title": "Annual Global Deaths", "clipHeight": 30},
      "scale": {"range": [0, 5000]}
    },
    "color": {"field": "Entity", "type": "nominal", "legend": None}
  }
}
vgl_pane.object = vega_disasters
```

Lets reset the plot back to the original:

```python
vgl_pane.object = vegalite
```

#### Exporting

You can export the current Vega or Vega-Lite specification using the pane's `export` method.

Supported output formats include:

- 'png' (`Image`)
- 'jpeg' (`Image`)
- 'svg' (`SVG`)
- 'pdf' (`PDF`)
- 'html' (`HTML`)
- 'url' (`HTML` to Vega Editor)
- 'scenegraph' (`JSON`)

Requires `vl-convert`, i.e. `pip install vl-convert-python`.

```python
vgl_pane.export('svg')
```

Additional kwargs may be passed to the [`vl-convert` functions](https://github.com/jonmmease/vl-convert/tree/main).

To cast to a pane, use `as_pane=True`.

```python
vgl_pane.export('png', scale=2, ppi=300, as_pane=True)
```

#### Responsive Sizing

The `vega-lite` specification can also be responsively sized by declaring the width or height to match the container:

```python
responsive_spec = dict(vega_disasters, width='container', title="Responsive Plot")

vgl_responsive_pane = pn.pane.Vega(responsive_spec)
vgl_responsive_pane
```

Please note that the `vega` specification does not support setting `width` and `height` to `container`.

#### DataFrame Data Values

For convenience we support a Pandas DataFrame as `data` `values`:

```python
dataframe_spec = {
    "title": "A Simple Bar Chart from a Pandas DataFrame",
    'config': {
        'mark': {'tooltip': None},
        'view': {'height': 200, 'width': 500}
    },
    'data': {'values': pd.DataFrame({'x': ['A', 'B', 'C', 'D', 'E'], 'y': [5, 3, 6, 7, 2]})},
    'mark': 'bar',
    'encoding': {'x': {'type': 'ordinal', 'field': 'x'},
                 'y': {'type': 'quantitative', 'field': 'y'}},
    '$schema': 'https://vega.github.io/schema/vega-lite/v3.2.1.json'
}
pn.pane.Vega(dataframe_spec)
```

### Altair

A more convenient way of defining a Vega chart is to declare it using [altair](https://altair-viz.github.io), which provides a declarative API on top of vega-lite. The ``Vega`` pane will automatically render the Vega-Lite spec when passed an Altair chart:

```python
import altair as alt
from vega_datasets import data

cars = data.cars()

chart = alt.Chart(cars).mark_circle(size=60).encode(
    x='Horsepower',
    y='Miles_per_Gallon',
    color='Origin',
    tooltip=['Name', 'Origin', 'Horsepower', 'Miles_per_Gallon']
).interactive()

altair_pane = pn.panel(chart)
altair_pane
```

The Altair chart can also be updated by updating the pane ``object``:

```python
altair_pane.object = chart.mark_circle(size=100)
```

All the usual layouts and composition operators that Altair supports can also be rendered:

```python
penguins_url = "https://raw.githubusercontent.com/vega/vega/master/docs/data/penguins.json"

chart1 = alt.Chart(penguins_url).mark_point().encode(
    x=alt.X('Beak Length (mm):Q', scale=alt.Scale(zero=False)),
    y=alt.Y('Beak Depth (mm):Q', scale=alt.Scale(zero=False)),
    color='Species:N'
).properties(
    height=300,
    width=300,
)

chart2 = alt.Chart(penguins_url).mark_bar().encode(
    x='count()',
    y=alt.Y('Beak Depth (mm):Q', bin=alt.Bin(maxbins=30)),
    color='Species:N'
).properties(
    height=300,
    width=100
)

pn.panel(chart1 | chart2)
```

### Selections

The `Vega` pane automatically syncs any selections expressed on the Vega/Altair chart. Three types of selections are currently supported:

- `selection_interval`: Allows selecting a intervals using a box-select tool, returns data in the form of `{<x-axis-name: [xmin, xmax], <y-axis-name>: [ymin, ymax]}`
- `selection_single`: Allows selecting a single point using clicks, returns a list of integer indices
- `selection_multi`: Allows selecting a multiple points using (shift+) click, returns a list of integer indices.

#### Interval selection

As an example we can add an Altair `selection_interval` selection to our chart:

```python
import pandas as pd

df = pd.read_json(penguins_url)

brush = alt.selection_interval(name='brush')  # selection of type "interval"

chart = alt.Chart(penguins_url).mark_point().encode(
    x=alt.X('Beak Length (mm):Q', scale=alt.Scale(zero=False)),
    y=alt.Y('Beak Depth (mm):Q', scale=alt.Scale(zero=False)),
    color=alt.condition(brush, 'Species:N', alt.value('lightgray'))
).properties(
    width=250,
    height=250
).add_params(
    brush
)

vega_pane = pn.pane.Vega(chart, debounce=10)

vega_pane
```

Note we specified a single `debounce` value, if we declare multiple selections we can instead declare a debounce value per named event by specifying it as a dictionary, e.g. `debounce={'brush': 10, ...}`.

The named selection will now appear on the `.selection` sub-object:

```python
vega_pane.selection
```

By inspecting the JSON representation of the Altair chart we can see how to express these selections in vega(-lite):

```python
chart.to_dict()['params']
```

#### Single & multi-selection

Both single and multi-selection return the indices of the selected data as a list (in the case of single selection the list is always of length 0 or 1).

```python
multi = alt.selection_point(name='multi')  # selection of type "multi"

multi_chart = alt.Chart(penguins_url).mark_point().encode(
    x=alt.X('Beak Length (mm):Q', scale=alt.Scale(zero=False)),
    y=alt.Y('Beak Depth (mm):Q', scale=alt.Scale(zero=False)),
    color=alt.condition(multi, 'Species:N', alt.value('lightgray'))
).properties(
    width=250,
    height=250
).add_params(
    multi
)

vega_multi = pn.pane.Vega(multi_chart, debounce=10)

vega_multi
```

The `multi` value is now available on the `selection` object:

```python
vega_multi.selection
```

To apply the selection we can simply use the `.iloc` method on the pandas DataFrame containing our data (try tapping on one or more points above and re-running the cell below):

```python
df.iloc[vega_multi.selection.multi]
```

For more background see the [Altair](https://altair-viz.github.io/user_guide/interactions.html) documentation on available interactions.

#### Filtering a table via a selection

To filter a table via a chart selection we're first going to bind the `brush` selection to a function which filters the dataframe to display only the selected values in the table. To achieve this, we need to know that the selection returns a dictionary in the format `{'column_name': [min, max]}`, which for our Penguins examples can look like this:

```python
{'Beak Length (mm)': [51.824, 53.952], 'Beak Depth (mm)': [18.796, 18.904]}
```

To display the selected values in a table, we will use the selection dictionary to construct a pandas query string that can be used with `DataFrame.query()`. Finally we are returning both the query string and the filtered table in a Column:

```python
def filtered_table(selection):
    if not selection:
        return '## No selection'
    query = ' & '.join(
        f'{crange[0]:.3f} <= `{col}` <= {crange[1]:.3f}'
        for col, crange in selection.items()
    )
    return pn.Column(
        f'Query: {query}',
        pn.pane.DataFrame(df.query(query), width=600, height=300)
    )

pn.Row(vega_pane, pn.bind(filtered_table, vega_pane.selection.param.brush))
```

Note that this way of constructing the query string means that Panel currently supports filtering the table via the max and min values of the selection area but does not check whether there are actually points present in this area of the chart.

#### Filtering another chart via a selection

Altair already provides a syntax for filtering one chart based on the selection in another, but one limitation is that these charts need to be displayed in the same layout for the filtering to work. By using Panel to filter one Altair chart based on another, we can place the charts anywhere in our app and still have the filtering work as expected.

One way to filter a chart based on the selection in another chart, is to to use the same approach as above and create the second chart with the dataframe filtered via `.query`. Altair also provides a way to do the filtering directly with the `transform_filter` method instead of using pandas. In the example below, we are constructing a [composed](https://vega.github.io/vega-lite/docs/predicate.html#composition) [range predicate](https://vega.github.io/vega-lite/docs/predicate.html#range-predicate) from our selection object and passing it to the `transform_filter` method of the second chart.

```python
def bar_counts(selection):
    if not selection:
        return '## No selection'
    range_predicate = {
        'and': [{
            'field': key,
            'range': [selection[key][0], selection[key][1]]
        } for key in selection]
    }
    return alt.Chart(penguins_url, width=220).mark_bar().encode(
        x='count()',
        y='Species:N',
        color=alt.Color('Species:N', legend=None)
    ).transform_filter(
        range_predicate
    )

pn.Column(vega_pane, pn.bind(bar_counts, vega_pane.selection.param.brush))
```

#### Filtering categorical data via a selection

Selections on categorical columns ('nominal' and 'ordinal' in Altair) return all the selected values in a list rather than just the min and max of the selection interval. Therefore, we need to construct the query string as follows:

```python
query = ' & '.join([f'`{col}` in {values}' for col, values in selection.items()])
```

In the example below we first check the data type in the column and then use either the categorical and quantitative query string as appropriate, which allows us to filter on a combination on categorical and numerical data.

```python
chart = alt.Chart(df).mark_tick().encode(
    x=alt.X('Beak Length (mm):Q', scale=alt.Scale(zero=False)),
    y='Species:N',
    color=alt.condition(brush, 'Species:N', alt.value('lightgray'))
).add_params(
    brush
)

def filtered_table(selection):
    if not selection:
        return '## No selection'
    query = ' & '.join(
        f'{values[0]} <= `{col}` <= {values[1]}'
        if pd.api.types.is_numeric_dtype(df[col])
        else f'`{col}` in {values}' 
        for col, values in selection.items()
    )
    return pn.Column(
        f'Query: {query}',
        pn.pane.DataFrame(df.query(query), width=600, height=300)
    )

vega_pane = pn.pane.Vega(chart, debounce=10)
pn.Row(vega_pane, pn.bind(filtered_table, vega_pane.selection.param.brush))
```

#### Filtering temporal data via a selection

Selections on temporal columns return the max and min of the selection interval, just as for quantitative data. However, these are returned as a Unix timestamp in milliseconds by default and therefore need to be converted to a pandas timestamp before they can be used in a query string. We can do this using `pd.to_datetime(value, unit="ms")` as in the example below.

```python
from vega_datasets import data

temps = data.seattle_temps()[:300]

brush = alt.selection_interval(name='brush')

chart = alt.Chart(temps).mark_circle().encode(
    x='date:T',
    y=alt.Y('temp:Q', scale={'zero': False}),
    color=alt.condition(brush, alt.value('coral'), alt.value('lightgray'))
).properties(
    width=500
).add_params(
    brush
)

def filtered_table(selection):
    if not selection:
        return '## No selection'
    query = ' & '.join(
        f'"{pd.to_datetime(values[0], unit="ms")}" <= `{col}` <= "{pd.to_datetime(values[1], unit="ms")}"'
        if pd.api.types.is_datetime64_any_dtype(temps[col]) else f'{values[0]} <= `{col}` <= {values[1]}'
        for col, values in selection.items()
    )
    return pn.Column(
        f'Query: {query}',
        pn.pane.DataFrame(temps.query(query), width=600, height=300)
    )

vega_pane = pn.pane.Vega(chart, debounce=10)
pn.Row(vega_pane, pn.bind(filtered_table, vega_pane.selection.param.brush))
```

### Controls

The `Vega` pane exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(vgl_responsive_pane.controls(jslink=True), vgl_responsive_pane, sizing_mode="stretch_width")
```

---
