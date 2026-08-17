# panel.layout.swipe module

The Swipe layout enables you to quickly compare two panels

class panel.layout.swipe.Swipe(\*objects, **params)
Bases: [ListLike](panel.layout.base.md#panel.layout.base.ListLike),
[ReactiveHTML](panel.reactive.md#panel.reactive.ReactiveHTML)

The Swipe layout enables you to quickly compare two panels laid out on
top of each other with a part of the *before* panel shown on one side of
a slider and a part of the *after* panel shown on the other side.

Attributes:
**after**

**before**

Methods

|  |  |
|----|----|
| [clone](#panel.layout.swipe.Swipe.clone)(\*objects, **params) | Makes a copy of the layout sharing the same parameters. |
| [select](#panel.layout.swipe.Swipe.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

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
>

`objects`` ``=`` ``Children(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'panel.viewable.Viewable'>,`` ``label='Objects')`
The list of child objects that make up the layout.

`slider_width`` ``=`` ``Integer(bounds=(0,`` ``25),`` ``default=5,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Slider`` ``width')`
The width of the slider in pixels

`slider_color`` ``=`` ``Color(allow_named=True,`` ``default='black',`` ``label='Slider`` ``color')`
The color of the slider

`start`` ``=`` ``Integer(bounds=(0,`` ``100),`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
Limits the minimum percentage the swipe handler can be moved to.

`end`` ``=`` ``Integer(bounds=(0,`` ``100),`` ``default=100,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
Limits the maximum percentage the swipe handler can be moved to.

`value`` ``=`` ``Integer(bounds=(0,`` ``100),`` ``default=50,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
The percentage of the *after* panel to show.

`_before`` ``=`` ``Parameter(allow_None=True,`` ``label='`` ``before')`

`_after`` ``=`` ``Parameter(allow_None=True,`` ``label='`` ``after')`

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
