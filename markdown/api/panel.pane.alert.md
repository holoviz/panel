# panel.pane.alert module

Bootstrap inspired Alerts

See [https://getbootstrap.com/docs/4.0/components/alerts/](https://getbootstrap.com/docs/4.0/components/alerts/)

class panel.pane.alert.Alert(object=None, **params)
Bases: [Markdown](panel.pane.markup.md#panel.pane.markup.Markdown)

The Alert pane allows providing contextual feedback messages for typical
user actions. The Alert supports markdown strings.

Reference:
[https://panel.holoviz.org/reference/panes/Alert.html](https://panel.holoviz.org/reference/panes/Alert.html)

Example:

\>\>\>
Alert('Some
important message',
alert_type='warning')

Methods

|  |  |
|----|----|
| [applies](#panel.pane.alert.Alert.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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
> [class="reference internal" title="panel.pane.markup.HTMLBasePane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
> [class="reference internal" title="panel.pane.markup.Markdown"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.Markdown](panel.pane.markup.md#panel.pane.markup.Markdown):
> dedent, disable_anchors, disable_math, extensions, hard_line_break,
> plugins, renderer, renderer_options
>
>

`alert_type`` ``=`` ``Selector(default='primary',`` ``label='Alert`` ``type',`` ``names={},`` ``objects=['primary',`` ``'secondary',`` ``'success',`` ``'danger',`` ``'warning',`` ``'info',`` ``'light',`` ``'dark'])`
The type of Alert and one of ‘primary’, ‘secondary’, ‘success’,
‘danger’, ‘warning’, ‘info’, ‘light’, ‘dark’.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
