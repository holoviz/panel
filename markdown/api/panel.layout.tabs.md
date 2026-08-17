# panel.layout.tabs module

Layout component to lay out objects in a set of tabs.

class panel.layout.tabs.Tabs(\*objects, **params)
Bases: [NamedListPanel](panel.layout.base.md#panel.layout.base.NamedListPanel)

The Tabs layout allows switching between multiple objects by clicking on
the corresponding tab header.

Tab labels may be defined explicitly as part of a tuple or will be
inferred from the name parameter of the tab’s contents.

Like Column and Row, Tabs has a list-like API with methods to append,
extend, clear, insert, pop, remove and \_\_setitem\_\_, which make it
possible to interactively update and modify the tabs.

Reference:
[https://panel.holoviz.org/reference/layouts/Tabs.html](https://panel.holoviz.org/reference/layouts/Tabs.html)

Example:

\>\>\>
pn.Tabs(('Scatter',
plot1),
some_pane_with_a_name)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, margin, styles, stylesheets, tags,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.layout.base.NamedListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.NamedListLike](panel.layout.base.md#panel.layout.base.NamedListLike):
> objects
>
> [class="reference internal"
> title="panel.layout.base.NamedListPanel"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.NamedListPanel](panel.layout.base.md#panel.layout.base.NamedListPanel):
> active, scroll
>
>

`height`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
The height of the component (in pixels). This can be either fixed or
preferred height, depending on height sizing policy.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The width of the component (in pixels). This can be either fixed or
preferred width, depending on width sizing policy.

`closable`` ``=`` ``Boolean(default=False,`` ``label='Closable')`
Whether it should be possible to close tabs.

`dynamic`` ``=`` ``Boolean(default=False,`` ``label='Dynamic')`
Dynamically populate only the active tab.

`tabs_location`` ``=`` ``Selector(default='above',`` ``label='Tabs`` ``location',`` ``names={},`` ``objects=['above',`` ``'below',`` ``'left',`` ``'right'])`
The location of the tabs relative to the tab contents.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
