# DataFrame
---
```python
import datetime as dt
import pandas as pd
import panel as pn

pn.extension()
```

The ``DataFrame`` widget allows displaying and editing a pandas DataFrame. Note that editing is not possible for multi-indexed DataFrames, in which case you will need to reduce the DataFrame to a single index. Also note that the `DataFrame` widget will eventually be replaced with the `Tabulator` widget, and so new code should be written to use Tabulator instead.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``aggregators``** (``dict``): A dictionary mapping from index name to an aggregator to be used for hierarchical multi-indexes (valid aggregators include 'min', 'max', 'mean' and 'sum'). If separate aggregators for different columns are required the dictionary may be nested as `{index_name: {column_name: aggregator}}`
* **``auto_edit``** (``boolean``): Whether clicking on a table cell automatically starts edit mode.
* **``autosize_mode``** (str): Describes the column autosizing mode with one of the following options:
  * ``"fit_columns"``
  Compute columns widths based on cell contents but ensure the
  table fits into the available viewport. This results in no
  horizontal scrollbar showing up, but data can get unreadable
  if there is not enough space available.

  * ``"fit_viewport"``
  Adjust the viewport size after computing columns widths based
  on cell contents.

  * ``"force_fit"``
  Fit columns into available space dividing the table width across
  the columns equally (equivalent to `fit_columns=True`).
  This results in no horizontal scrollbar showing up, but data
  can get unreadable if there is not enough space available.

  * ``"none"``
  Do not automatically compute column widths.
* **``editors``** (``dict``):  A dictionary mapping from column name to a bokeh `CellEditor` instance, which overrides the default.
* **``hierarchical``** (boolean, default=False): Whether to render multi-indexes as hierarchical index (note hierarchical must be enabled during instantiation and cannot be modified later)
* **``fit_columns``** (``boolean``, default=True): Whether columns should expand to the available width.
* **``formatters``** (``dict``): A dictionary mapping from column name to a bokeh `CellFormatter` instance, which overrides the default.
* **``frozen_columns``** (int): Integer indicating the number of columns to freeze. If set the  first N columns will be frozen which prevents them from scrolling out of frame.
* **``frozen_rows``**: (int): Integer indicating the number of rows to freeze. If set the first N rows will be frozen which prevents them from scrolling out of frame, if set to a negative value last N rows will be frozen.
* **``reorderable``** (``boolean``): Allows the reordering of a table's columns. To reorder a column, click and drag a table's header to the desired location in the table.  The columns on either side will remain in their previous order.
* **``row_height``** (``int``): The height of each table row.
* **``selection``** (``list``) The currently selected rows.
* **``show_index``** (``boolean``): Whether to show the index column.
* **``sortable``** (``sortable``): Allows to sort table's contents. By default natural order is preserved.  To sort a column, click on it's header. Clicking one more time changes sort direction. Use Ctrl + click to return to natural order. Use Shift + click to sort multiple columns simultaneously
* **``text_align``** (``dict`` or ``str``): A mapping from column name to alignment or a fixed column alignment, which should be one of 'left', 'center', 'right'.
* **`titles`** (``dict``): A mapping from column name to a title to override the name with.
* **``value``** (``pd.DataFrame``): The pandas DataFrame to display and edit
* **``widths``** (``dict``): A dictionary mapping from column name to column width in the rendered table.

##### Display

* **``disabled``** (boolean): Whether the widget is editable
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.

___

The ``DataFrame`` widget renders an table which allows directly editing the contents of the dataframe with any changes being synced with Python. Note that it modifies the ``pd.DataFrame`` in place.

```python
df = pd.DataFrame({
    'int': [1, 2, 3],
    'float': [3.14, 6.28, 9.42],
    'str': ['A', 'B', 'C'],
    'bool': [True, False, True],
    'date': [dt.date(2019, 1, 1), dt.date(2020, 1, 1), dt.date(2020, 1, 10)],
    'datetime': [dt.datetime(2019, 1, 1, 10), dt.datetime(2020, 1, 1, 12), dt.datetime(2020, 1, 10, 13)]
}, index=[1, 2, 3])

df_widget = pn.widgets.DataFrame(df, label='DataFrame')

df_widget
```

By default the widget will pick bokeh ``CellFormatter`` and ``CellEditor`` types appropriate to the dtype of the column. These may be overridden by explicit dictionaries mapping from the column name to the editor or formatter instance. For example below we create a ``SelectEditor`` instance to pick from four options in the ``str`` column and a ``NumberFormatter`` to customize the formatting of the float values:

```python
from bokeh.models.widgets.tables import SelectEditor, NumberFormatter

editor = SelectEditor(options=['A', 'B', 'C', 'D'])
formatter = NumberFormatter(format='0.00000') 

table = pn.widgets.DataFrame(df, editors={'str': editor}, formatters={'float': formatter})
table
```

Once initialized the ``selection`` property will return the integer indexes of the selected rows and the ``selected_dataframe`` property will return a new DataFrame containing just the selected rows:

