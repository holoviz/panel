# DataFrame
---
```python
import pandas as pd
import panel as pn

pn.extension()
```

The ``DataFrame`` pane renders pandas, dask and streamz ``DataFrame`` and ``Series`` types as an HTML table. The Pane supports all the arguments to the `DataFrame.to_html` function.

If you need to to display a larger `DataFrame` or use advanced table features and interactivity we recommend using the `Tabulator` widget or `Perspective` pane instead.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``bold_rows``** (boolean, default=True): Make the row labels bold in the output.
* **``border``** (int, default=0): Width of the border included in the opening ``table`` tag.
* **``classes``** (list[str]): CSS class(es) to apply to the resulting html table.
* **``col_space``** (int, str or dict): The minimum width of each column in CSS length units. An int is assumed to be px units.
* **``decimal``** (str, default='.'): Character recognized as decimal separator, e.g. ',' in Europe.
* **``escape``** (boolean, default=True): Convert the characters <, >, and & to HTML-safe sequences.
* **``float_format``** (function): Formatter function to apply to columns' elements if they are floats. The result of this function must be a unicode string.
* **``formatters``** (dict or list): Formatter functions to apply to columns' elements by position or name. The result of each function must be a unicode string.
* **``object``** (object): The DataFrame object being displayed
* **``header``** (boolean, default=True): Whether to print column labels.
* **``index``** (boolean, default=True): Whether to print index (row) labels.
* **``index_names``** (boolean, default=True): Whether to print the names of the indexes.
* **``justify``** (str): How to justify the column labels ('left', 'right', 'center', 'justify', 'justify-all', 'start', 'end', 'inherit', 'match-parent', 'initial', 'unset')
* **``max_rows``** (int): Maximum number of rows to display.
* **``max_cols``** (int): Maximum number of columns to display.
* **``na_rep``** (str, default='NaN'): String representation of NAN to use.
* **``render_links``** (boolean, default=False): Convert URLs to HTML links.
* **``show_dimensions``** (boolean, default=False): Display DataFrame dimensions (number of rows by number of columns).
* **``sparsify``** (boolean, default=True): Set to False for a DataFrame with a hierarchical index to print every multi-index key at each row.
* **``text_align``** (str): How to justify the non-header cells ('left', 'right', 'center')

___

The `DataFrame` uses the inbuilt HTML repr to render the underlying DataFrame:

```python
df = pd.DataFrame({
    'int': [1, 2, 3],
    'float': [3.14, 6.28, 9.42],
    'str': ['A', 'B', 'C'],
    'bool': [True, False, True],
}, index=[1, 2, 3])

df_pane = pn.pane.DataFrame(df, width=400)

df_pane
```

Like all other Panel objects changing a parameter will update the view allowing us to control the styling of the dataframe. In this example we will control these parameters using a set of widgets created directly from Pane:

```python
pn.panel(df_pane.param, parameters=['bold_rows', 'index', 'header', 'max_rows', 'show_dimensions'],
         widgets={'max_rows': {'start': 1, 'end': len(df), 'value': len(df)}})
```

By setting `escape` to False you can include *HTML markup* in your `Dataframe` pane

```python
links = pd.DataFrame({
    "site": ["Docs", "Discourse", "Github", "Twitter"], 
    "url": ["https://panel.holoviz.org/", "https://discourse.holoviz.org/", "https://github.com/holoviz/panel", "https://twitter.com/Panel_org"]
})
links["value"]="[" + links["site"] + "](" + links["url"] + ")"
pn.pane.DataFrame(links, escape=False, width=800, index=False)
```

## Larger DataFrames

For larger dataframes it can be useful to set `sizing_mode="stretch_both"` to make sure they don't *overflow*. When you do this, you can use `max_height` to specify the (maximum) height.

```python
from bokeh.sampledata.airport_routes import airports
```

```python
table = pn.pane.DataFrame(airports.head(50), sizing_mode="stretch_both", max_height=300)
table
```

```python
pn.Column("## Header", table, "## Footer", height=400, width=500).servable()
```

## Streamz DataFrames

In addition to rendering standard pandas `DataFrame` and `Series` types the `DataFrame` pane will also render updating `streamz` types.
Note:

- In a live kernel you should see the dataframe update every 0.5 seconds.
- `streamz` does currently not work in Pyodide/PyScript.

```python
from streamz.dataframe import Random

sdf = Random(interval='200ms', freq='50ms')

pn.pane.DataFrame(sdf, width=500)
```

```python
type(sdf.groupby('y').sum().x)
```

---
