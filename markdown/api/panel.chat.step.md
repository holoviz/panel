# panel.chat.step module

class panel.chat.step.ChatStep(\*objects, **params)
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
| [serialize](#panel.chat.step.ChatStep.serialize)(\[prefix_with_viewable_label, ...\]) | Format the object to a string. |
| [stream](#panel.chat.step.ChatStep.stream)(token\[, replace\]) | Stream a token to the last available string-like object. |
| [stream_title](#panel.chat.step.ChatStep.stream_title)(token\[, status, replace\]) | Stream a token to the title header. |

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
