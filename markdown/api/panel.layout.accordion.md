# panel.layout.accordion module

class panel.layout.accordion.Accordion(\*objects, **params)
Bases: [NamedListPanel](panel.layout.base.md#panel.layout.base.NamedListPanel)

The Accordion layout is a type of Card layout that allows switching
between multiple objects by clicking on the corresponding card header.

The labels for each card will default to the name parameter of the
card’s contents, but may also be defined explicitly as part of a tuple.

Like Column and Row, Accordion has a list-like API that allows
interactively updating and modifying the cards using the methods append,
extend, clear, insert, pop, remove and \_\_setitem\_\_.

Reference:
[https://panel.holoviz.org/reference/layouts/Accordion.html](https://panel.holoviz.org/reference/layouts/Accordion.html)

Example:

\>\>\>
pn.Accordion(some_pane_with_a_name,
("Plot",
some_plot))

Methods

|  |  |
|----|----|
| [select](#panel.layout.accordion.Accordion.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

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
> [class="reference internal" title="panel.layout.base.NamedListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.NamedListLike](panel.layout.base.md#panel.layout.base.NamedListLike):
> objects
>
> [class="reference internal"
> title="panel.layout.base.NamedListPanel"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.NamedListPanel](panel.layout.base.md#panel.layout.base.NamedListPanel):
> scroll
>
>

`active`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'int'>,`` ``label='Active')`
List of indexes of active cards.

`active_header_background`` ``=`` ``String(allow_None=True,`` ``label='Active`` ``header`` ``background')`
Color for currently active headers.

`header_color`` ``=`` ``String(default='',`` ``label='Header`` ``color')`
A valid CSS color to apply to the expand button.

`header_background`` ``=`` ``String(default='',`` ``label='Header`` ``background')`
A valid CSS color for the header background.

`toggle`` ``=`` ``Boolean(default=False,`` ``label='Toggle')`
Whether to toggle between active cards or allow multiple cards

select(selector: type \| Callable\[\[Viewable\], bool\] \| None = None) → list\[Viewable\]
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
