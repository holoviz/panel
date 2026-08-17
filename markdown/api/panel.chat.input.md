# panel.chat.input module

class panel.chat.input.ChatAreaInput(**params: Any)
Bases:
[TextAreaInput](panel.widgets.input.md#panel.widgets.input.TextAreaInput)

The ChatAreaInput allows entering any multiline string using a text
input box, with the ability to press enter to submit the message.

Unlike TextAreaInput, the ChatAreaInput defaults to auto_grow=True and
max_rows=10, and the value is not synced to the server until the enter
key is pressed so bind on value_input if you need to access the existing
value.

Lines are joined with the newline character n.

Reference:
[https://panel.holoviz.org/reference/chat/ChatAreaInput.html](https://panel.holoviz.org/reference/chat/ChatAreaInput.html)

Example:

\>\>\>
ChatAreaInput(max_rows=10)

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
> height, margin, disabled
>
> `panel.widgets.input._TextInputBase`: value,
> width, description, placeholder, value_input
>
> [class="reference internal"
> title="panel.widgets.input.TextAreaInput"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets. input .TextAreaInput](panel.widgets.input.md#panel.widgets.input.TextAreaInput):
> cols
>
>

`max_length`` ``=`` ``Integer(default=50000,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``length')`
Max count of characters in the input field.

`auto_grow`` ``=`` ``Boolean(default=True,`` ``label='Auto`` ``grow')`
Whether the text area should automatically grow vertically to
accommodate the current text.

`max_rows`` ``=`` ``Integer(allow_None=True,`` ``default=10,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``rows')`
When combined with auto_grow this determines the maximum number of rows
the input area can grow.

`rows`` ``=`` ``Integer(default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Rows')`
Number of rows in the text input field.

`resizable`` ``=`` ``Selector(default='height',`` ``label='Resizable',`` ``names={},`` ``objects=['both',`` ``'width',`` ``'height',`` ``False])`
Whether the layout is interactively resizable, and if so in which
dimensions: width, height, or both. Can only be set during
initialization.

`disabled_enter`` ``=`` ``Boolean(default=False,`` ``label='Disabled`` ``enter')`
If True, disables sending the message by pressing the enter_sends key.

`enter_sends`` ``=`` ``Boolean(default=True,`` ``label='Enter`` ``sends')`
If True, pressing the Enter key sends the message, if False it is sent
by pressing the Ctrl+Enter.

`enter_pressed`` ``=`` ``Event(default=False,`` ``label='Enter`` ``pressed')`
Event when the Enter/Ctrl+Enter key has been pressed.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
