# panel.chat.message module

The message module provides a low-level API for rendering chat messages.

class panel.chat.message.ChatMessage(object=None, **params)
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
| [select](#panel.chat.message.ChatMessage.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |
| [serialize](#panel.chat.message.ChatMessage.serialize)(\[prefix_with_viewable_label, ...\]) | Format the object to a string. |
| [stream](#panel.chat.message.ChatMessage.stream)(token\[, replace\]) | Updates the message with the new token traversing the object to allow updating nested objects. |
| [update](#panel.chat.message.ChatMessage.update)(value\[, user, avatar\]) | Updates the message with a new value, user and avatar. |

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

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
