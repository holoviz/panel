# panel.pane.textual module

class panel.pane.textual.Textual(object=None, **params)
Bases: [Pane](panel.pane.base.md#panel.pane.base.Pane)

The Textual pane provides a wrapper around a Textual App component,
rendering it inside a Terminal and running it on the existing Panel
event loop, i.e. either on the server or the notebook asyncio.EventLoop.

Reference:
[https://panel.holoviz.org/reference/panes/Textual.html](https://panel.holoviz.org/reference/panes/Textual.html)

Example:

\>\>\>
Textual(app)

Methods

|  |  |
|----|----|
| [applies](#panel.pane.textual.Textual.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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

classmethod applies(object)
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
