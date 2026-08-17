# panel.layout.gridstack module

class panel.layout.gridstack.GridStack(\*, allow_drag, allow_resize, state, mode, ncols, nrows, objects, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: [ReactiveHTML](panel.reactive.md#panel.reactive.ReactiveHTML),
[GridSpec](panel.layout.grid.md#panel.layout.grid.GridSpec)

The GridStack layout allows arranging multiple Panel objects in a grid
using a simple API to assign objects to individual grid cells or to a
grid span.

Other layout containers function like lists, but a GridSpec has an API
similar to a 2D array, making it possible to use 2D assignment to
populate, index, and slice the grid.

Reference:
[https://panel.holoviz.org/reference/layouts/GridStack.html](https://panel.holoviz.org/reference/layouts/GridStack.html)

Example:

\>\>\>
pn.extension('gridstack')
\>\>\> gstack
=
GridStack(sizing_mode='stretch_both')
\>\>\>
gstack\[
: ,
0:
3\]
=
pn.Spacer(styles=dict(background='red'))
\>\>\>
gstack\[0:2,
3:
9\]
=
pn.Spacer(styles=dict(background='green'))
\>\>\>
gstack\[2:4,
6:12\]
=
pn.Spacer(styles=dict(background='orange'))
\>\>\>
gstack\[4:6,
3:12\]
=
pn.Spacer(styles=dict(background='blue'))
\>\>\>
gstack\[0:2,
9:12\]
=
pn.Spacer(styles=dict(background='purple'))

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, margin, styles, stylesheets, tags,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.layout.grid.GridSpec"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.grid.GridSpec](panel.layout.grid.md#panel.layout.grid.GridSpec):
> objects, mode, ncols, nrows
>
>

`height`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
The height of the component (in pixels). This can be either fixed or
preferred height, depending on height sizing policy.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The width of the component (in pixels). This can be either fixed or
preferred width, depending on width sizing policy.

`allow_resize`` ``=`` ``Boolean(default=True,`` ``label='Allow`` ``resize')`
Allow resizing the grid cells.

`allow_drag`` ``=`` ``Boolean(default=True,`` ``label='Allow`` ``drag')`
Allow dragging the grid cells.

`state`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'dict'>,`` ``label='State')`
Current state of the grid (updated as items are resized and dragged).

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
