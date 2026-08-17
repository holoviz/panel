# panel.pane.plot module

Pane class which render plots from different libraries

class panel.pane.plot.Bokeh(object=None, **params)
Bases: [Pane](panel.pane.base.md#panel.pane.base.Pane)

The Bokeh pane allows displaying any displayable Bokeh model inside a
Panel app.

Reference:
[https://panel.holoviz.org/reference/panes/Bokeh.html](https://panel.holoviz.org/reference/panes/Bokeh.html)

Example:

\>\>\>
Bokeh(some_bokeh_figure)

Methods

|  |  |
|----|----|
| [applies](#panel.pane.plot.Bokeh.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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

`autodispatch`` ``=`` ``Boolean(default=True,`` ``label='Autodispatch')`
Whether to automatically dispatch events inside bokeh on_change and
on_event callbacks in the notebook.

`theme`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'bokeh.themes.theme.Theme'>,`` ``<class`` ``'str'>),`` ``label='Theme')`
Bokeh theme to apply to the plot.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.plot.Folium(object=None, **params)
Bases: [HTML](panel.pane.markup.md#panel.pane.markup.HTML)

The Folium pane wraps Folium map components.

Methods

|  |  |
|----|----|
| [applies](#panel.pane.plot.Folium.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [class="reference internal" title="panel.pane.markup.HTMLBasePane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
> [class="reference internal" title="panel.pane.markup.HTML"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTML](panel.pane.markup.md#panel.pane.markup.HTML):
> disable_math, sanitize_html, sanitize_hook
>
>

`sizing_mode`` ``=`` ``Selector(default='stretch_width',`` ``label='Sizing`` ``mode',`` ``names={},`` ``objects=['fixed',`` ``'stretch_width',`` ``'stretch_height',`` ``'stretch_both',`` ``'scale_width',`` ``'scale_height',`` ``'scale_both',`` ``None])`
How the component should size itself. This is a high-level setting for
maintaining width and height of the component. To gain more fine grained
control over sizing, use `width_policy`,
`height_policy` and
`aspect_ratio` instead (those take precedence
over `sizing_mode`).
`"fixed"` Component is not responsive. It will
retain its original width and height regardless of any subsequent
browser window resize events. `"stretch_width"`
Component will responsively resize to stretch to the available width,
without maintaining any aspect ratio. The height of the component
depends on the type of the component and may be fixed or fit to
component’s contents. `"stretch_height"`
Component will responsively resize to stretch to the available height,
without maintaining any aspect ratio. The width of the component depends
on the type of the component and may be fixed or fit to component’s
contents. `"stretch_both"` Component is
completely responsive, independently in width and height, and will
occupy all the available horizontal and vertical space, even if this
changes the aspect ratio of the component.
`"scale_width"` Component will responsively
resize to stretch to the available width, while maintaining the original
or provided aspect ratio. `"scale_height"`
Component will responsively resize to stretch to the available height,
while maintaining the original or provided aspect ratio.
`"scale_both"` Component will responsively
resize to both the available width and height, while maintaining the
original or provided aspect ratio.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.plot.Matplotlib(object=None, **params)
Bases: [Image](panel.pane.image.md#panel.pane.image.Image),
[IPyWidget](panel.pane.ipywidget.md#panel.pane.ipywidget.IPyWidget)

The Matplotlib pane allows displaying any displayable Matplotlib figure
inside a Panel app.

- It will render the plot to PNG at the declared DPI and then embed it.

- If you find the figure to be clipped on the edges, you can set
  tight=True

to automatically resize objects to fit within the pane. - If you have
installed ipympl you will also be able to use the interactive backend.

Reference:
[https://panel.holoviz.org/reference/panes/Matplotlib.html](https://panel.holoviz.org/reference/panes/Matplotlib.html)

Example:

\>\>\>
Matplotlib(some_matplotlib_figure,
dpi=144)

Attributes:
**filetype**

Methods

|  |  |
|----|----|
| [applies](#panel.pane.plot.Matplotlib.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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
> [class="reference internal" title="panel.pane.markup.HTMLBasePane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
> [class="reference internal" title="panel.pane.image.FileBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.FileBase](panel.pane.image.md#panel.pane.image.FileBase):
> embed
>
> [class="reference internal" title="panel.pane.image.ImageBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.ImageBase](panel.pane.image.md#panel.pane.image.ImageBase):
> alt_text, caption, fixed_aspect, link_url, target
>
>

`object`` ``=`` ``Parameter(allow_None=True,`` ``allow_refs=True,`` ``label='Object')`
The Matplotlib Figure being wrapped, which will be rendered as a Bokeh
model.

`dpi`` ``=`` ``Integer(bounds=(1,`` ``None),`` ``default=144,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Dpi')`
Scales the dpi of the matplotlib figure.

`encode`` ``=`` ``Boolean(default=False,`` ``label='Encode')`
Whether to encode SVG out as base64.

`format`` ``=`` ``Selector(default='png',`` ``label='Format',`` ``names={},`` ``objects=['png',`` ``'svg'])`
The format to render the plot as if the plot is not interactive.

`high_dpi`` ``=`` ``Boolean(default=True,`` ``label='High`` ``dpi')`
Whether to optimize output for high-dpi displays.

`interactive`` ``=`` ``Boolean(constant=True,`` ``default=False,`` ``label='Interactive')`
Whether to render interactive matplotlib plot with ipympl.

`tight`` ``=`` ``Boolean(default=False,`` ``label='Tight')`
Automatically adjust the figure size to fit the subplots and other
artist elements.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.plot.RGGPlot(object=None, **params)
Bases: [PNG](panel.pane.image.md#panel.pane.image.PNG)

An RGGPlot pane renders an r2py-based ggplot2 figure to png and wraps
the base64-encoded data in a bokeh Div model.

Methods

|  |  |
|----|----|
| [applies](#panel.pane.plot.RGGPlot.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [class="reference internal" title="panel.pane.markup.HTMLBasePane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
> [class="reference internal" title="panel.pane.image.FileBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.FileBase](panel.pane.image.md#panel.pane.image.FileBase):
> embed
>
> [class="reference internal" title="panel.pane.image.ImageBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.ImageBase](panel.pane.image.md#panel.pane.image.ImageBase):
> alt_text, caption, fixed_aspect, link_url, target
>
>

`height`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=400,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
The height of the component (in pixels). This can be either fixed or
preferred height, depending on height sizing policy.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=400,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The width of the component (in pixels). This can be either fixed or
preferred width, depending on width sizing policy.

`dpi`` ``=`` ``Integer(bounds=(1,`` ``None),`` ``default=144,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Dpi')`
Scales the dpi of the ggplot figure.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.plot.YT(object=None, **params)
Bases: [HTML](panel.pane.markup.md#panel.pane.markup.HTML)

YT panes wrap plottable objects from the YT library. By default, the
height and width are calculated by summing all contained plots, but can
optionally be specified explicitly to provide additional space.

Methods

|  |  |
|----|----|
| [applies](#panel.pane.plot.YT.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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
> [class="reference internal" title="panel.pane.markup.HTMLBasePane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
> [class="reference internal" title="panel.pane.markup.HTML"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTML](panel.pane.markup.md#panel.pane.markup.HTML):
> disable_math, sanitize_html, sanitize_hook
>
>

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
