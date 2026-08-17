# panel.pane.vizzu module

class panel.pane.vizzu.Vizzu(object=None, **params)
Bases: [ModelPane](panel.pane.base.md#panel.pane.base.ModelPane),
`SyncableData`

The Vizzu pane provides an interactive visualization component for
large, real-time datasets built on the Vizzu project.

Reference:
[https://panel.holoviz.org/reference/panes/Vizzu.html](https://panel.holoviz.org/reference/panes/Vizzu.html)

Example:

\>\>\>
Vizzu(df)

Methods

|  |  |
|----|----|
| [animate](#panel.pane.vizzu.Vizzu.animate)(anim\[, options\]) | Updates the chart with a new configuration. |
| [applies](#panel.pane.vizzu.Vizzu.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |
| [on_click](#panel.pane.vizzu.Vizzu.on_click)(callback) | Register a callback to be executed when any element in the chart is clicked on. |

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
> `panel.reactive.SyncableData`: selection
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
>

`animation`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Animation',`` ``nested_refs=True)`
Animation settings (see
[https://lib.vizzuhq.com/latest/reference/modules/Anim/](https://lib.vizzuhq.com/latest/reference/modules/Anim/)).

`config`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Config',`` ``nested_refs=True)`
The config contains all of the parameters needed to render a particular
static chart or a state of an animated chart (see [https://lib.vizzuhq.com/latest/reference/interfaces/Config.Chart/](https://lib.vizzuhq.com/latest/reference/interfaces/Config.Chart/)).

`click`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Click')`
Data associated with the latest click event.

`column_types`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Column`` ``types',`` ``nested_refs=True)`
Optional column definitions. If not defined will be inferred from the
data.

`duration`` ``=`` ``Integer(default=500,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Duration')`
The config contains all of the parameters needed to render a particular
static chart or a state of an animated chart.

`style`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Style',`` ``nested_refs=True)`
Style configuration of the chart.

`tooltip`` ``=`` ``Boolean(default=False,`` ``label='Tooltip')`
Whether to enable tooltips on the chart.

animate(anim: dict\[str, Any\], options: int \| dict\[str, Any\] \| None = None) → None
Updates the chart with a new configuration.

classmethod applies(object)
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

on_click(callback: Callable\[\[dict\], None\])
Register a callback to be executed when any element in the chart is
clicked on.

Parameters:
**callback: (callable)**
The callback to run on click events.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
