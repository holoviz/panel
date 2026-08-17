# panel.template package

## Subpackages

- [panel.template.bootstrap package](panel.template.bootstrap.md)
  - [Module contents](panel.template.bootstrap.md#module-panel.template.bootstrap)
    - [BootstrapTemplate](panel.template.bootstrap.md#panel.template.bootstrap.BootstrapTemplate)
      - [BootstrapTemplate.design](panel.template.bootstrap.md#panel.template.bootstrap.BootstrapTemplate.design)
    - [BootstrapTemplateActions](panel.template.bootstrap.md#panel.template.bootstrap.BootstrapTemplateActions)
- [panel.template.editable package](panel.template.editable.md)
  - [Module contents](panel.template.editable.md#module-panel.template.editable)
    - [EditableTemplate](panel.template.editable.md#panel.template.editable.EditableTemplate)
    - [TemplateEditor](panel.template.editable.md#panel.template.editable.TemplateEditor)
- [panel.template.fast package](panel.template.fast.md)
  - [Subpackages](panel.template.fast.md#subpackages)
    - [panel.template.fast.grid package](panel.template.fast.grid.md)
      - [Module contents](panel.template.fast.grid.md#module-panel.template.fast.grid)
    - [panel.template.fast.list package](panel.template.fast.list.md)
      - [Module contents](panel.template.fast.list.md#module-panel.template.fast.list)
  - [Submodules](panel.template.fast.md#submodules)
    - [panel.template.fast.base module](panel.template.fast.base.md)
      - [FastBaseTemplate](panel.template.fast.base.md#panel.template.fast.base.FastBaseTemplate)
      - [FastGridBaseTemplate](panel.template.fast.base.md#panel.template.fast.base.FastGridBaseTemplate)
  - [Module contents](panel.template.fast.md#module-panel.template.fast)
- [panel.template.golden package](panel.template.golden.md)
  - [Module contents](panel.template.golden.md#module-panel.template.golden)
    - [GoldenTemplate](panel.template.golden.md#panel.template.golden.GoldenTemplate)
      - [GoldenTemplate.resolve_resources()](panel.template.golden.md#panel.template.golden.GoldenTemplate.resolve_resources)
- [panel.template.material package](panel.template.material.md)
  - [Module contents](panel.template.material.md#module-panel.template.material)
    - [MaterialTemplate](panel.template.material.md#panel.template.material.MaterialTemplate)
      - [MaterialTemplate.design](panel.template.material.md#panel.template.material.MaterialTemplate.design)
    - [MaterialTemplateActions](panel.template.material.md#panel.template.material.MaterialTemplateActions)
- [panel.template.react package](panel.template.react.md)
  - [Module contents](panel.template.react.md#module-panel.template.react)
    - [ReactTemplate](panel.template.react.md#panel.template.react.ReactTemplate)
- [panel.template.slides package](panel.template.slides.md)
  - [Module contents](panel.template.slides.md#module-panel.template.slides)
    - [SlidesTemplate](panel.template.slides.md#panel.template.slides.SlidesTemplate)
- [panel.template.vanilla package](panel.template.vanilla.md)
  - [Module contents](panel.template.vanilla.md#module-panel.template.vanilla)
    - [VanillaTemplate](panel.template.vanilla.md#panel.template.vanilla.VanillaTemplate)
      - [VanillaTemplate.design](panel.template.vanilla.md#panel.template.vanilla.VanillaTemplate.design)

## Submodules

- [panel.template.base module](panel.template.base.md)
  - [BaseTemplate](panel.template.base.md#panel.template.base.BaseTemplate)
    - [BaseTemplate.design](panel.template.base.md#panel.template.base.BaseTemplate.design)
    - [BaseTemplate.resolve_resources()](panel.template.base.md#panel.template.base.BaseTemplate.resolve_resources)
    - [BaseTemplate.save()](panel.template.base.md#panel.template.base.BaseTemplate.save)
    - [BaseTemplate.select()](panel.template.base.md#panel.template.base.BaseTemplate.select)
    - [BaseTemplate.servable()](panel.template.base.md#panel.template.base.BaseTemplate.servable)
    - [BaseTemplate.server_doc()](panel.template.base.md#panel.template.base.BaseTemplate.server_doc)
    - [BaseTemplate.theme](panel.template.base.md#panel.template.base.BaseTemplate.theme)
  - [BasicTemplate](panel.template.base.md#panel.template.base.BasicTemplate)
    - [BasicTemplate.close_modal()](panel.template.base.md#panel.template.base.BasicTemplate.close_modal)
    - [BasicTemplate.open_modal()](panel.template.base.md#panel.template.base.BasicTemplate.open_modal)
  - [Template](panel.template.base.md#panel.template.base.Template)
    - [Template.add_panel()](panel.template.base.md#panel.template.base.Template.add_panel)
    - [Template.add_variable()](panel.template.base.md#panel.template.base.Template.add_variable)
  - [TemplateActions](panel.template.base.md#panel.template.base.TemplateActions)

## Module contents

class panel.template.BaseTemplate(template: str \| \_Template, items=None, nb_template: str \| \_Template \| None = None, **params)
Bases: `Parameterized`,
`MimeRenderMixin`,
`ServableMixin`,
[ResourceComponent](panel.io.resources.md#panel.io.resources.ResourceComponent)

Methods

|  |  |
|----|----|
| [resolve_resources](#panel.template.BaseTemplate.resolve_resources)(\[cdn, extras\]) | Resolves the resources required for this template component. |
| [save](#panel.template.BaseTemplate.save)(filename\[, title, resources, embed, ...\]) | Saves Panel objects to file. |
| [select](#panel.template.BaseTemplate.select)(\[selector\]) | Iterates over the Template and any potential children in the applying the Selector. |
| [servable](#panel.template.BaseTemplate.servable)(\[title, location, area, target\]) | Serves the template and returns self to allow it to display itself in a notebook context. |
| [server_doc](#panel.template.BaseTemplate.server_doc)(\[doc, title, location\]) | Returns a servable Document with the template attached. |

**Parameter Definitions**

------------------------------------------------------------------------

`config`` ``=`` ``ClassSelector(class_=<class`` ``'panel.config._base_config'>,`` ``constant=True,`` ``default=_base_config(css_files=[],`` ``js_files={},`` ``js_modules={},`` ``name='_base_config00108',`` ``raw_css=[]),`` ``label='Config')`
Configuration object declaring custom CSS and JS files to load
specifically for this template.

`design`` ``=`` ``ClassSelector(class_=<class`` ``'panel.theme.base.Design'>,`` ``default=<class`` ``'panel.theme.base.Design'>,`` ``label='Design')`
A Design applies themes to a template.

`location`` ``=`` ``Boolean(default=False,`` ``label='Location')`
Whether to add a Location component to this Template. Note if this is
set to true, the Jinja2 template must either insert all available roots
or explicitly embed the location root with : {{ embed(roots.location)
}}.

`theme`` ``=`` ``ClassSelector(class_=<class`` ``'panel.theme.base.Theme'>,`` ``constant=True,`` ``default=<class`` ``'panel.theme.base.DefaultTheme'>,`` ``label='Theme')`

design
alias of [Design](panel.theme.base.md#panel.theme.base.Design)

resolve_resources(cdn: bool \| t.Literal\['auto'\] = 'auto', extras: dict\[str, dict\[str, str\]\] \| None = None) → ResourcesType
Resolves the resources required for this template component.

Parameters:
**cdn: bool \| Literal\[‘auto’\]**
Whether to load resources from CDN or local server. If set to ‘auto’
value will be automatically determine based on global settings.

**extras: dict\[str, dict\[str, str\]\] \| None**
Additional resources to add to the bundle. Valid resource types include
js, js_modules and css.

Returns:
Dictionary containing JS and CSS resources.

save(filename: str \| PathLike \| IO, title: str \| None = None, resources=None, embed: bool = False, max_states: int = 1000, max_opts: int = 3, embed_json: bool = False, json_prefix: str = '', save_path: str = './', load_path: str \| None = None) → None
Saves Panel objects to file.

Parameters:
**filename: string or file-like object**
Filename to save the plot to

**title: string**
Optional title for the plot

**resources: bokeh resources**
One of the valid bokeh.resources (e.g. CDN or INLINE)

**embed: bool**
Whether the state space should be embedded in the saved file.

**max_states: int**
The maximum number of states to embed

**max_opts: int**
The maximum number of states for a single widget

**embed_json: boolean (default=True)**
Whether to export the data to json files

**json_prefix: str (default=’’)**
Prefix for the auto-generated json directory

**save_path: str (default=’./’)**
The path to save json files to

**load_path: str (default=None)**
The path or URL the json files will be loaded from.

select(selector=None)
Iterates over the Template and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

servable(title: str \| None = None, location: bool \| Location = True, area: str = 'main', target: str \| None = None) → Self
Serves the template and returns self to allow it to display itself in a
notebook context.

Parameters:
title : str
A string title to give the Document (if served as an app)

location : boolean or panel.io.location.Location
Whether to create a Location component to observe and set the URL
location.

**area: str (deprecated)**
The area of a template to add the component too. Only has an effect if
pn.config.template has been set.

**target: str**
Target area to write to. If a template has been configured on
pn.config.template this refers to the target area in the template while
in pyodide this refers to the ID of the DOM node to write to.

Returns:
The template object

server_doc(doc: Document \| None = None, title: str \| None = None, location: bool \| Location = True) → Document
Returns a servable Document with the template attached.

Parameters:
doc : bokeh.Document (optional)
The Bokeh Document to attach the panel to as a root, defaults to
bokeh.io.curdoc()

title : str
A string title to give the Document

location : boolean or panel.io.location.Location
Whether to create a Location component to observe and set the URL
location.

Returns:
doc : bokeh.Document
The Bokeh document the panel was attached to.

theme
alias of [DefaultTheme](panel.theme.base.md#panel.theme.base.DefaultTheme)

class panel.template.BootstrapTemplate(\*, \_actions, base_target, base_url, busy_indicator, collapsed_sidebar, favicon, header, header_background, header_color, logo, main, main_max_width, manifest, meta_author, meta_description, meta_keywords, meta_refresh, meta_viewport, modal, notifications, sidebar, sidebar_width, site, site_url, title, config, design, location, theme, name)
Bases:
[BasicTemplate](panel.template.base.md#panel.template.base.BasicTemplate)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal"
> title="panel.template.base.BaseTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BaseTemplate](panel.template.base.md#panel.template.base.BaseTemplate):
> config, theme
>
> [class="reference internal"
> title="panel.template.base.BasicTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BasicTemplate](panel.template.base.md#panel.template.base.BasicTemplate):
> location, busy_indicator, collapsed_sidebar, header, main,
> main_max_width, sidebar, modal, notifications, logo, favicon, title,
> site, site_url, manifest, meta_description, meta_keywords,
> meta_author, meta_refresh, meta_viewport, base_url, base_target,
> header_background, header_color
>
>

`design`` ``=`` ``ClassSelector(class_=<class`` ``'panel.theme.base.Design'>,`` ``default=<class`` ``'panel.theme.bootstrap.Bootstrap'>,`` ``label='Design')`
A Design applies a specific design system to a template.

`sidebar_width`` ``=`` ``Integer(default=350,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Sidebar`` ``width')`
The width of the sidebar in pixels. Default is 350.

`_actions`` ``=`` ``ClassSelector(class_=<class`` ``'panel.template.base.TemplateActions'>,`` ``default=BootstrapTemplateActions(),`` ``label='`` ``actions')`

design
alias of
[Bootstrap](panel.theme.bootstrap.md#panel.theme.bootstrap.Bootstrap)

class panel.template.DarkTheme(\*, base_css, bokeh_theme, css, name)
Bases: [Theme](panel.theme.base.md#panel.theme.base.Theme)

Baseclass for dark themes.

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.theme.base.Theme"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.theme.base.Theme](panel.theme.base.md#panel.theme.base.Theme):
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

class panel.template.DefaultTheme(\*, base_css, bokeh_theme, css, name)
Bases: [Theme](panel.theme.base.md#panel.theme.base.Theme)

Baseclass for default or light themes.

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.theme.base.Theme"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.theme.base.Theme](panel.theme.base.md#panel.theme.base.Theme):
> bokeh_theme, css
>
>

`base_css`` ``=`` ``Filename(check_exists=True,`` ``default=PosixPath('/Users/runner/work/panel/panel/panel/theme/css/default.css'),`` ``label='Base`` ``css',`` ``search_paths=[])`
A stylesheet declaring the base variables that define the color scheme.
By default this is inherited from a base class.

class panel.template.EditableTemplate(\*, editable, layout, local_save, \_actions, base_target, base_url, busy_indicator, collapsed_sidebar, favicon, header, header_background, header_color, logo, main, main_max_width, manifest, meta_author, meta_description, meta_keywords, meta_refresh, meta_viewport, modal, notifications, sidebar, sidebar_width, site, site_url, title, config, design, location, theme, name)
Bases: [VanillaTemplate](panel.template.vanilla.md#panel.template.vanilla.VanillaTemplate)

The EditableTemplate is a list based template with a header, sidebar,
main and modal area. The template allow interactively dragging, resizing
and hiding components on a grid.

The template builds on top of Muuri and interact.js.

Reference: [https://panel.holoviz.org/reference/templates/EditableTemplate.html](https://panel.holoviz.org/reference/templates/EditableTemplate.html)

Example:

\>\>\>
pn.template.EditableTemplate(
...
site="Panel",
title="EditableTemplate",
...
sidebar=\[pn.pane.Markdown("##
Settings"),
some_slider\],
...
main=\[some_python_object\]
...
).servable()

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal"
> title="panel.template.base.BaseTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BaseTemplate](panel.template.base.md#panel.template.base.BaseTemplate):
> config, theme
>
> [class="reference internal"
> title="panel.template.base.BasicTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BasicTemplate](panel.template.base.md#panel.template.base.BasicTemplate):
> location, busy_indicator, collapsed_sidebar, header, main,
> main_max_width, sidebar, sidebar_width, modal, notifications, logo,
> favicon, title, site, site_url, manifest, meta_description,
> meta_keywords, meta_author, meta_refresh, meta_viewport, base_url,
> base_target, header_background, header_color, \_actions
>
> href="panel.template.vanilla.html#panel.template.vanilla.VanillaTemplate"
> class="reference internal"
> title="panel.template.vanilla.VanillaTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.vanilla.VanillaTemplate:
> design
>
>

`editable`` ``=`` ``Boolean(default=True,`` ``label='Editable')`
Whether the template layout should be editable.

`layout`` ``=`` ``Dict(allow_refs=True,`` ``class_=<class`` ``'dict'>,`` ``default={},`` ``label='Layout')`
The layout definition of the template indexed by the id of each
component in the main area.

`local_save`` ``=`` ``Boolean(default=True,`` ``label='Local`` ``save')`
Whether to enable saving to local storage.

class panel.template.FastGridTemplate(\*, accent_base_color, background_color, corner_radius, font, font_url, header_accent_base_color, header_neutral_color, main_layout, neutral_color, shadow, sidebar_footer, theme_toggle, breakpoints, cols, compact, dimensions, prevent_collision, row_height, save_layout, \_actions, base_target, base_url, busy_indicator, collapsed_sidebar, favicon, header, header_background, header_color, logo, main, main_max_width, manifest, meta_author, meta_description, meta_keywords, meta_refresh, meta_viewport, modal, notifications, sidebar, sidebar_width, site, site_url, title, config, design, location, theme, name)
Bases: [FastGridBaseTemplate](panel.template.fast.base.md#panel.template.fast.base.FastGridBaseTemplate)

The FastGridTemplate is a grid based Template with a header, sidebar and
main area. It is based on the fast.design style and works well in both
default (light) and dark mode.

Reference: [https://panel.holoviz.org/reference/templates/FastGridTemplate.html](https://panel.holoviz.org/reference/templates/FastGridTemplate.html)

Example:

\>\>\> template
=
pn.template.FastGridTemplate(
...
site="Panel",
title="FastGridTemplate",
accent="#A01346",
...
sidebar=\[pn.pane.Markdown("##
Settings"),
some_slider\],
...
).servable()
\>\>\>
template.main\[0:6,:\]
= some_python_object

Some *accent* colors that work well are \#A01346 (Fast), \#00A170
(Mint), \#DAA520 (Golden Rod), \#2F4F4F (Dark Slate Grey), \#F08080
(Light Coral) and \#4099da (Summer Sky).

Please note the FastListTemplate cannot display in a notebook output
cell.

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal"
> title="panel.template.base.BaseTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BaseTemplate](panel.template.base.md#panel.template.base.BaseTemplate):
> config, theme
>
> [class="reference internal"
> title="panel.template.base.BasicTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BasicTemplate](panel.template.base.md#panel.template.base.BasicTemplate):
> location, busy_indicator, collapsed_sidebar, header, main_max_width,
> sidebar, sidebar_width, modal, notifications, logo, favicon, title,
> site, site_url, manifest, meta_description, meta_keywords,
> meta_author, meta_refresh, meta_viewport, base_url, base_target,
> header_background, header_color, \_actions
>
> [class="reference internal"
> title="panel.template.react.ReactTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.react.ReactTemplate](panel.template.react.md#panel.template.react.ReactTemplate):
> main, compact, cols, breakpoints, row_height, dimensions,
> prevent_collision, save_layout
>
> href="panel.template.fast.base.html#panel.template.fast.base.FastBaseTemplate"
> class="reference internal"
> title="panel.template.fast.base.FastBaseTemplate"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.fast.base.FastBaseTemplate:
> design, accent_base_color, background_color, corner_radius, font,
> font_url, header_neutral_color, header_accent_base_color,
> neutral_color, theme_toggle, shadow, sidebar_footer, main_layout
>
>

class panel.template.FastListTemplate(\*, collapsed_right_sidebar, right_sidebar, right_sidebar_footer, right_sidebar_width, accent_base_color, background_color, corner_radius, font, font_url, header_accent_base_color, header_neutral_color, main_layout, neutral_color, shadow, sidebar_footer, theme_toggle, \_actions, base_target, base_url, busy_indicator, collapsed_sidebar, favicon, header, header_background, header_color, logo, main, main_max_width, manifest, meta_author, meta_description, meta_keywords, meta_refresh, meta_viewport, modal, notifications, sidebar, sidebar_width, site, site_url, title, config, design, location, theme, name)
Bases: [FastBaseTemplate](panel.template.fast.base.md#panel.template.fast.base.FastBaseTemplate)

The FastListTemplate is a list based Template with a header, sidebar,
main, secondary (right) sidebar and modal area. It is based on the
fast.design style and works well in both default (light) and dark mode.

Reference: [https://panel.holoviz.org/reference/templates/FastListTemplate.html](https://panel.holoviz.org/reference/templates/FastListTemplate.html)

Example:

\>\>\>
pn.template.FastListTemplate(
...
site="Panel",
title="FastListTemplate",
accent="#A01346",
...
sidebar=\[pn.pane.Markdown("##
Settings"),
some_slider\],
...
main=\[some_python_object\]
...
).servable()

Some *accent* colors that work well are \#A01346 (Fast), \#00A170
(Mint), \#DAA520 (Golden Rod), \#2F4F4F (Dark Slate Grey), \#F08080
(Light Coral) and \#4099da (Summer Sky).

You can also use the FastListTemplate as shown below

\>\>\>
pn.extension(...,
template="fast")
\>\>\>
pn.state.template.param.update(site="Panel",
title="FastListTemplate",
accent="#A01346")
\>\>\>
pn.pane.Markdown("##
Settings").servable(target="sidebar")
\>\>\> some_slider
=
pn.widgets.IntSlider(...).servable(target="sidebar")
\>\>\> ...
\>\>\>
pn.panel(some_python_object).servable(target="main")

This api is great for more exploratory use cases.

Please note the FastListTemplate cannot display in a notebook output
cell.

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal"
> title="panel.template.base.BaseTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BaseTemplate](panel.template.base.md#panel.template.base.BaseTemplate):
> config, theme
>
> [class="reference internal"
> title="panel.template.base.BasicTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BasicTemplate](panel.template.base.md#panel.template.base.BasicTemplate):
> location, busy_indicator, collapsed_sidebar, header, main,
> main_max_width, sidebar, sidebar_width, modal, notifications, logo,
> favicon, title, site, site_url, manifest, meta_description,
> meta_keywords, meta_author, meta_refresh, meta_viewport, base_url,
> base_target, header_background, header_color, \_actions
>
> href="panel.template.fast.base.html#panel.template.fast.base.FastBaseTemplate"
> class="reference internal"
> title="panel.template.fast.base.FastBaseTemplate"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.fast.base.FastBaseTemplate:
> design, accent_base_color, background_color, corner_radius, font,
> font_url, header_neutral_color, header_accent_base_color,
> neutral_color, theme_toggle, shadow, sidebar_footer, main_layout
>
>

`collapsed_right_sidebar`` ``=`` ``Selector(constant=True,`` ``default=False,`` ``label='Collapsed`` ``right`` ``sidebar',`` ``names={},`` ``objects=[False])`
Whether the secondary sidebar on the right (if present) is initially
collapsed.

`right_sidebar`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.layout.base.ListLike'>,`` ``constant=True,`` ``label='Right`` ``sidebar')`
A list-like container which populates a secondary sidebar (on the
right).

`right_sidebar_footer`` ``=`` ``String(default='',`` ``label='Right`` ``sidebar`` ``footer')`
A HTML string appended to a secondary sidebar (right sidebar).

`right_sidebar_width`` ``=`` ``Integer(default=330,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Right`` ``sidebar`` ``width')`
The width of the secondary sidebar (right sidebar) in pixels. Default is
330.

class panel.template.GoldenTemplate(\*, \_actions, base_target, base_url, busy_indicator, collapsed_sidebar, favicon, header, header_background, header_color, logo, main, main_max_width, manifest, meta_author, meta_description, meta_keywords, meta_refresh, meta_viewport, modal, notifications, sidebar, sidebar_width, site, site_url, title, config, design, location, theme, name)
Bases:
[BasicTemplate](panel.template.base.md#panel.template.base.BasicTemplate)

GoldenTemplate is built on top of golden-layout library.

Methods

|  |  |
|----|----|
| [resolve_resources](#panel.template.GoldenTemplate.resolve_resources)(\[cdn, extras\]) | Resolves the resources required for this template component. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal"
> title="panel.template.base.BaseTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BaseTemplate](panel.template.base.md#panel.template.base.BaseTemplate):
> config, design, theme
>
> [class="reference internal"
> title="panel.template.base.BasicTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BasicTemplate](panel.template.base.md#panel.template.base.BasicTemplate):
> location, busy_indicator, collapsed_sidebar, header, main,
> main_max_width, sidebar, modal, notifications, logo, favicon, title,
> site, site_url, manifest, meta_description, meta_keywords,
> meta_author, meta_refresh, meta_viewport, base_url, base_target,
> header_background, header_color, \_actions
>
>

`sidebar_width`` ``=`` ``Integer(constant=True,`` ``default=20,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Sidebar`` ``width')`
The width of the sidebar in percent.

resolve_resources(cdn: bool \| t.Literal\['auto'\] = 'auto', extras: dict\[str, dict\[str, str\]\] \| None = None) → ResourcesType
Resolves the resources required for this template component.

Parameters:
**cdn: bool \| Literal\[‘auto’\]**
Whether to load resources from CDN or local server. If set to ‘auto’
value will be automatically determine based on global settings.

**extras: dict\[str, dict\[str, str\]\] \| None**
Additional resources to add to the bundle. Valid resource types include
js, js_modules and css.

Returns:
Dictionary containing JS and CSS resources.

class panel.template.MaterialTemplate(\*, \_actions, base_target, base_url, busy_indicator, collapsed_sidebar, favicon, header, header_background, header_color, logo, main, main_max_width, manifest, meta_author, meta_description, meta_keywords, meta_refresh, meta_viewport, modal, notifications, sidebar, sidebar_width, site, site_url, title, config, design, location, theme, name)
Bases:
[BasicTemplate](panel.template.base.md#panel.template.base.BasicTemplate)

MaterialTemplate is built on top of Material web components.

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal"
> title="panel.template.base.BaseTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BaseTemplate](panel.template.base.md#panel.template.base.BaseTemplate):
> config, theme
>
> [class="reference internal"
> title="panel.template.base.BasicTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BasicTemplate](panel.template.base.md#panel.template.base.BasicTemplate):
> location, busy_indicator, collapsed_sidebar, header, main,
> main_max_width, sidebar, modal, notifications, logo, favicon, title,
> site, site_url, manifest, meta_description, meta_keywords,
> meta_author, meta_refresh, meta_viewport, base_url, base_target,
> header_background, header_color
>
>

`design`` ``=`` ``ClassSelector(class_=<class`` ``'panel.theme.base.Design'>,`` ``default=<class`` ``'panel.theme.material.Material'>,`` ``label='Design')`
A Design applies a specific design system to a template.

`sidebar_width`` ``=`` ``Integer(default=370,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Sidebar`` ``width')`
The width of the sidebar in pixels. Default is 370.

`_actions`` ``=`` ``ClassSelector(class_=<class`` ``'panel.template.base.TemplateActions'>,`` ``default=MaterialTemplateActions(),`` ``label='`` ``actions')`

design
alias of
[Material](panel.theme.material.md#panel.theme.material.Material)

class panel.template.ReactTemplate(\*, breakpoints, cols, compact, dimensions, prevent_collision, row_height, save_layout, \_actions, base_target, base_url, busy_indicator, collapsed_sidebar, favicon, header, header_background, header_color, logo, main, main_max_width, manifest, meta_author, meta_description, meta_keywords, meta_refresh, meta_viewport, modal, notifications, sidebar, sidebar_width, site, site_url, title, config, design, location, theme, name)
Bases:
[BasicTemplate](panel.template.base.md#panel.template.base.BasicTemplate)

ReactTemplate is built on top of React Grid Layout web components.

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal"
> title="panel.template.base.BaseTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BaseTemplate](panel.template.base.md#panel.template.base.BaseTemplate):
> config, design, theme
>
> [class="reference internal"
> title="panel.template.base.BasicTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BasicTemplate](panel.template.base.md#panel.template.base.BasicTemplate):
> location, busy_indicator, collapsed_sidebar, header, main_max_width,
> sidebar, sidebar_width, modal, notifications, logo, favicon, title,
> site, site_url, manifest, meta_description, meta_keywords,
> meta_author, meta_refresh, meta_viewport, base_url, base_target,
> header_background, header_color, \_actions
>
>

`main`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.layout.grid.GridSpec'>,`` ``constant=True,`` ``label='Main')`
A list-like container which populates the main area.

`compact`` ``=`` ``Selector(label='Compact',`` ``names={},`` ``objects=[None,`` ``'vertical',`` ``'horizontal',`` ``'both'])`

`cols`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={'lg':`` ``12,`` ``'md':`` ``10,`` ``'sm':`` ``6,`` ``'xs':`` ``4,`` ``'xxs':`` ``2},`` ``label='Cols')`

`breakpoints`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={'lg':`` ``1200,`` ``'md':`` ``996,`` ``'sm':`` ``768,`` ``'xs':`` ``480,`` ``'xxs':`` ``0},`` ``label='Breakpoints')`

`row_height`` ``=`` ``Integer(default=150,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Row`` ``height')`

`dimensions`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={'minW':`` ``0,`` ``'maxW':`` ``inf,`` ``'minH':`` ``0,`` ``'maxH':`` ``inf},`` ``label='Dimensions')`
A dictionary of minimum/maximum width/height in grid units.

`prevent_collision`` ``=`` ``Boolean(default=False,`` ``label='Prevent`` ``collision')`
Prevent collisions between items.

`save_layout`` ``=`` ``Boolean(default=False,`` ``label='Save`` ``layout')`
Save layout to local storage.

class panel.template.SlidesTemplate(\*, reveal_config, reveal_theme, show_header, \_actions, base_target, base_url, busy_indicator, collapsed_sidebar, favicon, header, header_background, header_color, logo, main, main_max_width, manifest, meta_author, meta_description, meta_keywords, meta_refresh, meta_viewport, modal, notifications, sidebar, sidebar_width, site, site_url, title, config, design, location, theme, name)
Bases: [VanillaTemplate](panel.template.vanilla.md#panel.template.vanilla.VanillaTemplate)

SlidesTemplate is built on top of Vanilla web components.

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal"
> title="panel.template.base.BaseTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BaseTemplate](panel.template.base.md#panel.template.base.BaseTemplate):
> config, theme
>
> [class="reference internal"
> title="panel.template.base.BasicTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BasicTemplate](panel.template.base.md#panel.template.base.BasicTemplate):
> location, busy_indicator, header, main, main_max_width, sidebar,
> sidebar_width, modal, notifications, logo, favicon, title, site,
> site_url, manifest, meta_description, meta_keywords, meta_author,
> meta_refresh, meta_viewport, base_url, base_target, header_background,
> header_color, \_actions
>
> href="panel.template.vanilla.html#panel.template.vanilla.VanillaTemplate"
> class="reference internal"
> title="panel.template.vanilla.VanillaTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.vanilla.VanillaTemplate:
> design
>
>

`collapsed_sidebar`` ``=`` ``Selector(constant=True,`` ``default=True,`` ``label='Collapsed`` ``sidebar',`` ``names={},`` ``objects=[False,`` ``True])`
Whether the sidebar (if present) is initially collapsed.

`reveal_config`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Reveal`` ``config')`
Configuration parameters for reveal.js

`reveal_theme`` ``=`` ``Selector(label='Reveal`` ``theme',`` ``names={},`` ``objects=['black',`` ``'white',`` ``'league',`` ``'beige',`` ``'night',`` ``'solarized',`` ``'simple'])`
The reveal.js theme to load.

`show_header`` ``=`` ``Boolean(default=False,`` ``label='Show`` ``header')`
Whether to show the header component.

class panel.template.Template(template: str \| \_Template, nb_template: str \| \_Template \| None = None, items: dict\[str, t.Any\] \| None = None, **params)
Bases:
[BaseTemplate](panel.template.base.md#panel.template.base.BaseTemplate)

A Template is a high-level component to render multiple Panel objects
into a single HTML document defined through a Jinja2 template. The
Template object is given a Jinja2 template and then allows populating
this template by adding Panel objects, which are given unique names.
These unique names may then be referenced in the template to insert the
rendered Panel object at a specific location. For instance, given a
Jinja2 template that defines roots A and B like this:

>
>
> \<div\> {{ embed(roots.A) }} \</div\> \<div\> {{ embed(roots.B) }}
> \</div\>
>
>

We can then populate the template by adding panel ‘A’ and ‘B’ to the
Template object:

>
>
> template.add_panel(‘A’, pn.panel(‘A’)) template.add_panel(‘B’,
> pn.panel(‘B’))
>
>

Once a template has been fully populated it can be rendered using the
same API as other Panel objects. Note that all roots that have been
declared using the {{ embed(roots.A) }} syntax in the Jinja2 template
must be defined when rendered.

Since embedding complex CSS frameworks inside a notebook can have
undesirable side-effects and a notebook does not afford the same amount
of screen space a Template may given separate template and nb_template
objects. This allows for different layouts when served as a standalone
server and when used in the notebook.

Methods

|  |  |
|----|----|
| [add_panel](#panel.template.Template.add_panel)(name, panel\[, tags\]) | Add panels to the Template, which may then be referenced by the given name using the jinja2 embed macro. |
| [add_variable](#panel.template.Template.add_variable)(name, value) | Add parameters to the template, which may then be referenced by the given name in the Jinja2 template. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal"
> title="panel.template.base.BaseTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BaseTemplate](panel.template.base.md#panel.template.base.BaseTemplate):
> config, design, location, theme
>
>

add_panel(name: str, panel: Any, tags: list\[str\] = \[\]) → None
Add panels to the Template, which may then be referenced by the given
name using the jinja2 embed macro.

Parameters:
name : str
The name to refer to the panel by in the template

panel : panel.Viewable
A Panel component to embed in the template.

add_variable(name: str, value: Any) → None
Add parameters to the template, which may then be referenced by the
given name in the Jinja2 template.

Parameters:
name : str
The name to refer to the panel by in the template

value : object
Any valid Jinja2 variable type.

class panel.template.VanillaTemplate(\*, \_actions, base_target, base_url, busy_indicator, collapsed_sidebar, favicon, header, header_background, header_color, logo, main, main_max_width, manifest, meta_author, meta_description, meta_keywords, meta_refresh, meta_viewport, modal, notifications, sidebar, sidebar_width, site, site_url, title, config, design, location, theme, name)
Bases:
[BasicTemplate](panel.template.base.md#panel.template.base.BasicTemplate)

The VanillaTemplate is a basic template that depends solely on vanilla
HTML and JS, i.e. does not require any specific framework.

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal"
> title="panel.template.base.BaseTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BaseTemplate](panel.template.base.md#panel.template.base.BaseTemplate):
> config, theme
>
> [class="reference internal"
> title="panel.template.base.BasicTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BasicTemplate](panel.template.base.md#panel.template.base.BasicTemplate):
> location, busy_indicator, collapsed_sidebar, header, main,
> main_max_width, sidebar, sidebar_width, modal, notifications, logo,
> favicon, title, site, site_url, manifest, meta_description,
> meta_keywords, meta_author, meta_refresh, meta_viewport, base_url,
> base_target, header_background, header_color, \_actions
>
>

`design`` ``=`` ``ClassSelector(class_=<class`` ``'panel.theme.base.Design'>,`` ``default=<class`` ``'panel.theme.native.Native'>,`` ``label='Design')`
A Design applies a specific design system to a template.

design
alias of [Native](panel.theme.native.md#panel.theme.native.Native)

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
