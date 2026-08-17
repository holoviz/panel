# panel.layout.base module

Defines Layout classes which may be used to arrange panes and widgets in
flexible ways to build complex dashboards.

class panel.layout.base.Column(\*objects: Any, **params: Any)
Bases: [ListPanel](#panel.layout.base.ListPanel)

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
| [scroll_to](#panel.layout.base.Column.scroll_to)(index) | Scrolls to the child at the provided index. |

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
> [title="panel.layout.base.ListLike"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](#panel.layout.base.ListLike):
> objects
>
> [title="panel.layout.base.ListPanel"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListPanel](#panel.layout.base.ListPanel):
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

class panel.layout.base.ListLike(\*objects: Any, **params: Any)
Bases: `Parameterized`

Methods

|  |  |
|----|----|
| [append](#panel.layout.base.ListLike.append)(obj) | Appends an object to the layout. |
| [clear](#panel.layout.base.ListLike.clear)() | Clears the objects on this layout. |
| [clone](#panel.layout.base.ListLike.clone)(\*objects, **params) | Makes a copy of the layout sharing the same parameters. |
| [extend](#panel.layout.base.ListLike.extend)(objects) | Extends the objects on this layout with a list. |
| [index](#panel.layout.base.ListLike.index)(obj) | Returns the integer index of the supplied object in the list of objects. |
| [insert](#panel.layout.base.ListLike.insert)(index, obj) | Inserts an object in the layout at the specified index. |
| [pop](#panel.layout.base.ListLike.pop)(\[index\]) | Pops an item from the layout by index. |
| [remove](#panel.layout.base.ListLike.remove)(obj) | Removes an object from the layout. |
| [reverse](#panel.layout.base.ListLike.reverse)() | Reverses the objects in the layout. |

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

class panel.layout.base.ListPanel(\*objects: Any, **params: Any)
Bases: [ListLike](#panel.layout.base.ListLike),
[Panel](#panel.layout.base.Panel)

An abstract baseclass for Panel objects with list-like children.

Methods

|  |  |
|----|----|
| [clone](#panel.layout.base.ListPanel.clone)(\*objects, **params) | Makes a copy of the layout sharing the same parameters. |

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
> [title="panel.layout.base.ListLike"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](#panel.layout.base.ListLike):
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

class panel.layout.base.NamedListLike(\*items: list\[Any \| tuple\[str, Any\]\], **params: Any)
Bases: `Parameterized`

Methods

|  |  |
|----|----|
| [append](#panel.layout.base.NamedListLike.append)(pane) | Appends an object to the tabs. |
| [clear](#panel.layout.base.NamedListLike.clear)() | Clears the tabs. |
| [clone](#panel.layout.base.NamedListLike.clone)(\*objects, **params) | Makes a copy of the Tabs sharing the same parameters. |
| [extend](#panel.layout.base.NamedListLike.extend)(panes) | Extends the the tabs with a list. |
| [insert](#panel.layout.base.NamedListLike.insert)(index, pane) | Inserts an object in the tabs at the specified index. |
| [pop](#panel.layout.base.NamedListLike.pop)(\[index\]) | Pops an item from the tabs by index. |
| [remove](#panel.layout.base.NamedListLike.remove)(pane) | Removes an object from the tabs. |
| [reverse](#panel.layout.base.NamedListLike.reverse)() | Reverses the tabs. |

**Parameter Definitions**

------------------------------------------------------------------------

`objects`` ``=`` ``Children(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'panel.viewable.Viewable'>,`` ``label='Objects')`
The list of child objects that make up the layout.

append(pane: Any) → None
Appends an object to the tabs.

Parameters:
**obj (object): Panel component to add as a tab.**

clear() → None
Clears the tabs.

clone(\*objects: t.Any, **params: t.Any) → Self
Makes a copy of the Tabs sharing the same parameters.

Parameters:
**objects: Objects to add to the cloned Tabs object.**

**params: Keyword arguments override the parameters on the clone.**

Returns:
Cloned Tabs object

extend(panes: Iterable\[Any\]) → None
Extends the the tabs with a list.

Parameters:
**objects (list): List of panel components to add as tabs.**

insert(index: int, pane: Any) → None
Inserts an object in the tabs at the specified index.

Parameters:
**index (int): Index at which to insert the object.**

**object (object): Panel components to insert as tabs.**

pop(index: int = -1) → Viewable
Pops an item from the tabs by index.

Parameters:
**index (int): The index of the item to pop from the tabs.**

remove(pane: Viewable) → None
Removes an object from the tabs.

Parameters:
**obj (object): The object to remove from the tabs.**

reverse() → None
Reverses the tabs.

class panel.layout.base.NamedListPanel(\*items: list\[Any \| tuple\[str, Any\]\], **params: Any)
Bases:
[NamedListLike](#panel.layout.base.NamedListLike),
[Panel](#panel.layout.base.Panel)

Methods

|  |  |
|----|----|
| [clone](#panel.layout.base.NamedListPanel.clone)(\*objects, **params) | Makes a copy of the Tabs sharing the same parameters. |

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
> [title="panel.layout.base.NamedListLike"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.NamedListLike](#panel.layout.base.NamedListLike):
> objects
>
>

`active`` ``=`` ``Integer(bounds=(0,`` ``None),`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Active')`
Index of the currently displayed objects.

`scroll`` ``=`` ``Selector(default=False,`` ``label='Scroll',`` ``names={},`` ``objects=[False,`` ``True,`` ``'both-auto',`` ``'y-auto',`` ``'x-auto',`` ``'both',`` ``'x',`` ``'y'])`
Whether to add scrollbars if the content overflows the size of the
container. If “both-auto”, will only add scrollbars if the content
overflows in either directions. If “x-auto” or “y-auto”, will only add
scrollbars if the content overflows in the respective direction. If
“both”, will always add scrollbars. If “x” or “y”, will always add
scrollbars in the respective direction. If False, overflowing content
will be clipped. If True, will only add scrollbars in the direction of
the container, (e.g. Column: vertical, Row: horizontal).

clone(\*objects: t.Any, **params: t.Any) → Self
Makes a copy of the Tabs sharing the same parameters.

Parameters:
**objects: Objects to add to the cloned Tabs object.**

**params: Keyword arguments override the parameters on the clone.**

Returns:
Cloned Tabs object

class panel.layout.base.Panel(refs=None, **params)
Bases: [Reactive](panel.reactive.md#panel.reactive.Reactive),
[SizingModeMixin](#panel.layout.base.SizingModeMixin)

Abstract baseclass for a layout of Viewables.

Methods

|  |  |
|----|----|
| [get_root](#panel.layout.base.Panel.get_root)(\[doc, comm, preprocess\]) | Returns the root model and applies pre-processing hooks |
| [select](#panel.layout.base.Panel.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

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

class panel.layout.base.Row(\*objects: Any, **params: Any)
Bases: [ListPanel](#panel.layout.base.ListPanel)

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
> [title="panel.layout.base.ListLike"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](#panel.layout.base.ListLike):
> objects
>
> [title="panel.layout.base.ListPanel"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListPanel](#panel.layout.base.ListPanel):
> scroll
>
>

class panel.layout.base.SizingModeMixin
Bases: `object`

Mixin class to add support for computing sizing modes from the children
based on the direction the layout flows in.

class panel.layout.base.WidgetBox(\*objects: Any, **params: Any)
Bases: [ListPanel](#panel.layout.base.ListPanel)

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
> [title="panel.layout.base.ListLike"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](#panel.layout.base.ListLike):
> objects
>
> [title="panel.layout.base.ListPanel"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListPanel](#panel.layout.base.ListPanel):
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