```python
table.selection = [0, 2]

table.selected_dataframe
```

### Column layouts

By default the DataFrame widget will equally split the available horizontal space between the columns, reflecting the default value of the parameter: `autosize_mode="force_fit"`. Alternatively modes allow manually specifying the widths of the columns or automatically adjusting the column widths or overall table width to match the contents of the table.

#### Manual column widths

To manually adjust column widths set the `autosize_mode` to `"none"` and provide explicit `widths`:

```python
pn.widgets.DataFrame(df, autosize_mode='none', widths={'index': 50, 'int': 50, 'float': 50, 'str': 70, 'bool': 130}, width=350)
```

#### Autosize columns

To automatically adjust the columns depending on their content set `autosize_mode='fit_columns'`:

```python
pn.widgets.DataFrame(df, autosize_mode='fit_columns', width=300)
```

#### Autosize width

To automatically adjust the width of the columns **and** the overall table use `autosize_mode='fit_viewport'`:

```python
pn.widgets.DataFrame(df, autosize_mode='fit_viewport')
```

### Freezing rows and columns

Often times your table will be larger than can be displayed in a single viewport and scroll bars will be enabled. The issue with this is that you might want to make sure that certain information is always visible. This is where the `frozen_columns` and `frozen_rows` options come in.

#### Frozen columns

When you have a large number of columns and can't fit them all on the screen you might still want to make sure that certain columns do not scroll out of view. The `frozen_columns` option makes this possible by specifying the number of columns, counting from the left, that should be frozen, e.g. `frozen_columns=1` will freeze the last column:

```python
date_df = df.set_index('datetime').iloc[:5, :2]

pn.widgets.DataFrame(date_df, height=400, widths=150, frozen_columns=1, autosize_mode='none')
```

#### Frozen rows

Another common scenario is when you have certain rows with special meaning, e.g. aggregates which summarize the information in the rest of the table. In this case you may want to freeze those rows so they do not scroll out of view. You can achieve this by setting `frozen_columns` to an integer value. If the value is positive the first N rows will be frozen, if the value is negative the last N rows will be frozen:

```python
agg_df = pd.concat([date_df, date_df.median().to_frame('Median').T, date_df.mean().to_frame('Mean').T])
agg_df.index= agg_df.index.map(str)

pn.widgets.DataFrame(agg_df, frozen_rows=-2, height=400)
```

### Hierarchical Multi-index

The `DataFrame` widget can also render a hierarchical multi-index and aggregate over specific categories. If a DataFrame with a hierarchical multi-index is supplied and the `hierarchical` is enabled the widget will group data by the categories in the order they are defined in. Additionally for each group in the multi-index an aggregator may be provided which will aggregate over the values in that category.

For example we may load population data for locations around the world broken down by sex and age-group. If we specify aggregators over the 'AgeGrp' and 'Sex' indexes we can see the aggregated values for each of those groups (note that we do not have to specify an aggregator for the outer index since we specify the aggregators over the subgroups in this case the 'Sex'):

```python
from bokeh.sampledata.population import data as population_data 

pop_df = population_data[population_data.Year == 2020].set_index(['Location', 'AgeGrp', 'Sex'])[['Value']]

pn.widgets.DataFrame(value=pop_df, hierarchical=True, aggregators={'Sex': 'sum', 'AgeGrp': 'sum'}, height=400)
```

## Streaming

When we are monitoring a source of data that updates over time, we may want to update the table with the newly arriving data. However, we do not want to re-transmit the entire dataset each time. To handle efficient transfer of just the latest data, we can use the `.stream` method on the `DataFrame` object:

```python
import numpy as np

stream_df = pd.DataFrame(np.random.randn(10, 5), columns=list('ABCDE'))

stream_table = pn.widgets.DataFrame(stream_df, autosize_mode='fit_columns', width=450)
stream_table
```

As example, we will schedule a periodic callback that streams new data every 1000ms (i.e. 1s), five times in a row:

```python
def stream_data():
    stream_df = pd.DataFrame(np.random.randn(10, 5), columns=list('ABCDE'))
    stream_table.stream(stream_df)

pn.state.add_periodic_callback(stream_data, period=1000, count=5)
```

## Patching

In certain cases we don't want to update the table with new data but just patch existing data.

```python
patch_table = pn.widgets.DataFrame(df[['int', 'float', 'str', 'bool']])
patch_table
```

The easiest way to patch the data is by supplying a dictionary as the patch value. The dictionary should have the following structure:

    {
        column: [
            (index: int or slice, value),
            ...
        ],
        ...
    }

As an example, below we will patch the 'bool' and 'int' columns. On the `'bool'` column we will replace the 0th and 2nd row and on the `'int'` column we replace the first two rows:

```python
patch_table.patch({
    'bool': [
        (0, False),
        (2, False)
    ],
    'int': [
        (slice(0, 2), [3, 2])
    ]
}, as_index=False)
```

### Controls

The `DataFrame` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(df_widget.controls(jslink=True), df_widget)
```

---
