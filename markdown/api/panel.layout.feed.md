# panel.layout.feed module

class panel.layout.feed.Feed(\*objects, **params)
Bases: [Column](panel.layout.base.md#panel.layout.base.Column)

The Feed class inherits from the Column layout, thereby enabling the
arrangement of multiple panel objects within a vertical container.
However, it restrictively manages the number of objects displayed at any
moment. This layout is particularly useful for efficiently rendering a
substantial number of objects.

Similar to Column, the Feed provides a list-like API, including methods
such as append, extend, clear, insert, pop, remove, and \_\_setitem\_\_.
These methods facilitate interactive updates and modifications to the
layout.

Reference:
[https://panel.holoviz.org/reference/layouts/Feed.html](https://panel.holoviz.org/reference/layouts/Feed.html)

Example:

\>\>\>
pn.Feed(some_widget,
some_pane,
some_python_object,
...,
python_object_1002)

Methods

|  |  |
|----|----|
| [scroll_to_latest](#panel.layout.feed.Feed.scroll_to_latest)(\[scroll_limit\]) | Scrolls the Feed to the latest entry. |

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
> [class="reference internal" title="panel.layout.base.Column"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.Column](panel.layout.base.md#panel.layout.base.Column):
> auto_scroll_limit, scroll_button_threshold, scroll_position,
> view_latest
>
>

`scroll`` ``=`` ``Selector(default='y',`` ``label='Scroll',`` ``names={},`` ``objects=[False,`` ``True,`` ``'both-auto',`` ``'y-auto',`` ``'x-auto',`` ``'both',`` ``'x',`` ``'y'])`
Whether to add scrollbars if the content overflows the size of the
container. If “both-auto”, will only add scrollbars if the content
overflows in either directions. If “x-auto” or “y-auto”, will only add
scrollbars if the content overflows in the respective direction. If
“both”, will always add scrollbars. If “x” or “y”, will always add
scrollbars in the respective direction. If False, overflowing content
will be clipped. If True, will only add scrollbars in the direction of
the container, (e.g. Column: vertical, Row: horizontal).

`load_buffer`` ``=`` ``Integer(bounds=(0,`` ``None),`` ``default=50,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Load`` ``buffer')`
The number of objects loaded on each side of the visible objects. When
scrolled halfway into the buffer, the feed will automatically load
additional objects while unloading objects on the opposite side.

`visible_range`` ``=`` ``Range(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Visible`` ``range',`` ``length=2,`` ``readonly=True)`
Read-only upper and lower bounds of the currently visible feed objects.
This list is automatically updated based on scrolling.

scroll_to_latest(scroll_limit: float \| None = None) → None
Scrolls the Feed to the latest entry.

Parameters:
scroll_limit : float, optional
Maximum pixel distance from the latest object in the Feed to trigger
scrolling. If the distance exceeds this limit, scrolling will not occur.
If this is not set, it will always scroll to the latest while setting
this to 0 disables scrolling.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
