# panel.template.golden package

## Module contents

GoldenTemplate based on the golden-layout library.

class panel.template.golden.GoldenTemplate(\*, \_actions, base_target, base_url, busy_indicator, collapsed_sidebar, favicon, header, header_background, header_color, logo, main, main_max_width, manifest, meta_author, meta_description, meta_keywords, meta_refresh, meta_viewport, modal, notifications, sidebar, sidebar_width, site, site_url, title, config, design, location, theme, name)
Bases:
[BasicTemplate](panel.template.base.md#panel.template.base.BasicTemplate)

GoldenTemplate is built on top of golden-layout library.

Methods

|  |  |
|----|----|
| [resolve_resources](#panel.template.golden.GoldenTemplate.resolve_resources)(\[cdn, extras\]) | Resolves the resources required for this template component. |

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

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
