# panel.pane.perspective module

class panel.pane.perspective.Perspective(object=None, **params)
Bases: [ModelPane](panel.pane.base.md#panel.pane.base.ModelPane),
[ReactiveData](panel.reactive.md#panel.reactive.ReactiveData)

The Perspective pane provides an interactive visualization component for
large, real-time datasets built on the Perspective project.

Reference:
[https://panel.holoviz.org/reference/panes/Perspective.html](https://panel.holoviz.org/reference/panes/Perspective.html)

Example:

\>\>\>
Perspective(df,
plugin='hypergrid',
theme='pro-dark')

Attributes:
**priority**

Methods

|  |  |
|----|----|
| [applies](#panel.pane.perspective.Perspective.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |
| [on_click](#panel.pane.perspective.Perspective.on_click)(callback) | Register a callback to be executed when any row is clicked. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_height,
> max_width, max_height, styles, stylesheets, tags, width, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> `panel.reactive.SyncableData`: selection
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout
>
>

`min_width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=420,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Min`` ``width')`
Minimal width of the component (in pixels) if width is adjustable.

`object`` ``=`` ``Parameter(allow_None=True,`` ``allow_refs=True,`` ``label='Object')`
The plot data declared as a dictionary of arrays or a DataFrame.

`aggregates`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Aggregates',`` ``nested_refs=True)`
How to aggregate. For example {“x”: “distinct count”}

`columns`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``item_type=(<class`` ``'str'>,`` ``<class`` ``'int'>),`` ``label='Columns',`` ``nested_refs=True)`
A list of source columns to show as columns. For example \[“x”, “y”\]

`columns_config`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Columns`` ``config',`` ``nested_refs=True)`
Column configuration allowing specification of formatters, coloring and
a variety of other attributes for each column.

`editable`` ``=`` ``Boolean(allow_None=True,`` ``default=True,`` ``label='Editable')`
Whether items are editable.

`expressions`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'dict'>,`` ``<class`` ``'list'>),`` ``label='Expressions',`` ``nested_refs=True)`
A list of expressions computing new columns from existing columns. For
example \[“”x”+”index””\]

`split_by`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``item_type=(<class`` ``'str'>,`` ``<class`` ``'int'>),`` ``label='Split`` ``by',`` ``nested_refs=True)`
A list of source columns to pivot by. For example \[“x”, “y”\]

`filters`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``item_type=(<class`` ``'tuple'>,`` ``<class`` ``'list'>),`` ``label='Filters',`` ``nested_refs=True)`
How to filter. For example \[\[“x”, “\<”, 3\],\[“y”, “contains”,
“abc”\]\]

`group_by`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``item_type=(<class`` ``'str'>,`` ``<class`` ``'int'>),`` ``label='Group`` ``by')`
A list of source columns to group by. For example \[“x”, “y”\]

`selectable`` ``=`` ``Boolean(allow_None=True,`` ``default=True,`` ``label='Selectable')`
Whether items are selectable.

`sort`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``item_type=(<class`` ``'str'>,`` ``<class`` ``'int'>,`` ``<class`` ``'tuple'>,`` ``<class`` ``'list'>),`` ``label='Sort')`
How to sort. For example\[\[“x”,”desc”\]\]

`plugin`` ``=`` ``Selector(default='datagrid',`` ``label='Plugin',`` ``names={},`` ``objects=['hypergrid',`` ``'datagrid',`` ``'d3_y_bar',`` ``'d3_x_bar',`` ``'d3_xy_line',`` ``'d3_y_line',`` ``'d3_y_area',`` ``'d3_y_scatter',`` ``'d3_xy_scatter',`` ``'d3_treemap',`` ``'d3_sunburst',`` ``'d3_heatmap',`` ``'d3_candlestick',`` ``'d3_ohlc'])`
The name of a plugin to display the data. For example hypergrid or
d3_xy_scatter.

`plugin_config`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Plugin`` ``config',`` ``nested_refs=True)`
Configuration for the PerspectiveViewerPlugin.

`settings`` ``=`` ``Boolean(default=True,`` ``label='Settings')`
Whether to show the settings menu.

`theme`` ``=`` ``Selector(default='pro',`` ``label='Theme',`` ``names={},`` ``objects=['material',`` ``'material-dark',`` ``'monokai',`` ``'solarized',`` ``'solarized-dark',`` ``'vaporwave',`` ``'pro',`` ``'pro-dark'])`
The style of the PerspectiveViewer. For example pro-dark

`title`` ``=`` ``String(allow_None=True,`` ``label='Title')`
Title for the Perspective viewer.

classmethod applies(object)
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

on_click(callback: Callable\[\[PerspectiveClickEvent\], None\])
Register a callback to be executed when any row is clicked. The callback
is given a PerspectiveClickEvent declaring the config, column names, and
row values of the row that was clicked.

Parameters:
**callback: (callable)**
The callback to run on edit events.

priority: t.ClassVar\[float \| bool \| None\] = None

class panel.pane.perspective.Plugin(value)
Bases: `Enum`

The plugins (grids/charts) available in Perspective. Pass these into the
plugin arg in PerspectiveWidget or PerspectiveViewer.

static options()
Returns the list of options of the PerspectiveViewer, like Hypergrid,
Grid etc.

Returns:
options: list
A list of available options

panel.pane.perspective.deconstruct_pandas(data, kwargs=None)
Given a dataframe, flatten it by resetting the index and memoizing the
pivots that were applied.

This code was copied from the Perspective repository and is reproduced
under Apache 2.0 license. See the original at:

[finos/perspective](https://github.com/finos/perspective/blob/master/python/perspective/perspective/core/data/pd.py)

Parameters:
**data: (pandas.dataframe)**
A Pandas DataFrame to parse

Returns:
data: pandas.DataFrame
A flattened version of the DataFrame

kwargs: dict
A dictionary containing optional members columns, group_by, and
split_by.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
