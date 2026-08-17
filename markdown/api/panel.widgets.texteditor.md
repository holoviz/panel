# panel.widgets.texteditor module

Defines a WYSIWYG TextEditor widget based on quill.js.

class panel.widgets.texteditor.TextEditor(**params: Any)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The TextEditor widget provides a WYSIWYG (what-you-see-is-what-you-get)
rich text editor which outputs HTML.

The editor is built on top of the
\[Quill.js\]([https://quilljs.com/](https://quilljs.com/)) library.

Reference:
[https://panel.holoviz.org/reference/widgets/TextEditor.html](https://panel.holoviz.org/reference/widgets/TextEditor.html)

Example:

\>\>\>
TextEditor(placeholder='Enter
some text')

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
> height, margin, width
>
>

`value`` ``=`` ``String(default='',`` ``label='Value')`
State of the current text in the editor if on_keyup. Otherwise, only
upon loss of focus, i.e. clicking outside the editor, or pressing
\<Ctrl+Enter\> or \<Cmd+Enter\>.

`disabled`` ``=`` ``Boolean(default=False,`` ``label='Disabled')`
Whether the editor is disabled.

`mode`` ``=`` ``Selector(default='toolbar',`` ``label='Mode',`` ``names={},`` ``objects=['bubble',`` ``'toolbar'])`
Whether to display a toolbar or a bubble menu on highlight.

`on_keyup`` ``=`` ``Boolean(default=True,`` ``label='On`` ``keyup')`
Whether to update the value on every key press or only upon loss of
focus / hotkeys.

`toolbar`` ``=`` ``ClassSelector(class_=(<class`` ``'list'>,`` ``<class`` ``'bool'>),`` ``default=True,`` ``label='Toolbar')`
Toolbar configuration either as a boolean toggle or a configuration
specified as a list.

`placeholder`` ``=`` ``String(default='',`` ``label='Placeholder')`
Placeholder output when the editor is empty.

`selection`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Selection')`
The current text selection in the editor, as
`{"text":`` ``"..."}`
when the user has a non-empty selection, else
`{}`. Updates live as the selection changes.

`value_input`` ``=`` ``String(default='',`` ``label='Value`` ``input')`
State of the current text updated on every key press. Identical to value
if on_keyup.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
