# panel.layout.float module

class panel.layout.float.FloatPanel(\*objects, name='', **params)
Bases: [ListLike](panel.layout.base.md#panel.layout.base.ListLike),
[ReactiveHTML](panel.reactive.md#panel.reactive.ReactiveHTML)

Float provides a floating panel layout.

Reference:
[https://panel.holoviz.org/reference/layouts/FloatPanel.html](https://panel.holoviz.org/reference/layouts/FloatPanel.html)

Example:

\>\>\>
import
panel
as
pn \>\>\>
pn.extension("floatpanel")
\>\>\>
pn.layout.FloatPanel("**I
can float**!",
position="center",
width=300).servable()

Methods

|  |  |
|----|----|
| [clone](#panel.layout.float.FloatPanel.clone)(\*objects, **params) | Makes a copy of the layout sharing the same parameters. |
| [select](#panel.layout.float.FloatPanel.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
>

`config`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Config')`
Additional jsPanel configuration with precedence over parameter values.

`contained`` ``=`` ``Boolean(default=True,`` ``label='Contained')`
Whether the component is contained within parent container or completely
free floating.

`position`` ``=`` ``Selector(default='right-top',`` ``label='Position',`` ``names={},`` ``objects=['center',`` ``'left-top',`` ``'center-top',`` ``'right-top',`` ``'right-center',`` ``'right-bottom',`` ``'center-bottom',`` ``'left-bottom',`` ``'left-center'])`
The initial position if the container is free-floating.

`offsetx`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Offsetx')`
Horizontal offset in pixels.

`offsety`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Offsety')`
Vertical offset in pixels.

`theme`` ``=`` ``String(default='primary',`` ``label='Theme')`
The theme which can be one of: - Built-ins: ‘default’, ‘primary’,
‘secondary’, ‘info’, ‘success’, ‘warning’, ‘danger’, ‘light’, ‘dark’ and
‘none’ - HEX, RGB and HSL color values like ‘#123456’ Any standardized
color name like ‘forestgreen’ and color names from the Material Design
Color System like ‘purple900’ - Additionally a theme string may include
one of the modifiers ‘filled’, ‘filledlight’, ‘filleddark’ or
‘fillcolor’ separated from the theme color by a space like ‘primary

`status`` ``=`` ``Selector(default='normalized',`` ``label='Status',`` ``names={},`` ``objects=['normalized',`` ``'maximized',`` ``'minimized',`` ``'smallified',`` ``'smallifiedmax',`` ``'closed'])`
The current status of the panel.

clone(\*objects: t.Any, **params: t.Any) → Self
Makes a copy of the layout sharing the same parameters.

Parameters:
**objects: Objects to add to the cloned layout.**

**params: Keyword arguments override the parameters on the clone.**

Returns:
Cloned layout object

select(selector=None)
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
