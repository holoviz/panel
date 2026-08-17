# panel.widgets.player module

Defines Player widgets which offer media-player like controls.

class panel.widgets.player.DiscretePlayer(\*, value_throttled, direction, interval, loop_policy, preview_duration, scale_buttons, show_loop_controls, show_value, step, value_align, visible_buttons, visible_loop_options, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[PlayerBase](#panel.widgets.player.PlayerBase),
[SelectBase](panel.widgets.select.md#panel.widgets.select.SelectBase)

The DiscretePlayer provides controls to iterate through a list of
discrete options. The speed at which the widget plays is defined by the
interval (in milliseconds), but it is also possible to skip items using
the step parameter.

Reference: [https://panel.holoviz.org/reference/widgets/DiscretePlayer.html](https://panel.holoviz.org/reference/widgets/DiscretePlayer.html)

Example:

\>\>\>
DiscretePlayer(
...
name='Discrete
Player', ...
options=\[2,
4,
8,
16,
32,
64,
128\],
value=32,
...
loop_policy='loop',
...
value_align='start'
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
> margin, disabled
>
> [class="reference internal" title="panel.widgets.select.SelectBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](panel.widgets.select.md#panel.widgets.select.SelectBase):
> options
>
> [title="panel.widgets.player.PlayerBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.player.PlayerBase](#panel.widgets.player.PlayerBase):
> height, width, direction, loop_policy, preview_duration,
> show_loop_controls, step, value_align, scale_buttons, visible_buttons,
> visible_loop_options
>
>

`value`` ``=`` ``Parameter(allow_None=True,`` ``label='Value')`
Current player value

`interval`` ``=`` ``Integer(default=500,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Interval')`
Interval between updates

`show_value`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``value')`
Whether to show the widget value

`value_throttled`` ``=`` ``Parameter(allow_None=True,`` ``constant=True,`` ``label='Value`` ``throttled')`
Current player value

class panel.widgets.player.Player(\*, end, start, value_throttled, direction, interval, loop_policy, preview_duration, scale_buttons, show_loop_controls, show_value, step, value_align, visible_buttons, visible_loop_options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[PlayerBase](#panel.widgets.player.PlayerBase)

The Player provides controls to play and skip through a number of frames
defined by explicit start and end values. The speed at which the widget
plays is defined by the interval (in milliseconds), but it is also
possible to skip frames using the step parameter.

Reference:
[https://panel.holoviz.org/reference/widgets/Player.html](https://panel.holoviz.org/reference/widgets/Player.html)

Example:

\>\>\>
Player(name='Player',
start=0,
end=100,
value=32,
loop_policy='loop',
value_align='top_center')

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
> margin, disabled
>
> [title="panel.widgets.player.PlayerBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.player.PlayerBase](#panel.widgets.player.PlayerBase):
> height, width, direction, interval, loop_policy, preview_duration,
> show_loop_controls, show_value, step, value_align, scale_buttons,
> visible_buttons, visible_loop_options
>
>

`value`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
Current player value

`start`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
Lower bound on the slider value

`end`` ``=`` ``Integer(default=10,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
Upper bound on the slider value

`value_throttled`` ``=`` ``Integer(constant=True,`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``throttled')`
Current throttled player value.

class panel.widgets.player.PlayerBase(\*, direction, interval, loop_policy, preview_duration, scale_buttons, show_loop_controls, show_value, step, value_align, visible_buttons, visible_loop_options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

Methods

|             |     |
|-------------|-----|
| **pause**   |     |
| **play**    |     |
| **reverse** |     |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label, value
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
> margin, disabled
>
>

`height`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=80,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
The height of the component (in pixels). This can be either fixed or
preferred height, depending on height sizing policy.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=510,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of this component. If sizing_mode is set to stretch or scale mode
this will merely be used as a suggestion.

`direction`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Direction')`
Current play direction of the Player (-1: playing in reverse, 0: paused,
1: playing)

`interval`` ``=`` ``Integer(default=500,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Interval')`
Interval between updates, in milliseconds. Default is 500, i.e. two
updates per second.

`loop_policy`` ``=`` ``Selector(default='once',`` ``label='Loop`` ``policy',`` ``names={},`` ``objects=['once',`` ``'loop',`` ``'reflect'])`
Policy used when player hits last frame

`preview_duration`` ``=`` ``Integer(bounds=(0,`` ``None),`` ``default=1500,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Preview`` ``duration')`
Duration (in milliseconds) for showing the current FPS when clicking the
slower/faster buttons, before reverting to the icon.

`show_loop_controls`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``loop`` ``controls')`
Whether the loop controls radio buttons are shown

`show_value`` ``=`` ``Boolean(default=False,`` ``label='Show`` ``value')`
Whether to show the widget value

`step`` ``=`` ``Integer(default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
Number of frames to step forward and back by on each event.

`value_align`` ``=`` ``Selector(default='start',`` ``label='Value`` ``align',`` ``names={},`` ``objects=['start',`` ``'center',`` ``'end'])`
Location to display the value of the slider (“start”, “center”, “end”)

`scale_buttons`` ``=`` ``Number(default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Scale`` ``buttons')`
The scaling factor to resize the buttons.

`visible_buttons`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=['slower',`` ``'first',`` ``'previous',`` ``'reverse',`` ``'pause',`` ``'play',`` ``'next',`` ``'last',`` ``'faster'],`` ``label='Visible`` ``buttons')`
The buttons to display on the player.

`visible_loop_options`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=['once',`` ``'loop',`` ``'reflect'],`` ``label='Visible`` ``loop`` ``options')`
The loop options to display on the player.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
