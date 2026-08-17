# panel.widgets.widget module

class panel.widgets.widget.fixed(value: Any, **kwargs: Any)
Bases: `Parameterized`

A pseudo-widget whose value is fixed and never synced to the client.

Methods

|  |  |
|----|----|
| [get_interact_value](#panel.widgets.widget.fixed.get_interact_value)() | Return the value for this widget which should be passed to interactive functions. |

**Parameter Definitions**

------------------------------------------------------------------------

`description`` ``=`` ``String(default='',`` ``label='Description')`

`value`` ``=`` ``Parameter(allow_None=True,`` ``label='Value')`
Any Python object

get_interact_value()
Return the value for this widget which should be passed to interactive
functions. Custom widgets can change this method to process the raw
value `self.value`.

class panel.widgets.widget.widget(\*, name)
Bases: `ParameterizedFunction`

Attempts to find a widget appropriate for a given value.

Parameters:
**label: str**
The label of the resulting widget.

**value: Any**
The value to deduce a widget from.

**default: Any**
The default value for the resulting widget.

****params: Any**
Additional keyword arguments to pass to the widget.

Methods

|  |  |
|----|----|
| [widget_from_iterable](#panel.widgets.widget.widget.widget_from_iterable)(o, label) | Make widgets from an iterable. |
| [widget_from_single_value](#panel.widgets.widget.widget.widget_from_single_value)(o, label) | Make widgets from single values, which can be used as parameter defaults. |
| [widget_from_tuple](#panel.widgets.widget.widget.widget_from_tuple)(o, label, default) | Make widgets from a tuple abbreviation. |

Returns:
Widget

**Parameter Definitions**

------------------------------------------------------------------------

static widget_from_iterable(o, label: str) → Widget \| None
Make widgets from an iterable. This should not be done for a string or
tuple.

static widget_from_single_value(o, label: str) → Widget \| None
Make widgets from single values, which can be used as parameter
defaults.

static widget_from_tuple(o, label: str, default) → Widget \| None
Make widgets from a tuple abbreviation.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
