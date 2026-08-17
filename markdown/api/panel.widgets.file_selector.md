# panel.widgets.file_selector module

Defines a FileSelector widget which allows selecting files and
directories on the server.

class panel.widgets.file_selector.BaseFileNavigator(directory: AnyStr \| PathLike \| None = None, **params)
Bases: [BaseFileSelector](#panel.widgets.file_selector.BaseFileSelector),
[CompositeWidget](panel.widgets.base.md#panel.widgets.base.CompositeWidget)

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
> [class="reference internal"
> title="panel.widgets.file_selector.BaseFileSelector"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.file_selector.BaseFileSelector](#panel.widgets.file_selector.BaseFileSelector):
> directory, file_pattern, only_files, refresh_period, root_directory,
> value
>
>

class panel.widgets.file_selector.BaseFileSelector(directory: t.AnyStr \| os.PathLike \| None = None, fs: AbstractFileSystem \| None = None, **params)
Bases: `Parameterized`

Attributes:
**fs**

**Parameter Definitions**

------------------------------------------------------------------------

`directory`` ``=`` ``String(default='/Users/runner/work/panel/panel/doc',`` ``label='Directory')`
The directory to explore.

`file_pattern`` ``=`` ``String(default='*',`` ``label='File`` ``pattern')`
A glob-like pattern to filter the files.

`only_files`` ``=`` ``Boolean(default=False,`` ``label='Only`` ``files')`
Whether to only allow selecting files.

`refresh_period`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Refresh`` ``period')`
If set to non-None value indicates how frequently to refresh the
directory contents in milliseconds.

`root_directory`` ``=`` ``String(allow_None=True,`` ``label='Root`` ``directory')`
If set, overrides directory parameter as the root directory beyond which
users cannot navigate.

`value`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=(<class`` ``'str'>,`` ``<class`` ``'pathlib.Path'>),`` ``label='Value')`
List of selected files.

class panel.widgets.file_selector.FileSelector(directory: t.AnyStr \| os.PathLike \| None = None, fs: AbstractFileSystem \| None = None, **params)
Bases: [BaseFileNavigator](#panel.widgets.file_selector.BaseFileNavigator)

The FileSelector widget allows browsing the filesystem on the server and
selecting one or more files in a directory.

Reference:
[https://panel.holoviz.org/reference/widgets/FileSelector.html](https://panel.holoviz.org/reference/widgets/FileSelector.html)

Example:

\>\>\>
FileSelector(directory='~',
file_pattern='\*.png')

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
> [class="reference internal"
> title="panel.widgets.file_selector.BaseFileSelector"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.file_selector.BaseFileSelector](#panel.widgets.file_selector.BaseFileSelector):
> directory, file_pattern, only_files, refresh_period, root_directory,
> value
>
>

`show_hidden`` ``=`` ``Boolean(default=False,`` ``label='Show`` ``hidden')`
Whether to show hidden files and directories (starting with a period).

`size`` ``=`` ``Integer(default=10,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Size')`
The number of options shown at once (note this is the only way to
control the height of this widget)

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
