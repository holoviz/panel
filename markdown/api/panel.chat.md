# panel.chat package

## Submodules

- [panel.chat.feed module](panel.chat.feed.md)
  - [CallbackState](panel.chat.feed.md#panel.chat.feed.CallbackState)
  - [ChatFeed](panel.chat.feed.md#panel.chat.feed.ChatFeed)
    - [ChatFeed.add_step()](panel.chat.feed.md#panel.chat.feed.ChatFeed.add_step)
    - [ChatFeed.clear()](panel.chat.feed.md#panel.chat.feed.ChatFeed.clear)
    - [ChatFeed.prompt_user()](panel.chat.feed.md#panel.chat.feed.ChatFeed.prompt_user)
    - [ChatFeed.respond()](panel.chat.feed.md#panel.chat.feed.ChatFeed.respond)
    - [ChatFeed.scroll_to()](panel.chat.feed.md#panel.chat.feed.ChatFeed.scroll_to)
    - [ChatFeed.select()](panel.chat.feed.md#panel.chat.feed.ChatFeed.select)
    - [ChatFeed.send()](panel.chat.feed.md#panel.chat.feed.ChatFeed.send)
    - [ChatFeed.serialize()](panel.chat.feed.md#panel.chat.feed.ChatFeed.serialize)
    - [ChatFeed.stop()](panel.chat.feed.md#panel.chat.feed.ChatFeed.stop)
    - [ChatFeed.stream()](panel.chat.feed.md#panel.chat.feed.ChatFeed.stream)
    - [ChatFeed.trigger_post_hook()](panel.chat.feed.md#panel.chat.feed.ChatFeed.trigger_post_hook)
    - [ChatFeed.undo()](panel.chat.feed.md#panel.chat.feed.ChatFeed.undo)
  - [StopCallback](panel.chat.feed.md#panel.chat.feed.StopCallback)
- [panel.chat.icon module](panel.chat.icon.md)
  - [ChatCopyIcon](panel.chat.icon.md#panel.chat.icon.ChatCopyIcon)
  - [ChatReactionIcons](panel.chat.icon.md#panel.chat.icon.ChatReactionIcons)
    - [ChatReactionIcons.default_layout](panel.chat.icon.md#panel.chat.icon.ChatReactionIcons.default_layout)
- [panel.chat.input module](panel.chat.input.md)
  - [ChatAreaInput](panel.chat.input.md#panel.chat.input.ChatAreaInput)
- [panel.chat.interface module](panel.chat.interface.md)
  - [ChatInterface](panel.chat.interface.md#panel.chat.interface.ChatInterface)
    - [ChatInterface.active](panel.chat.interface.md#panel.chat.interface.ChatInterface.active)
    - [ChatInterface.active_widget](panel.chat.interface.md#panel.chat.interface.ChatInterface.active_widget)
    - [ChatInterface.send()](panel.chat.interface.md#panel.chat.interface.ChatInterface.send)
    - [ChatInterface.stream()](panel.chat.interface.md#panel.chat.interface.ChatInterface.stream)
- [panel.chat.langchain module](panel.chat.langchain.md)
  - [PanelCallbackHandler](panel.chat.langchain.md#panel.chat.langchain.PanelCallbackHandler)
    - [PanelCallbackHandler.on_chat_model_start()](panel.chat.langchain.md#panel.chat.langchain.PanelCallbackHandler.on_chat_model_start)
    - [PanelCallbackHandler.on_retriever_end()](panel.chat.langchain.md#panel.chat.langchain.PanelCallbackHandler.on_retriever_end)
    - [PanelCallbackHandler.on_retriever_error()](panel.chat.langchain.md#panel.chat.langchain.PanelCallbackHandler.on_retriever_error)
    - [PanelCallbackHandler.on_text()](panel.chat.langchain.md#panel.chat.langchain.PanelCallbackHandler.on_text)
- [panel.chat.message module](panel.chat.message.md)
  - [ChatMessage](panel.chat.message.md#panel.chat.message.ChatMessage)
    - [ChatMessage.select()](panel.chat.message.md#panel.chat.message.ChatMessage.select)
    - [ChatMessage.serialize()](panel.chat.message.md#panel.chat.message.ChatMessage.serialize)
    - [ChatMessage.stream()](panel.chat.message.md#panel.chat.message.ChatMessage.stream)
    - [ChatMessage.update()](panel.chat.message.md#panel.chat.message.ChatMessage.update)
- [panel.chat.step module](panel.chat.step.md)
  - [ChatStep](panel.chat.step.md#panel.chat.step.ChatStep)
    - [ChatStep.serialize()](panel.chat.step.md#panel.chat.step.ChatStep.serialize)
    - [ChatStep.stream()](panel.chat.step.md#panel.chat.step.ChatStep.stream)
    - [ChatStep.stream_title()](panel.chat.step.md#panel.chat.step.ChatStep.stream_title)
- [panel.chat.utils module](panel.chat.utils.md)
  - [avatar_lookup()](panel.chat.utils.md#panel.chat.utils.avatar_lookup)
  - [get_obj_label()](panel.chat.utils.md#panel.chat.utils.get_obj_label)
  - [serialize_recursively()](panel.chat.utils.md#panel.chat.utils.serialize_recursively)
  - [stream_to()](panel.chat.utils.md#panel.chat.utils.stream_to)
  - [to_alpha_numeric()](panel.chat.utils.md#panel.chat.utils.to_alpha_numeric)

## Module contents

### Panel chat makes creating chat components easy

Check out the widget gallery
[https://panel.holoviz.org/reference/index.html#chat](https://panel.holoviz.org/reference/index.html#chat)
for inspiration.

#### How to use Panel widgets in 3 simple steps

1.  Define your function

\>\>\> async
def
repeat_contents(contents,
user,
instance):
\>\>\>  yield
contents

2.  Define your widgets and callback.

\>\>\> chat_interface
=
ChatInterface(callback=repeat_contents)

3.  Layout the chat interface in a template

\>\>\> template
=
pn.template.FastListTemplate(
\>\>\>
title="Panel
Chat", \>\>\>
main=\[chat_interface\],
\>\>\> )
\>\>\>
template.servable()

For more detail see the Reference Gallery guide.
[https://panel.holoviz.org/reference/chat/ChatInterface.html](https://panel.holoviz.org/reference/chat/ChatInterface.html)

class panel.chat.ChatAreaInput(**params: Any)
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

class panel.chat.ChatFeed(\*objects, **params)
Bases: [ListPanel](panel.layout.base.md#panel.layout.base.ListPanel)

A ChatFeed holds a list of ChatMessage objects and provides convenient
APIs. to interact with them.

This includes methods to: - Send (append) messages to the chat log. -
Stream tokens to the latest ChatMessage in the chat log. - Execute
callbacks when a user sends a message. - Undo a number of sent
ChatMessage objects. - Clear the chat log of all ChatMessage objects.

Reference:
[https://panel.holoviz.org/reference/chat/ChatFeed.html](https://panel.holoviz.org/reference/chat/ChatFeed.html)

Example:

\>\>\> async
def
say_welcome(contents,
user,
instance):
\>\>\>  yield
"Welcome!" \>\>\>
yield "Glad you're here!"

\>\>\> chat_feed
=
ChatFeed(callback=say_welcome,
header="Welcome
Feed") \>\>\>
chat_feed.send("Hello
World!",
user="New
User",
avatar="😊")

Methods

|  |  |
|----|----|
| [add_step](#panel.chat.ChatFeed.add_step)(\[step, append, user, avatar, ...\]) | Adds a ChatStep component either by appending it to an existing ChatMessage or creating a new ChatMessage. |
| [clear](#panel.chat.ChatFeed.clear)() | Clears the chat log and returns the messages that were cleared. |
| [prompt_user](#panel.chat.ChatFeed.prompt_user)(component\[, callback, ...\]) | Prompts the user to interact with a form component. |
| [respond](#panel.chat.ChatFeed.respond)() | Executes the callback with the latest message in the chat log. |
| [scroll_to](#panel.chat.ChatFeed.scroll_to)(index) | Scrolls the chat log to the provided index. |
| [select](#panel.chat.ChatFeed.select)(\[selector\]) | Iterates over the ChatInterface and any potential children in the applying the selector. |
| [send](#panel.chat.ChatFeed.send)(value\[, user, avatar, respond, ...\]) | Sends a value and creates a new message in the chat log. |
| [serialize](#panel.chat.ChatFeed.serialize)(\[exclude_users, filter_by, ...\]) | Exports the chat log. |
| [stop](#panel.chat.ChatFeed.stop)() | Cancels the current callback task if possible. |
| [stream](#panel.chat.ChatFeed.stream)(value\[, user, avatar, message, ...\]) | Streams a token and updates the provided message, if provided. |
| [trigger_post_hook](#panel.chat.ChatFeed.trigger_post_hook)() | Triggers the post hook with the latest message in the chat log. |
| [undo](#panel.chat.ChatFeed.undo)(\[count\]) | Removes the last count of messages from the chat log and returns them. |

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
>

`margin`` ``=`` ``Margin(allow_None=True,`` ``allow_refs=True,`` ``default=5,`` ``label='Margin')`
Allows to create additional space around the component. May be specified
as a two-tuple of the form (vertical, horizontal) or a four-tuple (top,
right, bottom, left).

`objects`` ``=`` ``Children(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'panel.viewable.Viewable'>,`` ``label='Objects')`
The list of child objects that make up the layout.

`adaptive`` ``=`` ``Boolean(default=False,`` ``label='Adaptive')`
Whether to allow interrupting and restarting the callback when new
messages are sent while a callback is already running. When True,
sending a new message will cancel the current callback and start a new
one with the latest message.

`auto_scroll_limit`` ``=`` ``Integer(bounds=(0,`` ``None),`` ``default=200,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Auto`` ``scroll`` ``limit')`
Max pixel distance from the latest object in the Column to activate
automatic scrolling upon update. Setting to 0 disables auto-scrolling.

`callback`` ``=`` ``Callable(allow_None=True,`` ``label='Callback')`
Callback to execute when a user sends a message or when respond is
called. The signature must include the previous message value contents,
the previous user name, and the component instance.

`callback_exception`` ``=`` ``CallbackException(default='summary',`` ``label='Callback`` ``exception')`
How to handle exceptions raised by the callback. If “raise”, the
exception will be raised. If “summary”, a summary will be sent to the
chat feed. If “verbose” or “traceback”, the full traceback will be sent
to the chat feed. If “ignore”, the exception will be ignored. If a
callable is provided, the signature must contain the exception and
instance arguments and it will be called with the exception.

`callback_user`` ``=`` ``String(default='Assistant',`` ``label='Callback`` ``user')`
The default user name to use for the message provided by the callback.

`callback_avatar`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'str'>,`` ``<class`` ``'_io.BytesIO'>,`` ``<class`` ``'bytes'>,`` ``<class`` ``'panel.pane.image.ImageBase'>),`` ``label='Callback`` ``avatar')`
The default avatar to use for the entry provided by the callback. Takes
precedence over ChatMessage.default_avatars if set; else, if None,
defaults to the avatar set in ChatMessage.default_avatars if matching
key exists. Otherwise defaults to the first character of the
callback_user.

`edit_callback`` ``=`` ``Callable(allow_None=True,`` ``label='Edit`` ``callback')`
Callback to execute when a user edits a message. The signature must
include the new message value contents, the message_index, and the
instance.

`card_params`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Card`` ``params')`
Params to pass to Card, like header, header_background, header_color,
etc.

`collapsible`` ``=`` ``Boolean(constant=True,`` ``default=False,`` ``label='Collapsible',`` ``readonly=True)`
Whether the Card should be expandable and collapsible.

`disabled`` ``=`` ``Boolean(default=False,`` ``label='Disabled')`
Whether the feed is disabled.

`message_params`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Message`` ``params')`
Params to pass to each ChatMessage, like reaction_icons,
timestamp_format, show_avatar, show_user, and show_timestamp. Params
passed that are not ChatFeed params will be forwarded into
message_params.

`header`` ``=`` ``Parameter(allow_None=True,`` ``label='Header')`
The header of the chat feed; commonly used for the title. Can be a
string, pane, or widget.

`help_text`` ``=`` ``String(default='',`` ``label='Help`` ``text')`
If provided, initializes a chat message in the chat log using the
provided help text as the message object and help as the user. This is
useful for providing instructions, and will not be included in the
serialize method by default.

`load_buffer`` ``=`` ``Integer(bounds=(0,`` ``None),`` ``default=50,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Load`` ``buffer')`
The number of objects loaded on each side of the visible objects. When
scrolled halfway into the buffer, the feed will automatically load
additional objects while unloading objects on the opposite side.

`placeholder_text`` ``=`` ``String(default='',`` ``label='Placeholder`` ``text')`
The text to display next to the placeholder icon.

`placeholder_params`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={'user':`` ``'`` ``',`` ``'reaction_icons':`` ``{},`` ``'show_copy_icon':`` ``False,`` ``'show_timestamp':`` ``False,`` ``'show_edit_icon':`` ``False},`` ``label='Placeholder`` ``params')`
Params to pass to the placeholder ChatMessage, like reaction_icons,
timestamp_format, show_avatar, show_user, show_timestamp.

`placeholder_threshold`` ``=`` ``Number(bounds=(0,`` ``None),`` ``default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Placeholder`` ``threshold')`
Min duration in seconds of buffering before displaying the placeholder.
If 0, the placeholder will be disabled.

`post_hook`` ``=`` ``Callable(allow_None=True,`` ``label='Post`` ``hook')`
A hook to execute after a new message is *completely* added, i.e. the
generator is exhausted. The stream method will trigger this callback on
every call. The signature must include the message and instance
arguments.

`renderers`` ``=`` ``HookList(bounds=(0,`` ``None),`` ``default=[],`` ``label='Renderers')`
A callable or list of callables that accept the value and return a Panel
object to render the value. If a list is provided, will attempt to use
the first renderer that does not raise an exception. If None, will
attempt to infer the renderer from the value.

`scroll_button_threshold`` ``=`` ``Integer(bounds=(0,`` ``None),`` ``default=100,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Scroll`` ``button`` ``threshold')`
Min pixel distance from the latest object in the Column to display the
scroll button. Setting to 0 disables the scroll button.

`show_activity_dot`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``activity`` ``dot')`
Whether to show an activity dot on the ChatMessage while streaming the
callback response.

`view_latest`` ``=`` ``Boolean(default=True,`` ``label='View`` ``latest')`
Whether to scroll to the latest object on init. If not enabled the view
will be on the first object.

`_placeholder`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.chat.message.ChatMessage'>,`` ``label='`` ``placeholder')`
The placeholder wrapped in a ChatMessage object; primarily to prevent
recursion error in \_update_placeholder.

`_callback_state`` ``=`` ``Selector(default=<CallbackState.IDLE:`` ``'idle'>,`` ``label='`` ``callback`` ``state',`` ``names={},`` ``objects=[<CallbackState.IDLE:`` ``'idle'>,`` ``<CallbackState.RUNNING:`` ``'running'>,`` ``<CallbackState.GENERATING:`` ``'generating'>,`` ``<CallbackState.STOPPING:`` ``'stopping'>,`` ``<CallbackState.STOPPED:`` ``'stopped'>])`
The current state of the callback.

`_prompt_trigger`` ``=`` ``Event(default=False,`` ``label='`` ``prompt`` ``trigger')`
Triggers the prompt input.

`_callback_trigger`` ``=`` ``Event(default=False,`` ``label='`` ``callback`` ``trigger')`
Triggers the callback to respond.

`_disabled_stack`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'bool'>,`` ``label='`` ``disabled`` ``stack')`
The previous disabled state of the feed.

add_step(step: str \| list\[str\] \| ChatStep \| None = None, append: bool = True, user: str \| None = None, avatar: str \| bytes \| BytesIO \| None = None, steps_layout: ListLike \| None = None, default_layout: Literal\['column', 'card'\] = 'card', layout_params: dict\[str, Any\] \| None = None, last_messages: int = 1, **step_params) → ChatStep
Adds a ChatStep component either by appending it to an existing
ChatMessage or creating a new ChatMessage.

Parameters:
step : str \| list(str) \| ChatStep \| None
The objects to stream to the step.

append : bool
Whether to append to existing steps or create new steps.

user : str \| None
The user to stream as; overrides the message’s user if provided. Will
default to the user parameter. Only applicable if steps is “new”.

avatar : str \| bytes \| BytesIO \| None
The avatar to use; overrides the message’s avatar if provided. Will
default to the avatar parameter. Only applicable if steps is “new”.

steps_layout : ListLike \| None
An existing layout of steps to stream to, if None is provided it will
default to the last Column of steps or create a new one.

default_layout : str
The default layout to use if steps_layout is None. ‘column’ will create
a new Column layout. ‘card’ will create a new Card layout.

layout_params : dict \| None
Additional parameters to pass to the layout.

**last_messages: int**
The number of messages to go back to find the last message.

step_params : dict
Parameters to pass to the ChatStep.

clear() → list\[Any\]
Clears the chat log and returns the messages that were cleared.

Returns:
The messages that were cleared.

prompt_user(component: Widget \| ListPanel, callback: Callable \| None = None, predicate: Callable \| None = None, timeout: int = 120, timeout_message: str = 'Timed out', button_params: dict \| None = None, timeout_button_params: dict \| None = None, **send_kwargs) → None
Prompts the user to interact with a form component.

Parameters:
component : Widget \| ListPanel
The component to prompt the user with.

callback : Callable
The callback to execute once the user submits the form. The callback
should accept two arguments: the component and the ChatFeed instance.

predicate : Callable \| None
A predicate to evaluate the component’s state, e.g. widget has value. If
provided, the button will be enabled when the predicate returns True.
The predicate should accept the component as an argument.

timeout : int
The duration in seconds to wait before timing out.

timeout_message : str
The message to display when the timeout is reached.

button_params : dict \| None
Additional parameters to pass to the submit button.

timeout_button_params : dict \| None
Additional parameters to pass to the timeout button.

respond()
Executes the callback with the latest message in the chat log.

Typically called after streaming is completed, i.e. after a for loop
where stream is called multiple times. If not streaming, use the respond
keyword argument inside the send method instead.

scroll_to(index: int)
Scrolls the chat log to the provided index.

select(selector=None)
Iterates over the ChatInterface and any potential children in the
applying the selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

send(value: ChatMessage \| dict \| Any, user: str \| None = None, avatar: str \| bytes \| BytesIO \| None = None, respond: bool = True, trigger_post_hook: bool = True, **message_params) → ChatMessage \| None
Sends a value and creates a new message in the chat log.

If respond is True, additionally executes the callback, if provided.

Parameters:
value : ChatMessage \| dict \| Any
The message contents to send.

user : str \| None
The user to send as; overrides the message message’s user if provided.

avatar : str \| bytes \| BytesIO \| None
The avatar to use; overrides the message message’s avatar if provided.

respond : bool
Whether to execute the callback.

**trigger_post_hook: bool**
Whether to trigger the post hook after sending.

message_params : dict
Additional parameters to pass to the ChatMessage.

Returns:
The message that was created.

serialize(exclude_users: list\[str\] \| None = None, filter_by: Callable \| None = None, format: t.Literal\['transformers'\] = 'transformers', custom_serializer: Callable \| None = None, limit: int \| None = None, **serialize_kwargs)
Exports the chat log.

Parameters:
format : str
The format to export the chat log as; currently only supports
“transformers”.

exclude_users : list(str) \| None
A list of user (case insensitive names) to exclude from serialization.
If not provided, defaults to \[“help”\]. This will be executed before
filter_by.

filter_by : callable
A function to filter the chat log by. The function must accept and
return a list of ChatMessage objects.

custom_serializer : callable
A custom function to format the ChatMessage’s object. The function must
accept one positional argument, the ChatMessage object, and return a
string. If not provided, uses the serialize method on ChatMessage.

limit : int
The number of messages to serialize at most, starting from the last
message.

****serialize_kwargs**
Additional keyword arguments to use for the specified format.

- format=”transformers” role_names : dict(str, str \| list(str)) \| None

  >
  >
  > A dictionary mapping the role to the ChatMessage’s user name.
  > Defaults to {“user”: \[“user”\], “assistant”:
  > \[self.callback_user\]} if not set. The keys and values are case
  > insensitive as the strings will all be lowercased. The values can be
  > a string or a list of strings, e.g. {“user”: “user”, “assistant”:
  > \[“executor”, “langchain”\]}.
  >
  >

  default_rolestr
  The default role to use if the user name is not found in role_names.
  If this is set to None, raises a ValueError if the user name is not
  found.

Returns:
The chat log serialized in the specified format.

stop() → bool
Cancels the current callback task if possible.

Improved to properly cancel asyncio tasks.

Returns:
Whether the task was successfully stopped or done.

stream(value: str \| dict \| ChatMessage \| Viewable, user: str \| None = None, avatar: str \| bytes \| BytesIO \| None = None, message: ChatMessage \| None = None, replace: bool = False, trigger_post_hook: bool = False, **message_params) → ChatMessage \| None
Streams a token and updates the provided message, if provided. Otherwise
creates a new message in the chat log, so be sure the returned message
is passed back into the method, e.g. message = chat.stream(token,
message=message).

This method is primarily for outputs that are not generators– notably
LangChain. For most cases, use the send method instead.

Parameters:
value : str \| dict \| ChatMessage \| Viewable
The new token value to stream.

user : str \| None
The user to stream as; overrides the message’s user if provided.

avatar : str \| bytes \| BytesIO \| None
The avatar to use; overrides the message’s avatar if provided.

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

trigger_post_hook()
Triggers the post hook with the latest message in the chat log.

Typically called after streaming is completed, i.e. after a for loop
where stream is called multiple times. If not streaming, use the
trigger_post_hook keyword argument inside the send method instead.

undo(count: int = 1) → list\[Any\]
Removes the last count of messages from the chat log and returns them.

Parameters:
count : int
The number of messages to remove, starting from the last message.

Returns:
The messages that were removed.

class panel.chat.ChatInterface(\*objects, **params)
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
[active](#panel.chat.ChatInterface.active)
The currently active input widget tab index; -1 if there is only one
widget available which is not in a tab.

[active_widget](#panel.chat.ChatInterface.active_widget)
The currently active widget.

Methods

|  |  |
|----|----|
| [send](#panel.chat.ChatInterface.send)(value\[, user, avatar, respond, ...\]) | Sends a value and creates a new message in the chat log. |
| [stream](#panel.chat.ChatInterface.stream)(value\[, user, avatar, message, ...\]) | Streams a token and updates the provided message, if provided. |

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

class panel.chat.ChatMessage(object=None, **params)
Bases: [Pane](panel.pane.base.md#panel.pane.base.Pane)

Renders another component as a chat message with an associated user and
avatar with support for various content types.

This widget provides a structured view of chat messages, including
features like:

- Displaying user avatars, which can be text, emoji, or images.

- Showing the user’s name.

- Displaying the message timestamp in a customizable format.

- Associating reactions with messages and mapping them to icons.

- Rendering various content types including text, images, audio, video,
  and more.

Reference:
[https://panel.holoviz.org/reference/chat/ChatMessage.html](https://panel.holoviz.org/reference/chat/ChatMessage.html)

Example:

\>\>\>
ChatMessage(object="Hello
world!",
user="New
User",
avatar="😊")

Methods

|  |  |
|----|----|
| [select](#panel.chat.ChatMessage.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |
| [serialize](#panel.chat.ChatMessage.serialize)(\[prefix_with_viewable_label, ...\]) | Format the object to a string. |
| [stream](#panel.chat.ChatMessage.stream)(token\[, replace\]) | Updates the message with the new token traversing the object to allow updating nested objects. |
| [update](#panel.chat.ChatMessage.update)(value\[, user, avatar\]) | Updates the message with a new value, user and avatar. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, design, height, min_width, min_height,
> max_height, styles, stylesheets, tags, width, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout
>
>

`css_classes`` ``=`` ``List(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=['chat-message'],`` ``item_type=<class`` ``'str'>,`` ``label='Css`` ``classes',`` ``nested_refs=True)`
The CSS classes to apply to the widget.

`max_width`` ``=`` ``Integer(allow_None=True,`` ``allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=1200,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``width')`
Maximum width of the component (in pixels) if width is adjustable.

`object`` ``=`` ``Parameter(allow_None=True,`` ``label='Object')`
The message contents. Can be any Python object that panel can display.

`avatar`` ``=`` ``ClassSelector(class_=(<class`` ``'str'>,`` ``<class`` ``'_io.BytesIO'>,`` ``<class`` ``'bytes'>,`` ``<class`` ``'panel.pane.image.ImageBase'>),`` ``default='',`` ``label='Avatar')`
The avatar to use for the user. Can be a single character text, an
emoji, or anything supported by pn.pane.Image. If not set, checks if the
user is available in the default_avatars mapping; else uses the first
character of the name.

`avatar_lookup`` ``=`` ``Callable(allow_None=True,`` ``label='Avatar`` ``lookup')`
A function that can lookup an avatar from a user name. The function
signature should be (user: str) -\> Avatar. If this is set,
default_avatars is disregarded.

`default_avatars`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={'client':`` ``'🧑',`` ``'customer':`` ``'🧑',`` ``'employee':`` ``'🧑',`` ``'human':`` ``'🧑',`` ``'person':`` ``'🧑',`` ``'user':`` ``'🧑',`` ``'agent':`` ``'🤖',`` ``'ai':`` ``'🤖',`` ``'assistant':`` ``'🤖',`` ``'bot':`` ``'🤖',`` ``'chatbot':`` ``'🤖',`` ``'machine':`` ``'🤖',`` ``'robot':`` ``'🤖',`` ``'system':`` ``'⚙️',`` ``'exception':`` ``'❌',`` ``'error':`` ``'❌',`` ``'help':`` ``'❓',`` ``'input':`` ``'❗',`` ``'adult':`` ``'🧑',`` ``'baby':`` ``'👶',`` ``'boy':`` ``'👦',`` ``'child':`` ``'🧒',`` ``'girl':`` ``'👧',`` ``'man':`` ``'👨',`` ``'woman':`` ``'👩',`` ``'chatgpt':`` ``'{dist_path}assets/logo/gpt-3.svg',`` ``'gpt3':`` ``'{dist_path}assets/logo/gpt-3.svg',`` ``'gpt4':`` ``'{dist_path}assets/logo/gpt-4.svg',`` ``'dalle':`` ``'{dist_path}assets/logo/gpt-4.svg',`` ``'openai':`` ``'{dist_path}assets/logo/gpt-4.svg',`` ``'huggingface':`` ``'🤗',`` ``'calculator':`` ``'🧮',`` ``'langchain':`` ``'🦜',`` ``'retriever':`` ``'📄',`` ``'tool':`` ``'🛠️',`` ``'translator':`` ``'🌐',`` ``'wolfram':`` ``'{dist_path}assets/logo/wolfram.svg',`` ``'wolfram`` ``alpha':`` ``'{dist_path}assets/logo/wolfram.svg',`` ``'llama':`` ``'🦙',`` ``'llama2':`` ``'🐪',`` ``'plot':`` ``'📊',`` ``'lumen':`` ``'{dist_path}assets/logo/lumen.svg',`` ``'holoviews':`` ``'{dist_path}assets/logo/holoviews.svg',`` ``'hvplot':`` ``'{dist_path}assets/logo/hvplot.svg',`` ``'panel':`` ``'{dist_path}images/icon-vector.svg'},`` ``label='Default`` ``avatars')`
A default mapping of user names to their corresponding avatars to use
when the user is specified but the avatar is. You can modify, but not
replace the dictionary.

`edited`` ``=`` ``Event(default=False,`` ``label='Edited')`
An event that is triggered when the message is edited.

`footer_objects`` ``=`` ``Children(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'panel.viewable.Viewable'>,`` ``label='Footer`` ``objects')`
A list of objects to display in the column of the footer of the message.

`header_objects`` ``=`` ``Children(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'panel.viewable.Viewable'>,`` ``label='Header`` ``objects')`
A list of objects to display in the row of the header of the message.

`reactions`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'str'>,`` ``label='Reactions')`
Reactions to associate with the message.

`reaction_icons`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.chat.icon.ChatReactionIcons'>,`` ``label='Reaction`` ``icons')`
A mapping of reactions to their reaction icons; if not provided defaults
to {“favorite”: “heart”}.

`timestamp`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Timestamp')`
Timestamp of the message. Defaults to the creation time.

`timestamp_format`` ``=`` ``String(default='%H:%M',`` ``label='Timestamp`` ``format')`
The timestamp format.

`timestamp_tz`` ``=`` ``String(allow_None=True,`` ``label='Timestamp`` ``tz')`
The timezone to used for the creation timestamp; only applicable if
timestamp is not set. If None, tries to use
pn.state.browser_info.timezone, else, the default tz of
datetime.datetime.now(); see zoneinfo.available_timezones() for a list
of valid timezones.

`show_avatar`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``avatar')`
Whether to display the avatar of the user.

`show_edit_icon`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``edit`` ``icon')`
Whether to display the edit icon.

`show_user`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``user')`
Whether to display the name of the user.

`show_timestamp`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``timestamp')`
Whether to display the timestamp of the message.

`show_reaction_icons`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``reaction`` ``icons')`
Whether to display the reaction icons.

`show_copy_icon`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``copy`` ``icon')`
Whether to display the copy icon.

`show_activity_dot`` ``=`` ``Boolean(default=False,`` ``label='Show`` ``activity`` ``dot')`
Whether to show the activity dot.

`renderers`` ``=`` ``HookList(bounds=(0,`` ``None),`` ``default=[],`` ``label='Renderers')`
A callable or list of callables that accept the object and return a
Panel object to render the object. If a list is provided, will attempt
to use the first renderer that does not raise an exception. If None,
will attempt to infer the renderer from the object.

`user`` ``=`` ``Parameter(default='User',`` ``label='User')`
Name of the user who sent the message.

select(selector: type \| Callable\[\[Viewable\], bool\] \| None = None) → list\[Viewable\]
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

serialize(prefix_with_viewable_label: bool = True, prefix_with_container_label: bool = True) → str
Format the object to a string.

Parameters:
prefix_with_viewable_label : bool
Whether to include the name of the Viewable, or type of the viewable if
no name is specified.

prefix_with_container_label : bool
Whether to include the name of the container, or type of the container
if no name is specified.

Returns:
str
The serialized string.

stream(token: str, replace: bool = False)
Updates the message with the new token traversing the object to allow
updating nested objects. When traversing a nested Panel the last object
that supports rendering strings is updated, e.g. in a layout of
Column(Markdown(…), Image(…)) the Markdown pane is updated.

Parameters:
**token: str**
The token to stream to the text pane.

**replace: bool (default=False)**
Whether to replace the existing text.

update(value: MessageParams \| ChatMessage \| t.Any, user: str \| None = None, avatar: str \| bytes \| BytesIO \| None = None)
Updates the message with a new value, user and avatar.

Parameters:
value : ChatMessage \| dict \| Any
The message contents to send.

user : str \| None
The user to send as; overrides the message message’s user if provided.

avatar : str \| bytes \| BytesIO \| None
The avatar to use; overrides the message message’s avatar if provided.

class panel.chat.ChatReactionIcons(\*, active_icons, default_layout, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
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

class panel.chat.ChatStep(\*objects, **params)
Bases: [Card](panel.layout.card.md#panel.layout.card.Card)

A component that makes it easy to provide status updates and the ability
to stream updates to both the output(s) and the title.

Reference:
[https://panel.holoviz.org/reference/chat/ChatStep.html](https://panel.holoviz.org/reference/chat/ChatStep.html)

Example:

\>\>\>
ChatStep("Hello
world!",
title="Running
calculation...',
status="running")

Methods

|  |  |
|----|----|
| [serialize](#panel.chat.ChatStep.serialize)(\[prefix_with_viewable_label, ...\]) | Format the object to a string. |
| [stream](#panel.chat.ChatStep.stream)(token\[, replace\]) | Stream a token to the last available string-like object. |
| [stream_title](#panel.chat.ChatStep.stream_title)(token\[, status, replace\]) | Stream a token to the title header. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, design, height, min_width, min_height, max_width,
> max_height, styles, stylesheets, tags, width, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
> [class="reference internal" title="panel.layout.base.ListPanel"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListPanel](panel.layout.base.md#panel.layout.base.ListPanel):
> scroll
>
> [class="reference internal" title="panel.layout.base.Column"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.Column](panel.layout.base.md#panel.layout.base.Column):
> auto_scroll_limit, scroll_button_threshold, scroll_position,
> view_latest
>
> [class="reference internal" title="panel.layout.card.Card"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.card.Card](panel.layout.card.md#panel.layout.card.Card):
> css_classes, active_header_background, button_css_classes,
> collapsible, header_background, header_color, header_css_classes,
> hide_header, title_css_classes
>
>

`margin`` ``=`` ``Margin(allow_None=True,`` ``allow_refs=True,`` ``default=(5,`` ``5,`` ``5,`` ``10),`` ``label='Margin')`
Allows to create additional space around the component. May be specified
as a two-tuple of the form (vertical, horizontal) or a four-tuple (top,
right, bottom, left).

`collapsed`` ``=`` ``Boolean(default=False,`` ``label='Collapsed')`
Whether the contents of the Card are collapsed.

`header`` ``=`` ``Child(allow_None=True,`` ``class_=<class`` ``'panel.viewable.Viewable'>,`` ``constant=True,`` ``label='Header',`` ``readonly=True)`
A Panel component to display in the header bar of the Card. Will
override the given title if defined.

`title`` ``=`` ``String(constant=True,`` ``default='',`` ``label='Title')`
The title of the chat step. Will redirect to default_title on init.
After, it cannot be set directly; instead use the [\*](#id1)\_title params.

`collapsed_on_success`` ``=`` ``Boolean(default=True,`` ``label='Collapsed`` ``on`` ``success')`
Whether to collapse the card on completion.

`context_exception`` ``=`` ``Selector(default='raise',`` ``label='Context`` ``exception',`` ``names={},`` ``objects=['raise',`` ``'summary',`` ``'verbose',`` ``'ignore'])`
How to handle exceptions raised upon exiting the context manager. If
“raise”, the exception will be raised. If “summary”, a summary will be
sent to the chat step. If “verbose”, the full traceback will be sent to
the chat step. If “ignore”, the exception will be ignored.

`default_badges`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={'pending':`` ``<function`` ``<lambda>`` ``at`` ``0x117f54f40>,`` ``'running':`` ``<function`` ``<lambda>`` ``at`` ``0x117f54fe0>,`` ``'success':`` ``<function`` ``<lambda>`` ``at`` ``0x117f55080>,`` ``'failed':`` ``<function`` ``<lambda>`` ``at`` ``0x117f55120>},`` ``label='Default`` ``badges')`
Mapping from status to default status badge; keys must be one of
‘pending’, ‘running’, ‘success’, ‘failed’.

`default_title`` ``=`` ``String(default='',`` ``label='Default`` ``title')`
The default title to display if the other title params are unset.

`failed_title`` ``=`` ``String(allow_None=True,`` ``label='Failed`` ``title')`
Title to display when status is failed.

`pending_title`` ``=`` ``String(allow_None=True,`` ``label='Pending`` ``title')`
Title to display when status is pending.

`running_title`` ``=`` ``String(allow_None=True,`` ``label='Running`` ``title')`
Title to display when status is running.

`status`` ``=`` ``Selector(default='pending',`` ``label='Status',`` ``names={},`` ``objects=['pending',`` ``'running',`` ``'success',`` ``'failed'])`
The status of the chat step.

`success_title`` ``=`` ``String(allow_None=True,`` ``label='Success`` ``title')`
Title to display when status is success.

serialize(prefix_with_viewable_label: bool = True, prefix_with_container_label: bool = True) → str
Format the object to a string.

Parameters:
prefix_with_viewable_label : bool
Whether to include the name of the Viewable, or type of the viewable if
no name is specified.

prefix_with_container_label : bool
Whether to include the name of the container, or type of the container
if no name is specified.

Returns:
str
The serialized string.

stream(token: str \| None, replace: bool = False)
Stream a token to the last available string-like object.

Parameters:
token : str
The token to stream.

replace : bool
Whether to replace the existing text.

Returns:
Viewable
The updated message pane.

stream_title(token: str, status: Literal\['pending', 'running', 'success', 'failed', 'default'\] = 'running', replace: bool = False)
Stream a token to the title header.

Parameters:
token : str
The token to stream.

status : str
The status title to stream to, one of ‘pending’, ‘running’, ‘success’,
‘failed’, or “default”.

replace : bool
Whether to replace the existing text.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
