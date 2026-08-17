# panel.theme.base module

class panel.theme.base.DarkTheme(\*, base_css, bokeh_theme, css, name)
Bases: [Theme](#panel.theme.base.Theme)

Baseclass for dark themes.

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [title="panel.theme.base.Theme"> class="sourceCode python xref py py-class docutils literal notranslate">panel.theme.base.Theme](#panel.theme.base.Theme):
> css
>
>

`base_css`` ``=`` ``Filename(check_exists=True,`` ``default=PosixPath('/Users/runner/work/panel/panel/panel/theme/css/dark.css'),`` ``label='Base`` ``css',`` ``search_paths=[])`
A stylesheet declaring the base variables that define the color scheme.
By default this is inherited from a base class.

`bokeh_theme`` ``=`` ``ClassSelector(class_=(<class`` ``'bokeh.themes.theme.Theme'>,`` ``<class`` ``'str'>),`` ``default=<bokeh.themes.theme.Theme`` ``object`` ``at`` ``0x117daf950>,`` ``label='Bokeh`` ``theme')`
A Bokeh Theme class that declares properties to apply to Bokeh models.
This is necessary to ensure that plots and other canvas based components
are styled appropriately.

class panel.theme.base.DefaultTheme(\*, base_css, bokeh_theme, css, name)
Bases: [Theme](#panel.theme.base.Theme)

Baseclass for default or light themes.

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [title="panel.theme.base.Theme"> class="sourceCode python xref py py-class docutils literal notranslate">panel.theme.base.Theme](#panel.theme.base.Theme):
> bokeh_theme, css
>
>

`base_css`` ``=`` ``Filename(check_exists=True,`` ``default=PosixPath('/Users/runner/work/panel/panel/panel/theme/css/default.css'),`` ``label='Base`` ``css',`` ``search_paths=[])`
A stylesheet declaring the base variables that define the color scheme.
By default this is inherited from a base class.

class panel.theme.base.Design(theme=None, **params)
Bases: `Parameterized`,
[ResourceComponent](panel.io.resources.md#panel.io.resources.ResourceComponent)

Methods

|  |  |
|----|----|
| [apply](#panel.theme.base.Design.apply)(viewable, root\[, isolated\]) | Applies the Design to a Viewable and all it children. |
| [apply_bokeh_theme_to_model](#panel.theme.base.Design.apply_bokeh_theme_to_model)(model\[, ...\]) | Applies the Bokeh theme associated with this Design system to a model. |
| [params](#panel.theme.base.Design.params)(viewable\[, doc\]) | Provides parameter values to apply the provided Viewable. |
| [resolve_resources](#panel.theme.base.Design.resolve_resources)(\[cdn, extras, include_theme\]) | Resolves the resources required for this design component. |

**Parameter Definitions**

------------------------------------------------------------------------

`theme`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.theme.base.Theme'>,`` ``constant=True,`` ``label='Theme')`

apply(viewable: Viewable, root: Model, isolated: bool = True)
Applies the Design to a Viewable and all it children.

Parameters:
**viewable: Viewable**
The Viewable to apply the Design to.

**root: Model**
The root Bokeh model to apply the Design to.

**isolated: bool**
Whether the Design is applied to an individual component or embedded in
a template that ensures the resources, such as CSS variable definitions
and JS are already initialized.

apply_bokeh_theme_to_model(model: Model, theme_override=None)
Applies the Bokeh theme associated with this Design system to a model.

Parameters:
**model: bokeh.model.Model**
The Model to apply the theme on.

**theme_override: str \| None**
A different theme to apply.

params(viewable: Viewable, doc: Document \| None = None) → tuple\[dict\[str, t.Any\], dict\[str, t.Any\]\]
Provides parameter values to apply the provided Viewable.

Parameters:
**viewable: Viewable**
The Viewable to return modifiers for.

**doc: Document \| None**
Document the Viewable will be rendered into. Useful for caching any
stylesheets that are created.

Returns:
modifiers: Dict\[str, Any\]
Dictionary of parameter values to apply to the Viewable.

child_modifiers: Dict\[str, Any\]
Dictionary of parameter values to apply to the children of the Viewable.

resolve_resources(cdn: bool \| t.Literal\['auto'\] = 'auto', extras: dict\[str, dict\[str, str\]\] \| None = None, include_theme: bool = True) → ResourceTypes
Resolves the resources required for this design component.

Parameters:
**cdn: bool \| Literal\[‘auto’\]**
Whether to load resources from CDN or local server. If set to ‘auto’
value will be automatically determine based on global settings.

**extras: dict\[str, dict\[str, str\]\] \| None**
Additional resources to add to the bundle. Valid resource types include
js, js_modules and css.

**include_theme: bool**
Whether to include theme resources.

Returns:
Dictionary containing JS and CSS resources.

class panel.theme.base.Inherit
Bases: `object`

Singleton object to declare stylesheet inheritance.

class panel.theme.base.Theme(\*, base_css, bokeh_theme, css, name)
Bases: `Parameterized`

Theme objects declare the styles to switch between different color
modes. Each Design may declare any number of color themes.

modifiers
The modifiers override parameter values of Panel components.

**Parameter Definitions**

------------------------------------------------------------------------

`base_css`` ``=`` ``Filename(allow_None=True,`` ``check_exists=True,`` ``label='Base`` ``css',`` ``search_paths=[])`
A stylesheet declaring the base variables that define the color scheme.
By default this is inherited from a base class.

`bokeh_theme`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'bokeh.themes.theme.Theme'>,`` ``<class`` ``'str'>),`` ``label='Bokeh`` ``theme')`
A Bokeh Theme class that declares properties to apply to Bokeh models.
This is necessary to ensure that plots and other canvas based components
are styled appropriately.

`css`` ``=`` ``Filename(allow_None=True,`` ``check_exists=True,`` ``label='Css',`` ``search_paths=[])`
A stylesheet that overrides variables specifically for the Theme
subclass. In most cases, this is not necessary.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
