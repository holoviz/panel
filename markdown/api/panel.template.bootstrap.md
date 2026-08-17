# panel.template.bootstrap package

## Module contents

Bootstrap template based on the bootstrap.css library.

class panel.template.bootstrap.BootstrapTemplate(\*, \_actions, base_target, base_url, busy_indicator, collapsed_sidebar, favicon, header, header_background, header_color, logo, main, main_max_width, manifest, meta_author, meta_description, meta_keywords, meta_refresh, meta_viewport, modal, notifications, sidebar, sidebar_width, site, site_url, title, config, design, location, theme, name)
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

class panel.template.bootstrap.BootstrapTemplateActions(\*, close_modal, open_modal, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases:
[TemplateActions](panel.template.base.md#panel.template.base.TemplateActions)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal"
> title="panel.template.base.TemplateActions"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.TemplateActions](panel.template.base.md#panel.template.base.TemplateActions):
> open_modal, close_modal
>
>

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
