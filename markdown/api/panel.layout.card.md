# panel.layout.card module

class panel.layout.card.Card(\*objects, **params)
Bases: [Column](panel.layout.base.md#panel.layout.base.Column)

A Card layout allows arranging multiple panel objects in a collapsible,
vertical container with a header bar.

Reference:
[https://panel.holoviz.org/reference/layouts/Card.html](https://panel.holoviz.org/reference/layouts/Card.html)

Example:

\>\>\>
pn.Card(
...
some_widget,
some_pane,
some_python_object,
...
title='Card',
styles=dict(background='WhiteSmoke'),
... )

Methods

|  |  |
|----|----|
| [select](#panel.layout.card.Card.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, design, height, min_width, min_height, max_width,
> max_height, margin, styles, stylesheets, tags, width, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
> [class="reference internal" title="panel.layout.base.ListPanel"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListPanel](panel.layout.base.md#panel.layout.base.ListPanel):
> scroll
>
> [class="reference internal" title="panel.layout.base.Column"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.Column](panel.layout.base.md#panel.layout.base.Column):
> auto_scroll_limit, scroll_button_threshold, scroll_position,
> view_latest
>
>

`css_classes`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=['card'],`` ``item_type=<class`` ``'str'>,`` ``label='Css`` ``classes',`` ``nested_refs=True)`
CSS classes to apply to the overall Card.

`active_header_background`` ``=`` ``String(allow_None=True,`` ``label='Active`` ``header`` ``background')`
A valid CSS color for the header background when not collapsed.

`button_css_classes`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=['card-button'],`` ``label='Button`` ``css`` ``classes')`
CSS classes to apply to the button element.

`collapsible`` ``=`` ``Boolean(default=True,`` ``label='Collapsible')`
Whether the Card should be expandable and collapsible.

`collapsed`` ``=`` ``Boolean(default=False,`` ``label='Collapsed')`
Whether the contents of the Card are collapsed.

`header`` ``=`` ``Child(allow_None=True,`` ``class_=<class`` ``'panel.viewable.Viewable'>,`` ``label='Header')`
A Panel component to display in the header bar of the Card. Will
override the given title if defined.

`header_background`` ``=`` ``String(default='',`` ``label='Header`` ``background')`
A valid CSS color for the header background.

`header_color`` ``=`` ``String(default='',`` ``label='Header`` ``color')`
A valid CSS color to apply to the header text.

`header_css_classes`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=['card-header'],`` ``label='Header`` ``css`` ``classes')`
CSS classes to apply to the header element.

`hide_header`` ``=`` ``Boolean(default=False,`` ``label='Hide`` ``header')`
Whether to skip rendering the header.

`title_css_classes`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=['card-title'],`` ``label='Title`` ``css`` ``classes')`
CSS classes to apply to the header title.

`title`` ``=`` ``String(default='',`` ``label='Title')`
A title to be displayed in the Card header, will be overridden by the
header if defined.

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
