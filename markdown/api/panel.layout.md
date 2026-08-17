# panel.layout package

## Submodules

- [panel.layout.accordion module](panel.layout.accordion.md)
  - [Accordion](panel.layout.accordion.md#panel.layout.accordion.Accordion)
    - [Accordion.select()](panel.layout.accordion.md#panel.layout.accordion.Accordion.select)
- [panel.layout.base module](panel.layout.base.md)
  - [Column](panel.layout.base.md#panel.layout.base.Column)
    - [Column.scroll_to()](panel.layout.base.md#panel.layout.base.Column.scroll_to)
  - [ListLike](panel.layout.base.md#panel.layout.base.ListLike)
    - [ListLike.append()](panel.layout.base.md#panel.layout.base.ListLike.append)
    - [ListLike.clear()](panel.layout.base.md#panel.layout.base.ListLike.clear)
    - [ListLike.clone()](panel.layout.base.md#panel.layout.base.ListLike.clone)
    - [ListLike.extend()](panel.layout.base.md#panel.layout.base.ListLike.extend)
    - [ListLike.index()](panel.layout.base.md#panel.layout.base.ListLike.index)
    - [ListLike.insert()](panel.layout.base.md#panel.layout.base.ListLike.insert)
    - [ListLike.pop()](panel.layout.base.md#panel.layout.base.ListLike.pop)
    - [ListLike.remove()](panel.layout.base.md#panel.layout.base.ListLike.remove)
    - [ListLike.reverse()](panel.layout.base.md#panel.layout.base.ListLike.reverse)
  - [ListPanel](panel.layout.base.md#panel.layout.base.ListPanel)
    - [ListPanel.clone()](panel.layout.base.md#panel.layout.base.ListPanel.clone)
  - [NamedListLike](panel.layout.base.md#panel.layout.base.NamedListLike)
    - [NamedListLike.append()](panel.layout.base.md#panel.layout.base.NamedListLike.append)
    - [NamedListLike.clear()](panel.layout.base.md#panel.layout.base.NamedListLike.clear)
    - [NamedListLike.clone()](panel.layout.base.md#panel.layout.base.NamedListLike.clone)
    - [NamedListLike.extend()](panel.layout.base.md#panel.layout.base.NamedListLike.extend)
    - [NamedListLike.insert()](panel.layout.base.md#panel.layout.base.NamedListLike.insert)
    - [NamedListLike.pop()](panel.layout.base.md#panel.layout.base.NamedListLike.pop)
    - [NamedListLike.remove()](panel.layout.base.md#panel.layout.base.NamedListLike.remove)
    - [NamedListLike.reverse()](panel.layout.base.md#panel.layout.base.NamedListLike.reverse)
  - [NamedListPanel](panel.layout.base.md#panel.layout.base.NamedListPanel)
    - [NamedListPanel.clone()](panel.layout.base.md#panel.layout.base.NamedListPanel.clone)
  - [Panel](panel.layout.base.md#panel.layout.base.Panel)
    - [Panel.get_root()](panel.layout.base.md#panel.layout.base.Panel.get_root)
    - [Panel.select()](panel.layout.base.md#panel.layout.base.Panel.select)
  - [Row](panel.layout.base.md#panel.layout.base.Row)
  - [SizingModeMixin](panel.layout.base.md#panel.layout.base.SizingModeMixin)
  - [WidgetBox](panel.layout.base.md#panel.layout.base.WidgetBox)
- [panel.layout.card module](panel.layout.card.md)
  - [Card](panel.layout.card.md#panel.layout.card.Card)
    - [Card.select()](panel.layout.card.md#panel.layout.card.Card.select)
- [panel.layout.feed module](panel.layout.feed.md)
  - [Feed](panel.layout.feed.md#panel.layout.feed.Feed)
    - [Feed.scroll_to_latest()](panel.layout.feed.md#panel.layout.feed.Feed.scroll_to_latest)
- [panel.layout.flex module](panel.layout.flex.md)
  - [FlexBox](panel.layout.flex.md#panel.layout.flex.FlexBox)
    - [FlexBox.clone()](panel.layout.flex.md#panel.layout.flex.FlexBox.clone)
    - [FlexBox.select()](panel.layout.flex.md#panel.layout.flex.FlexBox.select)
- [panel.layout.float module](panel.layout.float.md)
  - [FloatPanel](panel.layout.float.md#panel.layout.float.FloatPanel)
    - [FloatPanel.clone()](panel.layout.float.md#panel.layout.float.FloatPanel.clone)
    - [FloatPanel.select()](panel.layout.float.md#panel.layout.float.FloatPanel.select)
- [panel.layout.grid module](panel.layout.grid.md)
  - [GridBox](panel.layout.grid.md#panel.layout.grid.GridBox)
  - [GridSpec](panel.layout.grid.md#panel.layout.grid.GridSpec)
    - [GridSpec.clone()](panel.layout.grid.md#panel.layout.grid.GridSpec.clone)
- [panel.layout.gridstack module](panel.layout.gridstack.md)
  - [GridStack](panel.layout.gridstack.md#panel.layout.gridstack.GridStack)
- [panel.layout.modal module](panel.layout.modal.md)
  - [Modal](panel.layout.modal.md#panel.layout.modal.Modal)
    - [Modal.create_button()](panel.layout.modal.md#panel.layout.modal.Modal.create_button)
    - [Modal.show()](panel.layout.modal.md#panel.layout.modal.Modal.show)
- [panel.layout.spacer module](panel.layout.spacer.md)
  - [Divider](panel.layout.spacer.md#panel.layout.spacer.Divider)
  - [HSpacer](panel.layout.spacer.md#panel.layout.spacer.HSpacer)
  - [Spacer](panel.layout.spacer.md#panel.layout.spacer.Spacer)
  - [VSpacer](panel.layout.spacer.md#panel.layout.spacer.VSpacer)
- [panel.layout.swipe module](panel.layout.swipe.md)
  - [Swipe](panel.layout.swipe.md#panel.layout.swipe.Swipe)
    - [Swipe.clone()](panel.layout.swipe.md#panel.layout.swipe.Swipe.clone)
    - [Swipe.select()](panel.layout.swipe.md#panel.layout.swipe.Swipe.select)
- [panel.layout.tabs module](panel.layout.tabs.md)
  - [Tabs](panel.layout.tabs.md#panel.layout.tabs.Tabs)

## Module contents

### Layout

Layouts can layout your python objects and panel components.

Most layouts behave as the Python containers you already know. For
example Column and Row behaves as lists. I.e. they have a list-like API
with methods to append, extend, clear, insert, pop, remove and
\_\_setitem\_\_, which make it possible to interactively update and
modify them.

Check out the Panel gallery of layouts
[https://panel.holoviz.org/reference/index.html#layouts](https://panel.holoviz.org/reference/index.html#layouts)
for inspiration.

#### How to use layouts in 2 simple steps

1.  Define your Python objects

\>\>\> some_python_object
= ...
\>\>\> some_widget
=
pn.widgets...
\>\>\> some_pane
=
pn.pane...

2.  Define your layouts

\>\>\>
pn.Column(some_python_object,
some_widget,
some_pane)

For more detail see the Getting Started Guide
[https://panel.holoviz.org/getting_started/index.html](https://panel.holoviz.org/getting_started/index.html)

class panel.layout.Accordion(\*objects, **params)
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
| [select](#panel.layout.Accordion.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

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

class panel.layout.Card(\*objects, **params)
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
| [select](#panel.layout.Card.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

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

class panel.layout.Column(\*objects: Any, **params: Any)
Bases: [ListPanel](panel.layout.base.md#panel.layout.base.ListPanel)

The Column layout allows arranging multiple panel objects in a vertical
container.

It has a list-like API with methods to append, extend, clear, insert,
pop, remove and \_\_setitem\_\_, which makes it possible to
interactively update and modify the layout.

Reference:
[https://panel.holoviz.org/reference/layouts/Column.html](https://panel.holoviz.org/reference/layouts/Column.html)

Example:

\>\>\>
pn.Column(some_widget,
some_pane,
some_python_object)

Methods

|  |  |
|----|----|
| [scroll_to](#panel.layout.Column.scroll_to)(index) | Scrolls to the child at the provided index. |

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
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
> [class="reference internal" title="panel.layout.base.ListPanel"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListPanel](panel.layout.base.md#panel.layout.base.ListPanel):
> scroll
>
>

`auto_scroll_limit`` ``=`` ``Integer(bounds=(0,`` ``None),`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Auto`` ``scroll`` ``limit')`
Max pixel distance from the latest object in the Column to activate
automatic scrolling upon update. Setting to 0 disables auto-scrolling.

`scroll_button_threshold`` ``=`` ``Integer(bounds=(0,`` ``None),`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Scroll`` ``button`` ``threshold')`
Min pixel distance from the latest object in the Column to display the
scroll button. Setting to 0 disables the scroll button.

`scroll_position`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Scroll`` ``position')`
Current scroll position of the Column. Setting this value will update
the scroll position of the Column. Setting to 0 will scroll to the top.

`view_latest`` ``=`` ``Boolean(default=False,`` ``label='View`` ``latest')`
Whether to scroll to the latest object on init. If not enabled the view
will be on the first object.

scroll_to(index: int)
Scrolls to the child at the provided index.

Parameters:
**index: int**
Index of the child object to scroll to.

class panel.layout.Divider(refs=None, **params)
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

class panel.layout.Feed(\*objects, **params)
Bases: [Column](panel.layout.base.md#panel.layout.base.Column)

The Feed class inherits from the Column layout, thereby enabling the
arrangement of multiple panel objects within a vertical container.
However, it restrictively manages the number of objects displayed at any
moment. This layout is particularly useful for efficiently rendering a
substantial number of objects.

Similar to Column, the Feed provides a list-like API, including methods
such as append, extend, clear, insert, pop, remove, and \_\_setitem\_\_.
These methods facilitate interactive updates and modifications to the
layout.

Reference:
[https://panel.holoviz.org/reference/layouts/Feed.html](https://panel.holoviz.org/reference/layouts/Feed.html)

Example:

\>\>\>
pn.Feed(some_widget,
some_pane,
some_python_object,
...,
python_object_1002)

Methods

|  |  |
|----|----|
| [scroll_to_latest](#panel.layout.Feed.scroll_to_latest)(\[scroll_limit\]) | Scrolls the Feed to the latest entry. |

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
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
> [class="reference internal" title="panel.layout.base.Column"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.Column](panel.layout.base.md#panel.layout.base.Column):
> auto_scroll_limit, scroll_button_threshold, scroll_position,
> view_latest
>
>

`scroll`` ``=`` ``Selector(default='y',`` ``label='Scroll',`` ``names={},`` ``objects=[False,`` ``True,`` ``'both-auto',`` ``'y-auto',`` ``'x-auto',`` ``'both',`` ``'x',`` ``'y'])`
Whether to add scrollbars if the content overflows the size of the
container. If “both-auto”, will only add scrollbars if the content
overflows in either directions. If “x-auto” or “y-auto”, will only add
scrollbars if the content overflows in the respective direction. If
“both”, will always add scrollbars. If “x” or “y”, will always add
scrollbars in the respective direction. If False, overflowing content
will be clipped. If True, will only add scrollbars in the direction of
the container, (e.g. Column: vertical, Row: horizontal).

`load_buffer`` ``=`` ``Integer(bounds=(0,`` ``None),`` ``default=50,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Load`` ``buffer')`
The number of objects loaded on each side of the visible objects. When
scrolled halfway into the buffer, the feed will automatically load
additional objects while unloading objects on the opposite side.

`visible_range`` ``=`` ``Range(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Visible`` ``range',`` ``length=2,`` ``readonly=True)`
Read-only upper and lower bounds of the currently visible feed objects.
This list is automatically updated based on scrolling.

scroll_to_latest(scroll_limit: float \| None = None) → None
Scrolls the Feed to the latest entry.

Parameters:
scroll_limit : float, optional
Maximum pixel distance from the latest object in the Feed to trigger
scrolling. If the distance exceeds this limit, scrolling will not occur.
If this is not set, it will always scroll to the latest while setting
this to 0 disables scrolling.

class panel.layout.FlexBox(\*objects, **params)
Bases: [ListLike](panel.layout.base.md#panel.layout.base.ListLike),
[ReactiveHTML](panel.reactive.md#panel.reactive.ReactiveHTML)

The FlexBox is a list-like layout (unlike GridSpec) that wraps objects
into a CSS flex container.

It has a list-like API with methods to append, extend, clear, insert,
pop, remove and \_\_setitem\_\_, which makes it possible to
interactively update and modify the layout. It exposes all the CSS
options for controlling the behavior and layout of the flex box.

Reference:
[https://panel.holoviz.org/reference/layouts/FlexBox.html](https://panel.holoviz.org/reference/layouts/FlexBox.html)

Example:

\>\>\>
pn.FlexBox(
...
some_python_object,
another_python_object,
..., ...
 the_last_python_object
... )

Methods

|  |  |
|----|----|
| [clone](#panel.layout.FlexBox.clone)(\*objects, **params) | Makes a copy of the layout sharing the same parameters. |
| [select](#panel.layout.FlexBox.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

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
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
>

`align_content`` ``=`` ``Selector(default='flex-start',`` ``label='Align`` ``content',`` ``names={},`` ``objects=['normal',`` ``'flex-start',`` ``'flex-end',`` ``'center',`` ``'space-between',`` ``'space-around',`` ``'space-evenly',`` ``'stretch',`` ``'start',`` ``'end',`` ``'baseline',`` ``'first`` ``baseline',`` ``'last`` ``baseline'])`
Defines how a flex container’s lines align when there is extra space in
the cross-axis.

`align_items`` ``=`` ``Selector(default='flex-start',`` ``label='Align`` ``items',`` ``names={},`` ``objects=['stretch',`` ``'flex-start',`` ``'flex-end',`` ``'center',`` ``'baseline',`` ``'first`` ``baseline',`` ``'last`` ``baseline',`` ``'start',`` ``'end',`` ``'self-start',`` ``'self-end'])`
Defines the default behavior for how flex items are laid out along the
cross axis on the current line.

`flex_direction`` ``=`` ``Selector(default='row',`` ``label='Flex`` ``direction',`` ``names={},`` ``objects=['row',`` ``'row-reverse',`` ``'column',`` ``'column-reverse'])`
This establishes the main-axis, thus defining the direction flex items
are placed in the flex container.

`flex_wrap`` ``=`` ``Selector(default='wrap',`` ``label='Flex`` ``wrap',`` ``names={},`` ``objects=['nowrap',`` ``'wrap',`` ``'wrap-reverse'])`
Whether and how to wrap items in the flex container.

`gap`` ``=`` ``String(default='',`` ``label='Gap')`
Defines the spacing between flex items, supporting various units (px,
em, rem, %, vw/vh).

`justify_content`` ``=`` ``Selector(default='flex-start',`` ``label='Justify`` ``content',`` ``names={},`` ``objects=['flex-start',`` ``'flex-end',`` ``'center',`` ``'space-between',`` ``'space-around',`` ``'space-evenly',`` ``'start',`` ``'end',`` ``'left',`` ``'right'])`
Defines the alignment along the main axis.

clone(\*objects: t.Any, **params: t.Any) → Self
Makes a copy of the layout sharing the same parameters.

Parameters:
**objects: Objects to add to the cloned layout.**

**params: Keyword arguments override the parameters on the clone.**

Returns:
Cloned layout object

select(selector=None)
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

class panel.layout.FloatPanel(\*objects, name='', **params)
Bases: [ListLike](panel.layout.base.md#panel.layout.base.ListLike),
[ReactiveHTML](panel.reactive.md#panel.reactive.ReactiveHTML)

Float provides a floating panel layout.

Reference:
[https://panel.holoviz.org/reference/layouts/FloatPanel.html](https://panel.holoviz.org/reference/layouts/FloatPanel.html)

Example:

\>\>\>
import
panel
as
pn \>\>\>
pn.extension("floatpanel")
\>\>\>
pn.layout.FloatPanel("**I
can float**!",
position="center",
width=300).servable()

Methods

|  |  |
|----|----|
| [clone](#panel.layout.FloatPanel.clone)(\*objects, **params) | Makes a copy of the layout sharing the same parameters. |
| [select](#panel.layout.FloatPanel.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

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
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
>

`config`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Config')`
Additional jsPanel configuration with precedence over parameter values.

`contained`` ``=`` ``Boolean(default=True,`` ``label='Contained')`
Whether the component is contained within parent container or completely
free floating.

`position`` ``=`` ``Selector(default='right-top',`` ``label='Position',`` ``names={},`` ``objects=['center',`` ``'left-top',`` ``'center-top',`` ``'right-top',`` ``'right-center',`` ``'right-bottom',`` ``'center-bottom',`` ``'left-bottom',`` ``'left-center'])`
The initial position if the container is free-floating.

`offsetx`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Offsetx')`
Horizontal offset in pixels.

`offsety`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Offsety')`
Vertical offset in pixels.

`theme`` ``=`` ``String(default='primary',`` ``label='Theme')`
The theme which can be one of: - Built-ins: ‘default’, ‘primary’,
‘secondary’, ‘info’, ‘success’, ‘warning’, ‘danger’, ‘light’, ‘dark’ and
‘none’ - HEX, RGB and HSL color values like ‘#123456’ Any standardized
color name like ‘forestgreen’ and color names from the Material Design
Color System like ‘purple900’ - Additionally a theme string may include
one of the modifiers ‘filled’, ‘filledlight’, ‘filleddark’ or
‘fillcolor’ separated from the theme color by a space like ‘primary

`status`` ``=`` ``Selector(default='normalized',`` ``label='Status',`` ``names={},`` ``objects=['normalized',`` ``'maximized',`` ``'minimized',`` ``'smallified',`` ``'smallifiedmax',`` ``'closed'])`
The current status of the panel.

clone(\*objects: t.Any, **params: t.Any) → Self
Makes a copy of the layout sharing the same parameters.

Parameters:
**objects: Objects to add to the cloned layout.**

**params: Keyword arguments override the parameters on the clone.**

Returns:
Cloned layout object

select(selector=None)
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

class panel.layout.GridBox(\*objects: Any, **params: Any)
Bases: [ListPanel](panel.layout.base.md#panel.layout.base.ListPanel)

The GridBox is a list-like layout (unlike GridSpec) that wraps objects
into a grid according to the specified nrows and ncols parameters.

It has a list-like API with methods to append, extend, clear, insert,
pop, remove and \_\_setitem\_\_, which makes it possible to
interactively update and modify the layout.

Reference:
[https://panel.holoviz.org/reference/layouts/GridBox.html](https://panel.holoviz.org/reference/layouts/GridBox.html)

Example:

\>\>\>
pn.GridBox(
...
python_object_1,
python_object_2,
..., ...
 python_object_24,
ncols=6
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
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
> [class="reference internal" title="panel.layout.base.ListPanel"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListPanel](panel.layout.base.md#panel.layout.base.ListPanel):
> scroll
>
>

`nrows`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Nrows')`
Number of rows to reflow the layout into.

`ncols`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Ncols')`
Number of columns to reflow the layout into.

class panel.layout.GridSpec(\*, mode, ncols, nrows, objects, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: [Panel](panel.layout.base.md#panel.layout.base.Panel)

The GridSpec is an *array like* layout that allows arranging multiple
Panel objects in a grid using a simple API to assign objects to
individual grid cells or to a grid span.

Other layout containers function like lists, but a GridSpec has an API
similar to a 2D array, making it possible to use 2D assignment to
populate, index, and slice the grid.

See GridStack for a similar layout that allows the user to resize and
drag the cells.

Reference:
[https://panel.holoviz.org/reference/layouts/GridSpec.html](https://panel.holoviz.org/reference/layouts/GridSpec.html)

Example:

\>\>\>
import
panel
as
pn \>\>\>
gspec =
pn.GridSpec(width=800,
height=600)
\>\>\>
gspec\[:,
0 \]
=
pn.Spacer(styles=dict(background='red'))
\>\>\>
gspec\[0,
1:3\]
=
pn.Spacer(styles=dict(background='green'))
\>\>\>
gspec\[1,
2:4\]
=
pn.Spacer(styles=dict(background='orange'))
\>\>\>
gspec\[2,
1:4\]
=
pn.Spacer(styles=dict(background='blue'))
\>\>\>
gspec\[0:1,
3:4\]
=
pn.Spacer(styles=dict(background='purple'))
\>\>\> gspec

Attributes:
**grid**

Methods

|  |  |
|----|----|
| [clone](#panel.layout.GridSpec.clone)(**params) | Makes a copy of the GridSpec sharing the same parameters. |

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

`objects`` ``=`` ``ChildDict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Objects')`
The dictionary of child objects that make up the grid.

`mode`` ``=`` ``Selector(default='warn',`` ``label='Mode',`` ``names={},`` ``objects=['warn',`` ``'error',`` ``'override'])`
Whether to warn, error or simply override on overlapping assignment.

`ncols`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Ncols')`
Limits the number of columns that can be assigned.

`nrows`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Nrows')`
Limits the number of rows that can be assigned.

clone(**params)
Makes a copy of the GridSpec sharing the same parameters.

Parameters:
**params: Keyword arguments override the parameters on the clone.**

Returns:
Cloned GridSpec object

class panel.layout.GridStack(\*, allow_drag, allow_resize, state, mode, ncols, nrows, objects, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: [ReactiveHTML](panel.reactive.md#panel.reactive.ReactiveHTML),
[GridSpec](panel.layout.grid.md#panel.layout.grid.GridSpec)

The GridStack layout allows arranging multiple Panel objects in a grid
using a simple API to assign objects to individual grid cells or to a
grid span.

Other layout containers function like lists, but a GridSpec has an API
similar to a 2D array, making it possible to use 2D assignment to
populate, index, and slice the grid.

Reference:
[https://panel.holoviz.org/reference/layouts/GridStack.html](https://panel.holoviz.org/reference/layouts/GridStack.html)

Example:

\>\>\>
pn.extension('gridstack')
\>\>\> gstack
=
GridStack(sizing_mode='stretch_both')
\>\>\>
gstack\[
: ,
0:
3\]
=
pn.Spacer(styles=dict(background='red'))
\>\>\>
gstack\[0:2,
3:
9\]
=
pn.Spacer(styles=dict(background='green'))
\>\>\>
gstack\[2:4,
6:12\]
=
pn.Spacer(styles=dict(background='orange'))
\>\>\>
gstack\[4:6,
3:12\]
=
pn.Spacer(styles=dict(background='blue'))
\>\>\>
gstack\[0:2,
9:12\]
=
pn.Spacer(styles=dict(background='purple'))

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
> [class="reference internal" title="panel.layout.grid.GridSpec"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.grid.GridSpec](panel.layout.grid.md#panel.layout.grid.GridSpec):
> objects, mode, ncols, nrows
>
>

`height`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
The height of the component (in pixels). This can be either fixed or
preferred height, depending on height sizing policy.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The width of the component (in pixels). This can be either fixed or
preferred width, depending on width sizing policy.

`allow_resize`` ``=`` ``Boolean(default=True,`` ``label='Allow`` ``resize')`
Allow resizing the grid cells.

`allow_drag`` ``=`` ``Boolean(default=True,`` ``label='Allow`` ``drag')`
Allow dragging the grid cells.

`state`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'dict'>,`` ``label='State')`
Current state of the grid (updated as items are resized and dragged).

class panel.layout.HSpacer(refs=None, **params)
Bases: [Spacer](panel.layout.spacer.md#panel.layout.spacer.Spacer)

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

class panel.layout.ListLike(\*objects: Any, **params: Any)
Bases: `Parameterized`

Methods

|  |  |
|----|----|
| [append](#panel.layout.ListLike.append)(obj) | Appends an object to the layout. |
| [clear](#panel.layout.ListLike.clear)() | Clears the objects on this layout. |
| [clone](#panel.layout.ListLike.clone)(\*objects, **params) | Makes a copy of the layout sharing the same parameters. |
| [extend](#panel.layout.ListLike.extend)(objects) | Extends the objects on this layout with a list. |
| [index](#panel.layout.ListLike.index)(obj) | Returns the integer index of the supplied object in the list of objects. |
| [insert](#panel.layout.ListLike.insert)(index, obj) | Inserts an object in the layout at the specified index. |
| [pop](#panel.layout.ListLike.pop)(\[index\]) | Pops an item from the layout by index. |
| [remove](#panel.layout.ListLike.remove)(obj) | Removes an object from the layout. |
| [reverse](#panel.layout.ListLike.reverse)() | Reverses the objects in the layout. |

**Parameter Definitions**

------------------------------------------------------------------------

`objects`` ``=`` ``Children(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'panel.viewable.Viewable'>,`` ``label='Objects')`
The list of child objects that make up the layout.

append(obj: Any) → None
Appends an object to the layout.

Parameters:
**obj (object): Panel component to add to the layout.**

clear() → list\[Viewable\]
Clears the objects on this layout.

Returns:
objects (list\[Viewable\]): List of cleared objects.

clone(\*objects: t.Any, **params: t.Any) → Self
Makes a copy of the layout sharing the same parameters.

Parameters:
**objects: Objects to add to the cloned layout.**

**params: Keyword arguments override the parameters on the clone.**

Returns:
Cloned layout object

extend(objects: Iterable\[Any\]) → None
Extends the objects on this layout with a list.

Parameters:
**objects (list): List of panel components to add to the layout.**

index(obj: Viewable) → int
Returns the integer index of the supplied object in the list of objects.

Parameters:
**obj (Viewable): Panel component to look up the index for.**

Returns:
index (int): Integer index of the object in the layout.

insert(index: int, obj: Any) → None
Inserts an object in the layout at the specified index.

Parameters:
**index (int): Index at which to insert the object.**

**object (object): Panel components to insert in the layout.**

pop(index: int = -1) → Viewable
Pops an item from the layout by index.

Parameters:
**index (int): The index of the item to pop from the layout.**

remove(obj: Viewable) → None
Removes an object from the layout.

Parameters:
**obj (object): The object to remove from the layout.**

reverse() → None
Reverses the objects in the layout.

class panel.layout.ListPanel(\*objects: Any, **params: Any)
Bases: [ListLike](panel.layout.base.md#panel.layout.base.ListLike),
[Panel](panel.layout.base.md#panel.layout.base.Panel)

An abstract baseclass for Panel objects with list-like children.

Methods

|  |  |
|----|----|
| [clone](#panel.layout.ListPanel.clone)(\*objects, **params) | Makes a copy of the layout sharing the same parameters. |

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
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
>

`scroll`` ``=`` ``Selector(default=False,`` ``label='Scroll',`` ``names={},`` ``objects=[False,`` ``True,`` ``'both-auto',`` ``'y-auto',`` ``'x-auto',`` ``'both',`` ``'x',`` ``'y'])`
Whether to add scrollbars if the content overflows the size of the
container. If “both-auto”, will only add scrollbars if the content
overflows in either directions. If “x-auto” or “y-auto”, will only add
scrollbars if the content overflows in the respective direction. If
“both”, will always add scrollbars. If “x” or “y”, will always add
scrollbars in the respective direction. If False, overflowing content
will be clipped. If True, will only add scrollbars in the direction of
the container, (e.g. Column: vertical, Row: horizontal).

clone(\*objects: Any, **params: Any)
Makes a copy of the layout sharing the same parameters.

Parameters:
**objects: Objects to add to the cloned layout.**

**params: Keyword arguments override the parameters on the clone.**

Returns:
Cloned layout object

class panel.layout.Modal(\*objects: Any, **params: Any)
Bases: [ListPanel](panel.layout.base.md#panel.layout.base.ListPanel)

Create a modal dialog that can be opened and closed.

Methods

|  |  |
|----|----|
| [create_button](#panel.layout.Modal.create_button)(action, **kwargs) | Create a button to show, hide or toggle the modal. |
| [show](#panel.layout.Modal.show)() | Starts a Bokeh server and displays the Viewable in a new tab. |

|            |     |
|------------|-----|
| **hide**   |     |
| **toggle** |     |

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
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
> [class="reference internal" title="panel.layout.base.ListPanel"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListPanel](panel.layout.base.md#panel.layout.base.ListPanel):
> scroll
>
>

`open`` ``=`` ``Boolean(default=False,`` ``label='Open')`
Whether to open the modal.

`show_close_button`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``close`` ``button')`
Whether to show a close button in the modal.

`background_close`` ``=`` ``Boolean(default=True,`` ``label='Background`` ``close')`
Whether to enable closing the modal when clicking the background.

create_button(action: Literal\['show', 'hide', 'toggle'\], **kwargs)
Create a button to show, hide or toggle the modal.

show()
Starts a Bokeh server and displays the Viewable in a new tab.

Parameters:
title : str \| None
A string title to give the Document (if served as an app)

**port: int (optional, default=0)**
Allows specifying a specific port

address : str
The address the server should listen on for HTTP requests.

**websocket_origin: str or list(str) (optional)**
A list of hosts that can connect to the websocket. This is typically
required when embedding a server app in an external web site. If None,
“localhost” is used.

**threaded: boolean (optional, default=False)**
Whether to launch the Server on a separate thread, allowing interactive
use.

**verbose: boolean (optional, default=True)**
Whether to print the address and port

open : boolean (optional, default=True)
Whether to open the server in a new browser tab

location : boolean or panel.io.location.Location
Whether to create a Location component to observe and set the URL
location.

Returns:
server: bokeh.server.Server or panel.io.server.StoppableThread
Returns the Bokeh server instance or the thread the server was launched
on (if threaded=True)

class panel.layout.Panel(refs=None, **params)
Bases: [Reactive](panel.reactive.md#panel.reactive.Reactive),
[SizingModeMixin](panel.layout.base.md#panel.layout.base.SizingModeMixin)

Abstract baseclass for a layout of Viewables.

Methods

|  |  |
|----|----|
| [get_root](#panel.layout.Panel.get_root)(\[doc, comm, preprocess\]) | Returns the root model and applies pre-processing hooks |
| [select](#panel.layout.Panel.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

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

get_root(doc: Document \| None = None, comm: Comm \| None = None, preprocess: bool = True) → Model
Returns the root model and applies pre-processing hooks

Parameters:
**doc: bokeh.Document**
Bokeh document the bokeh model will be attached to.

**comm: pyviz_comms.Comm**
Optional pyviz_comms when working in notebook

**preprocess: boolean (default=True)**
Whether to run preprocessing hooks

Returns:
Returns the bokeh model corresponding to this panel object

select(selector=None)
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

class panel.layout.Row(\*objects: Any, **params: Any)
Bases: [ListPanel](panel.layout.base.md#panel.layout.base.ListPanel)

The Row layout allows arranging multiple panel objects in a horizontal
container.

It has a list-like API with methods to append, extend, clear, insert,
pop, remove and \_\_setitem\_\_, which makes it possible to
interactively update and modify the layout.

Reference:
[https://panel.holoviz.org/reference/layouts/Row.html](https://panel.holoviz.org/reference/layouts/Row.html)

Example:

\>\>\>
pn.Row(some_widget,
some_pane,
some_python_object)

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
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
> [class="reference internal" title="panel.layout.base.ListPanel"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListPanel](panel.layout.base.md#panel.layout.base.ListPanel):
> scroll
>
>

class panel.layout.Spacer(refs=None, **params)
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

class panel.layout.Swipe(\*objects, **params)
Bases: [ListLike](panel.layout.base.md#panel.layout.base.ListLike),
[ReactiveHTML](panel.reactive.md#panel.reactive.ReactiveHTML)

The Swipe layout enables you to quickly compare two panels laid out on
top of each other with a part of the *before* panel shown on one side of
a slider and a part of the *after* panel shown on the other side.

Attributes:
**after**

**before**

Methods

|  |  |
|----|----|
| [clone](#panel.layout.Swipe.clone)(\*objects, **params) | Makes a copy of the layout sharing the same parameters. |
| [select](#panel.layout.Swipe.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

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

`objects`` ``=`` ``Children(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'panel.viewable.Viewable'>,`` ``label='Objects')`
The list of child objects that make up the layout.

`slider_width`` ``=`` ``Integer(bounds=(0,`` ``25),`` ``default=5,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Slider`` ``width')`
The width of the slider in pixels

`slider_color`` ``=`` ``Color(allow_named=True,`` ``default='black',`` ``label='Slider`` ``color')`
The color of the slider

`start`` ``=`` ``Integer(bounds=(0,`` ``100),`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
Limits the minimum percentage the swipe handler can be moved to.

`end`` ``=`` ``Integer(bounds=(0,`` ``100),`` ``default=100,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
Limits the maximum percentage the swipe handler can be moved to.

`value`` ``=`` ``Integer(bounds=(0,`` ``100),`` ``default=50,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
The percentage of the *after* panel to show.

`_before`` ``=`` ``Parameter(allow_None=True,`` ``label='`` ``before')`

`_after`` ``=`` ``Parameter(allow_None=True,`` ``label='`` ``after')`

clone(\*objects: t.Any, **params: t.Any) → Self
Makes a copy of the layout sharing the same parameters.

Parameters:
**objects: Objects to add to the cloned layout.**

**params: Keyword arguments override the parameters on the clone.**

Returns:
Cloned layout object

select(selector=None)
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

class panel.layout.Tabs(\*objects, **params)
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

class panel.layout.VSpacer(refs=None, **params)
Bases: [Spacer](panel.layout.spacer.md#panel.layout.spacer.Spacer)

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

class panel.layout.WidgetBox(\*objects: Any, **params: Any)
Bases: [ListPanel](panel.layout.base.md#panel.layout.base.ListPanel)

The WidgetBox layout allows arranging multiple panel objects in a
vertical (or horizontal) container.

It is largely identical to the Column layout, but has some default
styling that makes widgets be clearly grouped together visually.

It has a list-like API with methods to append, extend, clear, insert,
pop, remove and \_\_setitem\_\_, which make it possible to interactively
update and modify the layout.

Reference:
[https://panel.holoviz.org/reference/layouts/WidgetBox.html](https://panel.holoviz.org/reference/layouts/WidgetBox.html)

Example:

\>\>\>
pn.WidgetBox(some_widget,
another_widget)

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
>

`css_classes`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=['panel-widget-box'],`` ``item_type=<class`` ``'str'>,`` ``label='Css`` ``classes',`` ``nested_refs=True)`
CSS classes to apply to the layout.

`disabled`` ``=`` ``Boolean(default=False,`` ``label='Disabled')`
Whether the widget is disabled.

`horizontal`` ``=`` ``Boolean(default=False,`` ``label='Horizontal')`
Whether to lay out the widgets in a Row layout as opposed to a Column
layout.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
