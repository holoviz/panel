# panel.pane.streamz module

Renders Streamz Stream objects.

class panel.pane.streamz.Streamz(object=None, **params)
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
| [applies](#panel.pane.streamz.Streamz.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
