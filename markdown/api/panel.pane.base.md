# panel.pane.base module

Defines base classes for Pane components which allow wrapping a Python
object transforming it into a Bokeh model that can be rendered.

class panel.pane.base.ModelPane(object=None, **params)
Bases: [Pane](#panel.pane.base.Pane)

ModelPane provides a baseclass that allows quickly wrapping a Bokeh
model and translating parameters defined on the class with properties
defined on the model.

In simple cases subclasses only have to define the Bokeh model to render
to and the \_transform_object method which transforms the Python object
being wrapped into properties that the bokeh.model.Model can consume.

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [title="panel.pane.base.PaneBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](#panel.pane.base.PaneBase):
> margin, default_layout, object
>
>

class panel.pane.base.Pane(object=None, **params)
Bases: [PaneBase](#panel.pane.base.PaneBase),
[Reactive](panel.reactive.md#panel.reactive.Reactive)

Pane is the abstract baseclass for all atomic displayable units in the
Panel library.

Panes defines an extensible interface for wrapping arbitrary objects and
transforming them into renderable components.

Panes are reactive in the sense that when the object they are wrapping
is replaced or modified the UI will reflect the updated object.

Methods

|  |  |
|----|----|
| [clone](#panel.pane.base.Pane.clone)(\[object\]) | Makes a copy of the Pane sharing the same parameters. |
| [get_root](#panel.pane.base.Pane.get_root)(\[doc, comm, preprocess\]) | Returns the root model and applies pre-processing hooks |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [title="panel.pane.base.PaneBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](#panel.pane.base.PaneBase):
> margin, default_layout, object
>
>

clone(object: Any \| None = None, **params) → T
Makes a copy of the Pane sharing the same parameters.

Parameters:
**object: Optional new object to render**

**params: Keyword arguments override the parameters on the clone.**

Returns:
Cloned Pane object

get_root(doc: Document \| None = None, comm: Comm \| None = None, preprocess: bool = True) → Model
Returns the root model and applies pre-processing hooks

Parameters:
**doc: bokeh.document.Document**
Optional Bokeh document the bokeh model will be attached to.

**comm: pyviz_comms.Comm**
Optional pyviz_comms when working in notebook

**preprocess: bool (default=True)**
Whether to run preprocessing hooks

Returns:
Returns the bokeh model corresponding to this panel object

class panel.pane.base.PaneBase(object=None, **params)
Bases: [Layoutable](panel.viewable.md#panel.viewable.Layoutable)

PaneBase represents an abstract baseclass which can be used as a mix-in
class to define a component that mirrors the Pane API. This means that
this component will participate in the automatic resolution of the
appropriate pane type when Panel is asked to render an object of unknown
type.

The resolution of the appropriate pane type can be implemented using the
`applies` method and the
`priority` class attribute. The applies method
should either return a boolean value indicating whether the pane can
render the supplied object. If it can the priority determines which of
the panes that apply will be selected. If the priority is None then the
`applies` method must return a priority value.

Methods

|  |  |
|----|----|
| [applies](#panel.pane.base.PaneBase.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |
| [get_pane_type](#panel.pane.base.PaneBase.get_pane_type)() | Returns the applicable Pane type given an object by resolving the precedence of all types whose applies method declares that the object is supported. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
>

`margin`` ``=`` ``Margin(allow_None=True,`` ``default=(5,`` ``10),`` ``label='Margin')`
Allows to create additional space around the component. May be specified
as a two-tuple of the form (vertical, horizontal) or a four-tuple (top,
right, bottom, left).

`default_layout`` ``=`` ``ClassSelector(class_=(<class`` ``'panel.layout.base.ListLike'>,`` ``<class`` ``'panel.layout.base.NamedListLike'>),`` ``default=<class`` ``'panel.layout.base.Row'>,`` ``label='Default`` ``layout')`
Defines the layout the model(s) returned by the pane will be placed in.

`object`` ``=`` ``Parameter(allow_None=True,`` ``allow_refs=True,`` ``label='Object')`
The object being wrapped, which will be converted to a Bokeh model.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

default_layout
alias of [Row](panel.layout.base.md#panel.layout.base.Row)

classmethod get_pane_type(obj: Viewable, **kwargs: Any) → type\[Viewable\]\
classmethod get_pane_type(obj: Any, **kwargs: Any) → type\[PaneBase\]
Returns the applicable Pane type given an object by resolving the
precedence of all types whose applies method declares that the object is
supported.

Parameters:
**obj (object): The object type to return a Pane type for**

Returns:
The applicable Pane type with the highest precedence.

class panel.pane.base.ReplacementPane(object: Any = None, **params)
Bases: [Pane](#panel.pane.base.Pane)

ReplacementPane provides a baseclass for dynamic components that may
have to dynamically update or switch out their contents, e.g. a dynamic
callback that may return different objects to be rendered.

When the pane updates it either entirely replaces the underlying
bokeh.model.Model, by creating an internal layout to replace the
children on, or updates the existing model in place.

Methods

|  |  |
|----|----|
| [select](#panel.pane.base.ReplacementPane.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [title="panel.pane.base.PaneBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](#panel.pane.base.PaneBase):
> margin, default_layout
>
>

`object`` ``=`` ``Parameter(allow_None=True,`` ``label='Object')`
The object being wrapped, which will be converted to a Bokeh model.

`inplace`` ``=`` ``Boolean(default=False,`` ``label='Inplace')`
Whether to update the object inplace.

`_pane`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.viewable.Viewable'>,`` ``label='`` ``pane')`

select(selector: type \| Callable \| None = None) → list\[Viewable\]
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: (type \| callable \| None)**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

exception panel.pane.base.RerenderError(\*args, layout=None, **kwargs)
Bases: `RuntimeError`

Error raised when a pane requests re-rendering during initial render.

panel.pane.base.panel(obj: Any, **kwargs) → Viewable \| ServableMixin
Creates a displayable Panel object given any valid Python object.

The appropriate Pane to render a specific object is determined by
iterating over all defined Pane types and querying it’s .applies method
for a priority value.

Any keyword arguments are passed down to the applicable Pane.

Setting loading_indicator=True will display a loading indicator while
the function is being evaluated.

To lazily render components when the application loads, you may also
provide a Python function, with or without bound parameter dependencies
and set defer_load=True.

Reference: [https://panel.holoviz.org/explanation/components/components_overview.html#panes](https://panel.holoviz.org/explanation/components/components_overview.html#panes)

\>\>\>
pn.panel(some_python_object,
width=500)

Parameters:
**obj: object**
Any object to be turned into a Panel

****kwargs: dict**
Any keyword arguments to be passed to the applicable Pane

Returns:
layout: Viewable
A Viewable representation of the input object

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
