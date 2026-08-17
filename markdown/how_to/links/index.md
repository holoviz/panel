# Link Parameters with Callbacks API

If you need full control over how your GUI is set up then you can manually define widgets that link directly to other objects using either Python or JavaScript (JS) callbacks. Python callbacks are simple for Python users to write and can directly access Python data structures, while JS callbacks can directly manipulate the displayed HTML document and allow setting up dynamic behavior even for exported HTML files (with no Python process running). This section contains how-to guides that address common tasks related the use of callbacks.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: links
:link-type: doc

How to use the convenient, high-level `.link` API to link parameters in Python.
:::

:link: watchers
:link-type: doc

How to use the flexible, low-level `.watch` API to trigger callbacks in Python.
:::

:link: jslinks
:link-type: doc

How to link parameters of two objects in Javascript.
:::

:link: link_plots
:link-type: doc

How to link Bokeh and HoloViews plot parameters in Javascript.
:::

:link: jscallbacks
:link-type: doc

How to write arbitrary Javascript callbacks linking one or more objects.
:::

::::

## Examples

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:img-top: https://assets.holoviz.org/panel/how_to/links/bokeh_property_editor.png
:link: examples/bokeh_property_editor
:link-type: doc

Build a UI that allows editing a Bokeh figure in JS.
:::

:img-top: https://assets.holoviz.org/panel/how_to/links/deckgl.png
:link: examples/deckgl
:link-type: doc

JS Link JSON editors to allow live editing a Deck.gl plot.
:::

:img-top: https://assets.holoviz.org/panel/how_to/links/holoviews_glyph_link.png
:link: examples/holoviews_glyph_link
:link-type: doc

JS Link widgets to a glyph in a HoloViews plot.
:::

:img-top: https://assets.holoviz.org/panel/how_to/links/plotly.png
:link: examples/plotly
:link-type: doc

JS Link a widget to a Plotly plot.
:::

:img-top: https://assets.holoviz.org/panel/how_to/links/vega.png
:link: examples/vega_link
:link-type: doc

JS Link a widget to a Vega plot.
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

links
watchers
jslinks
link_plots
jscallbacks
```
