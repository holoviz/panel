# panel.layout.flex module

class panel.layout.flex.FlexBox(\*objects, **params)
Bases: [ListLike](panel.layout.base.md#panel.layout.base.ListLike),
[ReactiveHTML](panel.reactive.md#panel.reactive.ReactiveHTML)

The FlexBox is a list-like layout (unlike GridSpec) that wraps objects
into a CSS flex container.

It has a list-like API with methods to append, extend, clear, insert,
pop, remove and \_\_setitem\_\_, which makes it possible to
interactively update and modify the layout. It exposes all the CSS
options for controlling the behavior and layout of the flex box.

Reference:
[https://panel.holoviz.org/reference/layouts/FlexBox.html](https://panel.holoviz.org/reference/layouts/FlexBox.html)

Example:

\>\>\>
pn.FlexBox(
...
some_python_object,
another_python_object,
..., ...
 the_last_python_object
... )

Methods

|  |  |
|----|----|
| [clone](#panel.layout.flex.FlexBox.clone)(\*objects, **params) | Makes a copy of the layout sharing the same parameters. |
| [select](#panel.layout.flex.FlexBox.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

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

`align_content`` ``=`` ``Selector(default='flex-start',`` ``label='Align`` ``content',`` ``names={},`` ``objects=['normal',`` ``'flex-start',`` ``'flex-end',`` ``'center',`` ``'space-between',`` ``'space-around',`` ``'space-evenly',`` ``'stretch',`` ``'start',`` ``'end',`` ``'baseline',`` ``'first`` ``baseline',`` ``'last`` ``baseline'])`
Defines how a flex container’s lines align when there is extra space in
the cross-axis.

`align_items`` ``=`` ``Selector(default='flex-start',`` ``label='Align`` ``items',`` ``names={},`` ``objects=['stretch',`` ``'flex-start',`` ``'flex-end',`` ``'center',`` ``'baseline',`` ``'first`` ``baseline',`` ``'last`` ``baseline',`` ``'start',`` ``'end',`` ``'self-start',`` ``'self-end'])`
Defines the default behavior for how flex items are laid out along the
cross axis on the current line.

`flex_direction`` ``=`` ``Selector(default='row',`` ``label='Flex`` ``direction',`` ``names={},`` ``objects=['row',`` ``'row-reverse',`` ``'column',`` ``'column-reverse'])`
This establishes the main-axis, thus defining the direction flex items
are placed in the flex container.

`flex_wrap`` ``=`` ``Selector(default='wrap',`` ``label='Flex`` ``wrap',`` ``names={},`` ``objects=['nowrap',`` ``'wrap',`` ``'wrap-reverse'])`
Whether and how to wrap items in the flex container.

`gap`` ``=`` ``String(default='',`` ``label='Gap')`
Defines the spacing between flex items, supporting various units (px,
em, rem, %, vw/vh).

`justify_content`` ``=`` ``Selector(default='flex-start',`` ``label='Justify`` ``content',`` ``names={},`` ``objects=['flex-start',`` ``'flex-end',`` ``'center',`` ``'space-between',`` ``'space-around',`` ``'space-evenly',`` ``'start',`` ``'end',`` ``'left',`` ``'right'])`
Defines the alignment along the main axis.

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
