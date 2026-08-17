# Vizzu
---
```python
import numpy as np
import pandas as pd
import panel as pn

pn.extension('vizzu')
```

The ``Vizzu`` pane renders [Vizzu](https://lib.vizzuhq.com/) charts inside Panel. Note that to use the ``Vizzu`` pane in the notebook, the Panel extension has to be loaded with 'vizzu' as an argument to ensure that vizzu.js is initialized.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``object``** (dict | pd.DataFrame): The data expressed as a Python dictionary of arrays or DataFrame.
* **``animation``** (dict): Animation settings.
* **``config``** (dict): The config contains all of the parameters needed to render a particular static chart or a state of an animated chart.
* **``columns``** (list): Optional column definitions. If not defined will be inferred from the data.
* **``tooltips``** (boolean): Whether to enable tooltips on the chart.

Methods:

* **`animate`**: Accepts a dictionary of new 'data', 'config' and 'style' values which is used to update the chart.
* **`stream`**: Streams new data to the plot.
* **`patch`**: Patches one or more rows in the data.
___

The `Vizzu` pane is built on **version {{VIZZU_VERSION}}** of the [Vizzu Javascript](https://lib.vizzuhq.com/{{VIZZU_VERSION}}/) library.

The `Vizzu` renders a dataset (defined either as a dictionary of columns or a DataFrame) given a `config` defining how to plot the data:

```python
data = {
    'Name': ['Alice', 'Bob', 'Ted', 'Patrick', 'Jason', 'Teresa', 'John'],
    'Weight': 50+np.random.randint(0, 10, 7)*10
}

vizzu = pn.pane.Vizzu(
    data, config={'geometry': 'rectangle', 'x': 'Name', 'y': 'Weight', 'title': 'Weight by person'},
    duration=400, height=400, sizing_mode='stretch_width', tooltip=True
)

vizzu
```

One of the major selling points behind Vizzu is the dynamic animations when either the data or the `config` is updated, e.g. if we change the 'geometry' we can see the animation smoothly transition between the two states.

```python
vizzu.animate({'geometry': 'circle'})
```

```python
vizzu.animate({'geometry': 'area'})
```

Note that the Vizzu pane will keep track of any changes you make as part of the `.animate()` call ensuring that the plot can be re-created easily:

```python
print(vizzu.config)

vizzu
```

## Column Types

`Vizzu` supports two column types:

- `'dimension'`: Usually used for non-numeric data and/or the independent dimension of a chart (e.g. the x-axis)
- `'measure'`: Numeric values usually used for dependent variables of a chart (e.g. the y-axis values)

The `Vizzu` pane automatically infers the types based on the dtypes of the data but in certain cases it may be necessary to explicitly override the type of a column using `column_types` parameter. One common example is when plotting integers on the x-axis, which would ordinarily be treated as a 'measure' but should be treated as the independent dimension in the case of a line or bar chart.

The example below demonstrates this case, here we want to treat the 'index' as an independent variable and override the default inferred type with `column_types={'index': 'dimension'}`:

```python
df = pd.DataFrame(np.random.randn(50), columns=list('Y')).cumsum()

pn.pane.Vizzu(
    df, column_types={'index': 'dimension'}, config={'x': 'index', 'y': 'Y', 'geometry': 'line'},
    height=300, sizing_mode='stretch_width'
)
```

## Presets

Vizzu provides a variety of [preset chart types](https://lib.vizzuhq.com/latest/examples/presets/). In `ipyvizzu` these are expressed by calling [helper methods](https://ipyvizzu.vizzuhq.com/latest/tutorial/chart_presets/) on the `Config` object. The `Vizzu` pane instead allows you to provide `'preset'` as a key of the `config`. In the example below we dynamically create a `config` that switches the `preset` based on a `RadioButtonGroup`:

```python
windturbines = pd.read_csv('https://datasets.holoviz.org/windturbines/v1/windturbines.csv')

agg = windturbines.groupby(['p_year', 't_manu'])[['p_cap']].sum().sort_index(level=0).reset_index()

chart_type = pn.widgets.RadioButtonGroup(options={'Stream': 'stream', 'Bar': 'stackedColumn'}, align='center')

preset_chart = pn.pane.Vizzu(
    agg,
    config=pn.bind(lambda preset: {'preset': preset, 'x': 'p_year', 'y': 'p_cap', 'stackedBy': 't_manu'}, chart_type),
    column_types={'p_year': 'dimension'},
    height=500,
    sizing_mode='stretch_width',
    style={
        'plot': {
            "xAxis": {
                "label": {
                    "angle": "-45deg"
                }
            }
        }
    }
)

pn.Column(chart_type, preset_chart).embed()
```

## Controls

The `Vizzu` pane exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(vizzu.controls(jslink=True), vizzu)
```

---
