# panel.pane package

## Subpackages

- [panel.pane.vtk
  package](panel.pane.vtk.md)
  - [Submodules](panel.pane.vtk.md#submodules)
    - [panel.pane.vtk.enums module](panel.pane.vtk.enums.md)
      - [TextPosition](panel.pane.vtk.enums.md#panel.pane.vtk.enums.TextPosition)
    - [panel.pane.vtk.synchronizable_deserializer
      module](panel.pane.vtk.synchronizable_deserializer.md)
    - [panel.pane.vtk.synchronizable_serializer
      module](panel.pane.vtk.synchronizable_serializer.md)
    - [panel.pane.vtk.vtk module](panel.pane.vtk.vtk.md)
      - [AbstractVTK](panel.pane.vtk.vtk.md#panel.pane.vtk.vtk.AbstractVTK)
      - [BaseVTKRenderWindow](panel.pane.vtk.vtk.md#panel.pane.vtk.vtk.BaseVTKRenderWindow)
      - [SyncHelpers](panel.pane.vtk.vtk.md#panel.pane.vtk.vtk.SyncHelpers)
      - [VTK](panel.pane.vtk.vtk.md#panel.pane.vtk.vtk.VTK)
      - [VTKJS](panel.pane.vtk.vtk.md#panel.pane.vtk.vtk.VTKJS)
      - [VTKRenderWindow](panel.pane.vtk.vtk.md#panel.pane.vtk.vtk.VTKRenderWindow)
      - [VTKRenderWindowSynchronized](panel.pane.vtk.vtk.md#panel.pane.vtk.vtk.VTKRenderWindowSynchronized)
      - [VTKVolume](panel.pane.vtk.vtk.md#panel.pane.vtk.vtk.VTKVolume)
  - [Module contents](panel.pane.vtk.md#module-panel.pane.vtk)

## Submodules

- [panel.pane.alert module](panel.pane.alert.md)
  - [Alert](panel.pane.alert.md#panel.pane.alert.Alert)
    - [Alert.applies()](panel.pane.alert.md#panel.pane.alert.Alert.applies)
- [panel.pane.base module](panel.pane.base.md)
  - [ModelPane](panel.pane.base.md#panel.pane.base.ModelPane)
  - [Pane](panel.pane.base.md#panel.pane.base.Pane)
    - [Pane.clone()](panel.pane.base.md#panel.pane.base.Pane.clone)
    - [Pane.get_root()](panel.pane.base.md#panel.pane.base.Pane.get_root)
  - [PaneBase](panel.pane.base.md#panel.pane.base.PaneBase)
    - [PaneBase.applies()](panel.pane.base.md#panel.pane.base.PaneBase.applies)
    - [PaneBase.default_layout](panel.pane.base.md#panel.pane.base.PaneBase.default_layout)
    - [PaneBase.get_pane_type()](panel.pane.base.md#panel.pane.base.PaneBase.get_pane_type)
  - [ReplacementPane](panel.pane.base.md#panel.pane.base.ReplacementPane)
    - [ReplacementPane.select()](panel.pane.base.md#panel.pane.base.ReplacementPane.select)
  - [RerenderError](panel.pane.base.md#panel.pane.base.RerenderError)
  - [panel()](panel.pane.base.md#panel.pane.base.panel)
- [panel.pane.deckgl module](panel.pane.deckgl.md)
  - [DeckGL](panel.pane.deckgl.md#panel.pane.deckgl.DeckGL)
    - [DeckGL.applies()](panel.pane.deckgl.md#panel.pane.deckgl.DeckGL.applies)
    - [DeckGL.priority](panel.pane.deckgl.md#panel.pane.deckgl.DeckGL.priority)
  - [lower_camel_case_keys()](panel.pane.deckgl.md#panel.pane.deckgl.lower_camel_case_keys)
  - [to_camel_case()](panel.pane.deckgl.md#panel.pane.deckgl.to_camel_case)
- [panel.pane.echarts module](panel.pane.echarts.md)
  - [ECharts](panel.pane.echarts.md#panel.pane.echarts.ECharts)
    - [ECharts.applies()](panel.pane.echarts.md#panel.pane.echarts.ECharts.applies)
    - [ECharts.js_on_event()](panel.pane.echarts.md#panel.pane.echarts.ECharts.js_on_event)
    - [ECharts.on_event()](panel.pane.echarts.md#panel.pane.echarts.ECharts.on_event)
    - [ECharts.priority](panel.pane.echarts.md#panel.pane.echarts.ECharts.priority)
- [panel.pane.equation module](panel.pane.equation.md)
  - [LaTeX](panel.pane.equation.md#panel.pane.equation.LaTeX)
    - [LaTeX.applies()](panel.pane.equation.md#panel.pane.equation.LaTeX.applies)
    - [LaTeX.priority](panel.pane.equation.md#panel.pane.equation.LaTeX.priority)
- [panel.pane.holoviews module](panel.pane.holoviews.md)
  - [HoloViews](panel.pane.holoviews.md#panel.pane.holoviews.HoloViews)
    - [HoloViews.applies()](panel.pane.holoviews.md#panel.pane.holoviews.HoloViews.applies)
    - [HoloViews.jslink()](panel.pane.holoviews.md#panel.pane.holoviews.HoloViews.jslink)
    - [HoloViews.widget_layout](panel.pane.holoviews.md#panel.pane.holoviews.HoloViews.widget_layout)
  - [Interactive](panel.pane.holoviews.md#panel.pane.holoviews.Interactive)
    - [Interactive.applies()](panel.pane.holoviews.md#panel.pane.holoviews.Interactive.applies)
    - [Interactive.priority](panel.pane.holoviews.md#panel.pane.holoviews.Interactive.priority)
  - [find_links()](panel.pane.holoviews.md#panel.pane.holoviews.find_links)
  - [generate_panel_bokeh_map()](panel.pane.holoviews.md#panel.pane.holoviews.generate_panel_bokeh_map)
  - [is_bokeh_element_plot()](panel.pane.holoviews.md#panel.pane.holoviews.is_bokeh_element_plot)
  - [link_axes()](panel.pane.holoviews.md#panel.pane.holoviews.link_axes)
- [panel.pane.image module](panel.pane.image.md)
  - [AVIF](panel.pane.image.md#panel.pane.image.AVIF)
  - [FileBase](panel.pane.image.md#panel.pane.image.FileBase)
    - [FileBase.applies()](panel.pane.image.md#panel.pane.image.FileBase.applies)
  - [GIF](panel.pane.image.md#panel.pane.image.GIF)
  - [ICO](panel.pane.image.md#panel.pane.image.ICO)
  - [Image](panel.pane.image.md#panel.pane.image.Image)
    - [Image.applies()](panel.pane.image.md#panel.pane.image.Image.applies)
  - [ImageBase](panel.pane.image.md#panel.pane.image.ImageBase)
  - [JPG](panel.pane.image.md#panel.pane.image.JPG)
  - [PDF](panel.pane.image.md#panel.pane.image.PDF)
  - [PNG](panel.pane.image.md#panel.pane.image.PNG)
  - [SVG](panel.pane.image.md#panel.pane.image.SVG)
    - [SVG.applies()](panel.pane.image.md#panel.pane.image.SVG.applies)
  - [WebP](panel.pane.image.md#panel.pane.image.WebP)
- [panel.pane.ipywidget module](panel.pane.ipywidget.md)
  - [IPyLeaflet](panel.pane.ipywidget.md#panel.pane.ipywidget.IPyLeaflet)
    - [IPyLeaflet.applies()](panel.pane.ipywidget.md#panel.pane.ipywidget.IPyLeaflet.applies)
  - [IPyWidget](panel.pane.ipywidget.md#panel.pane.ipywidget.IPyWidget)
    - [IPyWidget.applies()](panel.pane.ipywidget.md#panel.pane.ipywidget.IPyWidget.applies)
  - [Reacton](panel.pane.ipywidget.md#panel.pane.ipywidget.Reacton)
    - [Reacton.applies()](panel.pane.ipywidget.md#panel.pane.ipywidget.Reacton.applies)
- [panel.pane.markup module](panel.pane.markup.md)
  - [DataFrame](panel.pane.markup.md#panel.pane.markup.DataFrame)
    - [DataFrame.applies()](panel.pane.markup.md#panel.pane.markup.DataFrame.applies)
  - [HTML](panel.pane.markup.md#panel.pane.markup.HTML)
    - [HTML.applies()](panel.pane.markup.md#panel.pane.markup.HTML.applies)
    - [HTML.priority](panel.pane.markup.md#panel.pane.markup.HTML.priority)
  - [HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane)
  - [JSON](panel.pane.markup.md#panel.pane.markup.JSON)
    - [JSON.applies()](panel.pane.markup.md#panel.pane.markup.JSON.applies)
    - [JSON.priority](panel.pane.markup.md#panel.pane.markup.JSON.priority)
  - [Markdown](panel.pane.markup.md#panel.pane.markup.Markdown)
    - [Markdown.applies()](panel.pane.markup.md#panel.pane.markup.Markdown.applies)
    - [Markdown.priority](panel.pane.markup.md#panel.pane.markup.Markdown.priority)
  - [Str](panel.pane.markup.md#panel.pane.markup.Str)
    - [Str.applies()](panel.pane.markup.md#panel.pane.markup.Str.applies)
- [panel.pane.media module](panel.pane.media.md)
  - [Audio](panel.pane.media.md#panel.pane.media.Audio)
    - [Audio.applies()](panel.pane.media.md#panel.pane.media.Audio.applies)
  - [TensorLike](panel.pane.media.md#panel.pane.media.TensorLike)
  - [TensorLikeMeta](panel.pane.media.md#panel.pane.media.TensorLikeMeta)
  - [Video](panel.pane.media.md#panel.pane.media.Video)
- [panel.pane.perspective module](panel.pane.perspective.md)
  - [Perspective](panel.pane.perspective.md#panel.pane.perspective.Perspective)
    - [Perspective.applies()](panel.pane.perspective.md#panel.pane.perspective.Perspective.applies)
    - [Perspective.on_click()](panel.pane.perspective.md#panel.pane.perspective.Perspective.on_click)
    - [Perspective.priority](panel.pane.perspective.md#panel.pane.perspective.Perspective.priority)
  - [Plugin](panel.pane.perspective.md#panel.pane.perspective.Plugin)
    - [Plugin.options()](panel.pane.perspective.md#panel.pane.perspective.Plugin.options)
  - [deconstruct_pandas()](panel.pane.perspective.md#panel.pane.perspective.deconstruct_pandas)
- [panel.pane.placeholder module](panel.pane.placeholder.md)
  - [Placeholder](panel.pane.placeholder.md#panel.pane.placeholder.Placeholder)
    - [Placeholder.update()](panel.pane.placeholder.md#panel.pane.placeholder.Placeholder.update)
- [panel.pane.plot module](panel.pane.plot.md)
  - [Bokeh](panel.pane.plot.md#panel.pane.plot.Bokeh)
    - [Bokeh.applies()](panel.pane.plot.md#panel.pane.plot.Bokeh.applies)
  - [Folium](panel.pane.plot.md#panel.pane.plot.Folium)
    - [Folium.applies()](panel.pane.plot.md#panel.pane.plot.Folium.applies)
  - [Matplotlib](panel.pane.plot.md#panel.pane.plot.Matplotlib)
    - [Matplotlib.applies()](panel.pane.plot.md#panel.pane.plot.Matplotlib.applies)
  - [RGGPlot](panel.pane.plot.md#panel.pane.plot.RGGPlot)
    - [RGGPlot.applies()](panel.pane.plot.md#panel.pane.plot.RGGPlot.applies)
  - [YT](panel.pane.plot.md#panel.pane.plot.YT)
    - [YT.applies()](panel.pane.plot.md#panel.pane.plot.YT.applies)
- [panel.pane.plotly module](panel.pane.plotly.md)
  - [Plotly](panel.pane.plotly.md#panel.pane.plotly.Plotly)
    - [Plotly.applies()](panel.pane.plotly.md#panel.pane.plotly.Plotly.applies)
- [panel.pane.streamz module](panel.pane.streamz.md)
  - [Streamz](panel.pane.streamz.md#panel.pane.streamz.Streamz)
    - [Streamz.applies()](panel.pane.streamz.md#panel.pane.streamz.Streamz.applies)
- [panel.pane.textual module](panel.pane.textual.md)
  - [Textual](panel.pane.textual.md#panel.pane.textual.Textual)
    - [Textual.applies()](panel.pane.textual.md#panel.pane.textual.Textual.applies)
- [panel.pane.vega module](panel.pane.vega.md)
  - [Vega](panel.pane.vega.md#panel.pane.vega.Vega)
    - [Vega.applies()](panel.pane.vega.md#panel.pane.vega.Vega.applies)
    - [Vega.export()](panel.pane.vega.md#panel.pane.vega.Vega.export)
  - [ds_as_cds()](panel.pane.vega.md#panel.pane.vega.ds_as_cds)
- [panel.pane.vizzu module](panel.pane.vizzu.md)
  - [Vizzu](panel.pane.vizzu.md#panel.pane.vizzu.Vizzu)
    - [Vizzu.animate()](panel.pane.vizzu.md#panel.pane.vizzu.Vizzu.animate)
    - [Vizzu.applies()](panel.pane.vizzu.md#panel.pane.vizzu.Vizzu.applies)
    - [Vizzu.on_click()](panel.pane.vizzu.md#panel.pane.vizzu.Vizzu.on_click)

## Module contents

### Panel panes renders the Python objects you know and love ❤️

Panes may render anything including plots, text, images, equations etc.

For example Panel contains Bokeh, HoloViews, Matplotlib and Plotly
panes.

Check out the Panel gallery of panes
[https://panel.holoviz.org/reference/index.html#panes](https://panel.holoviz.org/reference/index.html#panes)
for inspiration.

#### How to use Panel panes in 2 simple steps

1.  Define your Python objects

\>\>\> some_python_object
= ...
\>\>\>
another_python_object
= ...

2.  Define your panes

\>\>\>
pn.pane.SomePane(some_python_object).servable()
\>\>\>
pn.pane.AnotherPane(another_python_object).servable()

Most often you don’t have to wrap your Python object into a specific
pane. Just add your Python object to pn.panel, pn.Column, pn.Row or
other layouts, then Panel will automatically wrap it in the right pane.

For more detail see the Getting Started Guide
[https://panel.holoviz.org/getting_started/index.html](https://panel.holoviz.org/getting_started/index.html)

class panel.pane.AVIF(object=None, **params)
Bases: [ImageBase](panel.pane.image.md#panel.pane.image.ImageBase)

The AVIF pane embeds a .avif image file in a panel if provided a local
path, or will link to a remote image if provided a URL.

Reference: [https://panel.holoviz.org/reference/panes/AVIF.html](https://panel.holoviz.org/reference/panes/AVIF.html)

Example:

\>\>\>
AVIF(
...
'https://assets.holoviz.org/panel/samples/avif_sample.avif',
...
alt_text='A
nice tree', ...
link_url='https://en.wikipedia.org/wiki/AVIF',
...
width=500
... )

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
> [class="reference internal" title="panel.pane.image.FileBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.FileBase](panel.pane.image.md#panel.pane.image.FileBase):
> embed
>
> [class="reference internal" title="panel.pane.image.ImageBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.ImageBase](panel.pane.image.md#panel.pane.image.ImageBase):
> alt_text, caption, fixed_aspect, link_url, target
>
>

class panel.pane.Alert(object=None, **params)
Bases: [Markdown](panel.pane.markup.md#panel.pane.markup.Markdown)

The Alert pane allows providing contextual feedback messages for typical
user actions. The Alert supports markdown strings.

Reference:
[https://panel.holoviz.org/reference/panes/Alert.html](https://panel.holoviz.org/reference/panes/Alert.html)

Example:

\>\>\>
Alert('Some
important message',
alert_type='warning')

Methods

|  |  |
|----|----|
| [applies](#panel.pane.Alert.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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
> [class="reference internal" title="panel.pane.markup.Markdown"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.Markdown](panel.pane.markup.md#panel.pane.markup.Markdown):
> dedent, disable_anchors, disable_math, extensions, hard_line_break,
> plugins, renderer, renderer_options
>
>

`alert_type`` ``=`` ``Selector(default='primary',`` ``label='Alert`` ``type',`` ``names={},`` ``objects=['primary',`` ``'secondary',`` ``'success',`` ``'danger',`` ``'warning',`` ``'info',`` ``'light',`` ``'dark'])`
The type of Alert and one of ‘primary’, ‘secondary’, ‘success’,
‘danger’, ‘warning’, ‘info’, ‘light’, ‘dark’.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.Audio(object=None, **params)
Bases: `_MediaBase`

The Audio pane displays an audio player given a local or remote audio
file, a NumPy Array or Torch Tensor.

The pane also allows access and control over the player state including
toggling of playing/paused and loop state, the current time, and the
volume.

The audio player supports ogg, mp3, and wav files

If SciPy is installed, 1- or 2-dim Numpy Arrays and 1- or 2-dim Torch
Tensors are also supported. The dtype must be one of the following

- numpy: np.int16, np.uint16, np.float32, np.float64

- torch: torch.short, torch.int16, torch.half, torch.float16,
  torch.float, torch.float32,

torch.double, torch.float64

The array or Tensor input will be downsampled to 16bit and converted to
a wav file by SciPy.

Reference:
[https://panel.holoviz.org/reference/panes/Audio.html](https://panel.holoviz.org/reference/panes/Audio.html)

Example:

\>\>\>
Audio('http://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3',
name='Audio')

Methods

|  |  |
|----|----|
| [applies](#panel.pane.Audio.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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
> `panel.pane.media._MediaBase`: loop, time,
> throttle, paused, volume, autoplay, muted
>
>

`object`` ``=`` ``ClassSelector(allow_None=True,`` ``allow_refs=True,`` ``class_=(<class`` ``'str'>,`` ``<class`` ``'bytes'>,`` ``<class`` ``'pathlib.Path'>,`` ``<class`` ``'_io.BytesIO'>,`` ``<class`` ``'numpy.ndarray'>,`` ``<class`` ``'panel.pane.media.TensorLike'>),`` ``default='',`` ``label='Object')`
The audio file either local or remote, a 1- or 2-dim NumPy ndarray or a
1- or 2-dim Torch Tensor or a bytes or BytesIO object.

`sample_rate`` ``=`` ``Integer(default=44100,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Sample`` ``rate')`
The sample_rate of the audio when given a NumPy array or Torch tensor.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.Bokeh(object=None, **params)
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
| [applies](#panel.pane.Bokeh.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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

class panel.pane.DataFrame(object=None, **params)
Bases: [HTML](panel.pane.markup.md#panel.pane.markup.HTML)

The DataFrame pane renders pandas, dask and streamz DataFrame types
using their custom HTML repr.

In the case of a streamz DataFrame the rendered data will update
periodically.

Reference:
[https://panel.holoviz.org/reference/panes/DataFrame.html](https://panel.holoviz.org/reference/panes/DataFrame.html)

Example:

\>\>\>
DataFrame(df,
index=False,
max_rows=25,
width=400)

Methods

|  |  |
|----|----|
| [applies](#panel.pane.DataFrame.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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

`bold_rows`` ``=`` ``Boolean(default=True,`` ``label='Bold`` ``rows')`
Make the row labels bold in the output.

`border`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Border')`
A `border=border` attribute is included in the
opening \<table\> tag.

`classes`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=['panel-df'],`` ``label='Classes')`
CSS class(es) to apply to the resulting html table.

`col_space`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'str'>,`` ``<class`` ``'int'>,`` ``<class`` ``'dict'>),`` ``label='Col`` ``space')`
The minimum width of each column in CSS length units. An int is assumed
to be px units.

`decimal`` ``=`` ``String(default='.',`` ``label='Decimal')`
Character recognized as decimal separator, e.g. ‘,’ in Europe.

`escape`` ``=`` ``Boolean(default=True,`` ``label='Escape')`
Whether or not to escape the dataframe HTML. For security reasons the
default value is True.

`float_format`` ``=`` ``Callable(allow_None=True,`` ``label='Float`` ``format')`
Formatter function to apply to columns’ elements if they are floats. The
result of this function must be a unicode string.

`formatters`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'dict'>,`` ``<class`` ``'list'>),`` ``label='Formatters')`
Formatter functions to apply to columns’ elements by position or name.
The result of each function must be a unicode string.

`header`` ``=`` ``Boolean(default=True,`` ``label='Header')`
Whether to print column labels.

`index`` ``=`` ``Boolean(default=True,`` ``label='Index')`
Whether to print index (row) labels.

`index_names`` ``=`` ``Boolean(default=True,`` ``label='Index`` ``names')`
Prints the names of the indexes.

`justify`` ``=`` ``Selector(allow_None=True,`` ``label='Justify',`` ``names={},`` ``objects=['left',`` ``'right',`` ``'center',`` ``'justify',`` ``'justify-all',`` ``'start',`` ``'end',`` ``'inherit',`` ``'match-parent',`` ``'initial',`` ``'unset'])`
How to justify the column labels.

`max_rows`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``rows')`
Maximum number of rows to display.

`max_cols`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``cols')`
Maximum number of columns to display.

`na_rep`` ``=`` ``String(default='NaN',`` ``label='Na`` ``rep')`
String representation of NAN to use.

`render_links`` ``=`` ``Boolean(default=False,`` ``label='Render`` ``links')`
Convert URLs to HTML links.

`show_dimensions`` ``=`` ``Boolean(default=False,`` ``label='Show`` ``dimensions')`
Display DataFrame dimensions (number of rows by number of columns).

`sparsify`` ``=`` ``Boolean(default=True,`` ``label='Sparsify')`
Set to False for a DataFrame with a hierarchical index to print every
multi-index key at each row.

`text_align`` ``=`` ``Selector(label='Text`` ``align',`` ``names={},`` ``objects=['start',`` ``'end',`` ``'center'])`
Alignment of non-header cells.

`_object`` ``=`` ``Parameter(allow_None=True,`` ``label='`` ``object')`
Hidden parameter.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.DeckGL(object=None, **params)
Bases: [ModelPane](panel.pane.base.md#panel.pane.base.ModelPane)

The DeckGL pane renders the Deck.gl JSON specification as well as PyDeck
plots inside a panel.

Deck.gl is a very powerful WebGL-powered framework for visual
exploratory data analysis of large datasets.

Reference:
[https://panel.holoviz.org/reference/panes/DeckGL.html](https://panel.holoviz.org/reference/panes/DeckGL.html)

Example:

\>\>\>
pn.extension('deckgl')
\>\>\>
DeckGL(
...
some_deckgl_dict_or_pydeck_object,
...
mapbox_api_key=MAPBOX_KEY,
height=600
... )

Attributes:
**priority**

Methods

|  |  |
|----|----|
| [applies](#panel.pane.DeckGL.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

|               |     |
|---------------|-----|
| **is_pydeck** |     |

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

`mapbox_api_key`` ``=`` ``String(allow_None=True,`` ``label='Mapbox`` ``api`` ``key')`
The MapBox API key if not supplied by a PyDeck object.

`tooltips`` ``=`` ``ClassSelector(class_=(<class`` ``'bool'>,`` ``<class`` ``'dict'>),`` ``default=True,`` ``label='Tooltips')`
Whether to enable tooltips

`configuration`` ``=`` ``String(default='',`` ``label='Configuration')`
Custom configuration dictionary as json string

`click_state`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Click`` ``state')`
Contains the last click event on the DeckGL plot.

`hover_state`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Hover`` ``state')`
The current hover state of the DeckGL plot.

`view_state`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='View`` ``state')`
The current view state of the DeckGL plot.

`throttle`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={'view':`` ``200,`` ``'hover':`` ``200},`` ``label='Throttle')`
Throttling timeout (in milliseconds) for view state and hover events
sent from the frontend.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

priority: t.ClassVar\[float \| bool \| None\] = None

class panel.pane.ECharts(object=None, **params)
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
| [applies](#panel.pane.ECharts.applies)(object, **params) | Returns boolean or float indicating whether the Pane can render the object. |
| [js_on_event](#panel.pane.ECharts.js_on_event)(event, callback\[, query\]) | Register a Javascript event handler which triggers when the specified event is triggered. |
| [on_event](#panel.pane.ECharts.on_event)(event, callback\[, query\]) | Register anevent handler which triggers when the specified event is triggered. |

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

class panel.pane.GIF(object=None, **params)
Bases: [ImageBase](panel.pane.image.md#panel.pane.image.ImageBase)

The GIF pane embeds a .gif image file in a panel if provided a local
path, or will link to a remote image if provided a URL.

Reference: [https://panel.holoviz.org/reference/panes/GIF.html](https://panel.holoviz.org/reference/panes/GIF.html)

Example:

\>\>\>
GIF(
...
'https://upload.wikimedia.org/wikipedia/commons/b/b1/Loading_icon.gif',
...
alt_text='A
loading spinner', ...

link_url='https://commons.wikimedia.org/wiki/File:Loading_icon.gif',
...
width=500
... )

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
> [class="reference internal" title="panel.pane.image.FileBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.FileBase](panel.pane.image.md#panel.pane.image.FileBase):
> embed
>
> [class="reference internal" title="panel.pane.image.ImageBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.ImageBase](panel.pane.image.md#panel.pane.image.ImageBase):
> alt_text, caption, fixed_aspect, link_url, target
>
>

class panel.pane.HTML(object=None, **params)
Bases: [HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane)

HTML panes renders HTML strings and objects with a \_repr_html\_ method.

The height and width can optionally be specified, to allow room for
whatever is being wrapped.

Reference: [https://panel.holoviz.org/reference/panes/HTML.html](https://panel.holoviz.org/reference/panes/HTML.html)

Example:

\>\>\>
HTML(
...  "\<h1\>This is a HTML
pane\</h1\>", ...
styles={'background-color':
'#F6F6F6'}
... )

Attributes:
**priority**

Methods

|  |  |
|----|----|
| [applies](#panel.pane.HTML.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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
>

`disable_math`` ``=`` ``Boolean(default=True,`` ``label='Disable`` ``math')`
Whether to disable support for MathJax math rendering for strings
escaped with \$\$ delimiters.

`sanitize_html`` ``=`` ``Boolean(default=False,`` ``label='Sanitize`` ``html')`
Whether to sanitize HTML sent to the frontend.

`sanitize_hook`` ``=`` ``Callable(label='Sanitize`` ``hook')`
Sanitization callback to apply if sanitize_html=True.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

priority: t.ClassVar\[float \| bool \| None\] = None

class panel.pane.HoloViews(object=None, **params)
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
| [applies](#panel.pane.HoloViews.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |
| [jslink](#panel.pane.HoloViews.jslink)(target\[, code, args, bidirectional\]) | Links properties on the this Reactive object to those on the target Reactive object in JS code. |

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

class panel.pane.ICO(object=None, **params)
Bases: [ImageBase](panel.pane.image.md#panel.pane.image.ImageBase)

The ICO pane embeds an .ico image file in a panel if provided a local
path, or will link to a remote image if provided a URL.

Reference: [https://panel.holoviz.org/reference/panes/ICO.html](https://panel.holoviz.org/reference/panes/ICO.html)

Example:

\>\>\>
ICO(
...
some_url,
...
alt_text='An
.ico file', ...
link_url='https://en.wikipedia.org/wiki/ICO\_(file_format)',
...
width=50
...

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
> [class="reference internal" title="panel.pane.image.FileBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.FileBase](panel.pane.image.md#panel.pane.image.FileBase):
> embed
>
> [class="reference internal" title="panel.pane.image.ImageBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.ImageBase](panel.pane.image.md#panel.pane.image.ImageBase):
> alt_text, caption, fixed_aspect, link_url, target
>
>

class panel.pane.IPyLeaflet(object=None, **params)
Bases:
[IPyWidget](panel.pane.ipywidget.md#panel.pane.ipywidget.IPyWidget)

Methods

|  |  |
|----|----|
| [applies](#panel.pane.IPyLeaflet.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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
> margin, default_layout
>
> [class="reference internal" title="panel.pane.ipywidget.IPyWidget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.ipywidget.IPyWidget](panel.pane.ipywidget.md#panel.pane.ipywidget.IPyWidget):
> object
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

class panel.pane.IPyWidget(object=None, **params)
Bases: [Pane](panel.pane.base.md#panel.pane.base.Pane)

The IPyWidget pane renders any ipywidgets model both in the notebook and
in a deployed server.

When rendering ipywidgets on the server you must add ipywidgets to
pn.extension. You must not do this in Jupyterlab as this may render
Jupyterlab unusable.

Reference:
[https://panel.holoviz.org/reference/panes/IPyWidget.html](https://panel.holoviz.org/reference/panes/IPyWidget.html)

Example:

\>\>\>
IPyWidget(some_ipywidget)

Methods

|  |  |
|----|----|
| [applies](#panel.pane.IPyWidget.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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
The IPywidget being wrapped, which will be converted to a Bokeh model.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.Interactive(object=None, **params)
Bases: [Pane](panel.pane.base.md#panel.pane.base.Pane)

Attributes:
**priority**

Methods

|  |  |
|----|----|
| [applies](#panel.pane.Interactive.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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

class panel.pane.JPG(object=None, **params)
Bases: [ImageBase](panel.pane.image.md#panel.pane.image.ImageBase)

The JPG pane embeds a .jpg or .jpeg image file in a panel if provided a
local path, or will link to a remote image if provided a URL.

Reference: [https://panel.holoviz.org/reference/panes/JPG.html](https://panel.holoviz.org/reference/panes/JPG.html)

Example:

\>\>\>
JPG(
...
'https://www.gstatic.com/webp/gallery/4.sm.jpg',
...
alt_text='A
nice tree', ...
link_url='https://en.wikipedia.org/wiki/JPEG',
...
width=500
... )

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
> [class="reference internal" title="panel.pane.image.FileBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.FileBase](panel.pane.image.md#panel.pane.image.FileBase):
> embed
>
> [class="reference internal" title="panel.pane.image.ImageBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.ImageBase](panel.pane.image.md#panel.pane.image.ImageBase):
> alt_text, caption, fixed_aspect, link_url, target
>
>

class panel.pane.JSON(object=None, **params)
Bases: [HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane)

The JSON pane allows rendering arbitrary JSON strings, dicts and other
json serializable objects in a panel.

Reference: [https://panel.holoviz.org/reference/panes/JSON.html](https://panel.holoviz.org/reference/panes/JSON.html)

Example:

\>\>\>
JSON(json_obj,
theme='light',
height=300,
width=500)

Attributes:
**priority**

Methods

|  |  |
|----|----|
| [applies](#panel.pane.JSON.applies)(object, **params) | Returns boolean or float indicating whether the Pane can render the object. |

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
>

`depth`` ``=`` ``Integer(bounds=(-1,`` ``None),`` ``default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Depth')`
Depth to which the JSON tree will be expanded on initialization.

`encoder`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'json.encoder.JSONEncoder'>,`` ``label='Encoder')`
Custom JSONEncoder class used to serialize objects to JSON string.

`hover_preview`` ``=`` ``Boolean(default=False,`` ``label='Hover`` ``preview')`
Whether to display a hover preview for collapsed nodes.

`theme`` ``=`` ``Selector(default='light',`` ``label='Theme',`` ``names={},`` ``objects=['light',`` ``'dark'])`
If no value is provided, it defaults to the current theme set by
pn.config.theme, as specified in the JSON.THEME_CONFIGURATION
dictionary. If not defined there, it falls back to the default parameter
value.

classmethod applies(object: Any, **params) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

priority: t.ClassVar\[float \| bool \| None\] = None

class panel.pane.LaTeX(object=None, **params)
Bases: [ModelPane](panel.pane.base.md#panel.pane.base.ModelPane)

The LaTeX pane allows rendering LaTeX equations. It uses either KaTeX or
MathJax depending on the defined renderer.

By default it will use the renderer loaded in the extension (e.g.
pn.extension(‘katex’)), defaulting to KaTeX if both are loaded.

Reference:
[https://panel.holoviz.org/reference/panes/LaTeX.html](https://panel.holoviz.org/reference/panes/LaTeX.html)

Example:

\>\>\>
pn.extension('katex')
\>\>\>
LaTeX(
...  'The LaTeX pane supports
two delimiters: \$LaTeX\$ and \\LaTeX\\',
...
styles={'font-size':
'18pt'},
width=800
... )

Attributes:
**priority**

Methods

|  |  |
|----|----|
| [applies](#panel.pane.LaTeX.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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

`renderer`` ``=`` ``Selector(allow_None=True,`` ``label='Renderer',`` ``names={},`` ``objects=['katex',`` ``'mathjax'])`
The JS renderer used to render the LaTeX expression. Defaults to katex.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

priority: t.ClassVar\[float \| bool \| None\] = None

class panel.pane.Markdown(object=None, **params)
Bases: [HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane)

The Markdown pane allows rendering arbitrary markdown strings in a
panel.

It renders strings containing valid Markdown as well as objects with a
\_repr_markdown\_ method, and may define custom CSS styles.

Reference:
[https://panel.holoviz.org/reference/panes/Markdown.html](https://panel.holoviz.org/reference/panes/Markdown.html)

Example:

\>\>\>
Markdown("#
This is a header")

Attributes:
**priority**

Methods

|  |  |
|----|----|
| [applies](#panel.pane.Markdown.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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
>

`dedent`` ``=`` ``Boolean(default=True,`` ``label='Dedent')`
Whether to dedent common whitespace across all lines.

`disable_anchors`` ``=`` ``Boolean(default=False,`` ``label='Disable`` ``anchors')`
Whether to disable automatically adding anchors to headings.

`disable_math`` ``=`` ``Boolean(default=False,`` ``label='Disable`` ``math')`
Whether to disable support for MathJax math rendering for strings
escaped with \$\$ delimiters.

`extensions`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=['extra',`` ``'smarty',`` ``'codehilite'],`` ``label='Extensions',`` ``nested_refs=True)`
Markdown extension to apply when transforming markup. Does not apply if
renderer is set to ‘markdown-it’ or ‘myst’.

`hard_line_break`` ``=`` ``Boolean(default=False,`` ``label='Hard`` ``line`` ``break')`
Whether simple new lines are rendered as hard line breaks. False by
default to conform with the original Markdown spec. Not supported by the
‘myst’ renderer.

`plugins`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``label='Plugins',`` ``nested_refs=True)`
Additional markdown-it-py plugins to use.

`renderer`` ``=`` ``Selector(default='markdown-it',`` ``label='Renderer',`` ``names={},`` ``objects=['markdown-it',`` ``'myst',`` ``'markdown'])`
Markdown renderer implementation.

`renderer_options`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Renderer`` ``options',`` ``nested_refs=True)`
Options to pass to the markdown renderer.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

priority: t.ClassVar\[float \| bool \| None\] = None

class panel.pane.Matplotlib(object=None, **params)
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
| [applies](#panel.pane.Matplotlib.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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

class panel.pane.PDF(object=None, **params)
Bases: [FileBase](panel.pane.image.md#panel.pane.image.FileBase)

The PDF pane embeds a .pdf image file in a panel if provided a local
path, or will link to a remote image if provided a URL.

Reference: [https://panel.holoviz.org/reference/panes/PDF.html](https://panel.holoviz.org/reference/panes/PDF.html)

Example:

\>\>\>
PDF(
...
'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf',
...
width=300,
height=410
... )

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
> [class="reference internal" title="panel.pane.image.FileBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.FileBase](panel.pane.image.md#panel.pane.image.FileBase):
> embed
>
>

`start_page`` ``=`` ``Integer(default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start`` ``page')`
Start page of the pdf, by default the first page.

class panel.pane.PNG(object=None, **params)
Bases: [ImageBase](panel.pane.image.md#panel.pane.image.ImageBase)

The PNG pane embeds a .png image file in a panel if provided a local
path, or will link to a remote image if provided a URL.

Reference: [https://panel.holoviz.org/reference/panes/PNG.html](https://panel.holoviz.org/reference/panes/PNG.html)

Example:

\>\>\>
PNG(
...
'https://panel.holoviz.org/\_static/logo_horizontal.png',
...
alt_text='The
Panel Logo', ...
link_url='https://panel.holoviz.org/index.html',
...
width=500
... )

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
> [class="reference internal" title="panel.pane.image.FileBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.FileBase](panel.pane.image.md#panel.pane.image.FileBase):
> embed
>
> [class="reference internal" title="panel.pane.image.ImageBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.ImageBase](panel.pane.image.md#panel.pane.image.ImageBase):
> alt_text, caption, fixed_aspect, link_url, target
>
>

class panel.pane.Pane(object=None, **params)
Bases: [PaneBase](panel.pane.base.md#panel.pane.base.PaneBase),
[Reactive](panel.reactive.md#panel.reactive.Reactive)

Pane is the abstract baseclass for all atomic displayable units in the
Panel library.

Panes defines an extensible interface for wrapping arbitrary objects and
transforming them into renderable components.

Panes are reactive in the sense that when the object they are wrapping
is replaced or modified the UI will reflect the updated object.

Methods

|  |  |
|----|----|
| [clone](#panel.pane.Pane.clone)(\[object\]) | Makes a copy of the Pane sharing the same parameters. |
| [get_root](#panel.pane.Pane.get_root)(\[doc, comm, preprocess\]) | Returns the root model and applies pre-processing hooks |

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

clone(object: Any \| None = None, **params) → T
Makes a copy of the Pane sharing the same parameters.

Parameters:
**object: Optional new object to render**

**params: Keyword arguments override the parameters on the clone.**

Returns:
Cloned Pane object

get_root(doc: Document \| None = None, comm: Comm \| None = None, preprocess: bool = True) → Model
Returns the root model and applies pre-processing hooks

Parameters:
**doc: bokeh.document.Document**
Optional Bokeh document the bokeh model will be attached to.

**comm: pyviz_comms.Comm**
Optional pyviz_comms when working in notebook

**preprocess: bool (default=True)**
Whether to run preprocessing hooks

Returns:
Returns the bokeh model corresponding to this panel object

class panel.pane.PaneBase(object=None, **params)
Bases: [Layoutable](panel.viewable.md#panel.viewable.Layoutable)

PaneBase represents an abstract baseclass which can be used as a mix-in
class to define a component that mirrors the Pane API. This means that
this component will participate in the automatic resolution of the
appropriate pane type when Panel is asked to render an object of unknown
type.

The resolution of the appropriate pane type can be implemented using the
`applies` method and the
`priority` class attribute. The applies method
should either return a boolean value indicating whether the pane can
render the supplied object. If it can the priority determines which of
the panes that apply will be selected. If the priority is None then the
`applies` method must return a priority value.

Methods

|  |  |
|----|----|
| [applies](#panel.pane.PaneBase.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |
| [get_pane_type](#panel.pane.PaneBase.get_pane_type)() | Returns the applicable Pane type given an object by resolving the precedence of all types whose applies method declares that the object is supported. |

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
>

`margin`` ``=`` ``Margin(allow_None=True,`` ``default=(5,`` ``10),`` ``label='Margin')`
Allows to create additional space around the component. May be specified
as a two-tuple of the form (vertical, horizontal) or a four-tuple (top,
right, bottom, left).

`default_layout`` ``=`` ``ClassSelector(class_=(<class`` ``'panel.layout.base.ListLike'>,`` ``<class`` ``'panel.layout.base.NamedListLike'>),`` ``default=<class`` ``'panel.layout.base.Row'>,`` ``label='Default`` ``layout')`
Defines the layout the model(s) returned by the pane will be placed in.

`object`` ``=`` ``Parameter(allow_None=True,`` ``allow_refs=True,`` ``label='Object')`
The object being wrapped, which will be converted to a Bokeh model.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

default_layout
alias of [Row](panel.layout.base.md#panel.layout.base.Row)

classmethod get_pane_type(obj: Any, **kwargs: Any) → type\[Viewable\] \| type\[PaneBase\]
Returns the applicable Pane type given an object by resolving the
precedence of all types whose applies method declares that the object is
supported.

Parameters:
**obj (object): The object type to return a Pane type for**

Returns:
The applicable Pane type with the highest precedence.

class panel.pane.ParamFunction(object=None, **params)
Bases: [ParamRef](#panel.pane.ParamRef)

ParamFunction panes wrap functions decorated with the param.depends
decorator and rerenders the output when any of the function’s
dependencies change. This allows building reactive components into a
Panel which depend on other parameters, e.g. tying the value of a widget
to some other output.

Methods

|  |  |
|----|----|
| [applies](#panel.pane.ParamFunction.applies)(object, **kwargs) | Returns boolean or float indicating whether the Pane can render the object. |

|          |     |
|----------|-----|
| **eval** |     |

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
> [class="reference internal" title="panel.pane.base.ReplacementPane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.ReplacementPane](panel.pane.base.md#panel.pane.base.ReplacementPane):
> object, inplace, \_pane
>
> [title="panel.param.ParamRef"> class="sourceCode python xref py py-class docutils literal notranslate">panel.param.ParamRef](#panel.pane.ParamRef):
> defer_load, generator_mode, lazy, loading_indicator
>
>

classmethod applies(object: Any, **kwargs) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.ParamMethod(object=None, **params)
Bases: [ParamRef](#panel.pane.ParamRef)

ParamMethod panes wrap methods on parameterized classes and rerenders
the plot when any of the method’s parameters change. By default
ParamMethod will watch all parameters on the class owning the method or
can be restricted to certain parameters by annotating the method using
the param.depends decorator. The method may return any object which
itself can be rendered as a Pane.

Methods

|  |  |
|----|----|
| [applies](#panel.pane.ParamMethod.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

|          |     |
|----------|-----|
| **eval** |     |

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
> [class="reference internal" title="panel.pane.base.ReplacementPane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.ReplacementPane](panel.pane.base.md#panel.pane.base.ReplacementPane):
> object, inplace, \_pane
>
> [title="panel.param.ParamRef"> class="sourceCode python xref py py-class docutils literal notranslate">panel.param.ParamRef](#panel.pane.ParamRef):
> defer_load, generator_mode, lazy, loading_indicator
>
>

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.ParamRef(object=None, **params)
Bases: [ReplacementPane](panel.pane.base.md#panel.pane.base.ReplacementPane)

ParamRef wraps any valid parameter reference and resolves it
dynamically, re-rendering the output. If enabled it will attempt to
update the previously rendered component inplace.

Methods

|  |  |
|----|----|
| [applies](#panel.pane.ParamRef.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

|          |     |
|----------|-----|
| **eval** |     |

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
> [class="reference internal" title="panel.pane.base.ReplacementPane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.ReplacementPane](panel.pane.base.md#panel.pane.base.ReplacementPane):
> object, inplace, \_pane
>
>

`defer_load`` ``=`` ``Boolean(allow_None=True,`` ``label='Defer`` ``load')`
Whether to defer load until after the page is rendered. Can be set as
parameter or by setting panel.config.defer_load.

`generator_mode`` ``=`` ``Selector(default='replace',`` ``label='Generator`` ``mode',`` ``names={},`` ``objects=['append',`` ``'replace'])`
Whether generators should ‘append’ to or ‘replace’ existing output.

`lazy`` ``=`` ``Boolean(default=False,`` ``label='Lazy')`
Whether to lazily evaluate the contents of the object only when it is
required for rendering.

`loading_indicator`` ``=`` ``Boolean(default=False,`` ``label='Loading`` ``indicator')`
Whether to show a loading indicator while the pane is updating. Can be
set as parameter or by setting panel.config.loading_indicator.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.Perspective(object=None, **params)
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
| [applies](#panel.pane.Perspective.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |
| [on_click](#panel.pane.Perspective.on_click)(callback) | Register a callback to be executed when any row is clicked. |

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

class panel.pane.Placeholder(object=None, **params)
Bases: [ReplacementPane](panel.pane.base.md#panel.pane.base.ReplacementPane)

The Placeholder pane serves as a placeholder for other Panel components.
It can be used to display a message while a computation is running, for
example.

Reference:
[https://panel.holoviz.org/reference/panes/Placeholder.html](https://panel.holoviz.org/reference/panes/Placeholder.html)

Example:

\>\>\> with
Placeholder("⏳
Idle"): ...
placeholder.object
= "🏃 Running..."

Methods

|  |  |
|----|----|
| [update](#panel.pane.Placeholder.update)(object) | Updates the object on the Placeholder. |

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
> [class="reference internal" title="panel.pane.base.ReplacementPane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.ReplacementPane](panel.pane.base.md#panel.pane.base.ReplacementPane):
> object, inplace, \_pane
>
>

update(object)
Updates the object on the Placeholder.

Parameters:
**object: The object to update the Placeholder with.**

class panel.pane.Plotly(object=None, **params)
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
| [applies](#panel.pane.Plotly.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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

class panel.pane.RGGPlot(object=None, **params)
Bases: [PNG](panel.pane.image.md#panel.pane.image.PNG)

An RGGPlot pane renders an r2py-based ggplot2 figure to png and wraps
the base64-encoded data in a bokeh Div model.

Methods

|  |  |
|----|----|
| [applies](#panel.pane.RGGPlot.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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

class panel.pane.ReactiveExpr(object=None, **params)
Bases: [Pane](panel.pane.base.md#panel.pane.base.Pane)

ReactiveExpr generates a UI for param.rx objects by rendering the
widgets and outputs.

Attributes:
**widgets**

Methods

|  |  |
|----|----|
| [applies](#panel.pane.ReactiveExpr.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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

`center`` ``=`` ``Boolean(default=False,`` ``label='Center')`
Whether to center the output.

`show_widgets`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``widgets')`
Whether to display the widget inputs.

`widget_layout`` ``=`` ``ClassSelector(class_=<class`` ``'panel.layout.base.ListLike'>,`` ``constant=True,`` ``default=<class`` ``'panel.layout.base.WidgetBox'>,`` ``label='Widget`` ``layout')`
The layout object to display the widgets in.

`widget_location`` ``=`` ``Selector(default='left_top',`` ``label='Widget`` ``location',`` ``names={},`` ``objects=['left',`` ``'right',`` ``'top',`` ``'bottom',`` ``'top_left',`` ``'top_right',`` ``'bottom_left',`` ``'bottom_right',`` ``'left_top',`` ``'right_top',`` ``'right_bottom'])`
The location of the widgets relative to the output of the reactive
expression.

classmethod applies(object)
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

widget_layout
alias of [WidgetBox](panel.layout.base.md#panel.layout.base.WidgetBox)

class panel.pane.Reacton(object=None, **params)
Bases:
[IPyWidget](panel.pane.ipywidget.md#panel.pane.ipywidget.IPyWidget)

Methods

|  |  |
|----|----|
| [applies](#panel.pane.Reacton.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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
> [class="reference internal" title="panel.pane.ipywidget.IPyWidget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.ipywidget.IPyWidget](panel.pane.ipywidget.md#panel.pane.ipywidget.IPyWidget):
> object
>
>

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.SVG(object=None, **params)
Bases: [ImageBase](panel.pane.image.md#panel.pane.image.ImageBase)

The SVG pane embeds a .svg image file in a panel if provided a local
path, or will link to a remote image if provided a URL.

Reference: [https://panel.holoviz.org/reference/panes/SVG.html](https://panel.holoviz.org/reference/panes/SVG.html)

Example:

\>\>\>
SVG(
...
'https://upload.wikimedia.org/wikipedia/commons/6/6b/Bitmap_VS_SVG.svg',
...
alt_text='A
gif vs svg comparison',
...
link_url='https://en.wikipedia.org/wiki/SVG',
...
width=300,
height=400
... )

Methods

|  |  |
|----|----|
| [applies](#panel.pane.SVG.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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
> [class="reference internal" title="panel.pane.image.FileBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.FileBase](panel.pane.image.md#panel.pane.image.FileBase):
> embed
>
> [class="reference internal" title="panel.pane.image.ImageBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.ImageBase](panel.pane.image.md#panel.pane.image.ImageBase):
> alt_text, caption, fixed_aspect, link_url, target
>
>

`encode`` ``=`` ``Boolean(default=True,`` ``label='Encode')`
Whether to enable base64 encoding of the SVG, base64 encoded SVGs do not
support links.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.Str(object=None, **params)
Bases: [HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane)

The Str pane allows rendering arbitrary text and objects in a panel.

Unlike Markdown and HTML, a Str is interpreted as a raw string without
applying any markup and is displayed in a fixed-width font by default.

The pane will render any text, and if given an object will display the
object’s Python repr.

Reference: [https://panel.holoviz.org/reference/panes/Str.html](https://panel.holoviz.org/reference/panes/Str.html)

Example:

\>\>\>
Str(
...  'This raw string will not
be formatted, except for the applied
style.', ...
styles={'font-size':
'12pt'}
... )

Methods

|  |  |
|----|----|
| [applies](#panel.pane.Str.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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
>

classmethod applies(object: Any) → bool
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.Streamz(object=None, **params)
Bases: [ReplacementPane](panel.pane.base.md#panel.pane.base.ReplacementPane)

The Streamz pane renders streamz Stream objects emitting arbitrary
objects, unlike the DataFrame pane which specifically handles streamz
DataFrame and Series objects and exposes various formatting objects.

Reference:
[https://panel.holoviz.org/reference/panes/Streamz.html](https://panel.holoviz.org/reference/panes/Streamz.html)

Example:

\>\>\>
Streamz(some_streamz_stream_object,
always_watch=True)

Methods

|  |  |
|----|----|
| [applies](#panel.pane.Streamz.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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
> [class="reference internal" title="panel.pane.base.ReplacementPane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.ReplacementPane](panel.pane.base.md#panel.pane.base.ReplacementPane):
> object, inplace, \_pane
>
>

`always_watch`` ``=`` ``Boolean(default=False,`` ``label='Always`` ``watch')`
Whether to watch even when not displayed.

`rate_limit`` ``=`` ``Number(bounds=(0,`` ``None),`` ``default=0.1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Rate`` ``limit')`
The minimum interval between events.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.Textual(object=None, **params)
Bases: [Pane](panel.pane.base.md#panel.pane.base.Pane)

The Textual pane provides a wrapper around a Textual App component,
rendering it inside a Terminal and running it on the existing Panel
event loop, i.e. either on the server or the notebook asyncio.EventLoop.

Reference:
[https://panel.holoviz.org/reference/panes/Textual.html](https://panel.holoviz.org/reference/panes/Textual.html)

Example:

\>\>\>
Textual(app)

Methods

|  |  |
|----|----|
| [applies](#panel.pane.Textual.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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

classmethod applies(object)
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.VTK(obj, **params)
Bases: `object`

The VTK pane renders a VTK scene inside a panel, making it possible to
interact with complex geometries in 3D.

Reference: [https://panel.holoviz.org/reference/panes/VTK.html](https://panel.holoviz.org/reference/panes/VTK.html)

Example:

\>\>\>
pn.extension('vtk')
\>\>\>
VTK(some_vtk_object,
width=500,
height=500)

This is a Class factory and allows to switch between VTKJS,
VTKRenderWindow, and VTKRenderWindowSynchronized pane as a function of
the object type and when the serialisation of the vtkRenderWindow
occurs.

Once a pane is returned by this class (inst = VTK(object)), one can use
pn.help(inst) to see parameters available for the current pane

class panel.pane.VTKVolume(object=None, **params)
Bases: [AbstractVTK](panel.pane.vtk.vtk.md#panel.pane.vtk.vtk.AbstractVTK)

The VTKVolume pane renders 3d volumetric data defined on regular grids.
It may be constructed from a 3D NumPy array or a vtkVolume.

The pane provides a number of interactive control which can be set
either through callbacks from Python or Javascript callbacks.

Reference:
[https://panel.holoviz.org/reference/panes/VTKVolume.html](https://panel.holoviz.org/reference/panes/VTKVolume.html)

Example:

\>\>\>
pn.extension('vtk')
\>\>\>
VTKVolume(
...
data_matrix,
spacing=(3,2,1),
interpolation='nearest',
...
edge_gradient=0,
sampling=0,
...
sizing_mode='stretch_width',
height=400,
... )

Methods

|  |  |
|----|----|
| [applies](#panel.pane.VTKVolume.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |
| [register_serializer](#panel.pane.VTKVolume.register_serializer)(class_type, serializer) | Register a serializer for a given type of class. |

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
> [class="reference internal" title="panel.pane.vtk.vtk.AbstractVTK"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.vtk.vtk.AbstractVTK](panel.pane.vtk.vtk.md#panel.pane.vtk.vtk.AbstractVTK):
> axes, camera, color_mappers, orientation_widget,
> interactive_orientation_widget
>
>

`ambient`` ``=`` ``Number(default=0.2,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Ambient',`` ``step=0.01)`
Value to control the ambient lighting. It is the light an object gives
even in the absence of strong light. It is constant in all directions.

`controller_expanded`` ``=`` ``Boolean(default=True,`` ``label='Controller`` ``expanded')`
If True the volume controller panel options is expanded in the view

`colormap`` ``=`` ``Selector(default='erdc_rainbow_bright',`` ``label='Colormap',`` ``names={},`` ``objects=['KAAMS',`` ``'Cool`` ``to`` ``Warm',`` ``'Cool`` ``to`` ``Warm`` ``(Extended)',`` ``'Warm`` ``to`` ``Cool',`` ``'Warm`` ``to`` ``Cool`` ``(Extended)',`` ``'Rainbow`` ``Desaturated',`` ``'Cold`` ``and`` ``Hot',`` ``'Black-Body`` ``Radiation',`` ``'X`` ``Ray',`` ``'Grayscale',`` ``'BkRd',`` ``'BkGn',`` ``'BkBu',`` ``'BkMa',`` ``'BkCy',`` ``'Black,`` ``Blue`` ``and`` ``White',`` ``'Black,`` ``Orange`` ``and`` ``White',`` ``'Linear`` ``YGB`` ``1211g',`` ``'Linear`` ``Green`` ``(Gr4L)',`` ``'Linear`` ``Blue`` ``(8_31f)',`` ``'Blue`` ``to`` ``Red`` ``Rainbow',`` ``'Red`` ``to`` ``Blue`` ``Rainbow',`` ``'Rainbow`` ``Blended`` ``White',`` ``'Rainbow`` ``Blended`` ``Grey',`` ``'Rainbow`` ``Blended`` ``Black',`` ``'Blue`` ``to`` ``Yellow',`` ``'blot',`` ``'CIELab`` ``Blue`` ``to`` ``Red',`` ``'jet',`` ``'rainbow',`` ``'erdc_rainbow_bright',`` ``'erdc_rainbow_dark',`` ``'nic_CubicL',`` ``'nic_CubicYF',`` ``'gist_earth',`` ``'2hot',`` ``'erdc_red2yellow_BW',`` ``'erdc_marine2gold_BW',`` ``'erdc_blue2gold_BW',`` ``'erdc_sapphire2gold_BW',`` ``'erdc_red2purple_BW',`` ``'erdc_purple2pink_BW',`` ``'erdc_pbj_lin',`` ``'erdc_blue2green_muted',`` ``'erdc_blue2green_BW',`` ``'GREEN-WHITE_LINEAR',`` ``'erdc_green2yellow_BW',`` ``'blue2cyan',`` ``'erdc_blue2cyan_BW',`` ``'erdc_blue_BW',`` ``'BLUE-WHITE',`` ``'erdc_purple_BW',`` ``'erdc_magenta_BW',`` ``'magenta',`` ``'RED-PURPLE',`` ``'erdc_red_BW',`` ``'RED_TEMPERATURE',`` ``'erdc_orange_BW',`` ``'heated_object',`` ``'erdc_gold_BW',`` ``'erdc_brown_BW',`` ``'copper_Matlab',`` ``'pink_Matlab',`` ``'bone_Matlab',`` ``'gray_Matlab',`` ``'Purples',`` ``'Blues',`` ``'Greens',`` ``'PuBu',`` ``'BuPu',`` ``'BuGn',`` ``'GnBu',`` ``'GnBuPu',`` ``'BuGnYl',`` ``'PuRd',`` ``'RdPu',`` ``'Oranges',`` ``'Reds',`` ``'RdOr',`` ``'BrOrYl',`` ``'RdOrYl',`` ``'CIELab_blue2red',`` ``'blue2yellow',`` ``'erdc_blue2gold',`` ``'erdc_blue2yellow',`` ``'erdc_cyan2orange',`` ``'erdc_purple2green',`` ``'erdc_purple2green_dark',`` ``'coolwarm',`` ``'BuRd',`` ``'Spectral_lowBlue',`` ``'GnRP',`` ``'GYPi',`` ``'GnYlRd',`` ``'GBBr',`` ``'PuOr',`` ``'PRGn',`` ``'PiYG',`` ``'OrPu',`` ``'BrBG',`` ``'GyRd',`` ``'erdc_divHi_purpleGreen',`` ``'erdc_divHi_purpleGreen_dim',`` ``'erdc_divLow_icePeach',`` ``'erdc_divLow_purpleGreen',`` ``'Haze_green',`` ``'Haze_lime',`` ``'Haze',`` ``'Haze_cyan',`` ``'nic_Edge',`` ``'erdc_iceFire_H',`` ``'erdc_iceFire_L',`` ``'hsv',`` ``'hue_L60',`` ``'Spectrum',`` ``'Warm',`` ``'Cool',`` ``'Blues',`` ``'Wild`` ``Flower',`` ``'Citrus',`` ``'Brewer`` ``Diverging`` ``Purple-Orange`` ``(11)',`` ``'Brewer`` ``Diverging`` ``Purple-Orange`` ``(10)',`` ``'Brewer`` ``Diverging`` ``Purple-Orange`` ``(9)',`` ``'Brewer`` ``Diverging`` ``Purple-Orange`` ``(8)',`` ``'Brewer`` ``Diverging`` ``Purple-Orange`` ``(7)',`` ``'Brewer`` ``Diverging`` ``Purple-Orange`` ``(6)',`` ``'Brewer`` ``Diverging`` ``Purple-Orange`` ``(5)',`` ``'Brewer`` ``Diverging`` ``Purple-Orange`` ``(4)',`` ``'Brewer`` ``Diverging`` ``Purple-Orange`` ``(3)',`` ``'Brewer`` ``Diverging`` ``Spectral`` ``(11)',`` ``'Brewer`` ``Diverging`` ``Spectral`` ``(10)',`` ``'Brewer`` ``Diverging`` ``Spectral`` ``(9)',`` ``'Brewer`` ``Diverging`` ``Spectral`` ``(8)',`` ``'Brewer`` ``Diverging`` ``Spectral`` ``(7)',`` ``'Brewer`` ``Diverging`` ``Spectral`` ``(6)',`` ``'Brewer`` ``Diverging`` ``Spectral`` ``(5)',`` ``'Brewer`` ``Diverging`` ``Spectral`` ``(4)',`` ``'Brewer`` ``Diverging`` ``Spectral`` ``(3)',`` ``'Brewer`` ``Diverging`` ``Brown-Blue-Green`` ``(11)',`` ``'Brewer`` ``Diverging`` ``Brown-Blue-Green`` ``(10)',`` ``'Brewer`` ``Diverging`` ``Brown-Blue-Green`` ``(9)',`` ``'Brewer`` ``Diverging`` ``Brown-Blue-Green`` ``(8)',`` ``'Brewer`` ``Diverging`` ``Brown-Blue-Green`` ``(7)',`` ``'Brewer`` ``Diverging`` ``Brown-Blue-Green`` ``(6)',`` ``'Brewer`` ``Diverging`` ``Brown-Blue-Green`` ``(5)',`` ``'Brewer`` ``Diverging`` ``Brown-Blue-Green`` ``(4)',`` ``'Brewer`` ``Diverging`` ``Brown-Blue-Green`` ``(3)',`` ``'Brewer`` ``Sequential`` ``Blue-Green`` ``(9)',`` ``'Brewer`` ``Sequential`` ``Blue-Green`` ``(8)',`` ``'Brewer`` ``Sequential`` ``Blue-Green`` ``(7)',`` ``'Brewer`` ``Sequential`` ``Blue-Green`` ``(6)',`` ``'Brewer`` ``Sequential`` ``Blue-Green`` ``(5)',`` ``'Brewer`` ``Sequential`` ``Blue-Green`` ``(4)',`` ``'Brewer`` ``Sequential`` ``Blue-Green`` ``(3)',`` ``'Brewer`` ``Sequential`` ``Yellow-Orange-Brown`` ``(9)',`` ``'Brewer`` ``Sequential`` ``Yellow-Orange-Brown`` ``(8)',`` ``'Brewer`` ``Sequential`` ``Yellow-Orange-Brown`` ``(7)',`` ``'Brewer`` ``Sequential`` ``Yellow-Orange-Brown`` ``(6)',`` ``'Brewer`` ``Sequential`` ``Yellow-Orange-Brown`` ``(5)',`` ``'Brewer`` ``Sequential`` ``Yellow-Orange-Brown`` ``(4)',`` ``'Brewer`` ``Sequential`` ``Yellow-Orange-Brown`` ``(3)',`` ``'Brewer`` ``Sequential`` ``Blue-Purple`` ``(9)',`` ``'Brewer`` ``Sequential`` ``Blue-Purple`` ``(8)',`` ``'Brewer`` ``Sequential`` ``Blue-Purple`` ``(7)',`` ``'Brewer`` ``Sequential`` ``Blue-Purple`` ``(6)',`` ``'Brewer`` ``Sequential`` ``Blue-Purple`` ``(5)',`` ``'Brewer`` ``Sequential`` ``Blue-Purple`` ``(4)',`` ``'Brewer`` ``Sequential`` ``Blue-Purple`` ``(3)',`` ``'Brewer`` ``Qualitative`` ``Accent',`` ``'Brewer`` ``Qualitative`` ``Dark2',`` ``'Brewer`` ``Qualitative`` ``Set2',`` ``'Brewer`` ``Qualitative`` ``Pastel2',`` ``'Brewer`` ``Qualitative`` ``Pastel1',`` ``'Brewer`` ``Qualitative`` ``Set1',`` ``'Brewer`` ``Qualitative`` ``Paired',`` ``'Brewer`` ``Qualitative`` ``Set3',`` ``'Traffic`` ``Lights',`` ``'Traffic`` ``Lights`` ``For`` ``Deuteranopes',`` ``'Traffic`` ``Lights`` ``For`` ``Deuteranopes`` ``2',`` ``'Muted`` ``Blue-Green',`` ``'Green-Blue`` ``Asymmetric`` ``Divergent`` ``(62Blbc)',`` ``'Asymmtrical`` ``Earth`` ``Tones`` ``(6_21b)',`` ``'Yellow`` ``15',`` ``'Magma`` ``(matplotlib)',`` ``'Inferno`` ``(matplotlib)',`` ``'Plasma`` ``(matplotlib)',`` ``'Viridis`` ``(matplotlib)',`` ``'BlueObeliskElements'])`
Name of the colormap used to transform pixel value in color.

`diffuse`` ``=`` ``Number(default=0.7,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Diffuse',`` ``step=0.01)`
Value to control the diffuse Lighting. It relies on both the light
direction and the object surface normal.

`display_volume`` ``=`` ``Boolean(default=True,`` ``label='Display`` ``volume')`
If set to True, the 3D representation of the volume is displayed using
ray casting.

`display_slices`` ``=`` ``Boolean(default=False,`` ``label='Display`` ``slices')`
If set to true, the orthgonal slices in the three (X, Y, Z) directions
are displayed. Position of each slice can be controlled using
slice\_(i,j,k) parameters.

`edge_gradient`` ``=`` ``Number(bounds=(0,`` ``1),`` ``default=0.4,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Edge`` ``gradient',`` ``step=0.01)`
Parameter to adjust the opacity of the volume based on the gradient
between voxels.

`interpolation`` ``=`` ``Selector(default='fast_linear',`` ``label='Interpolation',`` ``names={},`` ``objects=['fast_linear',`` ``'linear',`` ``'nearest'])`
interpolation type for sampling a volume. nearest interpolation will
snap to the closest voxel, linear will perform trilinear interpolation
to compute a scalar value from surrounding voxels. fast_linear under
WebGL 1 will perform bilinear interpolation on X and Y but use nearest
for Z. This is slightly faster than full linear at the cost of no Z axis
linear interpolation.

`mapper`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Mapper')`
Lookup Table in format {low, high, palette}

`max_data_size`` ``=`` ``Number(default=33.554432,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``data`` ``size')`
Maximum data size transfer allowed without subsampling

`nan_opacity`` ``=`` ``Number(bounds=(0.0,`` ``1.0),`` ``default=1.0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Nan`` ``opacity')`
Opacity applied to nan values in slices

`origin`` ``=`` ``Tuple(allow_None=True,`` ``label='Origin',`` ``length=3)`
Origin of the volume in the scene coordinates. If None, the origin is
set to (0, 0, 0)

`render_background`` ``=`` ``Color(allow_named=True,`` ``default='#52576e',`` ``label='Render`` ``background')`
Allows to specify the background color of the 3D rendering. The value
must be specified as an hexadecimal color string.

`rescale`` ``=`` ``Boolean(default=False,`` ``label='Rescale')`
If set to True the colormap is rescaled between min and max value of the
non-transparent pixel, otherwise the full range of the pixel values are
used.

`shadow`` ``=`` ``Boolean(default=True,`` ``label='Shadow')`
If set to False, then the mapper for the volume will not perform shading
computations, it is the same as setting ambient=1, diffuse=0,
specular=0.

`sampling`` ``=`` ``Number(bounds=(0,`` ``1),`` ``default=0.4,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Sampling',`` ``step=0.01)`
Parameter to adjust the distance between samples used for rendering. The
lower the value is the more precise is the representation but it is more
computationally intensive.

`spacing`` ``=`` ``Tuple(default=(1,`` ``1,`` ``1),`` ``label='Spacing',`` ``length=3)`
Distance between voxel in each direction

`specular`` ``=`` ``Number(default=0.3,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Specular',`` ``step=0.01)`
Value to control specular lighting. It is the light reflects back toward
the camera when hitting the object.

`specular_power`` ``=`` ``Number(default=8.0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Specular`` ``power')`
Specular power refers to how much light is reflected in a mirror like
fashion, rather than scattered randomly in a diffuse manner.

`slice_i`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Slice`` ``i')`
Integer parameter to control the position of the slice normal to the X
direction.

`slice_j`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Slice`` ``j')`
Integer parameter to control the position of the slice normal to the Y
direction.

`slice_k`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Slice`` ``k')`
Integer parameter to control the position of the slice normal to the Z
direction.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

classmethod register_serializer(class_type, serializer)
Register a serializer for a given type of class. A serializer is a
function which take an instance of class_type (like a vtk.vtkImageData)
as input and return a numpy array of the data

class panel.pane.Vega(object=None, **params)
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
| [applies](#panel.pane.Vega.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |
| [export](#panel.pane.Vega.export)(fmt\[, as_pane\]) | Exports the Vega spec to various formats. |

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

class panel.pane.Video(object=None, **params)
Bases: `_MediaBase`

The Video Pane displays a video player given a local or remote video
file.

The widget also allows access and control over the player state
including toggling of playing/paused and loop state, the current time,
and the volume.

Depending on the browser the video player supports mp4, webm, and ogg
containers and a variety of codecs.

Reference:
[https://panel.holoviz.org/reference/panes/Video.html](https://panel.holoviz.org/reference/panes/Video.html)

Example:

\>\>\>
Video(
...
'https://file-examples-com.github.io/uploads/2017/04/file_example_MP4_640_3MG.mp4',
...
width=640,
height=360,
loop=True
... )

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
> `panel.pane.media._MediaBase`: loop, time,
> throttle, paused, autoplay, muted
>
>

`object`` ``=`` ``ClassSelector(allow_None=True,`` ``allow_refs=True,`` ``class_=(<class`` ``'str'>,`` ``<class`` ``'pathlib.Path'>,`` ``<class`` ``'_io.BytesIO'>,`` ``<class`` ``'bytes'>),`` ``default='',`` ``label='Object')`
The video file either local or remote as a string or URL or as a bytes
or BytesIO object.

`volume`` ``=`` ``Integer(bounds=(0,`` ``100),`` ``default=100,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Volume')`
The volume of the media player.

class panel.pane.Vizzu(object=None, **params)
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
| [animate](#panel.pane.Vizzu.animate)(anim\[, options\]) | Updates the chart with a new configuration. |
| [applies](#panel.pane.Vizzu.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |
| [on_click](#panel.pane.Vizzu.on_click)(callback) | Register a callback to be executed when any element in the chart is clicked on. |

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

class panel.pane.YT(object=None, **params)
Bases: [HTML](panel.pane.markup.md#panel.pane.markup.HTML)

YT panes wrap plottable objects from the YT library. By default, the
height and width are calculated by summing all contained plots, but can
optionally be specified explicitly to provide additional space.

Methods

|  |  |
|----|----|
| [applies](#panel.pane.YT.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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

panel.pane.panel(obj: Any, **kwargs) → Viewable \| ServableMixin
Creates a displayable Panel object given any valid Python object.

The appropriate Pane to render a specific object is determined by
iterating over all defined Pane types and querying it’s .applies method
for a priority value.

Any keyword arguments are passed down to the applicable Pane.

Setting loading_indicator=True will display a loading indicator while
the function is being evaluated.

To lazily render components when the application loads, you may also
provide a Python function, with or without bound parameter dependencies
and set defer_load=True.

Reference: [https://panel.holoviz.org/explanation/components/components_overview.html#panes](https://panel.holoviz.org/explanation/components/components_overview.html#panes)

\>\>\>
pn.panel(some_python_object,
width=500)

Parameters:
**obj: object**
Any object to be turned into a Panel

****kwargs: dict**
Any keyword arguments to be passed to the applicable Pane

Returns:
layout: Viewable
A Viewable representation of the input object

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
