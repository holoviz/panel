# panel.template.fast.base module

class panel.template.fast.base.FastBaseTemplate(\*, accent_base_color, background_color, corner_radius, font, font_url, header_accent_base_color, header_neutral_color, main_layout, neutral_color, shadow, sidebar_footer, theme_toggle, \_actions, base_target, base_url, busy_indicator, collapsed_sidebar, favicon, header, header_background, header_color, logo, main, main_max_width, manifest, meta_author, meta_description, meta_keywords, meta_refresh, meta_viewport, modal, notifications, sidebar, sidebar_width, site, site_url, title, config, design, location, theme, name)
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
> main_max_width, sidebar, sidebar_width, modal, notifications, logo,
> favicon, title, site, site_url, manifest, meta_description,
> meta_keywords, meta_author, meta_refresh, meta_viewport, base_url,
> base_target, header_background, header_color, \_actions
>
>

`design`` ``=`` ``ClassSelector(class_=<class`` ``'panel.theme.base.Design'>,`` ``default=<class`` ``'panel.theme.fast.Fast'>,`` ``label='Design')`
A Design applies a specific design system to a template.

`accent_base_color`` ``=`` ``Color(allow_named=True,`` ``default='#0072B5',`` ``label='Accent`` ``base`` ``color')`
Optional body accent color override.

`background_color`` ``=`` ``Color(allow_None=True,`` ``allow_named=True,`` ``label='Background`` ``color')`
Optional body background color override.

`corner_radius`` ``=`` ``Integer(bounds=(0,`` ``25),`` ``default=3,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Corner`` ``radius')`
The corner radius applied to controls.

`font`` ``=`` ``String(default='',`` ``label='Font')`
The font name(s) to apply.

`font_url`` ``=`` ``String(default='',`` ``label='Font`` ``url')`
A font url to import.

`header_neutral_color`` ``=`` ``Color(allow_None=True,`` ``allow_named=True,`` ``label='Header`` ``neutral`` ``color')`
Optional header neutral color override.

`header_accent_base_color`` ``=`` ``Color(allow_None=True,`` ``allow_named=True,`` ``label='Header`` ``accent`` ``base`` ``color')`
Optional header accent color override.

`neutral_color`` ``=`` ``Color(allow_None=True,`` ``allow_named=True,`` ``label='Neutral`` ``color')`
Optional body neutral color override.

`theme_toggle`` ``=`` ``Boolean(default=True,`` ``label='Theme`` ``toggle')`
If True a switch to toggle the Theme is shown.

`shadow`` ``=`` ``Boolean(default=False,`` ``label='Shadow')`
Optional shadow override. Whether or not to apply shadow.

`sidebar_footer`` ``=`` ``String(default='',`` ``label='Sidebar`` ``footer')`
A HTML string appended to the sidebar

`main_layout`` ``=`` ``Selector(default='card',`` ``names={},`` ``objects=[None,`` ``'card'])`
What to wrap the main components into. Options are ‘’ (i.e. none) and
‘card’ (Default). Could be extended to Accordion, Tab etc. in the
future.

design
alias of [Fast](panel.theme.fast.md#panel.theme.fast.Fast)

class panel.template.fast.base.FastGridBaseTemplate(\*, accent_base_color, background_color, corner_radius, font, font_url, header_accent_base_color, header_neutral_color, main_layout, neutral_color, shadow, sidebar_footer, theme_toggle, breakpoints, cols, compact, dimensions, prevent_collision, row_height, save_layout, \_actions, base_target, base_url, busy_indicator, collapsed_sidebar, favicon, header, header_background, header_color, logo, main, main_max_width, manifest, meta_author, meta_description, meta_keywords, meta_refresh, meta_viewport, modal, notifications, sidebar, sidebar_width, site, site_url, title, config, design, location, theme, name)
Bases: [FastBaseTemplate](#panel.template.fast.base.FastBaseTemplate),
[ReactTemplate](panel.template.react.md#panel.template.react.ReactTemplate)

Combines the FastTemplate and the React template.

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
> [class="reference internal"
> title="panel.template.fast.base.FastBaseTemplate"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.fast.base.FastBaseTemplate](#panel.template.fast.base.FastBaseTemplate):
> design, accent_base_color, background_color, corner_radius, font,
> font_url, header_neutral_color, header_accent_base_color,
> neutral_color, theme_toggle, shadow, sidebar_footer, main_layout
>
>

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
