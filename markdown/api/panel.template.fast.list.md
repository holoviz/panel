# panel.template.fast.list package

## Module contents

The FastListTemplate provides a list layout based on similar to the
Panel VanillaTemplate but in the Fast.design style and enabling the use
of Fast components.

class panel.template.fast.list.FastListTemplate(\*, collapsed_right_sidebar, right_sidebar, right_sidebar_footer, right_sidebar_width, accent_base_color, background_color, corner_radius, font, font_url, header_accent_base_color, header_neutral_color, main_layout, neutral_color, shadow, sidebar_footer, theme_toggle, \_actions, base_target, base_url, busy_indicator, collapsed_sidebar, favicon, header, header_background, header_color, logo, main, main_max_width, manifest, meta_author, meta_description, meta_keywords, meta_refresh, meta_viewport, modal, notifications, sidebar, sidebar_width, site, site_url, title, config, design, location, theme, name)
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

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
