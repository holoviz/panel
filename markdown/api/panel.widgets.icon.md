# panel.widgets.icon module

class panel.widgets.icon.ButtonIcon(\*, clicks, toggle_duration, active_icon, icon, size, description, description_delay, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_ClickableIcon`,
`_ClickButton`,
`TooltipMixin`

The ButtonIcon widget facilitates event triggering upon button clicks.

This widget displays a default icon initially. Upon being clicked, an
active_icon appears for a specified toggle_duration.

For instance, the ButtonIcon can be effectively utilized to implement a
feature akin to ChatGPT’s copy-to-clipboard button.

The button incorporates a value attribute, which alternates between
False and True as the click event is processed.

Furthermore, it includes an clicks attribute, enabling subscription to
click events for further actions or monitoring.

Reference:
[https://panel.holoviz.org/reference/widgets/ButtonIcon.html](https://panel.holoviz.org/reference/widgets/ButtonIcon.html)

Example:

\>\>\> button_icon
=
pn.widgets.ButtonIcon(
...
icon='clipboard',
...
active_icon='check',
...
description='Copy',
...
toggle_duration=2000
... )

Methods

|  |  |
|----|----|
| [on_click](#panel.widgets.icon.ButtonIcon.on_click)(callback) | Register a callback to be executed when the button is clicked. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets._mixin.TooltipMixin`:
> description, description_delay
>
> `panel.widgets.icon._ClickableIcon`:
> active_icon, icon, size
>
>

`value`` ``=`` ``Boolean(default=False,`` ``label='Value')`
Toggles from False to True while the event is being processed.

`clicks`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Clicks')`
The number of times the button has been clicked.

`toggle_duration`` ``=`` ``Integer(default=75,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Toggle`` ``duration')`
The number of milliseconds the active_icon should be shown for and how
long the button should be disabled for.

on_click(callback: Callable\[\[param.parameterized.Event\], None\]) → param.parameterized.Watcher
Register a callback to be executed when the button is clicked.

The callback is given an Event argument declaring the number of clicks.

Parameters:
**callback: (Callable\[\[param.parameterized.Event\], None\])**
The function to run on click events. Must accept a positional Event
argument

Returns:
watcher: param.Parameterized.Watcher
A Watcher that executes the callback when the MenuButton is clicked.

class panel.widgets.icon.ToggleIcon(**params: Any)
Bases: `_ClickableIcon`,
`TooltipMixin`

The ToggleIcon widget allows toggling a single condition between
True/False states. This widget is interchangeable with the Checkbox and
Toggle widget.

This widget incorporates a value attribute, which alternates between
False and True.

Reference:
[https://panel.holoviz.org/reference/widgets/ToggleIcon.html](https://panel.holoviz.org/reference/widgets/ToggleIcon.html)

Example:

\>\>\>
pn.widgets.ToggleIcon(
...
icon="thumb-up",
active_icon="thumb-down",
size="4em",
description="Like"
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets._mixin.TooltipMixin`:
> description, description_delay
>
> `panel.widgets.icon._ClickableIcon`: value,
> active_icon, icon, size
>
>

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
