# panel.pane.placeholder module

Defines the Placeholder pane which serves as a placeholder for other
Panel components.

class panel.pane.placeholder.Placeholder(object=None, **params)
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
| [update](#panel.pane.placeholder.Placeholder.update)(object) | Updates the object on the Placeholder. |

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

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
