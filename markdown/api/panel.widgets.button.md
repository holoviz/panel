# panel.widgets.button module

Defines the Button and button-like widgets which allow triggering events
or merely toggling between on-off states.

class panel.widgets.button.Button(\*, clicks, button_style, button_type, color, variant, icon, icon_size, description, description_delay, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_ButtonBase`,
`_ClickButton`,
[IconMixin](#panel.widgets.button.IconMixin),
`TooltipMixin`

The Button widget allows triggering events when the button is clicked.

The Button provides a value parameter, which will toggle from False to
True while the click event is being processed

It also provides an additional clicks parameter, that can be watched to
subscribe to click events.

Reference: [https://panel.holoviz.org/reference/widgets/Button.html#widgets-gallery-button](https://panel.holoviz.org/reference/widgets/Button.html#widgets-gallery-button)

Example:

\>\>\>
pn.widgets.Button(name='Click
me',
icon='caret-right',
color='primary')

Methods

|  |  |
|----|----|
| [jslink](#panel.widgets.button.Button.jslink)(target\[, code, args, bidirectional\]) | Links properties on the this Button to those on the target object in Javascript (JS) code. |
| [on_click](#panel.widgets.button.Button.on_click)(callback) | Register a callback to be executed when the Button is clicked. |

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
> [title="panel.widgets.button.IconMixin"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.button.IconMixin](#panel.widgets.button.IconMixin):
> icon, icon_size
>
> `panel.widgets.button._ButtonBase`:
> button_type, button_style, color, variant
>
>

`value`` ``=`` ``Event(allow_refs=True,`` ``default=False,`` ``label='Value')`
Toggles from False to True while the event is being processed.

`clicks`` ``=`` ``Integer(allow_refs=True,`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Clicks')`
Number of clicks (can be listened to)

jslink(target: JSLinkTarget, code: dict\[str, str\] \| None = None, args: dict\[str, t.Any\] \| None = None, bidirectional: bool = False, **links: str) → Link
Links properties on the this Button to those on the target object in
Javascript (JS) code.

Supports two modes, either specify a mapping between the source and
target model properties as keywords or provide a dictionary of JS code
snippets which maps from the source parameter to a JS code snippet which
is executed when the property changes.

Parameters:
**target: panel.viewable.Viewable \| bokeh.model.Model \| holoviews.core.dimension.Dimensioned**
The target to link the value(s) to.

**code: dict**
Custom code which will be executed when the widget value changes.

**args: dict**
A mapping of objects to make available to the JS callback

**bidirectional: boolean**
Whether to link source and target bi-directionally. Default is False.

****links: dict\[str,str\]**
A mapping between properties on the source model and the target model
property to link it to.

Returns:
Link
The Link can be used unlink the widget and the target model.

on_click(callback: Callable\[\[param.parameterized.Event\], None \| Awaitable\[None\]\]) → param.parameterized.Watcher
Register a callback to be executed when the Button is clicked.

The callback is given an Event argument declaring the number of clicks

Parameters:
**callback:**
The function to run on click events. Must accept a positional Event
argument. Can be a sync or async function

Returns:
watcher: param.Parameterized.Watcher
A Watcher that executes the callback when the button is clicked.

class panel.widgets.button.IconMixin(**params: Any)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

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
> height, margin, width, disabled
>
>

`icon`` ``=`` ``String(allow_None=True,`` ``allow_refs=True,`` ``label='Icon')`
An icon to render to the left of the button label. Either an SVG or an
icon name which is loaded from [https://tabler-icons.io](https://tabler-icons.io).

`icon_size`` ``=`` ``String(allow_refs=True,`` ``default='1em',`` ``label='Icon`` ``size')`
Size of the icon as a string, e.g. 12px or 1em.

class panel.widgets.button.MenuButton(\*, clicked, items, split, button_style, button_type, color, variant, icon, icon_size, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_ButtonBase`,
`_ClickButton`,
[IconMixin](#panel.widgets.button.IconMixin)

The MenuButton widget allows specifying a list of menu items to select
from triggering events when the button is clicked.

Unlike other widgets, it does not have a value parameter. Instead it has
a clicked parameter that can be watched to trigger events and which
reports the last clicked menu item.

Reference:
[https://panel.holoviz.org/reference/widgets/MenuButton.html](https://panel.holoviz.org/reference/widgets/MenuButton.html)

Example:

\>\>\> menu_items
=
\[('Option
A',
'a'),
('Option
B',
'b'),
None,
('Option
C',
'c')\]
\>\>\>
MenuButton(name='Dropdown',
items=menu_items,
color='primary')

Methods

|  |  |
|----|----|
| [on_click](#panel.widgets.button.MenuButton.on_click)(callback) | Register a callback to be executed when the button is clicked. |

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
> height, margin, width, disabled
>
> [title="panel.widgets.button.IconMixin"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.button.IconMixin](#panel.widgets.button.IconMixin):
> icon, icon_size
>
> `panel.widgets.button._ButtonBase`:
> button_type, button_style, color, variant
>
>

`clicked`` ``=`` ``String(allow_None=True,`` ``label='Clicked')`
Last menu item that was clicked.

`items`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=(<class`` ``'str'>,`` ``<class`` ``'tuple'>,`` ``<class`` ``'NoneType'>),`` ``label='Items')`
Menu items in the dropdown. Allows strings, tuples of the form (title,
value) or Nones to separate groups of items.

`split`` ``=`` ``Boolean(default=False,`` ``label='Split')`
Whether to add separate dropdown area to button.

on_click(callback: Callable\[\[param.parameterized.Event\], None\]) → param.parameterized.Watcher
Register a callback to be executed when the button is clicked.

The callback is given an Event argument declaring the number of clicks

Parameters:
**callback: (Callable\[\[param.parameterized.Event\], None\])**
The function to run on click events. Must accept a positional Event
argument

Returns:
watcher: param.Parameterized.Watcher
A Watcher that executes the callback when the MenuButton is clicked.

class panel.widgets.button.Toggle(**params: Any)
Bases: `_ButtonBase`,
[IconMixin](#panel.widgets.button.IconMixin)

The Toggle widget allows toggling a single condition between True/False
states.

This widget is interchangeable with the Checkbox widget.

Reference:
[https://panel.holoviz.org/reference/widgets/Toggle.html](https://panel.holoviz.org/reference/widgets/Toggle.html)

Example:

\>\>\>
Toggle(name='Toggle',
color='success')

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
> [title="panel.widgets.button.IconMixin"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.button.IconMixin](#panel.widgets.button.IconMixin):
> icon, icon_size
>
> `panel.widgets.button._ButtonBase`:
> button_type, button_style, color, variant
>
>

`value`` ``=`` ``Boolean(default=False,`` ``label='Value')`
Whether the button is currently toggled.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
