# panel.template.slides package

## Module contents

Vanilla template

class panel.template.slides.SlidesTemplate(\*, reveal_config, reveal_theme, show_header, \_actions, base_target, base_url, busy_indicator, collapsed_sidebar, favicon, header, header_background, header_color, logo, main, main_max_width, manifest, meta_author, meta_description, meta_keywords, meta_refresh, meta_viewport, modal, notifications, sidebar, sidebar_width, site, site_url, title, config, design, location, theme, name)
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

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
