# panel.chat.interface module

The interface module provides an even higher-level API for interacting
with a list of ChatMessage objects compared to the ChatFeed through a
frontend input UI.

class panel.chat.interface.ChatInterface(\*objects, **params)
Bases: [ChatFeed](panel.chat.feed.md#panel.chat.feed.ChatFeed)

High level widget that contains the chat log and the chat input.

Reference:
[https://panel.holoviz.org/reference/chat/ChatInterface.html](https://panel.holoviz.org/reference/chat/ChatInterface.html)

Example:

\>\>\> async
def
repeat_contents(contents,
user,
instance):
\>\>\>  yield
contents

\>\>\> chat_interface
=
ChatInterface(
...
callback=repeat_contents,
widgets=\[TextInput(),
FileInput()\]
... )

Attributes:
[active](#panel.chat.interface.ChatInterface.active)
The currently active input widget tab index; -1 if there is only one
widget available which is not in a tab.

[active_widget](#panel.chat.interface.ChatInterface.active_widget)
The currently active widget.

Methods

|  |  |
|----|----|
| [send](#panel.chat.interface.ChatInterface.send)(value\[, user, avatar, respond, ...\]) | Sends a value and creates a new message in the chat log. |
| [stream](#panel.chat.interface.ChatInterface.stream)(value\[, user, avatar, message, ...\]) | Streams a token and updates the provided message, if provided. |

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
> [class="reference internal" title="panel.layout.base.ListPanel"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListPanel](panel.layout.base.md#panel.layout.base.ListPanel):
> scroll
>
> [class="reference internal" title="panel.chat.feed.ChatFeed"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.chat.feed.ChatFeed](panel.chat.feed.md#panel.chat.feed.ChatFeed):
> margin, objects, adaptive, auto_scroll_limit, callback,
> callback_exception, callback_user, callback_avatar, edit_callback,
> card_params, collapsible, disabled, message_params, header, help_text,
> load_buffer, placeholder_text, placeholder_params,
> placeholder_threshold, post_hook, renderers, scroll_button_threshold,
> show_activity_dot, view_latest, \_placeholder, \_callback_state,
> \_prompt_trigger, \_callback_trigger, \_disabled_stack
>
>

`auto_send_types`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'type'>,`` ``label='Auto`` ``send`` ``types')`
The widget types to automatically send when the user presses enter or
clicks away from the widget. If not provided, defaults to \[TextInput\].

`avatar`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'str'>,`` ``<class`` ``'_io.BytesIO'>,`` ``<class`` ``'bytes'>,`` ``<class`` ``'panel.pane.image.ImageBase'>),`` ``label='Avatar')`
The avatar to use for the user. Can be a single character text, an
emoji, or anything supported by pn.pane.Image. If not set, uses the
first character of the name.

`reset_on_send`` ``=`` ``Boolean(default=True,`` ``label='Reset`` ``on`` ``send')`
Whether to reset the widget’s value after sending a message; has no
effect for TextInput.

`show_send`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``send')`
Whether to show the send button.

`show_stop`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``stop')`
Whether to show the stop button temporarily replacing the send button
during callback; has no effect if callback is not async.

`show_rerun`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``rerun')`
Whether to show the rerun button.

`show_undo`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``undo')`
Whether to show the undo button.

`show_clear`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``clear')`
Whether to show the clear button.

`show_button_name`` ``=`` ``Boolean(allow_None=True,`` ``label='Show`` ``button`` ``name')`
Whether to show the button name.

`show_button_tooltips`` ``=`` ``Boolean(default=False,`` ``label='Show`` ``button`` ``tooltips')`
Whether to show the button tooltips.

`user`` ``=`` ``String(default='User',`` ``label='User')`
Name of the ChatInterface user.

`widgets`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'panel.widgets.base.WidgetBase'>,`` ``<class`` ``'list'>),`` ``label='Widgets')`
Widgets to use for the input. If not provided, defaults to
\[TextInput\].

`button_properties`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Button`` ``properties')`
Allows addition of functionality or customization of buttons by
supplying a mapping from the button name to a dictionary containing the
icon, callback, post_callback, and/or js_on_click keys. If the button
names correspond to default buttons (send, rerun, undo, clear), the
default icon can be updated and if a callback key value pair is
provided, the specified callback functionality runs before the existing
one. For button names that don’t match existing ones, new buttons are
created and must include a callback, post_callback, and/or js_on_click
key. The provided callbacks should have a signature that accepts two
positional arguments: instance (the ChatInterface instance) and event
(the button click event). The js_on_click key should be a str or dict.
If str, provide the JavaScript code; else if dict, it must have a code
key, containing the JavaScript code to execute when the button is
clicked, and optionally an args key, containing dictionary of arguments
to pass to the JavaScript code.

`_widgets`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='`` ``widgets')`
The input widgets.

`_input_container`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.layout.base.Row'>,`` ``label='`` ``input`` ``container')`
The input message row that wraps the input layout (Tabs / Row) to easily
swap between Tabs and Rows, depending on number of widgets.

`_input_layout`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'panel.layout.base.Row'>,`` ``<class`` ``'panel.layout.tabs.Tabs'>),`` ``label='`` ``input`` ``layout')`
The input layout that contains the input widgets.

`_button_data`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='`` ``button`` ``data')`
Metadata and data related to the buttons.

`_buttons`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='`` ``buttons')`
The rendered buttons.

property active: int
The currently active input widget tab index; -1 if there is only one
widget available which is not in a tab.

Returns:
The active input widget tab index.

property active_widget: WidgetBase
The currently active widget.

Returns:
The active widget.

send(value: ChatMessage \| dict \| Any, user: str \| None = None, avatar: str \| bytes \| BytesIO \| None = None, respond: bool = True, trigger_post_hook: bool = True, **message_params) → ChatMessage \| None
Sends a value and creates a new message in the chat log.

If respond is True, additionally executes the callback, if provided.

Parameters:
value : ChatMessage \| dict \| Any
The message contents to send.

user : str \| None
The user to send as; overrides the message message’s user if provided.
Will default to the user parameter.

avatar : str \| bytes \| BytesIO \| None
The avatar to use; overrides the message message’s avatar if provided.
Will default to the avatar parameter.

respond : bool
Whether to execute the callback.

**trigger_post_hook: bool**
Whether to trigger the post hook after sending.

message_params : dict
Additional parameters to pass to the ChatMessage.

Returns:
The message that was created.

stream(value: str \| dict \| ChatMessage \| Viewable, user: str \| None = None, avatar: str \| bytes \| BytesIO \| None = None, message: ChatMessage \| None = None, replace: bool = False, trigger_post_hook: bool = False, **message_params) → ChatMessage \| None
Streams a token and updates the provided message, if provided. Otherwise
creates a new message in the chat log, so be sure the returned message
is passed back into the method, e.g. message = chat.stream(token,
message=message).

This method is primarily for outputs that are not generators– notably
LangChain. For most cases, use the send method instead.

Parameters:
value : str \| dict \| ChatMessage
The new token value to stream.

user : str \| None
The user to stream as; overrides the message’s user if provided. Will
default to the user parameter.

avatar : str \| bytes \| BytesIO \| None
The avatar to use; overrides the message’s avatar if provided. Will
default to the avatar parameter.

message : ChatMessage \| None
The message to update.

replace : bool
Whether to replace the existing text when streaming a string or dict.

**trigger_post_hook: bool**
Whether to trigger the post hook after streaming.

message_params : dict
Additional parameters to pass to the ChatMessage.

Returns:
The message that was updated.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
