# panel.pane.holoviews module

HoloViews integration for Panel including a Pane to render HoloViews

objects and their widgets and support for Links

class panel.pane.holoviews.HoloViews(object=None, **params)
Bases: [Pane](panel.pane.base.md#panel.pane.base.Pane)

HoloViews panes render any HoloViews object using the currently selected
backend (‘bokeh’ (default), ‘matplotlib’ or ‘plotly’).

To be able to use the plotly backend you must add plotly to
pn.extension.

Reference:
[https://panel.holoviz.org/reference/panes/HoloViews.html](https://panel.holoviz.org/reference/panes/HoloViews.html)

Example:

\>\>\>
HoloViews(some_holoviews_object)

Methods

|  |  |
|----|----|
| [applies](#panel.pane.holoviews.HoloViews.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |
| [jslink](#panel.pane.holoviews.HoloViews.jslink)(target\[, code, args, bidirectional\]) | Links properties on the this Reactive object to those on the target Reactive object in JS code. |

|                             |     |
|-----------------------------|-----|
| **widgets_from_dimensions** |     |

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

`backend`` ``=`` ``Selector(label='Backend',`` ``names={},`` ``objects=['bokeh',`` ``'matplotlib',`` ``'plotly'])`
The HoloViews backend used to render the plot (if None defaults to the
currently selected renderer).

`center`` ``=`` ``Boolean(default=False,`` ``label='Center')`
Whether to center the plot.

`default_widgets`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``constant=True,`` ``default={'date':`` ``<class`` ``'panel.widgets.input.DatetimeInput'>,`` ``'discrete':`` ``<class`` ``'panel.widgets.select.Select'>,`` ``'discrete_numeric':`` ``<class`` ``'panel.widgets.slider.DiscreteSlider'>,`` ``'float':`` ``(<class`` ``'panel.widgets.slider.FloatSlider'>,`` ``<class`` ``'panel.widgets.slider.EditableFloatSlider'>),`` ``'int':`` ``(<class`` ``'panel.widgets.slider.IntSlider'>,`` ``<class`` ``'panel.widgets.slider.EditableIntSlider'>),`` ``'scrubber':`` ``<class`` ``'panel.widgets.player.Player'>},`` ``label='Default`` ``widgets')`
Mapping that determines which widgets are used by default when
constructing interactive controls for HoloViews dimensions. Keys and
expected values: - `'date'`: For datetime
ranges. - `'discrete'`: For categorical
values. - `'discrete_numeric'`: For discrete,
numeric values. - `'float'`: For continuous
floating-point ranges. - `'int'`: For integer
ranges. - `'scrubber'`: For stepping through
frame sequences. Note that float and int widgets may be given a tuple to
select between the static case (i.e. a HoloMap) and dynamic case (i.e. a
DynamicMap).

`format`` ``=`` ``Selector(default='png',`` ``label='Format',`` ``names={},`` ``objects=['png',`` ``'svg'])`
The format to render Matplotlib plots with.

`linked_axes`` ``=`` ``Boolean(default=True,`` ``label='Linked`` ``axes')`
Whether to link the axes of bokeh plots inside this pane across a panel
layout.

`renderer`` ``=`` ``Parameter(allow_None=True,`` ``label='Renderer')`
Explicit renderer instance to use for rendering the HoloViews plot.
Overrides the backend.

`theme`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'bokeh.themes.theme.Theme'>,`` ``<class`` ``'str'>),`` ``label='Theme')`
Bokeh theme to apply to the HoloViews plot.

`widget_location`` ``=`` ``Selector(default='right_top',`` ``label='Widget`` ``location',`` ``names={},`` ``objects=['left',`` ``'bottom',`` ``'right',`` ``'top',`` ``'top_left',`` ``'top_right',`` ``'bottom_left',`` ``'bottom_right',`` ``'left_top',`` ``'left_bottom',`` ``'right_top',`` ``'right_bottom'])`
The layout of the plot and the widgets. The value refers to the position
of the widgets relative to the plot.

`widget_layout`` ``=`` ``Selector(constant=True,`` ``default=<class`` ``'panel.layout.base.WidgetBox'>,`` ``label='Widget`` ``layout',`` ``names={},`` ``objects=[<class`` ``'panel.layout.base.WidgetBox'>,`` ``<class`` ``'panel.layout.base.Row'>,`` ``<class`` ``'panel.layout.base.Column'>])`
The layout object to display the widgets in.

`widget_type`` ``=`` ``Selector(default='individual',`` ``label='Widget`` ``type',`` ``names={},`` ``objects=['individual',`` ``'scrubber'])`
Whether to generate individual widgets for each dimension or on global
scrubber.

`widgets`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Widgets')`
A mapping from dimension name to a widget instance which will be used to
override the default widgets.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

jslink(target, code=None, args=None, bidirectional=False, **links)
Links properties on the this Reactive object to those on the target
Reactive object in JS code.

Supports two modes, either specify a mapping between the source and
target model properties as keywords or provide a dictionary of JS code
snippets which maps from the source parameter to a JS code snippet which
is executed when the property changes.

Parameters:
**target: panel.viewable.Viewable \| bokeh.model.Model \| holoviews.core.dimension.Dimensioned**
The target to link the value to.

**code: dict**
Custom code which will be executed when the widget value changes.

**args: dict**
A mapping of objects to make available to the JS callback

**bidirectional: boolean**
Whether to link source and target bi-directionally

**links: dict**
A mapping between properties on the source model and the target model
property to link it to.

Returns:
link: GenericLink
The GenericLink which can be used unlink the widget and the target
model.

widget_layout
alias of [WidgetBox](panel.layout.base.md#panel.layout.base.WidgetBox)

class panel.pane.holoviews.Interactive(object=None, **params)
Bases: [Pane](panel.pane.base.md#panel.pane.base.Pane)

Attributes:
**priority**

Methods

|  |  |
|----|----|
| [applies](#panel.pane.holoviews.Interactive.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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

`object`` ``=`` ``Parameter(allow_None=True,`` ``label='Object')`
The object being wrapped, which will be converted to a Bokeh model.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

priority: t.ClassVar\[float \| bool \| None\] = None

panel.pane.holoviews.find_links(root_view, root_model)
Traverses the supplied Viewable searching for Links between any
HoloViews based panes.

panel.pane.holoviews.generate_panel_bokeh_map(root_model, panel_views)
mapping panel elements to its bokeh models

panel.pane.holoviews.is_bokeh_element_plot(plot)
Checks whether plotting instance is a HoloViews ElementPlot rendered
with the bokeh backend.

panel.pane.holoviews.link_axes(root_view, root_model)
Pre-processing hook to allow linking axes across HoloViews bokeh plots.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
