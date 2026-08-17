# panel.theme.material module

class panel.theme.material.Material(theme=None, **params)
Bases: [Design](panel.theme.base.md#panel.theme.base.Design)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.theme.base.Design"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.theme.base.Design](panel.theme.base.md#panel.theme.base.Design):
> theme
>
>

class panel.theme.material.MaterialDarkTheme(\*, base_css, bokeh_theme, css, name)
Bases: [MaterialThemeMixin](#panel.theme.material.MaterialThemeMixin),
[DarkTheme](panel.theme.base.md#panel.theme.base.DarkTheme)

The MaterialDarkTheme is a Dark Theme in the style of Material Design

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.theme.base.DarkTheme"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.theme.base.DarkTheme](panel.theme.base.md#panel.theme.base.DarkTheme):
> base_css
>
> [class="reference internal"
> title="panel.theme.material.MaterialThemeMixin"> class="sourceCode python xref py py-class docutils literal notranslate">panel.theme.material.MaterialThemeMixin](#panel.theme.material.MaterialThemeMixin):
> css
>
>

`bokeh_theme`` ``=`` ``ClassSelector(class_=(<class`` ``'bokeh.themes.theme.Theme'>,`` ``<class`` ``'str'>),`` ``default=<bokeh.themes.theme.Theme`` ``object`` ``at`` ``0x117dc5650>,`` ``label='Bokeh`` ``theme')`
A Bokeh Theme class that declares properties to apply to Bokeh models.
This is necessary to ensure that plots and other canvas based components
are styled appropriately.

class panel.theme.material.MaterialDefaultTheme(\*, base_css, bokeh_theme, css, name)
Bases: [MaterialThemeMixin](#panel.theme.material.MaterialThemeMixin),
[DefaultTheme](panel.theme.base.md#panel.theme.base.DefaultTheme)

The MaterialDefaultTheme is a light theme.

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.theme.base.DefaultTheme"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.theme.base.DefaultTheme](panel.theme.base.md#panel.theme.base.DefaultTheme):
> base_css
>
> [class="reference internal"
> title="panel.theme.material.MaterialThemeMixin"> class="sourceCode python xref py py-class docutils literal notranslate">panel.theme.material.MaterialThemeMixin](#panel.theme.material.MaterialThemeMixin):
> css
>
>

`bokeh_theme`` ``=`` ``ClassSelector(class_=(<class`` ``'bokeh.themes.theme.Theme'>,`` ``<class`` ``'str'>),`` ``default=<bokeh.themes.theme.Theme`` ``object`` ``at`` ``0x117a71410>,`` ``label='Bokeh`` ``theme')`
A Bokeh Theme class that declares properties to apply to Bokeh models.
This is necessary to ensure that plots and other canvas based components
are styled appropriately.

class panel.theme.material.MaterialThemeMixin(\*, css, name)
Bases: `Parameterized`

**Parameter Definitions**

------------------------------------------------------------------------

`css`` ``=`` ``Filename(check_exists=True,`` ``default=PosixPath('/Users/runner/work/panel/panel/panel/theme/css/material_variables.css'),`` ``label='Css',`` ``search_paths=[])`

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
