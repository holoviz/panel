# panel.widgets.misc module

Miscellaneous widgets which do not fit into the other main categories.

class panel.widgets.misc.FileDownload(file=None, **params)
Bases:
[IconMixin](panel.widgets.button.md#panel.widgets.button.IconMixin)

The FileDownload widget allows a user to download a file.

It works either by sending the file data to the browser on
initialization ([\`](#id1)embed\`=True), or when the button is
clicked.

Reference:
[https://panel.holoviz.org/reference/widgets/FileDownload.html](https://panel.holoviz.org/reference/widgets/FileDownload.html)

Example:

\>\>\>
FileDownload(file='IntroductionToPanel.ipynb',
filename='intro.ipynb')

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> value
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
> [class="reference internal" title="panel.widgets.button.IconMixin"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.button.IconMixin](panel.widgets.button.md#panel.widgets.button.IconMixin):
> icon, icon_size
>
>

`label`` ``=`` ``String(default='Download`` ``file',`` ``label='Label')`
The label of the download button

`auto`` ``=`` ``Boolean(default=True,`` ``label='Auto')`
Whether to download on the initial click or allow for right-click save
as.

`button_type`` ``=`` ``Selector(default='default',`` ``label='Button`` ``type',`` ``names={},`` ``objects=['default',`` ``'primary',`` ``'success',`` ``'warning',`` ``'danger',`` ``'light'])`
A button theme; should be one of ‘default’ (white), ‘primary’ (blue),
‘success’ (green), ‘info’ (yellow), ‘light’ (light), or ‘danger’ (red).
The same value is exposed as `color`.

`button_style`` ``=`` ``Selector(default='solid',`` ``label='Button`` ``style',`` ``names={},`` ``objects=['solid',`` ``'outline'])`
A button style to switch between ‘solid’, ‘outline’. The same value is
exposed as `variant`.

`color`` ``=`` ``Selector(default='default',`` ``label='Color',`` ``names={},`` ``objects=['default',`` ``'primary',`` ``'success',`` ``'warning',`` ``'danger',`` ``'light'])`
Semantic color of the button; alias for
`button_type`.

`variant`` ``=`` ``Selector(default='solid',`` ``label='Variant',`` ``names={},`` ``objects=['solid',`` ``'outline'])`
Visual variant of the button; alias for
`button_style` (‘solid’ or ‘outline’).

`callback`` ``=`` ``Callable(allow_None=True,`` ``label='Callback')`
A callable that returns the file path or file-like object.

`data`` ``=`` ``String(allow_None=True,`` ``label='Data')`
The data being transferred.

`embed`` ``=`` ``Boolean(default=False,`` ``label='Embed')`
Whether to embed the file on initialization.

`file`` ``=`` ``Parameter(allow_None=True,`` ``label='File')`
The file, Path, file-like object or file contents to transfer. If the
file is not pointing to a file on disk a filename must also be provided.

`filename`` ``=`` ``String(allow_None=True,`` ``label='Filename')`
A filename which will also be the default name when downloading the
file.

`description`` ``=`` ``String(allow_None=True,`` ``label='Description')`
An HTML string describing the function of this component.

`_clicks`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``clicks')`
Internal counter for button clicks.

`_transfers`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``transfers')`

class panel.widgets.misc.JSONEditor(**params: Any)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The JSONEditor provides a visual editor for JSON-serializable
datastructures, e.g. Python dictionaries and lists, with functionality
for different editing modes, inserting objects and validation using JSON
Schema.

Reference:
[https://panel.holoviz.org/reference/widgets/JSONEditor.html](https://panel.holoviz.org/reference/widgets/JSONEditor.html)

Example:

\>\>\>
JSONEditor(value={
...  'dict'
:
{'key':
'value'},
...  'float'
:
3.14,
...  'int'
:
1, ...
 'list' :
\[1,
2,
3\], ...
 'string':
'A string',
... },
mode='code')

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
>

`value`` ``=`` ``Parameter(default={},`` ``label='Value')`
JSON data to be edited.

`menu`` ``=`` ``Boolean(default=True,`` ``label='Menu')`
Adds main menu bar - Contains format, sort, transform, search etc.
functionality. true by default. Applicable in all types of mode.

`mode`` ``=`` ``Selector(default='tree',`` ``label='Mode',`` ``names={},`` ``objects=['tree',`` ``'view',`` ``'form',`` ``'text',`` ``'preview'])`
Sets the editor mode. In ‘view’ mode, the data and datastructure is
read-only. In ‘form’ mode, only the value can be changed, the data
structure is read-only. Mode ‘code’ requires the Ace editor to be loaded
on the page. Mode ‘text’ shows the data as plain text. The ‘preview’
mode can handle large JSON documents up to 500 MiB. It shows a preview
of the data, and allows to transform, sort, filter, format, or compact
the data.

`search`` ``=`` ``Boolean(default=True,`` ``label='Search')`
Enables a search box in the upper right corner of the JSONEditor. true
by default. Only applicable when mode is ‘tree’, ‘view’, or ‘form’.

`selection`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'str'>,`` ``label='Selection')`
Current selection.

`schema`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Schema')`
Validate the JSON object against a JSON schema. A JSON schema describes
the structure that a JSON object must have, like required properties or
the type that a value must have. See [http://json-schema.org/](http://json-schema.org/) for more
information.

`templates`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'dict'>,`` ``label='Templates')`
Array of templates that will appear in the context menu, Each template
is a json object precreated that can be added as a object value to any
node in your document.

class panel.widgets.misc.VideoStream(**params: Any)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The VideoStream displays a video from a local stream (for example from a
webcam) and allows accessing the streamed video data from Python.

Reference:
[https://panel.holoviz.org/reference/widgets/VideoStream.html](https://panel.holoviz.org/reference/widgets/VideoStream.html)

Example:

\>\>\>
VideoStream(label='Video
Stream',
timeout=100)

Methods

|  |  |
|----|----|
| [snapshot](#panel.widgets.misc.VideoStream.snapshot)() | Triggers a snapshot of the current VideoStream state to sync the widget value. |

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
>

`value`` ``=`` ``String(default='',`` ``label='Value')`
A base64 representation of the video stream snapshot.

`format`` ``=`` ``Selector(default='png',`` ``label='Format',`` ``names={},`` ``objects=['png',`` ``'jpeg'])`
The file format as which the video is returned.

`paused`` ``=`` ``Boolean(default=False,`` ``label='Paused')`
Whether the video is currently paused

`timeout`` ``=`` ``Number(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Timeout')`
Interval between snapshots in millisecons

snapshot()
Triggers a snapshot of the current VideoStream state to sync the widget
value.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
