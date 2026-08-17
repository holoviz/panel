# panel.widgets.tables module

class panel.widgets.tables.BaseTable(value=None, **params)
Bases: [ReactiveData](panel.reactive.md#panel.reactive.ReactiveData),
[Widget](panel.widgets.base.md#panel.widgets.base.Widget)

Attributes:
[current_view](#panel.widgets.tables.BaseTable.current_view)
Returns the current view of the table after filtering and sorting are
applied.

**indexes**

[selected_dataframe](#panel.widgets.tables.BaseTable.selected_dataframe)
Returns a DataFrame of the currently selected rows.

Methods

|  |  |
|----|----|
| [add_filter](#panel.widgets.tables.BaseTable.add_filter)(filter\[, column\]) | Adds a filter to the table which can be a static value or dynamic parameter based object which will automatically update the table when changed.. |
| [patch](#panel.widgets.tables.BaseTable.patch)(patch_value\[, as_index\]) | Efficiently patches (updates) the existing value with the patch_value. |
| [remove_filter](#panel.widgets.tables.BaseTable.remove_filter)(filter) | Removes a filter which was previously added. |
| [stream](#panel.widgets.tables.BaseTable.stream)(stream_value\[, rollover, reset_index\]) | Streams (appends) the stream_value provided to the existing value in an efficient manner. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
>

`value`` ``=`` ``Parameter(allow_None=True,`` ``allow_refs=True,`` ``label='Value')`
The widget value which the widget type resolves to when used as a
reactive param reference.

`selection`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'int'>,`` ``label='Selection')`
The currently selected rows of the table.

`aggregators`` ``=`` ``Dict(allow_refs=True,`` ``class_=<class`` ``'dict'>,`` ``default={},`` ``label='Aggregators',`` ``nested_refs=True)`
A dictionary mapping from index name to an aggregator to be used for
hierarchical multi-indexes (valid aggregators include ‘min’, ‘max’,
‘mean’ and ‘sum’). If separate aggregators for different columns are
required the dictionary may be nested as {index_name: {column_name:
aggregator}}

`editables`` ``=`` ``Dict(allow_refs=True,`` ``class_=<class`` ``'dict'>,`` ``default={},`` ``label='Editables',`` ``nested_refs=True)`
Allows to edit table’s contents for a particular column.

`editors`` ``=`` ``Dict(allow_refs=True,`` ``class_=<class`` ``'dict'>,`` ``default={},`` ``label='Editors',`` ``nested_refs=True)`
Bokeh CellEditor to use for a particular column (overrides the default
chosen based on the type).

`formatters`` ``=`` ``Dict(allow_refs=True,`` ``class_=<class`` ``'dict'>,`` ``default={},`` ``label='Formatters',`` ``nested_refs=True)`
Bokeh CellFormatter to use for a particular column (overrides the
default chosen based on the type).

`hierarchical`` ``=`` ``Boolean(allow_refs=True,`` ``constant=True,`` ``default=False,`` ``label='Hierarchical')`
Whether to generate a hierarchical index.

`row_height`` ``=`` ``Integer(default=40,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Row`` ``height')`
The height of each table row.

`show_index`` ``=`` ``Boolean(allow_refs=True,`` ``default=True,`` ``label='Show`` ``index')`
Whether to show the index column.

`sorters`` ``=`` ``List(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'dict'>,`` ``label='Sorters')`
A list of sorters to apply during pagination.

`text_align`` ``=`` ``ClassSelector(allow_refs=True,`` ``class_=(<class`` ``'dict'>,`` ``<class`` ``'str'>),`` ``default={},`` ``label='Text`` ``align',`` ``nested_refs=True)`
A mapping from column name to alignment or a fixed column alignment,
which should be one of ‘left’, ‘center’, ‘right’.

`titles`` ``=`` ``Dict(allow_refs=True,`` ``class_=<class`` ``'dict'>,`` ``default={},`` ``label='Titles',`` ``nested_refs=True)`
A mapping from column name to a title to override the name with.

`widths`` ``=`` ``ClassSelector(allow_refs=True,`` ``class_=(<class`` ``'dict'>,`` ``<class`` ``'int'>),`` ``default={},`` ``label='Widths',`` ``nested_refs=True)`
A mapping from column name to column width or a fixed column width.

add_filter(filter: Any, column: str \| None = None)
Adds a filter to the table which can be a static value or dynamic
parameter based object which will automatically update the table when
changed..

When a static value, widget or parameter is supplied the filtering will
follow a few well defined behaviors:

>
>
> - scalar: Filters by checking for equality
>
> - tuple: A tuple will be interpreted as range.
>
> - list: A list will be interpreted as a set of discrete
>   scalars and the filter will check if the values in the column match
>   any of the items in the list.
>
>

Parameters:
**filter: Widget, param.Parameter or FunctionType**
The value by which to filter the DataFrame along the declared column, or
a function accepting the DataFrame to be filtered and returning a
filtered copy of the DataFrame.

**column: str or None**
Column to which the filter will be applied, if the filter is a constant
value, widget or parameter.

Raises:
ValueError: If the filter type is not supported or no column
was declared.

property current_view
Returns the current view of the table after filtering and sorting are
applied.

patch(patch_value, as_index=True)
Efficiently patches (updates) the existing value with the patch_value.

Parameters:
**patch_value: pd.DataFrame \| pd.Series \| Dict**
The value(s) to patch the existing value with.

**as_index: boolean, optional**
Whether to treat the patch index as DataFrame indexes (True) or as
simple integer index. Default is True.

Raises:
ValueError: Raised if the patch_value is not a supported type.

Examples

Patch a DataFrame with a Dictionary row. \>\>\> value =
pd.DataFrame({“x”: \[1, 2\], “y”: \[“a”, “b”\]}) \>\>\> tabulator =
Tabulator(value=value) \>\>\> patch_value = {“x”: \[(0, 3)\]} \>\>\>
tabulator.patch(patch_value) \>\>\> tabulator.value.to_dict(“list”)
{‘x’: \[3, 2\], ‘y’: \[‘a’, ‘b’\]}

Patch a Dataframe with a Dictionary of Columns. \>\>\> value =
pd.DataFrame({“x”: \[1, 2\], “y”: \[“a”, “b”\]}) \>\>\> tabulator =
Tabulator(value=value) \>\>\> patch_value = {“x”: \[(slice(2), (3,4))\],
“y”: \[(1,’d’)\]} \>\>\> tabulator.patch(patch_value) \>\>\>
tabulator.value.to_dict(“list”) {‘x’: \[3, 4\], ‘y’: \[‘a’, ‘d’\]}

Patch a DataFrame with a Series. Please note the index is used in the
update. \>\>\> value = pd.DataFrame({“x”: \[1, 2\], “y”: \[“a”, “b”\]})
\>\>\> tabulator = Tabulator(value=value) \>\>\> patch_value =
pd.Series({“index”: 1, “x”: 4, “y”: “d”}) \>\>\>
tabulator.patch(patch_value) \>\>\> tabulator.value.to_dict(“list”)
{‘x’: \[1, 4\], ‘y’: \[‘a’, ‘d’\]}

Patch a Dataframe with a Dataframe. Please note the index is used in the
update. \>\>\> value = pd.DataFrame({“x”: \[1, 2\], “y”: \[“a”, “b”\]})
\>\>\> tabulator = Tabulator(value=value) \>\>\> patch_value =
pd.DataFrame({“x”: \[3, 4\], “y”: \[“c”, “d”\]}) \>\>\>
tabulator.patch(patch_value) \>\>\> tabulator.value.to_dict(“list”)
{‘x’: \[3, 4\], ‘y’: \[‘c’, ‘d’\]}

remove_filter(filter)
Removes a filter which was previously added.

property selected_dataframe
Returns a DataFrame of the currently selected rows.

stream(stream_value, rollover=None, reset_index=True)
Streams (appends) the stream_value provided to the existing value in an
efficient manner.

Parameters:
**stream_value: (pd.DataFrame \| pd.Series \| Dict)**
The new value(s) to append to the existing value.

**rollover: int**
A maximum column size, above which data from the start of the column
begins to be discarded. If None, then columns will continue to grow
unbounded.

**reset_index: (bool, default=True)**
If True and the stream_value is a DataFrame, then its index is reset.
Helps to keep the index unique and named index

Raises:
ValueError: Raised if the stream_value is not a supported type.

Examples

Stream a Series to a DataFrame \>\>\> value = pd.DataFrame({“x”: \[1,
2\], “y”: \[“a”, “b”\]}) \>\>\> tabulator = Tabulator(value=value)
\>\>\> stream_value = pd.Series({“x”: 4, “y”: “d”}) \>\>\>
tabulator.stream(stream_value) \>\>\> tabulator.value.to_dict(“list”)
{‘x’: \[1, 2, 4\], ‘y’: \[‘a’, ‘b’, ‘d’\]}

Stream a Dataframe to a Dataframe \>\>\> value = pd.DataFrame({“x”: \[1,
2\], “y”: \[“a”, “b”\]}) \>\>\> tabulator = Tabulator(value=value)
\>\>\> stream_value = pd.DataFrame({“x”: \[3, 4\], “y”: \[“c”, “d”\]})
\>\>\> tabulator.stream(stream_value) \>\>\>
tabulator.value.to_dict(“list”) {‘x’: \[1, 2, 3, 4\], ‘y’: \[‘a’, ‘b’,
‘c’, ‘d’\]}

Stream a Dictionary row to a DataFrame \>\>\> value = pd.DataFrame({“x”:
\[1, 2\], “y”: \[“a”, “b”\]}) \>\>\> tabulator = Tabulator(value=value)
\>\>\> stream_value = {“x”: 4, “y”: “d”} \>\>\>
tabulator.stream(stream_value) \>\>\> tabulator.value.to_dict(“list”)
{‘x’: \[1, 2, 4\], ‘y’: \[‘a’, ‘b’, ‘d’\]}

Stream a Dictionary of Columns to a Dataframe \>\>\> value =
pd.DataFrame({“x”: \[1, 2\], “y”: \[“a”, “b”\]}) \>\>\> tabulator =
Tabulator(value=value) \>\>\> stream_value = {“x”: \[3, 4\], “y”: \[“c”,
“d”\]} \>\>\> tabulator.stream(stream_value) \>\>\>
tabulator.value.to_dict(“list”) {‘x’: \[1, 2, 3, 4\], ‘y’: \[‘a’, ‘b’,
‘c’, ‘d’\]}

class panel.widgets.tables.ColumnSpec
Bases: `TypedDict`

class panel.widgets.tables.DataFrame(value=None, **params)
Bases:
[BaseTable](#panel.widgets.tables.BaseTable)

The DataFrame widget allows displaying and editing a pandas DataFrame.

Note that editing is not possible for multi-indexed DataFrames, in which
case you will need to reduce the DataFrame to a single index.

Also note that the DataFrame widget will eventually be replaced with the
Tabulator widget, and so new code should be written to use Tabulator
instead.

Reference:
[https://panel.holoviz.org/reference/widgets/DataFrame.html](https://panel.holoviz.org/reference/widgets/DataFrame.html)

Example:

\>\>\>
DataFrame(df,
name='DataFrame')

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> [title="panel.widgets.tables.BaseTable"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.tables.BaseTable](#panel.widgets.tables.BaseTable):
> value, selection, aggregators, editables, editors, formatters,
> hierarchical, row_height, show_index, sorters, text_align, titles,
> widths
>
>

`auto_edit`` ``=`` ``Boolean(default=False,`` ``label='Auto`` ``edit')`
Whether clicking on a table cell automatically starts edit mode.

`autosize_mode`` ``=`` ``Selector(default='force_fit',`` ``label='Autosize`` ``mode',`` ``names={},`` ``objects=['none',`` ``'fit_columns',`` ``'fit_viewport',`` ``'force_fit'])`
Determines the column autosizing mode, as one of the following options:
`"fit_columns"` Compute column widths based on
cell contents while ensuring the table fits into the available viewport.
This results in no horizontal scrollbar showing up, but data can get
unreadable if there is not enough space available.
`"fit_viewport"` Adjust the viewport size after
computing column widths based on cell contents.
`"force_fit"` Fit columns into available space
dividing the table width across the columns equally (equivalent to
fit_columns=True). This results in no horizontal scrollbar showing up,
but data can get unreadable if there is not enough space available.
`"none"` Do not automatically compute column
widths.

`fit_columns`` ``=`` ``Boolean(allow_None=True,`` ``label='Fit`` ``columns')`
Whether columns should expand to the available width. This results in no
horizontal scrollbar showing up, but data can get unreadable if there is
no enough space available.

`frozen_columns`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Frozen`` ``columns')`
Integer indicating the number of columns to freeze. If set, the first N
columns will be frozen, which prevents them from scrolling out of frame.

`frozen_rows`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Frozen`` ``rows')`
Integer indicating the number of rows to freeze. If set, the first N
rows will be frozen, which prevents them from scrolling out of frame; if
set to a negative value the last N rows will be frozen.

`reorderable`` ``=`` ``Boolean(default=True,`` ``label='Reorderable')`
Allows the reordering of a table’s columns. To reorder a column, click
and drag a table’s header to the desired location in the table. The
columns on either side will remain in their previous order.

`sortable`` ``=`` ``Boolean(default=True,`` ``label='Sortable')`
Allows to sort table’s contents. By default natural order is preserved.
To sort a column, click on its header. Clicking one more time changes
sort direction. Use Ctrl + click to return to natural order. Use Shift +
click to sort multiple columns simultaneously.

class panel.widgets.tables.GroupSpec
Bases: `TypedDict`

class panel.widgets.tables.Tabulator(value=None, **params)
Bases:
[BaseTable](#panel.widgets.tables.BaseTable)

The Tabulator widget wraps the \[Tabulator
js\]([http://tabulator.info/](http://tabulator.info/)) table to provide
a full-featured, very powerful interactive table.

Reference:
[https://panel.holoviz.org/reference/widgets/Tabulator.html](https://panel.holoviz.org/reference/widgets/Tabulator.html)

Example:

\>\>\>
Tabulator(df,
theme='site',
pagination='remote',
page_size=25)

Attributes:
[current_view](#panel.widgets.tables.Tabulator.current_view)
Returns the current view of the table after filtering and sorting are
applied.

Methods

|  |  |
|----|----|
| [download](#panel.widgets.tables.Tabulator.download)(\[filename\]) | Triggers downloading of the table as a CSV or JSON. |
| [download_menu](#panel.widgets.tables.Tabulator.download_menu)(\[text_kwargs, button_kwargs\]) | Returns a menu containing a TextInput and Button widget to set the filename and trigger a client-side download of the data. |
| [on_click](#panel.widgets.tables.Tabulator.on_click)(callback\[, column\]) | Register a callback to be executed when any cell is clicked. |
| [on_edit](#panel.widgets.tables.Tabulator.on_edit)(callback) | Register a callback to be executed when a cell is edited. |
| [stream](#panel.widgets.tables.Tabulator.stream)(stream_value\[, rollover, ...\]) | Streams (appends) the stream_value provided to the existing value in an efficient manner. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> [title="panel.widgets.tables.BaseTable"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.tables.BaseTable](#panel.widgets.tables.BaseTable):
> value, aggregators, editables, editors, formatters, hierarchical,
> show_index, sorters, text_align, titles, widths
>
>

`selection`` ``=`` ``_ListValidateWithCallable(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'int'>,`` ``label='Selection')`
The currently selected rows of the table. It validates its values
against ‘selectable_rows’ if used.

`row_height`` ``=`` ``Integer(allow_refs=True,`` ``default=30,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Row`` ``height')`
The height of each table row.

`buttons`` ``=`` ``Dict(allow_refs=True,`` ``class_=<class`` ``'dict'>,`` ``default={},`` ``label='Buttons',`` ``nested_refs=True)`
Dictionary mapping from column name to a HTML element to use as the
button icon.

`container_popup`` ``=`` ``Boolean(allow_refs=True,`` ``default=True,`` ``label='Container`` ``popup')`
If True, popups will appear within the table container, otherwise popups
will be appended to the body element of the DOM.

`expanded`` ``=`` ``List(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'int'>,`` ``label='Expanded',`` ``nested_refs=True)`
List of expanded rows, only applicable if a row_content function has
been defined.

`embed_content`` ``=`` ``Boolean(allow_refs=True,`` ``default=False,`` ``label='Embed`` ``content')`
Whether to embed the row_content or render it dynamically when a row is
expanded.

`filters`` ``=`` ``List(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'dict'>,`` ``label='Filters')`
List of client-side filters declared as dictionaries containing ‘field’,
‘type’ and ‘value’ keys.

`frozen_columns`` ``=`` ``ClassSelector(allow_refs=True,`` ``class_=(<class`` ``'list'>,`` ``<class`` ``'dict'>),`` ``default=[],`` ``label='Frozen`` ``columns',`` ``nested_refs=True)`
One of: - List indicating the columns to freeze. The column(s) may be
selected by name or index. - Dict indicating columns to freeze as keys
and their freeze location as values, freeze location is either ‘right’
or ‘left’.

`frozen_rows`` ``=`` ``List(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'int'>,`` ``label='Frozen`` ``rows',`` ``nested_refs=True)`
List indicating the rows to freeze. If set, the first N rows will be
frozen, which prevents them from scrolling out of frame; if set to a
negative value the last N rows will be frozen.

`groups`` ``=`` ``Dict(allow_refs=True,`` ``class_=<class`` ``'dict'>,`` ``default={},`` ``label='Groups',`` ``nested_refs=True)`
Dictionary mapping defining the groups.

`groupby`` ``=`` ``List(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'str'>,`` ``label='Groupby',`` ``nested_refs=True)`
Groups rows in the table by one or more columns.

`header_align`` ``=`` ``ClassSelector(allow_refs=True,`` ``class_=(<class`` ``'dict'>,`` ``<class`` ``'str'>),`` ``default={},`` ``label='Header`` ``align',`` ``nested_refs=True)`
A mapping from column name to alignment or a fixed column alignment,
which should be one of ‘left’, ‘center’, ‘right’.

`header_filters`` ``=`` ``ClassSelector(allow_None=True,`` ``allow_refs=True,`` ``class_=(<class`` ``'bool'>,`` ``<class`` ``'dict'>),`` ``label='Header`` ``filters',`` ``nested_refs=True)`
Whether to enable filters in the header or dictionary configuring
filters for each column.

`header_tooltips`` ``=`` ``Dict(allow_refs=True,`` ``class_=<class`` ``'dict'>,`` ``default={},`` ``label='Header`` ``tooltips')`
Dictionary mapping from column name to a tooltip to show when hovering
over the column header.

`hidden_columns`` ``=`` ``List(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'str'>,`` ``label='Hidden`` ``columns',`` ``nested_refs=True)`
List of columns to hide.

`movable_columns`` ``=`` ``Boolean(allow_refs=True,`` ``default=False,`` ``label='Movable`` ``columns')`
Whether columns can be reordered by dragging their headers.

`layout`` ``=`` ``Selector(allow_refs=True,`` ``default='fit_data_table',`` ``label='Layout',`` ``names={},`` ``objects=['fit_data',`` ``'fit_data_fill',`` ``'fit_data_stretch',`` ``'fit_data_table',`` ``'fit_columns'])`
Describes the column layout mode with one of the following options
‘fit_columns’, ‘fit_data’, ‘fit_data_stretch’, ‘fit_data_fill’,
‘fit_data_table’.

`initial_page_size`` ``=`` ``Integer(allow_refs=True,`` ``bounds=(1,`` ``None),`` ``default=20,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Initial`` ``page`` ``size')`
Initial page size if page_size is None and therefore automatically set.

`pagination`` ``=`` ``Selector(allow_None=True,`` ``allow_refs=True,`` ``label='Pagination',`` ``names={},`` ``objects=['local',`` ``'remote'])`
Defines the pagination mode of the Tabulator. - None No pagination is
applied, all rows are rendered. - ‘local’ (client-side) Pagination is
applied locally, i.e. the entire DataFrame is loaded and then
paginated. - ‘remote’ (server-side) Pagination is applied remotely, i.e.
only the current page is loaded from the server.

`page`` ``=`` ``Integer(allow_refs=True,`` ``default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Page')`
Currently selected page (indexed starting at 1), if pagination is
enabled.

`page_size`` ``=`` ``Integer(allow_None=True,`` ``allow_refs=True,`` ``bounds=(1,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Page`` ``size')`
Number of rows to render per page, if pagination is enabled.

`row_content`` ``=`` ``Callable(allow_None=True,`` ``label='Row`` ``content')`
A function which is given the DataFrame row and should return a Panel
object to render as additional detail below the row. The function may
also be asynchronous.

`selectable`` ``=`` ``ClassSelector(allow_refs=True,`` ``class_=(<class`` ``'bool'>,`` ``<class`` ``'str'>,`` ``<class`` ``'int'>),`` ``default=True,`` ``label='Selectable')`
Defines the selection mode of the Tabulator. - True Selects rows on
click. To select multiple use Ctrl-select, to select a range use
Shift-select - False Disables selection - ‘checkbox’ Adds a column of
checkboxes to toggle selections - ‘checkbox-single’ Same as ‘checkbox’
but header does not allow select/deselect all - ‘toggle’ Selection
toggles when clicked - int The maximum number of selectable rows.

`selectable_rows`` ``=`` ``Callable(allow_None=True,`` ``allow_refs=True,`` ``label='Selectable`` ``rows')`
A function which given a DataFrame should return a list of rows by
integer index, which are selectable.

`sortable`` ``=`` ``ClassSelector(allow_refs=True,`` ``class_=(<class`` ``'bool'>,`` ``<class`` ``'dict'>),`` ``default=True,`` ``label='Sortable')`
Whether the columns in the table should be sortable. Can either be
specified as a simple boolean toggling the behavior on and off or as a
dictionary specifying the option per column.

`theme`` ``=`` ``Selector(allow_refs=True,`` ``default='simple',`` ``label='Theme',`` ``names={},`` ``objects=['default',`` ``'site',`` ``'simple',`` ``'midnight',`` ``'modern',`` ``'bootstrap',`` ``'bootstrap4',`` ``'materialize',`` ``'bulma',`` ``'semantic-ui',`` ``'fast',`` ``'bootstrap5'])`
Tabulator CSS theme to apply to table.

`theme_classes`` ``=`` ``List(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'str'>,`` ``label='Theme`` ``classes',`` ``nested_refs=True)`
List of extra CSS classes to apply to the Tabulator element to customize
the theme.

`title_formatters`` ``=`` ``Dict(allow_refs=True,`` ``class_=<class`` ``'dict'>,`` ``default={},`` ``label='Title`` ``formatters',`` ``nested_refs=True)`
Tabulator formatter specification to use for a particular column header
title.

property current_view: pd.DataFrame
Returns the current view of the table after filtering and sorting are
applied.

download(filename: str = 'table.csv')
Triggers downloading of the table as a CSV or JSON.

Parameters:
**filename: str**
The filename to save the table as.

download_menu(text_kwargs={}, button_kwargs={})
Returns a menu containing a TextInput and Button widget to set the
filename and trigger a client-side download of the data.

Parameters:
**text_kwargs: dict**
Keyword arguments passed to the TextInput constructor

**button_kwargs: dict**
Keyword arguments passed to the Button constructor

Returns:
filename: TextInput
The TextInput widget setting a filename.

button: Button
The Button that triggers a download.

on_click(callback: Callable\[\[CellClickEvent\], None\], column: str \| None = None)
Register a callback to be executed when any cell is clicked. The
callback is given a CellClickEvent declaring the column and row of the
cell that was clicked.

Parameters:
**callback: (callable)**
The callback to run on edit events.

**column: (str)**
Optional argument restricting the callback to a specific column.

on_edit(callback: Callable\[\[TableEditEvent\], None\])
Register a callback to be executed when a cell is edited. Whenever a
cell is edited on_edit callbacks are called with a TableEditEvent as the
first argument containing the column, row and value of the edited cell.

Parameters:
**callback: (callable)**
The callback to run on edit events.

stream(stream_value, rollover=None, reset_index=True, follow=True)
Streams (appends) the stream_value provided to the existing value in an
efficient manner.

Parameters:
**stream_value: (pd.DataFrame \| pd.Series \| Dict)**
The new value(s) to append to the existing value.

**rollover: int**
A maximum column size, above which data from the start of the column
begins to be discarded. If None, then columns will continue to grow
unbounded.

**reset_index: (bool, default=True)**
If True and the stream_value is a DataFrame, then its index is reset.
Helps to keep the index unique and named index

Raises:
ValueError: Raised if the stream_value is not a supported type.

Examples

Stream a Series to a DataFrame \>\>\> value = pd.DataFrame({“x”: \[1,
2\], “y”: \[“a”, “b”\]}) \>\>\> tabulator = Tabulator(value=value)
\>\>\> stream_value = pd.Series({“x”: 4, “y”: “d”}) \>\>\>
tabulator.stream(stream_value) \>\>\> tabulator.value.to_dict(“list”)
{‘x’: \[1, 2, 4\], ‘y’: \[‘a’, ‘b’, ‘d’\]}

Stream a Dataframe to a Dataframe \>\>\> value = pd.DataFrame({“x”: \[1,
2\], “y”: \[“a”, “b”\]}) \>\>\> tabulator = Tabulator(value=value)
\>\>\> stream_value = pd.DataFrame({“x”: \[3, 4\], “y”: \[“c”, “d”\]})
\>\>\> tabulator.stream(stream_value) \>\>\>
tabulator.value.to_dict(“list”) {‘x’: \[1, 2, 3, 4\], ‘y’: \[‘a’, ‘b’,
‘c’, ‘d’\]}

Stream a Dictionary row to a DataFrame \>\>\> value = pd.DataFrame({“x”:
\[1, 2\], “y”: \[“a”, “b”\]}) \>\>\> tabulator = Tabulator(value=value)
\>\>\> stream_value = {“x”: 4, “y”: “d”} \>\>\>
tabulator.stream(stream_value) \>\>\> tabulator.value.to_dict(“list”)
{‘x’: \[1, 2, 4\], ‘y’: \[‘a’, ‘b’, ‘d’\]}

Stream a Dictionary of Columns to a Dataframe \>\>\> value =
pd.DataFrame({“x”: \[1, 2\], “y”: \[“a”, “b”\]}) \>\>\> tabulator =
Tabulator(value=value) \>\>\> stream_value = {“x”: \[3, 4\], “y”: \[“c”,
“d”\]} \>\>\> tabulator.stream(stream_value) \>\>\>
tabulator.value.to_dict(“list”) {‘x’: \[1, 2, 3, 4\], ‘y’: \[‘a’, ‘b’,
‘c’, ‘d’\]}

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
