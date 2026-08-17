# panel.layout.spacer module

Spacer components to add horizontal or vertical space to a layout.

class panel.layout.spacer.Divider(refs=None, **params)
Bases: [Reactive](panel.reactive.md#panel.reactive.Reactive)

A Divider draws a horizontal rule (a \<hr\> tag in HTML) to separate
multiple components in a layout. It automatically spans the full width
of the container.

Reference:
[https://panel.holoviz.org/reference/layouts/Divider.html](https://panel.holoviz.org/reference/layouts/Divider.html)

Example:

\>\>\>
pn.Column(
...  '# Lorem
Ipsum', ...
pn.layout.Divider(),
...  'A very long text...
' \>\>\> )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
>

`width_policy`` ``=`` ``Selector(constant=True,`` ``default='fit',`` ``label='Width`` ``policy',`` ``names={},`` ``objects=['auto',`` ``'fixed',`` ``'fit',`` ``'min',`` ``'max'],`` ``readonly=True)`
Describes how the component should maintain its width.
`"auto"` Use component’s preferred sizing
policy. `"fixed"` Use exactly
`width` pixels. Component will overflow if it
can’t fit in the available horizontal space.
`"fit"` Use component’s preferred width (if
set) and allow it to fit into the available horizontal space within the
minimum and maximum width bounds (if set). Component’s width neither
will be aggressively minimized nor maximized.
`"min"` Use as little horizontal space as
possible, not less than the minimum width (if set). The starting point
is the preferred width (if set). The width of the component may shrink
or grow depending on the parent layout, aspect management and other
factors. `"max"` Use as much horizontal space
as possible, not more than the maximum width (if set). The starting
point is the preferred width (if set). The width of the component may
shrink or grow depending on the parent layout, aspect management and
other factors.

class panel.layout.spacer.HSpacer(refs=None, **params)
Bases: [Spacer](#panel.layout.spacer.Spacer)

The HSpacer layout provides responsive horizontal spacing.

Using this component we can space objects equidistantly in a layout and
allow the empty space to shrink when the browser is resized.

How-to: [https://panel.holoviz.org/how_to/layout/spacing.html#spacer-components](https://panel.holoviz.org/how_to/layout/spacing.html#spacer-components)

Example:

\>\>\>
pn.Row(
...
pn.layout.HSpacer(),
'Item 1',
...
pn.layout.HSpacer(),
'Item 2',
...
pn.layout.HSpacer()
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
>

`sizing_mode`` ``=`` ``Parameter(constant=True,`` ``default='stretch_width',`` ``label='Sizing`` ``mode',`` ``readonly=True)`
How the component should size itself. This is a high-level setting for
maintaining width and height of the component. To gain more fine grained
control over sizing, use `width_policy`,
`height_policy` and
`aspect_ratio` instead (those take precedence
over `sizing_mode`).
`"fixed"` Component is not responsive. It will
retain its original width and height regardless of any subsequent
browser window resize events. `"stretch_width"`
Component will responsively resize to stretch to the available width,
without maintaining any aspect ratio. The height of the component
depends on the type of the component and may be fixed or fit to
component’s contents. `"stretch_height"`
Component will responsively resize to stretch to the available height,
without maintaining any aspect ratio. The width of the component depends
on the type of the component and may be fixed or fit to component’s
contents. `"stretch_both"` Component is
completely responsive, independently in width and height, and will
occupy all the available horizontal and vertical space, even if this
changes the aspect ratio of the component.
`"scale_width"` Component will responsively
resize to stretch to the available width, while maintaining the original
or provided aspect ratio. `"scale_height"`
Component will responsively resize to stretch to the available height,
while maintaining the original or provided aspect ratio.
`"scale_both"` Component will responsively
resize to both the available width and height, while maintaining the
original or provided aspect ratio.

class panel.layout.spacer.Spacer(refs=None, **params)
Bases: [Reactive](panel.reactive.md#panel.reactive.Reactive)

The Spacer layout is a very versatile component which makes it easy to
put fixed or responsive spacing between objects.

Like all other components spacers support both absolute and responsive
sizing modes.

How-to: [https://panel.holoviz.org/how_to/layout/spacing.html#spacer-components](https://panel.holoviz.org/how_to/layout/spacing.html#spacer-components)

Example:

\>\>\>
pn.Row(
...
1,
pn.Spacer(width=200),
...
2,
pn.Spacer(width=100),
...  3
... )

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

class panel.layout.spacer.VSpacer(refs=None, **params)
Bases: [Spacer](#panel.layout.spacer.Spacer)

The VSpacer layout provides responsive vertical spacing.

Using this component we can space objects equidistantly in a layout and
allow the empty space to shrink when the browser is resized.

Reference: [https://panel.holoviz.org/how_to/layout/spacing.html#spacer-components](https://panel.holoviz.org/how_to/layout/spacing.html#spacer-components)

Example:

\>\>\>
pn.Column(
...
pn.layout.VSpacer(),
'Item 1',
...
pn.layout.VSpacer(),
'Item 2',
...
pn.layout.VSpacer()
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
>

`sizing_mode`` ``=`` ``Parameter(constant=True,`` ``default='stretch_height',`` ``label='Sizing`` ``mode',`` ``readonly=True)`
How the component should size itself. This is a high-level setting for
maintaining width and height of the component. To gain more fine grained
control over sizing, use `width_policy`,
`height_policy` and
`aspect_ratio` instead (those take precedence
over `sizing_mode`).
`"fixed"` Component is not responsive. It will
retain its original width and height regardless of any subsequent
browser window resize events. `"stretch_width"`
Component will responsively resize to stretch to the available width,
without maintaining any aspect ratio. The height of the component
depends on the type of the component and may be fixed or fit to
component’s contents. `"stretch_height"`
Component will responsively resize to stretch to the available height,
without maintaining any aspect ratio. The width of the component depends
on the type of the component and may be fixed or fit to component’s
contents. `"stretch_both"` Component is
completely responsive, independently in width and height, and will
occupy all the available horizontal and vertical space, even if this
changes the aspect ratio of the component.
`"scale_width"` Component will responsively
resize to stretch to the available width, while maintaining the original
or provided aspect ratio. `"scale_height"`
Component will responsively resize to stretch to the available height,
while maintaining the original or provided aspect ratio.
`"scale_both"` Component will responsively
resize to both the available width and height, while maintaining the
original or provided aspect ratio.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
