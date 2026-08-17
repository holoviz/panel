# panel.template.react package

## Module contents

React template

class panel.template.react.ReactTemplate(\*, breakpoints, cols, compact, dimensions, prevent_collision, row_height, save_layout, \_actions, base_target, base_url, busy_indicator, collapsed_sidebar, favicon, header, header_background, header_color, logo, main, main_max_width, manifest, meta_author, meta_description, meta_keywords, meta_refresh, meta_viewport, modal, notifications, sidebar, sidebar_width, site, site_url, title, config, design, location, theme, name)
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

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
