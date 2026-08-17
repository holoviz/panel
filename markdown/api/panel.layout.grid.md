# panel.layout.grid module

Layout components to lay out objects in a grid.

class panel.layout.grid.GridBox(\*objects: Any, **params: Any)
Bases: [ListPanel](panel.layout.base.md#panel.layout.base.ListPanel)

The GridBox is a list-like layout (unlike GridSpec) that wraps objects
into a grid according to the specified nrows and ncols parameters.

It has a list-like API with methods to append, extend, clear, insert,
pop, remove and \_\_setitem\_\_, which makes it possible to
interactively update and modify the layout.

Reference:
[https://panel.holoviz.org/reference/layouts/GridBox.html](https://panel.holoviz.org/reference/layouts/GridBox.html)

Example:

\>\>\>
pn.GridBox(
...
python_object_1,
python_object_2,
..., ...
 python_object_24,
ncols=6
... )

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
> [class="reference internal" title="panel.layout.base.ListPanel"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListPanel](panel.layout.base.md#panel.layout.base.ListPanel):
> scroll
>
>

`nrows`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Nrows')`
Number of rows to reflow the layout into.

`ncols`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Ncols')`
Number of columns to reflow the layout into.

class panel.layout.grid.GridSpec(\*, mode, ncols, nrows, objects, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: [Panel](panel.layout.base.md#panel.layout.base.Panel)

The GridSpec is an *array like* layout that allows arranging multiple
Panel objects in a grid using a simple API to assign objects to
individual grid cells or to a grid span.

Other layout containers function like lists, but a GridSpec has an API
similar to a 2D array, making it possible to use 2D assignment to
populate, index, and slice the grid.

See GridStack for a similar layout that allows the user to resize and
drag the cells.

Reference:
[https://panel.holoviz.org/reference/layouts/GridSpec.html](https://panel.holoviz.org/reference/layouts/GridSpec.html)

Example:

\>\>\>
import
panel
as
pn \>\>\>
gspec =
pn.GridSpec(width=800,
height=600)
\>\>\>
gspec\[:,
0 \]
=
pn.Spacer(styles=dict(background='red'))
\>\>\>
gspec\[0,
1:3\]
=
pn.Spacer(styles=dict(background='green'))
\>\>\>
gspec\[1,
2:4\]
=
pn.Spacer(styles=dict(background='orange'))
\>\>\>
gspec\[2,
1:4\]
=
pn.Spacer(styles=dict(background='blue'))
\>\>\>
gspec\[0:1,
3:4\]
=
pn.Spacer(styles=dict(background='purple'))
\>\>\> gspec

Attributes:
**grid**

Methods

|  |  |
|----|----|
| [clone](#panel.layout.grid.GridSpec.clone)(**params) | Makes a copy of the GridSpec sharing the same parameters. |

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

`objects`` ``=`` ``ChildDict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Objects')`
The dictionary of child objects that make up the grid.

`mode`` ``=`` ``Selector(default='warn',`` ``label='Mode',`` ``names={},`` ``objects=['warn',`` ``'error',`` ``'override'])`
Whether to warn, error or simply override on overlapping assignment.

`ncols`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Ncols')`
Limits the number of columns that can be assigned.

`nrows`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Nrows')`
Limits the number of rows that can be assigned.

clone(**params)
Makes a copy of the GridSpec sharing the same parameters.

Parameters:
**params: Keyword arguments override the parameters on the clone.**

Returns:
Cloned GridSpec object

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
