# panel.pane.plotly module

Defines a PlotlyPane which renders a plotly plot using PlotlyPlot bokeh
model.

class panel.pane.plotly.Plotly(object=None, **params)
Bases: [ModelPane](panel.pane.base.md#panel.pane.base.ModelPane)

The Plotly pane renders Plotly plots inside a panel.

Note that

- the Panel extension has to be loaded with plotly as an argument to

ensure that Plotly.js is initialized. - it supports click, hover and
selection events. - it optimizes the plot rendering by using binary
serialization for any array data found on the Plotly object.

Reference:
[https://panel.holoviz.org/reference/panes/Plotly.html](https://panel.holoviz.org/reference/panes/Plotly.html)

Example:

\>\>\>
pn.extension('plotly')
\>\>\>
Plotly(some_plotly_figure,
width=500,
height=500)

Methods

|  |  |
|----|----|
| [applies](#panel.pane.plotly.Plotly.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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

`click_data`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Click`` ``data')`
Click event data from plotly_click event.

`doubleclick_data`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Doubleclick`` ``data')`
Click event data from plotly_doubleclick event.

`clickannotation_data`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Clickannotation`` ``data')`
Clickannotation event data from plotly_clickannotation event.

`config`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Config',`` ``nested_refs=True)`
Plotly configuration options. See
[https://plotly.com/javascript/configuration-options/](https://plotly.com/javascript/configuration-options/)

`hover_data`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Hover`` ``data')`
Hover event data from plotly_hover and plotly_unhover events.

`link_figure`` ``=`` ``Boolean(default=True,`` ``label='Link`` ``figure')`
Attach callbacks to the Plotly figure to update output when it is
modified in place.

`relayout_data`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Relayout`` ``data',`` ``nested_refs=True)`
Relayout event data from plotly_relayout event

`restyle_data`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``label='Restyle`` ``data',`` ``nested_refs=True)`
Restyle event data from plotly_restyle event

`selected_data`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Selected`` ``data',`` ``nested_refs=True)`
Selected event data from plotly_selected and plotly_deselect events.

`viewport`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Viewport',`` ``nested_refs=True)`
Current viewport state, i.e. the x- and y-axis limits of the displayed
plot. Updated on plotly_relayout, plotly_relayouting and plotly_restyle
events.

`viewport_update_policy`` ``=`` ``Selector(default='mouseup',`` ``label='Viewport`` ``update`` ``policy',`` ``names={},`` ``objects=['mouseup',`` ``'continuous',`` ``'throttle'])`
Policy by which the viewport parameter is updated during user
interactions. \* “mouseup”: updates are synchronized when mouse button
is released after panning \* “continuous”: updates are synchronized
continually while panning \* “throttle”: updates are synchronized while
panning, at intervals determined by the viewport_update_throttle
parameter

`viewport_update_throttle`` ``=`` ``Integer(bounds=(0,`` ``None),`` ``default=200,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Viewport`` ``update`` ``throttle')`
Time interval in milliseconds at which viewport updates are synchronized
when viewport_update_policy is “throttle”.

`_render_count`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``render`` ``count')`
Number of renders, increment to trigger re-render

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
