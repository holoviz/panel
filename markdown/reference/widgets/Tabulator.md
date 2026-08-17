# Tabulator
---
```python
import datetime as dt
import numpy as np
import pandas as pd
import panel as pn

np.random.seed(7)
pn.extension('tabulator')
```

The `Tabulator` widget allows displaying and editing a pandas DataFrame. The `Tabulator` is a largely backward compatible replacement for the `DataFrame` widget and will eventually replace it. It is built on the **version {{TABULATOR_VERSION}}** of the [Tabulator](https://tabulator.info/) library, which provides for a wide range of features.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **`aggregators`** (`dict`): A dictionary mapping from index name to an aggregator to be used for `hierarchical` multi-indexes (valid aggregators include 'min', 'max', 'mean' and 'sum'). If separate aggregators for different columns are required the dictionary may be nested as `{index_name: {column_name: aggregator}}`
* **`buttons`** (`dict`): A dictionary of buttons to add to the table mapping from column name to the HTML contents of the button cell, e.g. `{'print': '<i class="fa fa-print"></i>'}`. Buttons are added after all data columns.
* **`configuration`** (`dict`): A dictionary mapping used to specify *Tabulator* options not explicitly exposed by Panel.
* **`container_popup`** (`boolean`): If True (default), popups will appear within the table container, otherwise popups will be appended to the body element of the DOM.
* **`editables`** (`dict`): A dictionary mapping from column name to a `JSCode` instance that optionally allows cell editing.
* **`editors`** (`dict`):  A dictionary mapping from column name to a bokeh `CellEditor` instance or *Tabulator* editor specification.
* **`embed_content`** (`boolean`): Whether to embed the `row_content` or to dynamically fetch it when a row is expanded.
* **`expanded`** (`list`): The currently expanded rows as a list of integer indexes.
* **`filters`** (`list`): A list of client-side filter definitions that are applied to the table.
* **`formatters`** (`dict`): A dictionary mapping from column name to a bokeh `CellFormatter` instance or *Tabulator* formatter specification.
* **`frozen_columns`** (`list` or `dict`): Defines the frozen columns:
  * `list`
      List of columns to freeze, preventing them from scrolling out of frame. Column can be specified by name or index.
  * `dict`
      Dict of columns to freeze and the position in table (`'left'` or `'right'`) to freeze them in. Column names or index can be used as keys. If value does not match
      `left` or `right` then the default behaviour is to not be frozen at all.
* **`frozen_rows`**: (`list`): List of rows to freeze, preventing them from scrolling out of frame. Rows can be specified by positive or negative index.
* **`groupby`** (`list`): Groups rows in the table by one or more columns.
* **`header_align`** (`dict` or `str`): A mapping from column name to header alignment or a fixed header alignment, which should be one of `'left'`, `'center'`, `'right'`.
* **`header_filters`** (`boolean`/`dict`): A boolean enabling filters in the column headers or a dictionary providing filter definitions for specific columns.
* **`header_tooltips`** (`dict`): Dictionary mapping from column name to a tooltip to show when hovering over the column header.
* **`hidden_columns`** (`list`): List of columns to hide.
* **`hierarchical`** (boolean, default=False): Whether to render multi-indexes as hierarchical index (note hierarchical must be enabled during instantiation and cannot be modified later)
* **`initial_page_size`** (`int`, `default=20`): If pagination is enabled and `page_size` this determines the initial size of each page before rendering.
* **`layout`** (`str`, `default='fit_data_table'`): Describes the column layout mode with one of the following options `'fit_columns'`, `'fit_data'`, `'fit_data_stretch'`, `'fit_data_fill'`, `'fit_data_table'`.
* **`movable_columns`** (`boolean`, `default=False`): Whether columns can be reordered by dragging their headers.
* **`page`** (`int`, `default=1`): Current page, if pagination is enabled.
* **`page_size`** (`int | None`, `default=None`): Number of rows on each page, if pagination is enabled. By default the number of rows is automatically determined based on the number of rows that fit on screen. If None the initial amount of data is determined by the `initial_page_size`.
* **`pagination`** (`str`, `default=None`):  Set to `'local` or `'remote'` to enable pagination; by default pagination is disabled with the value set to `None`.
* **`row_content`** (`callable`): A function that receives the expanded row (`pandas.Series`) as input and should return a Panel object to render into the expanded region below the row. The function may also be asynchronous.
* **`selection`** (`list`): The currently selected rows as a list of integer indexes.
* **`selectable`** (`boolean` or `str` or `int`, `default=True`): Defines the selection mode:
  * `True`
      Selects rows on click. To select multiple use Ctrl-select, to select a range use Shift-select
  * `False`
      Disables selection
  * `'checkbox'`
      Adds a column of checkboxes to toggle selections
  * `'checkbox-single'`
      Same as 'checkbox' but header does not allow select/deselect all
  * `'toggle'`
      Selection toggles when clicked
  * `int`
      The maximum number of selectable rows.
* **`selectable_rows`** (`callable`): A function that should return a list of integer indexes given a DataFrame indicating which rows may be selected.
* **`show_index`** (`boolean`, `default=True`): Whether to show the index column.
* **`sortable`** (`bool | dict[str, bool]`, `default=True`): Whether the table is sortable or whether individual columns are sortable. If specified as a bool applies globally otherwise sorting can be enabled/disabled per column.
* **`sorters`** (`list`): A list of sorter definitions mapping where each item should declare the column to sort on and the direction to sort, e.g. `[{'field': 'column_name', 'dir': 'asc'}, {'field': 'another_column', 'dir': 'desc'}]`.
* **`text_align`** (`dict` or `str`): A mapping from column name to alignment or a fixed column alignment, which should be one of `'left'`, `'center'`, `'right'`.
* **`theme`** (`str`, `default='simple'`): The CSS theme to apply (note that changing the theme will restyle all tables on the page), which should be one of `'default'`, `'site'`, `'simple'`, `'midnight'`, `'modern'`, `'bootstrap'`, `'bootstrap4'`, `'bootstrap5'`, `'materialize'`, `'bulma'`, `'semantic-ui'`, or `'fast'`.
* **`theme_classes`** (`list[str]`): List of extra CSS classes to apply to the Tabulator element to customize the theme.
* **`title_formatters`** (`dict`): A dictionary mapping from column name to a *Tabulator* formatter specification.
* **`titles`** (`dict`): A mapping from column name to a title to override the name with.
* **`value`** (`pd.DataFrame`): The pandas DataFrame to display and edit
* **`widths`** (`dict`): A dictionary mapping from column name to column width in the rendered table.

##### Display

* **`disabled`** (`boolean`): Whether the cells are editable
* **`label`** (`str`): The title of the widget
* **`name`** (`str`): Deprecated alias for ``label``; use ``label`` instead.

##### Properties

* **`current_view`** (`DataFrame`): The current view of the table that is displayed, i.e. after sorting and filtering are applied. `current_view` isn't guaranteed to be in sync with the displayed current view when sorters are applied and values are edited, in which case `current_view` is sorted while the displayed table isn't.
* **`selected_dataframe`** (`DataFrame`): A DataFrame reflecting the currently selected rows.

##### Callbacks

* **`on_click`**: Allows registering callbacks which are given `CellClickEvent` objects containing the `column`, `row` and `value` of the clicked cell.
* **`on_edit`**: Allows registering callbacks which are given `TableEditEvent` objects containing the `column`, `row`, `value` and `old` value of the edited cell.

##### Specific methods

* **`add_filter`**: Adds a filter to the table which can be a static value or dynamic parameter based object which will automatically update the table when changed.
* **`remove_filter`**: Removes a filter which was previously added.
* **`download`**: Triggers downloading of the table as a CSV or JSON.
* **`download_menu`**: Returns a menu containing a TextInput and Button widget to set the filename and trigger a client-side download of the data.
* **`patch`**: Efficiently patches (updates) the existing value with the `patch_value`.def
* **`stream`**: Efficiently stream new data rows.

In both these callbacks `row` is the index of the `value` DataFrame.
___

The `Tabulator` widget renders a DataFrame using an interactive grid, which allows directly editing the contents of the DataFrame in place, with any changes being synced with Python. The `Tabulator` will usually determine the appropriate formatter appropriately based on the type of the data:

```python
df = pd.DataFrame({
    'int': [1, 2, 3],
    'float': [3.14, 6.28, 9.42],
    'str': ['A', 'B', 'C'],
    'bool': [True, False, True],
    'date': [dt.date(2019, 1, 1), dt.date(2020, 1, 1), dt.date(2020, 1, 10)],
    'datetime': [dt.datetime(2019, 1, 1, 10), dt.datetime(2020, 1, 1, 12), dt.datetime(2020, 1, 10, 13)]
}, index=[1, 2, 3])

df_widget = pn.widgets.Tabulator(df, buttons={'Print': "<i class='fa fa-print'></i>"})
df_widget
```

## Formatters

By default the widget will pick Bokeh `CellFormatter` and `CellEditor` types appropriate to the dtype of the column. These may be overridden by explicit dictionaries mapping from the column name to the editor or formatter instance. For example below we create a `NumberFormatter` to customize the formatting of the numbers in the `float` column and a `BooleanFormatter` instance to display the values in the `bool` column with tick crosses:

```python
from bokeh.models.widgets.tables import NumberFormatter, BooleanFormatter

bokeh_formatters = {
    'float': NumberFormatter(format='0.00000'),
    'bool': BooleanFormatter(),
}

pn.widgets.Tabulator(df, formatters=bokeh_formatters)
```

The list of valid Bokeh formatters includes:

* [BooleanFormatter](https://docs.bokeh.org/en/latest/docs/reference/models/widgets/tables.html#bokeh.models.BooleanFormatter)
* [DateFormatter](https://docs.bokeh.org/en/latest/docs/reference/models/widgets/tables.html#bokeh.models.DateFormatter)
* [NumberFormatter](https://docs.bokeh.org/en/latest/docs/reference/models/widgets/tables.html#bokeh.models.NumberFormatter)
* [HTMLTemplateFormatter](https://docs.bokeh.org/en/latest/docs/reference/models/widgets/tables.html#bokeh.models.HTMLTemplateFormatter)
* [StringFormatter](https://docs.bokeh.org/en/latest/docs/reference/models/widgets/tables.html#bokeh.models.StringFormatter)
* [ScientificFormatter](https://docs.bokeh.org/en/latest/docs/reference/models/widgets/tables.html#bokeh.models.ScientificFormatter)

However in addition to the formatters exposed by Bokeh it is also possible to provide valid formatters built into the *Tabulator* library. These may be defined either as a string or as a dictionary declaring the `type` and other arguments, which are passed to *Tabulator* as the `formatterParams`:

```python
tabulator_formatters = {
    'float': {'type': 'progress', 'max': 10},
    'bool': {'type': 'tickCross'}
}

pn.widgets.Tabulator(df, formatters=tabulator_formatters)
```

Lastly, it is also possible to use the `JSCode` helper to implement a custom formatter:

```python
code = """
function format(cell, formatterParams, onRendered) {
    return cell.getValue() ? "✅" : "❌"
}
"""

tabulator_formatters = {
    'float': {'type': 'progress', 'max': 10},
    'bool': pn.io.JSCode(code)
}

pn.widgets.Tabulator(df, formatters=tabulator_formatters)
```

The list of valid *Tabulator* formatters can be found in the [Tabulator documentation](https://tabulator.info/docs/{{TABULATOR_VERSION_WWW}}/format#format-builtin).

Note that the equivalent specification may also be applied for column titles using the `title_formatters` parameter (but does not support Bokeh `CellFormatter` types).

## Editors/Editing

Just like the formatters, the `Tabulator` will natively understand the Bokeh `Editor` types. However, in the background it will replace most of them with equivalent editors natively supported by the *Tabulator* library:

```python
from bokeh.models.widgets.tables import CheckboxEditor, NumberEditor, SelectEditor

bokeh_editors = {
    'float': NumberEditor(),
    'bool': CheckboxEditor(),
    'str': SelectEditor(options=['A', 'B', 'C', 'D']),
}

pn.widgets.Tabulator(df[['float', 'bool', 'str']], editors=bokeh_editors)
```

Therefore it is often preferable to use one of the [*Tabulator* editors](https://tabulator.info/docs/{{TABULATOR_VERSION_WWW}}/edit#edit) directly. Setting the editor of a column to `None` makes that column non-editable. Note that in addition to the standard *Tabulator* editors the `Tabulator` widget also supports `'date'` and `'datetime'` editors:

```python
tabulator_editors = {
    'int': None,
    'float': {'type': 'number', 'max': 10, 'step': 0.1},
    'bool': {'type': 'tickCross', 'tristate': True, 'indeterminateValue': None},
    'str': {'type': 'list', 'valuesLookup': True},
    'date': 'date',
    'datetime': 'datetime'
}

edit_table = pn.widgets.Tabulator(df, editors=tabulator_editors)

edit_table
```

When editing a cell the data stored on the `Tabulator.value` is updated and you can listen to any changes using the usual `.param.watch(callback, 'value')` mechanism. Since the DataFrame is edited in place, the `old` value on that event is a copy of the table as it was before the edit while the `new` value is the DataFrame you passed in. However if you need to know precisely which cell was changed you may also attach an `on_edit` callback which will be passed a `TableEditEvent` containing the:

- `column`: Name of the edited column
- `row`: Integer index of the edited row of the `value` DataFrame
- `old`: Old cell value
- `value`: New cell value

```python
edit_table.on_edit(lambda e: print(e.column, e.row, e.old, e.value))
```

### Nested editor
Suppose you want an editor to depend on values in another cell. The `nested` type can be used. The `nested` type needs two arguments, `options` and `lookup_order`; the latter describes how the `options` should be looked up.

Let's create a simple DataFrame with three columns, the `2` column now depends on the values in the `0` and `1` column. If the `0` is `A`, the `2` column should always be between 1 and 5. If the `0` column is `B`, the `2` column will now also depend on the `1` column.

```python
options = {
    "A": ["A.1", "A.2", "A.3", "A.4", "A.5"],
    "B": {
        "1": ["B1.1", "B1.2", "B1.3"],
        "2": ["B2.1", "B2.2", "B2.3"],
        "3": ["B3.1", "B3.2", "B3.3"],
    },
}
tabulator_editors = {
    "0": {"type": "list", "values": ["A", "B"]},
    "1": {"type": "list", "values": [1, 2, 3]},
    "Nested Selection": {"type": "nested", "options": options, "lookup_order": ["0", "1"]},
}

nested_df = pd.DataFrame({"0": ["A", "B", "A"], "1": [1, 2, 3], "Nested Selection": [None, None, None]})
nested_table = pn.widgets.Tabulator(nested_df, editors=tabulator_editors, show_index=False)
nested_table
```

Some things to note about the `nested` editor:
- Only string keys can be used in `options` dictionary.
- Care must be taken so there is always a valid option for the `nested` editor.
- No guarantee is made that the value shown is a `nested` editor is a valid option.

For the last point, you can use an `on_edit` callback, which either change the value or clear it. Below is an example of how to clear it.

```python
def clear_nested_column(event):
    if event.column in ["0", "1"]:
        nested_table.patch({"2": [(event.row, None)]})

nested_table.on_edit(clear_nested_column)
```

### Optional editing
It is also possible to use the `JSCode` helper to implement an optional editing:

```python
code = """
function format(cell) {
    var data = cell.getRow().getData();
    return data.bool;
}
"""

editables = {
    "float": pn.io.JSCode(code),
}

pn.widgets.Tabulator(df[["float", "bool", "str"]], editables=editables)
```

## Column layouts

By default the DataFrame widget will adjust the sizes of both the columns and the table based on the contents, reflecting the default value of the parameter: `layout="fit_data_table"`. Alternative modes allow manually specifying the widths of the columns, giving each column equal widths, or adjusting just the size of the columns.

### Manual column widths

To manually adjust column widths provide explicit `widths` for each of the columns:

```python
custom_df = df.iloc[:3, :]

pn.widgets.Tabulator(custom_df, widths={'index': 70, 'A': 50, 'B': 50, 'C': 70, 'D': 130})
```

You can also declare a single width for all columns this way:

```python
pn.widgets.Tabulator(custom_df, widths=130)
```

or even use percentage widths:

```python
pn.widgets.Tabulator(custom_df, widths={'index': '5%', 'A': '15%', 'B': '15%', 'C': '25%', 'D': '40%'}, sizing_mode='stretch_width')
```

### Autosize columns

To automatically adjust the columns depending on their content set `layout='fit_data'`:

```python
pn.widgets.Tabulator(custom_df, layout='fit_data', width=400)
```

To ensure that the table fits all the data but also stretches to fill all the available space, set `layout='fit_data_stretch'`:

```python
pn.widgets.Tabulator(custom_df, layout='fit_data_stretch', width=400)
```

The `'fit_data_fill'` option on the other hand won't stretch the last column but still fill the space:

```python
pn.widgets.Tabulator(custom_df, layout='fit_data_fill', width=400)
```

Perhaps the most useful of these options is `layout='fit_data_table'` (and therefore the default) since this will automatically size both the columns and the table:

```python
pn.widgets.Tabulator(custom_df, layout='fit_data_table')
```

### Equal size

The simplest option is simply to allocate each column equal amount of size:

```python
pn.widgets.Tabulator(custom_df, layout='fit_columns', width=650)
```

## Alignment

The content of a column or its header can be horizontally aligned with `text_align` and `header_align`. These two parameters accept either a string that globally defines the alignment or a dictionary that declares which particular columns are meant to be aligned and how.

```python
pn.widgets.Tabulator(df.iloc[:, :2], header_align='center', text_align={'int': 'center', 'float': 'left'}, widths=150)
```

## Styling

The ability to style the contents of a table based on its content and other considerations is very important. Thankfully `pandas` provides a powerful [styling API](https://pandas.pydata.org/pandas-docs/stable/user_guide/style.html), which can be used in conjunction with the `Tabulator` widget. Specifically the `Tabulator` widget exposes a `.style` attribute just like a `pandas.DataFrame` which lets the user apply custom styling using methods like `.apply` and `.applymap`. For a detailed guide to styling see the [Pandas documentation](https://pandas.pydata.org/pandas-docs/stable/user_guide/style.html).

Here we will demonstrate with a simple example, starting with a basic table:

```python
style_df = pd.DataFrame(np.random.randn(4, 5), columns=list('ABCDE'))
styled = pn.widgets.Tabulator(style_df)
```

Next we define two functions which apply styling cell-wise (`color_negative_red`) and column-wise (`highlight_max`), which we then apply to the `Tabulator` using the `.style` API and then display the `styled` table:

```python
def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    color = 'red' if val < 0 else 'black'
    return 'color: %s' % color

def highlight_max(s):
    '''
    highlight the maximum in a Series yellow.
    '''
    is_max = s == s.max()
    return ['background-color: yellow' if v else '' for v in is_max]

styled.style.map(color_negative_red).apply(highlight_max)

styled
```

You can style your tables with gradients using the `.text_gradient` or `.background_gradient` methods, along with [named Matplotlib color maps](https://matplotlib.org/stable/gallery/color/colormap_reference.html).

**Note:** Styling with gradients requires Matplotlib to be installed.

```python
gradient_table = pn.widgets.Tabulator(style_df)
gradient_table.style.text_gradient(cmap="RdYlGn", subset=["B", "C"])
gradient_table.style.background_gradient(cmap="RdYlGn", subset=["D", "E"])
gradient_table
```

## Theming

The Tabulator library ships with a number of themes, which are defined as CSS stylesheets. For that reason changing the theme on one table will affect all tables on the page and it will usually be preferable to see the theme once at the class level like this:

```python
pn.widgets.Tabulator.theme = 'default'
```

For a full list of themes see the [Tabulator documentation](https://tabulator.info/docs/{{TABULATOR_VERSION_WWW}}/theme), however the default themes include:

- `'simple'`
- `'default'`
- `'midnight'`
- `'site'`
- `'modern'`
- `'bootstrap'`
- `'bootstrap4'`
- `'materialize'`
- `'semantic-ui'`
- `'bulma'`

Additionally, you may provide additional theming classes [as described here](https://tabulator.info/docs/{{TABULATOR_VERSION_WWW}}/theme#framework).

```python
pn.widgets.Tabulator(df, theme='bootstrap5', theme_classes=['thead-dark', 'table-sm'])
```

### Changing font-size

Font-size may vary from theme to theme. E.g with 'bootstrap' it is 13px while with 'bootstrap5' it is 16px. Below is one way to overwrite the font-size value for theme 'bootstrap5' to 10px.

```python
pn.widgets.Tabulator(df, theme='bootstrap5', stylesheets=[":host .tabulator {font-size: 10px;}"])
```

## Selection/Click

The `selection` parameter controls which rows in the table are selected and can be set from Python and updated by selecting rows on the frontend:

```python
sel_df = pd.DataFrame(np.random.randn(3, 5), columns=list('ABCDE'))

select_table = pn.widgets.Tabulator(sel_df, selection=[0, 2])
select_table
```

Once initialized, the `selection` parameter will return the integer indexes of the selected rows, while the `selected_dataframe` property will return a new DataFrame containing just the selected rows:

```python
select_table.selection = [1]

select_table.selected_dataframe
```

The `selectable` parameter declares how the selections work.

- `True`: Selects rows on click. To select multiple use Ctrl-select, to select a range use Shift-select
- `False`: Disables selection
- `'checkbox'`: Adds a column of checkboxes to toggle selections
- `'checkbox-single'`: Same as `'checkbox'` but disables (de)select-all in the header
- `'toggle'`: Selection toggles when clicked
- Any positive `int`: A number that sets the maximum number of selectable rows

```python
pn.widgets.Tabulator(sel_df, selection=[0, 2], selectable='checkbox')
```

Additionally we can also disable selection for specific rows by providing a `selectable_rows` function. The function must accept a `DataFrame` and return a list of integer indexes indicating which rows are selectable, e.g. here we disable selection for every second row:

```python
select_table = pn.widgets.Tabulator(sel_df, selectable_rows=lambda df: list(range(0, len(df), 2)))
select_table
```

To trigger events based on an exact cell that was clicked you may also register an `on_click` callback which is called whenever a cell is clicked.

```python
def click(event):
    print(f'Clicked cell in {event.column!r} column, row {event.row!r} with value {event.value!r}')

select_table.on_click(click) 
# Optionally we can also limit the callback to a specific column
# select_table.on_click(click, column='A') 
```

### Freezing rows and columns

Sometimes your table will be larger than can be displayed in a single viewport, in which case scroll bars will be enabled. In such cases, you might want to make sure that certain information is always visible. This is where the `frozen_columns` and `frozen_rows` options come in.

#### Frozen columns

When you have a large number of columns and can't fit them all on the screen you might still want to make sure that certain columns do not scroll out of view. The `frozen_columns` option makes this possible by specifying a list of columns that should be frozen, e.g. `frozen_columns=['index']` will freeze the index column:

```python
pn.widgets.Tabulator(df, frozen_columns=['index'], width=400)
```

By default, columns given in the list format are frozen to the left hand side of the table. If you want to customize where columns are frozen to on the table, you can specify this with a dictionary:

```python
pn.widgets.Tabulator(df, frozen_columns={'index': 'left', 'float': 'right'}, width=400)
```

The 'index' column will be frozen on the left side of the table, and the 'float' on the right. Non-frozen columns will scroll between these two.

#### Frozen rows

Another common scenario is when you have certain rows with special meaning, e.g. aggregates that summarize the information in the rest of the table. In this case you may want to freeze those rows so they do not scroll out of view. You can achieve this by setting a list of `frozen_rows` by integer index (which can be positive or negative, where negative values are relative to the end of the table):

```python
date_df = df.set_index('date').iloc[:5, :2]
agg_df = pd.concat([date_df, date_df.median().to_frame('Median').T, date_df.mean().to_frame('Mean').T])
agg_df.index= agg_df.index.map(str)

pn.widgets.Tabulator(agg_df, frozen_rows=[-2, -1], height=200)
```

## Row contents

A table can only display so much information without becoming difficult to scan. We may want to render additional information to a table row to provide additional context. To make this possible you can provide a `row_content` function which is given the table row as an argument (a `pandas.Series` object) and should return a panel object that will be rendered into an expanding region below the row. By default the contents are fetched dynamically whenever a row is expanded, however using the `embed_content` parameter we can embed all the content. The function may also be asynchronous.

Below we create a periodic table of elements where the Wikipedia page for each element will be rendered into the expanded region:

```python
from bokeh.sampledata.periodic_table import elements

periodic_df = elements[['atomic number', 'name', 'atomic mass', 'metal', 'year discovered']].set_index('atomic number')

content_fn = lambda row: pn.pane.HTML(
    f'<iframe src="https://en.wikipedia.org/wiki/{row["name"]}?printable=yes" width="100%" height="200px"></iframe>',
    sizing_mode='stretch_width'
)

periodic_table = pn.widgets.Tabulator(
    periodic_df, height=350, layout='fit_columns', sizing_mode='stretch_width',
    row_content=content_fn, embed_content=True
)

periodic_table
```

The currently expanded rows can be accessed and set on the `expanded` parameter:

```python
periodic_table.expanded
```

## Grouping

Another useful option is the ability to group specific rows together, which can be achieved using `groups` parameter. The `groups` parameter should be composed of a dictionary mapping from the group titles to the column names:

```python
pn.widgets.Tabulator(style_df.iloc[:3], groups={'Group 1': ['A', 'B'], 'Group 2': ['C', 'D']})
```

## MultiIndex columns

When a DataFrame has MultiIndex columns, grouping is automatically performed based on the column levels, and the configuration of each column can be customized as shown below:

```python
columns = pd.MultiIndex.from_tuples(
    [("Group 1", "A"), ("Group 1", "B"), ("Group 2", "C"), ("Group 2", "D"), ("E", "")]
)
multicolumn_df = pd.DataFrame(np.random.randn(4, 5), columns=columns)
pn.widgets.Tabulator(
    multicolumn_df,
    formatters={("Group 1", "A"): NumberFormatter(format="0.00")},
    editors={("Group 1", "B"): {"type": "number", "max": 10, "step": 0.1}},
    titles={
        ("Group 1",): "Group_1",
        ("Group 1", "B"): "b",
    },
    header_tooltips={("Group 1", "B"): "Tooltips for group 1.b"},
)
```

## Groupby

In addition to grouping columns we can also group rows by the values along one or more columns:

```python
from bokeh.sampledata.autompg import autompg

pn.widgets.Tabulator(autompg, groupby=['yr', 'origin'], height=240)
```

### Hierarchical Multi-index

The `Tabulator` widget can also render a hierarchical multi-index and aggregate over specific categories. If a DataFrame with a hierarchical multi-index is supplied and the `hierarchical` is enabled the widget will group data by the categories in the order they are defined in. Additionally for each group in the multi-index an aggregator may be provided which will aggregate over the values in that category.

We will use the Automobile Mileage dataset for various car models from the 1970s and 1980s around the world, broken down by regions, model years and manufacturers. The dataset includes details on car characteristics and performance metrics.

```python
from bokeh.sampledata.autompg import autompg_clean as autompg_df

autompg_df = autompg_df.set_index(["origin", "yr", "mfr"])
autompg_df.head(3)
```

If we specify aggregators over the 'origin' (region) and 'yr' (model year) indexes, we can see the aggregated values for each of those groups. Note that if no aggregators are specified to an outer index level, it will be aggregated with the default method of `sum`.

```python
pn.widgets.Tabulator(value=autompg_df, hierarchical=True, aggregators={"origin": "mean", "yr": "mean"}, height=200)
```

Separate aggregators for different columns are also supported. You can specify the `aggregators` as a nested dictionary as `{index_name: {column_name: aggregator}}`

Applied to the same dataset, we can aggregate the data in the `mpg` (miles per galon) and `hp` columns differently, with `mean` and `max`, respectively.

```python
nested_aggs = {"origin": {"mpg": "mean", "hp": "max"}, "yr": {"mpg": "mean", "hp": "max"}}
pn.widgets.Tabulator(value=autompg_df[["mpg", "hp"]], hierarchical=True, aggregators=nested_aggs, height=200)
```

## Pagination

When working with large tables it is generally not advisible to display the whole table at once. In these scenarios we can enable either `'local'` or `'remote'` pagination, which will render only a single page of data at the same time. In the case of `'remote'` pagination only the currently viewed data is actually transferred from the backend server to the frontend and new data is fetched dynamically when we switch the page or filter and sort the data. Note that Panel will automatically enable `'local'` pagination for tables larger than 200 rows and enable `'remote'` pagination for tables larger than 10 000 rows. This protection may be overridden by explicitly setting the `pagination` parameter.

The pagination setting may be enabled by setting `pagination='remote'` or `pagination='local'` and the size of each page can be set using the `page_size` option:

```python
large_df = pd.DataFrame({'A': np.random.rand(10000)})
pn.widgets.Tabulator(large_df, pagination='remote', page_size=3)
```

Note that the default `page_size` is None, which means it will measure the height of the rows and try to fit the appropriate number of rows into the available space. To override the number of rows sent to the frontend before the measurement has taken place set the `initial_page_size`.

Contrary to the `'remote'` option, `'local'` pagination transfers all of the data but still allows to display it on multiple pages:

```python
medium_df = pd.DataFrame({'A': np.random.rand(1000)})
pn.widgets.Tabulator(medium_df, pagination='local', page_size=3)
```

## Filtering

A very common scenario is that you want to attach a number of filters to a table in order to view just a subset of the data. You can achieve this through callbacks or other reactive approaches but the  `.add_filter` method makes it much easier.

#### Constant and Widget filters

The simplest approach to filtering is to select along a column with a constant or dynamic value. The `.add_filter` method allows passing in constant values, widgets and Param `Parameter`s. If a widget or `Parameter` is provided the table will watch the object for changes in the value and update the data in response. The filtering will depend on the type of the constant or dynamic value:

- scalar: Filters by checking for equality
- `tuple`: A tuple will be interpreted as range, the *start* and *end* bounds being both included in the range. Setting one of the bounds to `None` create an open-ended bound.
- `list`/`set`: A list or set will be interpreted as a set of discrete scalars and the filter will check if the values in the column match any of the items in the list.

As an example we will create a DataFrame with some data of mixed types:

```python
filter_table = pn.widgets.Tabulator(df)
filter_table
```

Now we will start adding filters one-by-one, e.g. to start with we add a filter for the `'A'` column, selecting a range from 0 to 3:

```python
filter_table.add_filter((1, 2), 'int')
```

Next we add dynamic widget based filter, a `RangeSlider` which allows us to further narrow down the data along the `'A'` column:

```python
slider = pn.widgets.RangeSlider(start=0, end=3, label='A Filter')
filter_table.add_filter(slider, 'int')
```

Lastly we will add a `MultiSelect` filter along the `'C'` column:

```python
select = pn.widgets.MultiSelect(options=list('ABC'), label='str Filter')
filter_table.add_filter(select, 'str')
```

Now let's display the table alongside the widget based filters:

```python
pn.Row(
    pn.Column(slider, select),
    filter_table
)
```

After filtering (and sorting) you can inspect the current view with the `current_view` property:

```python
select.value = ['A', 'B']
filter_table.current_view
```

#### Function based filtering

For more complex filtering tasks you can supply a function that should accept the DataFrame to be filtered as the first argument and must return a filtered copy of the data. Let's start by loading some data.

```python
import sqlite3

from bokeh.sampledata.movies_data import movie_path

con = sqlite3.Connection(movie_path)
movies_df = pd.read_sql('SELECT Title, Year, Genre, Director, Writer, Rating, imdbRating from omdb', con)
movies_df = movies_df[~movies_df.Director.isna()]

movies_table = pn.widgets.Tabulator(movies_df, pagination='remote', page_size=4)
```

By using the `pn.bind` function, which binds widget and `Parameter` values to a function, complex filtering can be achieved. E.g. here we will add a filter function that tests whether the string or regex is contained in the 'Director' column of a listing of thousands of movies:

```python
director_filter = pn.widgets.TextInput(label='Director filter', value='Chaplin')

def contains_filter(df, pattern, column):
    if not pattern:
        return df
    return df[df[column].str.contains(pattern)]
    
movies_table.add_filter(pn.bind(contains_filter, pattern=director_filter, column='Director'))    

pn.Row(director_filter, movies_table)
```

### Client-side filtering

In addition to the Python API the `Tabulator` widget also offers a client-side filtering API, which can be exposed through `header_filters` or by manually setting filters in the rendered table. The API for declaring header filters is almost identical to the API for defining [Editors](#Editors). The `header_filters` can either be enabled by setting it to `True` or by manually supplying filter types for each column. The types of filters supports all the same options as the editors, in fact if you do not declare explicit `header_filters` the `Tabulator` widget will simply use the defined `editors` to determine the correct filter type:

```python
tabulator_editors = {
    'float': {'type': 'number', 'max': 10, 'step': 0.1},
    'bool': {'type': 'tickCross', 'tristate': True, 'indeterminateValue': None},
    'str': {'type': 'list', 'valuesLookup': True},
}

header_filter_table = pn.widgets.Tabulator(
    df[['float', 'bool', 'str']], height=140, width=400, layout='fit_columns',
    editors=tabulator_editors, header_filters=True
)
header_filter_table
```

When a filter is applied client-side the `filters` parameter is synced with Python. The definition of `filters` looks something like this:

```
[{'field': 'Director', 'type': '=', 'value': 'Steven Spielberg'}]
```

Try applying a filter and then inspect the `filters` parameter:

For all supported filtering types see the [*Tabulator* Filtering documentation](https://tabulator.info/docs/{{TABULATOR_VERSION_WWW}}/filter).

If we want to change the filter type for the `header_filters` we can do so in the definition by supplying a dictionary indexed by the column names and then either providing a dictionary which may define the `'type'`, a comparison `'func'`, a `'placeholder'` and any additional keywords supported by the particular filter type.

```python
movie_filters = {
    'Title': {'type': 'input', 'func': 'like', 'placeholder': 'Enter title'},
    'Year': {'placeholder': 'Enter year'},
    'Genre': {'type': 'input', 'func': 'like', 'placeholder': 'Enter genre'},
    'Director': {'type': 'input', 'func': 'like', 'placeholder': 'Enter director'},
    'Writer': {'type': 'input', 'func': 'like', 'placeholder': 'Enter writer'},
    'Rating': {'type': 'list', 'func': 'in', 'valuesLookup': True, 'sort': 'asc', 'multiselect': True},
    'imdbRating': {'type': 'number', 'func': '>=', 'placeholder': 'Enter minimum rating'},
}

filter_table = pn.widgets.Tabulator(
    movies_df.iloc[:200], pagination='local', layout='fit_columns', page_size=4, sizing_mode='stretch_width',
    header_filters=movie_filters
)
filter_table
```

## Downloading

The `Tabulator` widget also supports triggering a download of the data as a CSV or JSON file depending on the filename. The download can be triggered with the `.download()` method, which optionally accepts the filename as the first argument.

To trigger the download client-side (i.e. without involving the server) you can use the `.download_menu` method which creates a `TextInput` and `Button` widget, which allow setting the filename and triggering the download respectively:

```python
download_df = pd.DataFrame(np.random.randn(4, 5), columns=list('ABCDE'))

download_table = pn.widgets.Tabulator(download_df)

filename, button = download_table.download_menu(
    text_kwargs={'label': 'Enter filename', 'value': 'default.csv'},
    button_kwargs={'label': 'Download table'}
)

pn.Row(
    pn.Column(filename, button),
    download_table
)
```

Note that when `pagination='remote'` is enabled the download feature will only include the current page for technical reasons. If you want to support downloading all the data use the [`FileDownload` widget](./FileDownload).

## Buttons

If you want to trigger custom actions by clicking on a table cell you may declare a set of `buttons` that are rendered in columns after all the data columns. To respond to button clicks you can register a callback using the general `on_click` method:

```python
button_table = pn.widgets.Tabulator(df, buttons={
    'print': '<i class="fa fa-print"></i>',
    'check': '<i class="fa fa-check"></i>'
})

string = pn.widgets.StaticText()

button_table.on_click(
    lambda e: string.param.update(value=f'Clicked {e.column!r} on row {e.row}')
)

pn.Row(button_table, string)
```

 Please note, that in a server context you will have to include the *font awesome* css file to get the button icons rendered, i.e. use

 ```python
 pn.extension("tabulator", ..., css_files=["https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css"])
 ```

## Streaming

When we are monitoring some source of data that updates over time, we may want to update the table with the newly arriving data. However, we do not want to transmit the entire dataset each time. To handle efficient transfer of just the latest data, we can use the `.stream` method on the `Tabulator` object:

```python
stream_df = pd.DataFrame(np.random.randn(5, 5), columns=list('ABCDE'))

stream_table = pn.widgets.Tabulator(stream_df, layout='fit_columns', width=450, height=400)
stream_table
```

As example, we will schedule a periodic callback that streams new data every 1000ms (i.e. 1s) five times in a row:

```python
def stream_data(follow=True):
    stream_df = pd.DataFrame(np.random.randn(5, 5), columns=list('ABCDE'))
    stream_table.stream(stream_df, follow=follow)

pn.state.add_periodic_callback(stream_data, period=1000, count=5);
```

If you are viewing this example with a live Python kernel you will be able to watch the table update and scroll along. If we want to disable the scrolling behavior, we can set `follow=False`:

```python
stream_data(follow=False)
```

## Patching

In certain cases we don't want to update the table with new data but just patch existing data.

```python
df = pd.DataFrame(
    {'col_A': ['foo', 'bar', 'baz'], 'col_B': [10, 20, 30], 'col_C': ['o', 'o', 'o']},
    index=['x', 'y', 'z'],
)
```

```python
patch_table = pn.widgets.Tabulator(df)
patch_table
```

The easiest way to patch the data is by supplying a dictionary as the patch value. The dictionary should have the following structure:

```python
{
    column: [
        (index: int or slice, value),
        ...
    ],
    ...
}
```

As an example, below we will patch the `'col_A'` and `'col_B'` columns. On the `'col_A'` column we will replace the 0th and 2nd row and on the `'col_B'` column we replace the first two rows:

```python
patch_table.patch({
    'col_A': [
        (0, 'FOO'),
        (2, 'BAZ')
    ],
    'col_B': [
        (slice(0, 2), [100, 200])
    ]
}, as_index=False)
```

The `as_index` keyword parameter of `patch` is True by default, in which case the DataFrame index is used to locate the rows to patch. When False, like in the example above, the patch indexes are treated as simple integer indexes starting from 0. The two lines below update the same cells.

```python
patch_table.patch({'col_C': [('x', 'O'), ('y', 'OO')]})
# Equivalent to:
patch_table.patch({'col_C': [(0, 'O'), (0, 'OO')]}, as_index=False)
```

The patch value can also be a Pandas DataFrame or a Series.

```python
patch_table.patch(pd.DataFrame({'col_A': ['foo', 'baz']}, index=['x', 'z']))
# Equivalent to:
patch_table.patch(pd.DataFrame({'col_A': ['foo', 'baz']}, index=[0, 2]), as_index=False)
```

```python
patch_table.patch(pd.Series(['FOO', 'BAZ'], index=['x', 'z'], name='col_A'))
# Equivalent to:
patch_table.patch(pd.Series(['FOO', 'BAZ'], index=[0, 2], name='col_A'), as_index=False)
```

## Static Configuration

Panel does not expose all options available from Tabulator, if a desired option is not natively supported, it can be set via the `configuration` argument.
This dictionary can be seen as a base dictionary which the tabulator object fills and passes to the Tabulator javascript-library.

As an example, we can enable `clipboard` functionality and set the `rowHeight` options. `columnDefaults` takes a dictionary used to configure the columns specifically, in this example we disable header sorting with `headerSort`.

```python
df = pd.DataFrame({
    'int': [1, 2, 3],
    'float': [3.14, 6.28, 9.42],
    'str': ['A', 'B', 'C'],
    'bool': [True, False, True],
    'date': [dt.date(2019, 1, 1), dt.date(2020, 1, 1), dt.date(2020, 1, 10)]
}, index=[1, 2, 3])

pn.widgets.Tabulator(df, configuration={
    'clipboard': True,
    'rowHeight': 50,
    'columnDefaults': {
        'headerSort': False,
    },
})
```

These and other available *Tabulator* options are listed at [Tabulator Options](https://tabulator.info/docs/{{TABULATOR_VERSION_WWW}}/options).

Obviously not all options will work though, especially any settable callbacks and options which are set by the internal Panel tabulator module.
Additionally it should be noted that the configuration parameter is not responsive so it can only be set at instantiation time.

---
