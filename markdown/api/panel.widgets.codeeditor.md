# panel.widgets.codeeditor module

Defines the CodeEditor widget based on Ace.

class panel.widgets.codeeditor.CodeEditor(\*, annotations, filename, indent, language, on_keyup, print_margin, readonly, soft_tabs, theme, value_input, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The CodeEditor widget allows displaying and editing code in the powerful
Ace editor.

Reference:
[https://panel.holoviz.org/reference/widgets/CodeEditor.html](https://panel.holoviz.org/reference/widgets/CodeEditor.html)

Example:

\>\>\>
CodeEditor(value=py_code,
language='python',
theme='monokai')

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
State of the current code in the editor if on_keyup. Otherwise, only
upon loss of focus, i.e. clicking outside the editor, or pressing
\<Ctrl+Enter\> or \<Cmd+Enter\>.

`annotations`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'dict'>,`` ``label='Annotations')`
List of annotations to add to the editor.

`filename`` ``=`` ``String(default='',`` ``label='Filename')`
Filename from which to deduce language

`language`` ``=`` ``String(default='text',`` ``label='Language')`
Language of the editor

`indent`` ``=`` ``Integer(default=4,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Indent')`
The default indent size.

`on_keyup`` ``=`` ``Boolean(default=True,`` ``label='On`` ``keyup')`
Whether to update the value on every key press or only upon loss of
focus / hotkeys.

`print_margin`` ``=`` ``Boolean(default=False,`` ``label='Print`` ``margin')`
Whether to show the a print margin.

`readonly`` ``=`` ``Boolean(default=False,`` ``label='Readonly')`
Define if editor content can be modified. Alias for disabled.

`soft_tabs`` ``=`` ``Boolean(default=False,`` ``label='Soft`` ``tabs')`
Whether to use spaces instead of tabs.

`theme`` ``=`` ``Selector(default='github_light_default',`` ``label='Theme',`` ``names={},`` ``objects=['ambiance',`` ``'chaos',`` ``'chrome',`` ``'cloud9_day',`` ``'cloud9_night',`` ``'clouds',`` ``'clouds_midnight',`` ``'cobalt',`` ``'crimson_editor',`` ``'dawn',`` ``'dracula',`` ``'dreamweaver',`` ``'eclipse',`` ``'github',`` ``'github_dark',`` ``'github_light_default',`` ``'gob',`` ``'gruvbox',`` ``'idle_fingers',`` ``'iplastic',`` ``'katzenmilch',`` ``'kr_theme',`` ``'kuroir',`` ``'merbivore',`` ``'merbivore_soft',`` ``'mono_industrial',`` ``'monokai',`` ``'nord_dark',`` ``'one_dark',`` ``'pastel_on_dark',`` ``'solarized_dark',`` ``'solarized_light',`` ``'sqlserver',`` ``'terminal',`` ``'textmate',`` ``'tomorrow',`` ``'tomorrow_night',`` ``'tomorrow_night_blue',`` ``'tomorrow_night_bright',`` ``'tomorrow_night_eighties',`` ``'twilight',`` ``'vibrant_ink',`` ``'xcode'])`
If no value is provided, it defaults to the current theme set by
pn.config.theme, as specified in the CodeEditor.THEME_CONFIGURATION
dictionary. If not defined there, it falls back to the default parameter
value.

`value_input`` ``=`` ``String(default='',`` ``label='Value`` ``input')`
State of the current code updated on every key press. Identical to value
if on_keyup.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
