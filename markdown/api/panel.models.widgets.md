# panel.models.widgets module

Custom bokeh Widget models.

class panel.models.widgets.Button(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `Button`

Attributes:
**tooltip**
A tooltip with plain text or rich HTML contents, providing general help
or description of a widget’s or component’s function.

**tooltip_delay**
Delay (in milliseconds) to display the tooltip after the cursor has
hovered over the Button, default is 500ms.

tooltip
A tooltip with plain text or rich HTML contents, providing general help
or description of a widget’s or component’s function.

tooltip_delay
Delay (in milliseconds) to display the tooltip after the cursor has
hovered over the Button, default is 500ms.

class panel.models.widgets.CheckboxButtonGroup(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `CheckboxButtonGroup`

Attributes:
**tooltip**
A tooltip with plain text or rich HTML contents, providing general help
or description of a widget’s or component’s function.

**tooltip_delay**
Delay (in milliseconds) to display the tooltip after the cursor has
hovered over the Button, default is 500ms.

tooltip
A tooltip with plain text or rich HTML contents, providing general help
or description of a widget’s or component’s function.

tooltip_delay
Delay (in milliseconds) to display the tooltip after the cursor has
hovered over the Button, default is 500ms.

class panel.models.widgets.CustomMultiSelect(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `MultiSelect`

MultiSelect widget which allows capturing double tap events.

class panel.models.widgets.CustomSelect(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `Select`

Custom widget that extends the base Bokeh Select by adding a parameter
to disable one or more options.

Attributes:
**disabled_options**
List of options to disable.

**size**

disabled_options
List of options to disable.

class panel.models.widgets.DiscretePlayer(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: [Player](#panel.models.widgets.Player)

Attributes:
**options**
List of discrete options.

options
List of discrete options.

class panel.models.widgets.DoubleClickEvent(model, option=None)
Bases: `ModelEvent`

class panel.models.widgets.EnterEvent(model, value_input)
Bases: `ModelEvent`

class panel.models.widgets.FileDownload(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `InputWidget`

Attributes:
**auto**
Whether to download on click

**button_type**
A style for the button, signifying it’s role.

**clicks**
A private property that used to trigger
`on_click` event handler.

**data**
Encoded URI data.

**embed**
Whether the data is pre-embedded.

**filename**
Filename to use on download

**icon**
An optional image appearing to the left of button’s text. An instance of
`Icon` (such as
`BuiltinIcon`,
`SVGIcon`, or
`TablerIcon`).\`

**label**
The text label for the button to display.

auto
Whether to download on click

button_type
A style for the button, signifying it’s role.

clicks
A private property that used to trigger
`on_click` event handler.

data
Encoded URI data.

embed
Whether the data is pre-embedded.

filename
Filename to use on download

icon
An optional image appearing to the left of button’s text. An instance of
`Icon` (such as
`BuiltinIcon`,
`SVGIcon`, or
`TablerIcon`).\`

label
The text label for the button to display.

class panel.models.widgets.Player(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `Widget`

The Player widget provides controls to play through a number of frames.

Attributes:
**direction**
Current play direction of the Player (-1: playing in reverse, 0: paused,
1: playing)

**end**
Upper bound of the Player slider

**interval**
Interval between updates

**loop_policy**

**preview_duration**
Duration (in milliseconds) for showing the current FPS when clicking the
slower/faster buttons, before reverting to the icon.

**scale_buttons**
Percentage to scale the size of the buttons by

**show_loop_controls**
Whether the loop controls radio buttons are shown

**show_value**
Whether to show the widget value

**start**
Lower bound of the Player slider

**step**
Number of steps to advance the player by.

**title**
The slider’s label (supports math
text).

**value**
Current value of the player app

**value_align**
Location to display the value of the slider (“start” “center”, “end”)

**value_throttled**
Current throttled value of the player app

**visible_buttons**
The buttons to display on the player.

**visible_loop_options**
The loop options to display on the player.

direction
Current play direction of the Player (-1: playing in reverse, 0: paused,
1: playing)

end
Upper bound of the Player slider

interval
Interval between updates

preview_duration
Duration (in milliseconds) for showing the current FPS when clicking the
slower/faster buttons, before reverting to the icon.

scale_buttons
Percentage to scale the size of the buttons by

show_loop_controls
Whether the loop controls radio buttons are shown

show_value
Whether to show the widget value

start
Lower bound of the Player slider

step
Number of steps to advance the player by.

title
The slider’s label (supports math
text).

value
Current value of the player app

value_align
Location to display the value of the slider (“start” “center”, “end”)

value_throttled
Current throttled value of the player app

visible_buttons
The buttons to display on the player.

visible_loop_options
The loop options to display on the player.

class panel.models.widgets.RadioButtonGroup(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `RadioButtonGroup`

Attributes:
**tooltip**
A tooltip with plain text or rich HTML contents, providing general help
or description of a widget’s or component’s function.

**tooltip_delay**
Delay (in milliseconds) to display the tooltip after the cursor has
hovered over the Button, default is 500ms.

tooltip
A tooltip with plain text or rich HTML contents, providing general help
or description of a widget’s or component’s function.

tooltip_delay
Delay (in milliseconds) to display the tooltip after the cursor has
hovered over the Button, default is 500ms.

class panel.models.widgets.SingleSelect(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `InputWidget`

Single-select widget.

Attributes:
**disabled_options**
List of options to disable.

**options**
Available selection options. Options may be provided either as a list of
possible string values, or as a list of tuples, each of the form
`(value,`` ``label)`.
In the latter case, the visible widget text for each value will be
corresponding given label.

**size**
The number of visible options in the dropdown list. (This uses the
`select` HTML element’s
`size` attribute. Some browsers might not show
less than 3 options.)

**value**
Initial or selected value.

disabled_options
List of options to disable.

options
Available selection options. Options may be provided either as a list of
possible string values, or as a list of tuples, each of the form
`(value,`` ``label)`.
In the latter case, the visible widget text for each value will be
corresponding given label.

size
The number of visible options in the dropdown list. (This uses the
`select` HTML element’s
`size` attribute. Some browsers might not show
less than 3 options.)

value
Initial or selected value.

class panel.models.widgets.TextAreaInput(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `TextAreaInput`

Attributes:
**auto_grow**
Whether the text area should automatically grow vertically to
accommodate the current text.

**max_rows**
Maximum number of rows the input area can grow to if auto_grow is
enabled.

auto_grow
Whether the text area should automatically grow vertically to
accommodate the current text.

max_rows
Maximum number of rows the input area can grow to if auto_grow is
enabled.

class panel.models.widgets.TextInput(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `TextInput`

class panel.models.widgets.TooltipIcon(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `Widget`

Attributes:
**description**
The tooltip held by the icon

description
The tooltip held by the icon

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
