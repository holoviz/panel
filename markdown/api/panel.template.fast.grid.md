# panel.template.fast.grid package

## Module contents

The FastGridTemplate provides a grid layout based on React Grid Layout
similar to the Panel ReactTemplate but in the Fast.design style and
enabling the use of Fast components.

class panel.template.fast.grid.FastGridTemplate(\*, accent_base_color, background_color, corner_radius, font, font_url, header_accent_base_color, header_neutral_color, main_layout, neutral_color, shadow, sidebar_footer, theme_toggle, breakpoints, cols, compact, dimensions, prevent_collision, row_height, save_layout, \_actions, base_target, base_url, busy_indicator, collapsed_sidebar, favicon, header, header_background, header_color, logo, main, main_max_width, manifest, meta_author, meta_description, meta_keywords, meta_refresh, meta_viewport, modal, notifications, sidebar, sidebar_width, site, site_url, title, config, design, location, theme, name)
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

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
