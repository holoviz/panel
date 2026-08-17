# panel.chat.feed module

The feed module provides a high-level API for interacting with a list of
ChatMessage objects through the backend methods.

class panel.chat.feed.CallbackState(value)
Bases: `Enum`

class panel.chat.feed.ChatFeed(\*objects, **params)
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
| [add_step](#panel.chat.feed.ChatFeed.add_step)(\[step, append, user, avatar, ...\]) | Adds a ChatStep component either by appending it to an existing ChatMessage or creating a new ChatMessage. |
| [clear](#panel.chat.feed.ChatFeed.clear)() | Clears the chat log and returns the messages that were cleared. |
| [prompt_user](#panel.chat.feed.ChatFeed.prompt_user)(component\[, callback, ...\]) | Prompts the user to interact with a form component. |
| [respond](#panel.chat.feed.ChatFeed.respond)() | Executes the callback with the latest message in the chat log. |
| [scroll_to](#panel.chat.feed.ChatFeed.scroll_to)(index) | Scrolls the chat log to the provided index. |
| [select](#panel.chat.feed.ChatFeed.select)(\[selector\]) | Iterates over the ChatInterface and any potential children in the applying the selector. |
| [send](#panel.chat.feed.ChatFeed.send)(value\[, user, avatar, respond, ...\]) | Sends a value and creates a new message in the chat log. |
| [serialize](#panel.chat.feed.ChatFeed.serialize)(\[exclude_users, filter_by, ...\]) | Exports the chat log. |
| [stop](#panel.chat.feed.ChatFeed.stop)() | Cancels the current callback task if possible. |
| [stream](#panel.chat.feed.ChatFeed.stream)(value\[, user, avatar, message, ...\]) | Streams a token and updates the provided message, if provided. |
| [trigger_post_hook](#panel.chat.feed.ChatFeed.trigger_post_hook)() | Triggers the post hook with the latest message in the chat log. |
| [undo](#panel.chat.feed.ChatFeed.undo)(\[count\]) | Removes the last count of messages from the chat log and returns them. |

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

exception panel.chat.feed.StopCallback
Bases: `Exception`

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
