# panel.template.editable package

## Module contents

Editable template

class panel.template.editable.EditableTemplate(\*, editable, layout, local_save, \_actions, base_target, base_url, busy_indicator, collapsed_sidebar, favicon, header, header_background, header_color, logo, main, main_max_width, manifest, meta_author, meta_description, meta_keywords, meta_refresh, meta_viewport, modal, notifications, sidebar, sidebar_width, site, site_url, title, config, design, location, theme, name)
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

class panel.template.editable.TemplateEditor(\*, layout, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: [ReactiveHTML](panel.reactive.md#panel.reactive.ReactiveHTML)

Component responsible for watching the template for changes and syncing
the current layout state with Python.

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
>

`layout`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'dict'>,`` ``label='Layout')`
The current layout of the template, which is updated by the editor. It
is a list of dictionaries with the keys ‘id’, ‘width’, ‘height’, and
‘visible’. The ‘id’ corresponds to the component’s model id, while
‘width’ and ‘height’ are in percentage of the grid cell size.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
