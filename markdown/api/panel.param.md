# panel.param module

Defines the Param pane which converts Parameterized classes into a set
of widgets.

class panel.param.Param(object=None, **params)
Bases: [Pane](panel.pane.base.md#panel.pane.base.Pane)

Param panes render a Parameterized class into a set of interactive
widgets that are dynamically linked to the parameter values of the
class.

Reference:
[https://panel.holoviz.org/reference/panes/Param.html](https://panel.holoviz.org/reference/panes/Param.html)

Example:

\>\>\>
import
param \>\>\>
import
panel
as
pn \>\>\>
pn.extension()

\>\>\>
class
App(param.Parameterized):
\>\>\>  some_text
=
param.String(default="Hello")
\>\>\>  some_float
=
param.Number(default=1,
bounds=(0,
10),
step=0.1)
\>\>\>  some_boolean
=
param.Boolean(default=True)

\>\>\> app
=
App()

\>\>\>
pn.Param(app,
parameters=\["some_text",
"some_float"\],
show_name=False).servable()

Attributes:
**widgets**

Methods

|  |  |
|----|----|
| [applies](#panel.param.Param.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |
| [get_root](#panel.param.Param.get_root)(\[doc, comm, preprocess\]) | Returns the root model and applies pre-processing hooks |
| [select](#panel.param.Param.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |
| [widget](#panel.param.Param.widget)(p_name\[, parameterized, widget_spec\]) | Get widget for param_name |

|                 |     |
|-----------------|-----|
| **widget_type** |     |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin
>
>

`height`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
Height of widgetbox the parameter widgets are displayed in.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of widgetbox the parameter widgets are displayed in.

`default_layout`` ``=`` ``ClassSelector(class_=(<class`` ``'panel.layout.base.ListLike'>,`` ``<class`` ``'panel.layout.base.NamedListLike'>),`` ``default=<class`` ``'panel.layout.base.Column'>,`` ``label='Default`` ``layout')`
Defines the layout the model(s) returned by the pane will be placed in.

`object`` ``=`` ``Parameter(allow_None=True,`` ``label='Object')`
The object being wrapped, which will be converted to a Bokeh model.

`display_threshold`` ``=`` ``Number(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Display`` ``threshold')`
Parameters with precedence below this value are not displayed.

`default_precedence`` ``=`` ``Number(default=1e-08,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Default`` ``precedence')`
Precedence value to use for parameters with no declared precedence. By
default, zero predecence is available for forcing some parameters to the
top of the list, and other values above the default_precedence values
can be used to sort or group parameters arbitrarily.

`expand`` ``=`` ``Boolean(default=False,`` ``label='Expand')`
Whether parameterized subobjects are expanded or collapsed on
instantiation.

`expand_button`` ``=`` ``Boolean(allow_None=True,`` ``label='Expand`` ``button')`
Whether to add buttons to expand and collapse sub-objects.

`expand_layout`` ``=`` ``Parameter(default=<class`` ``'panel.layout.base.Column'>,`` ``label='Expand`` ``layout')`
Layout to expand sub-objects into.

`hide_constant`` ``=`` ``Boolean(default=False,`` ``label='Hide`` ``constant')`
Whether to hide widgets of constant parameters.

`initializer`` ``=`` ``Callable(allow_None=True,`` ``label='Initializer')`
User-supplied function that will be called on initialization, usually to
update the default Parameter values of the underlying parameterized
object.

`parameters`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'str'>,`` ``label='Parameters')`
If set this serves as a allowlist of parameters to display on the
supplied Parameterized object.

`show_labels`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``labels')`
Whether to show labels for each widget

`show_name`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``name')`
Whether to show the parameterized object’s name

`sort`` ``=`` ``ClassSelector(class_=(<class`` ``'bool'>,`` ``<class`` ``'collections.abc.Callable'>),`` ``default=False,`` ``label='Sort')`
If True the widgets will be sorted alphabetically by label. If a
callable is provided it will be used to sort the Parameters, for example
lambda x: x\[1\].label\[::-1\] will sort by the reversed label.

`widgets`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Widgets')`
Dictionary of widget overrides, mapping from parameter name to widget
class.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

default_layout
alias of [Column](panel.layout.base.md#panel.layout.base.Column)

expand_layout
alias of [Column](panel.layout.base.md#panel.layout.base.Column)

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

select(selector=None)
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

widget(p_name: str, parameterized: Parameterized \| None = None, widget_spec: type\[WidgetBase\] \| dict \| None = None)
Get widget for param_name

class panel.param.ParamFunction(object=None, **params)
Bases:
[ParamRef](panel.pane.md#panel.pane.ParamRef)

ParamFunction panes wrap functions decorated with the param.depends
decorator and rerenders the output when any of the function’s
dependencies change. This allows building reactive components into a
Panel which depend on other parameters, e.g. tying the value of a widget
to some other output.

Methods

|  |  |
|----|----|
| [applies](#panel.param.ParamFunction.applies)(object, **kwargs) | Returns boolean or float indicating whether the Pane can render the object. |

|          |     |
|----------|-----|
| **eval** |     |

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
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout
>
> [class="reference internal" title="panel.pane.base.ReplacementPane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.ReplacementPane](panel.pane.base.md#panel.pane.base.ReplacementPane):
> object, inplace, \_pane
>
> [title="panel.param.ParamRef"> class="sourceCode python xref py py-class docutils literal notranslate">panel.param.ParamRef](panel.pane.md#panel.pane.ParamRef):
> defer_load, generator_mode, lazy, loading_indicator
>
>

classmethod applies(object: Any, **kwargs) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.param.ParamMethod(object=None, **params)
Bases:
[ParamRef](panel.pane.md#panel.pane.ParamRef)

ParamMethod panes wrap methods on parameterized classes and rerenders
the plot when any of the method’s parameters change. By default
ParamMethod will watch all parameters on the class owning the method or
can be restricted to certain parameters by annotating the method using
the param.depends decorator. The method may return any object which
itself can be rendered as a Pane.

Methods

|  |  |
|----|----|
| [applies](#panel.param.ParamMethod.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

|          |     |
|----------|-----|
| **eval** |     |

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
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout
>
> [class="reference internal" title="panel.pane.base.ReplacementPane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.ReplacementPane](panel.pane.base.md#panel.pane.base.ReplacementPane):
> object, inplace, \_pane
>
> [title="panel.param.ParamRef"> class="sourceCode python xref py py-class docutils literal notranslate">panel.param.ParamRef](panel.pane.md#panel.pane.ParamRef):
> defer_load, generator_mode, lazy, loading_indicator
>
>

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.param.ReactiveExpr(object=None, **params)
Bases: [Pane](panel.pane.base.md#panel.pane.base.Pane)

ReactiveExpr generates a UI for param.rx objects by rendering the
widgets and outputs.

Attributes:
**widgets**

Methods

|  |  |
|----|----|
| [applies](#panel.param.ReactiveExpr.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

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
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout
>
>

`object`` ``=`` ``Parameter(allow_None=True,`` ``label='Object')`
The object being wrapped, which will be converted to a Bokeh model.

`center`` ``=`` ``Boolean(default=False,`` ``label='Center')`
Whether to center the output.

`show_widgets`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``widgets')`
Whether to display the widget inputs.

`widget_layout`` ``=`` ``ClassSelector(class_=<class`` ``'panel.layout.base.ListLike'>,`` ``constant=True,`` ``default=<class`` ``'panel.layout.base.WidgetBox'>,`` ``label='Widget`` ``layout')`
The layout object to display the widgets in.

`widget_location`` ``=`` ``Selector(default='left_top',`` ``label='Widget`` ``location',`` ``names={},`` ``objects=['left',`` ``'right',`` ``'top',`` ``'bottom',`` ``'top_left',`` ``'top_right',`` ``'bottom_left',`` ``'bottom_right',`` ``'left_top',`` ``'right_top',`` ``'right_bottom'])`
The location of the widgets relative to the output of the reactive
expression.

classmethod applies(object)
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

widget_layout
alias of [WidgetBox](panel.layout.base.md#panel.layout.base.WidgetBox)

panel.param.set_values(\*parameterizeds, **param_values)
Temporarily sets parameter values to the specified values on all
supplied Parameterized objects.

Parameters:
**parameterizeds: tuple(param.Parameterized)**
Any number of parameterized objects.

**param_values: dict**
A dictionary of parameter names and temporary values.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
