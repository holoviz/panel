# panel.pane.echarts module

class panel.pane.echarts.ECharts(object=None, **params)
Bases: [ModelPane](panel.pane.base.md#panel.pane.base.ModelPane)

ECharts panes allow rendering echarts.js dictionaries and pyecharts
plots.

Reference:
[https://panel.holoviz.org/reference/panes/ECharts.html](https://panel.holoviz.org/reference/panes/ECharts.html)

Example:

\>\>\>
pn.extension('echarts')
\>\>\>
ECharts(some_echart_dict_or_pyecharts_object,
height=480,
width=640)

Attributes:
**priority**

Methods

|  |  |
|----|----|
| [applies](#panel.pane.echarts.ECharts.applies)(object, **params) | Returns boolean or float indicating whether the Pane can render the object. |
| [js_on_event](#panel.pane.echarts.ECharts.js_on_event)(event, callback\[, query\]) | Register a Javascript event handler which triggers when the specified event is triggered. |
| [on_event](#panel.pane.echarts.ECharts.on_event)(event, callback\[, query\]) | Register anevent handler which triggers when the specified event is triggered. |

|                  |     |
|------------------|-----|
| **is_pyecharts** |     |

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
> margin, default_layout
>
>

`object`` ``=`` ``Parameter(allow_None=True,`` ``allow_refs=True,`` ``label='Object')`
The Echarts object being wrapped. Can be an Echarts dictionary or a
pyecharts chart

`options`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Options')`
An optional dict of options passed to Echarts.setOption. Allows to
fine-tune the rendering behavior. For example, you might want to use
options={ “replaceMerge”: \[‘series’\] }) when updating the objects with
a value containing a smaller number of series.

`renderer`` ``=`` ``Selector(default='canvas',`` ``label='Renderer',`` ``names={},`` ``objects=['canvas',`` ``'svg'])`
Whether to render as HTML canvas or SVG

`theme`` ``=`` ``Selector(default='default',`` ``label='Theme',`` ``names={},`` ``objects=['default',`` ``'light',`` ``'dark'])`
Theme to apply to plots.

classmethod applies(object: Any, **params) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

js_on_event(event: str, callback: str \| CustomJS, query: str \| None = None, **args)
Register a Javascript event handler which triggers when the specified
event is triggered. The callback can be a snippet of Javascript code or
a bokeh CustomJS object making it possible to manipulate other models in
response to an event.

Reference:
[https://apache.github.io/echarts-handbook/en/concepts/event/](https://apache.github.io/echarts-handbook/en/concepts/event/)

Parameters:
**event: str**
The name of the event to register a handler on, e.g. ‘click’.

**code: str**
The event handler to be executed when the event fires.

**query: str \| None**
A query that determines when the event fires.

**args: Viewable**
A dictionary of Viewables to make available in the namespace of the
object.

on_event(event: str, callback: Callable, query: str \| None = None)
Register anevent handler which triggers when the specified event is
triggered.

Reference:
[https://apache.github.io/echarts-handbook/en/concepts/event/](https://apache.github.io/echarts-handbook/en/concepts/event/)

Parameters:
**event: str**
The name of the event to register a handler on, e.g. ‘click’.

**callback: str \| CustomJS**
The event handler to be executed when the event fires.

**query: str \| None**
A query that determines when the event fires.

priority: t.ClassVar\[float \| bool \| None\] = None

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
