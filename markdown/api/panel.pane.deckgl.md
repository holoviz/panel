# panel.pane.deckgl module

Defines a PyDeck Pane which renders a PyDeck plot using a PyDeckPlot
bokeh model.

class panel.pane.deckgl.DeckGL(object=None, **params)
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
| [applies](#panel.pane.deckgl.DeckGL.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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

panel.pane.deckgl.lower_camel_case_keys(attrs)
Makes all the keys in a dictionary camel-cased and lower-case

Parameters:
attrs : dict
Dictionary for which all the keys should be converted to camel-case

panel.pane.deckgl.to_camel_case(snake_case: str) → str
Makes a snake case string into a camel case one

Parameters:
snake_case : str
Snake-cased string (e.g., “snake_cased”) to be converted to camel-case
(e.g., “camelCase”)

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
