# panel.template.vanilla package

## Module contents

Vanilla template

class panel.template.vanilla.VanillaTemplate(\*, \_actions, base_target, base_url, busy_indicator, collapsed_sidebar, favicon, header, header_background, header_color, logo, main, main_max_width, manifest, meta_author, meta_description, meta_keywords, meta_refresh, meta_viewport, modal, notifications, sidebar, sidebar_width, site, site_url, title, config, design, location, theme, name)
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
