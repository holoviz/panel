# panel.pane.vega module

class panel.pane.vega.Vega(object=None, **params)
Bases: [ModelPane](panel.pane.base.md#panel.pane.base.ModelPane)

The Vega pane renders Vega-lite based plots (including those from
Altair) inside a panel.

Note

- to use the Vega pane, the Panel extension has to be

loaded with ‘vega’ as an argument to ensure that vega.js is
initialized. - it supports selection events - it optimizes the plot
rendering by using binary serialization for any array data found on the
Vega/Altair object, providing huge speedups over the standard JSON
serialization employed by Vega natively.

Reference: [https://panel.holoviz.org/reference/panes/Vega.html](https://panel.holoviz.org/reference/panes/Vega.html)

Example:

\>\>\>
pn.extension('vega')
\>\>\>
Vega(some_vegalite_dict_or_altair_object,
height=240)

Methods

|  |  |
|----|----|
| [applies](#panel.pane.vega.Vega.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |
| [export](#panel.pane.vega.Vega.export)(fmt\[, as_pane\]) | Exports the Vega spec to various formats. |

|               |     |
|---------------|-----|
| **is_altair** |     |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
>

`debounce`` ``=`` ``ClassSelector(class_=(<class`` ``'int'>,`` ``<class`` ``'dict'>),`` ``default=20,`` ``label='Debounce')`
Declares the debounce time in milliseconds either for all events or if a
dictionary is provided for individual events.

`selection`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'param.parameterized.Parameterized'>,`` ``label='Selection')`
The Selection object reflects any selections available on the supplied
vega plot into Python.

`show_actions`` ``=`` ``Boolean(default=False,`` ``label='Show`` ``actions')`
Whether to show Vega actions.

`theme`` ``=`` ``Selector(allow_None=True,`` ``label='Theme',`` ``names={},`` ``objects=['excel',`` ``'ggplot2',`` ``'quartz',`` ``'vox',`` ``'fivethirtyeight',`` ``'dark',`` ``'latimes',`` ``'urbaninstitute',`` ``'googlecharts'])`
A theme to apply to the plot. Must be one of ‘excel’, ‘ggplot2’,
‘quartz’, ‘vox’, ‘fivethirtyeight’, ‘dark’, ‘latimes’, ‘urbaninstitute’,
or ‘googlecharts’.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

export(fmt: VEGA_EXPORT_FORMATS, as_pane: bool = False, **kwargs: dict) → bytes \| str \| dict \| ModelPane
Exports the Vega spec to various formats.

The export method converts the Vega/Altair specification to different
output formats. It requires vl-convert-python to be installed.

Parameters:
fmt : str
The format to export to. Must be one of ‘png’, ‘jpeg’, ‘svg’, ‘pdf’,
‘html’, ‘url’, ‘scenegraph’.

as_pane : bool, default False
If True, wraps the exported data in the appropriate Panel pane.

**kwargs : dict
Additional keyword arguments passed to the vl-convert functions.

Returns:
bytes \| str \| ModelPane
The exported data in the requested format, or a Panel pane if
as_pane=True.

Raises:
ImportError
If vl-convert-python is not installed.

ValueError
If an unsupported format is specified.

Examples

\>\>\> vega_pane
=
Vega(spec_dict)
\>\>\> png_bytes
=
vega_pane.export('png')
\>\>\> image_pane
=
vega_pane.export('png',
as_pane=True)

panel.pane.vega.ds_as_cds(dataset)
Converts Vega dataset into Bokeh ColumnDataSource data
(Narwhals-compatible)

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
