# panel.chat.icon module

The icon module provides a low-level API for rendering chat related
icons.

class panel.chat.icon.ChatCopyIcon(\*, \_request_sync, \_synced, fill, value, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: [ReactiveHTML](panel.reactive.md#panel.reactive.ReactiveHTML)

ChatCopyIcon copies the value to the clipboard when clicked. To avoid
sending the value to the frontend the value is only synced after the
icon is clicked.

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, design, height, min_width, min_height, max_width,
> max_height, margin, styles, stylesheets, tags, width, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
>

`css_classes`` ``=`` ``List(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=['copy-icon'],`` ``item_type=<class`` ``'str'>,`` ``label='Css`` ``classes',`` ``nested_refs=True)`
The CSS classes of the widget.

`fill`` ``=`` ``String(default='none',`` ``label='Fill')`
The fill color of the icon.

`value`` ``=`` ``String(allow_None=True,`` ``label='Value')`
The text to copy to the clipboard.

`_synced`` ``=`` ``String(allow_None=True,`` ``label='`` ``synced')`
The text to copy to the clipboard.

`_request_sync`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``request`` ``sync')`

class panel.chat.icon.ChatReactionIcons(\*, active_icons, default_layout, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[CompositeWidget](panel.widgets.base.md#panel.widgets.base.CompositeWidget)

A widget to display reaction icons that can be clicked on.

Parameters:
value : List
The selected reactions.

options : Dict
A key-value pair of reaction values and their corresponding tabler icon
names found on [https://tabler-icons.io](https://tabler-icons.io).

active_icons : Dict
The mapping of reactions to their corresponding active icon names; if
not set, the active icon name will default to its “filled” version.

**Reference: https://panel.holoviz.org/reference/chat/ChatReactionIcons.html**

**:Example:**

**\>\>\> ChatReactionIcons(value=\[“like”\], options={“like”: “thumb-up”, “dislike”: “thumb-down”})**

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, design, min_width, min_height, max_width,
> max_height, styles, stylesheets, tags, width_policy, height_policy,
> sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, width, disabled
>
>

`value`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``label='Value')`
The active reactions.

`css_classes`` ``=`` ``List(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=['reaction-icons'],`` ``item_type=<class`` ``'str'>,`` ``label='Css`` ``classes',`` ``nested_refs=True)`
The CSS classes of the widget.

`margin`` ``=`` ``Margin(allow_None=True,`` ``allow_refs=True,`` ``default=0,`` ``label='Margin')`
Allows to create additional space around the component. May be specified
as a two-tuple of the form (vertical, horizontal) or a four-tuple (top,
right, bottom, left).

`active_icons`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Active`` ``icons')`
The mapping of reactions to their corresponding active icon names. If
not set, the active icon name will default to its “filled” version.

`options`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={'favorite':`` ``'heart'},`` ``label='Options')`
A key-value pair of reaction values and their corresponding tabler icon
names found on [https://tabler-icons.io](https://tabler-icons.io).

`default_layout`` ``=`` ``ClassSelector(class_=<class`` ``'panel.layout.base.Panel'>,`` ``default=<class`` ``'panel.layout.base.Column'>,`` ``label='Default`` ``layout')`
The layout to use for the icons. Defaults to Column, which stacks the
icons vertically.

default_layout
alias of [Column](panel.layout.base.md#panel.layout.base.Column)

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
