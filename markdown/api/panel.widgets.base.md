# panel.widgets.base module

Defines the Widget base class which provides bi-directional
communication between the rendered dashboard and the Widget parameters.

class panel.widgets.base.CompositeWidget(\*, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [Widget](#panel.widgets.base.Widget)

A baseclass for widgets which are made up of two or more other widgets

Methods

|  |  |
|----|----|
| [select](#panel.widgets.base.CompositeWidget.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [title="panel.widgets.base.WidgetBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](#panel.widgets.base.WidgetBase):
> label, value
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [title="panel.widgets.base.Widget"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](#panel.widgets.base.Widget):
> height, margin, width, disabled
>
>

select(selector: type \| Callable\[\[Viewable\], bool\] \| None = None) → list\[Viewable\]
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

class panel.widgets.base.Widget(**params: Any)
Bases: [Reactive](panel.reactive.md#panel.reactive.Reactive),
[WidgetBase](#panel.widgets.base.WidgetBase)

Widgets allow syncing changes in bokeh widget models with the parameters
on the Widget instance.

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [title="panel.widgets.base.WidgetBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](#panel.widgets.base.WidgetBase):
> label, value
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
>

`height`` ``=`` ``Integer(allow_None=True,`` ``allow_refs=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
The height of the component (in pixels). This can be either fixed or
preferred height, depending on height sizing policy.

`margin`` ``=`` ``Margin(allow_None=True,`` ``allow_refs=True,`` ``default=(5,`` ``10),`` ``label='Margin')`
Allows to create additional space around the component. May be specified
as a two-tuple of the form (vertical, horizontal) or a four-tuple (top,
right, bottom, left).

`width`` ``=`` ``Integer(allow_None=True,`` ``allow_refs=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The width of the component (in pixels). This can be either fixed or
preferred width, depending on width sizing policy.

`disabled`` ``=`` ``Boolean(allow_refs=True,`` ``default=False,`` ``label='Disabled')`
Whether the widget is disabled.

class panel.widgets.base.WidgetBase(**params: Any)
Bases: `Parameterized`

WidgetBase provides an abstract baseclass for widget components which
can be used to implement a custom widget-like type without implementing
the methods associated with a Reactive Panel component, e.g. it may be
used as a mix-in to a PyComponent or JSComponent.

Attributes:
**rx**

Methods

|  |  |
|----|----|
| [from_param](#panel.widgets.base.WidgetBase.from_param)(parameter, **params) | Construct a widget from a Parameter and link the two bi-directionally. |
| [from_values](#panel.widgets.base.WidgetBase.from_values)(values, **params) | Creates an instance of this Widget where the parameters are inferred from the data. |

**Parameter Definitions**

------------------------------------------------------------------------

`label`` ``=`` ``String(allow_refs=True,`` ``default='',`` ``label='Label')`
The label for the widget.

`value`` ``=`` ``Parameter(allow_None=True,`` ``label='Value')`
The widget value which the widget type resolves to when used as a
reactive param reference.

classmethod from_param(parameter: param.Parameter, **params) → T
Construct a widget from a Parameter and link the two bi-directionally.

Parameters:
**parameter: param.Parameter**
A parameter to create the widget from.

Returns:
Widget instance linked to the supplied parameter

classmethod from_values(values, **params)
Creates an instance of this Widget where the parameters are inferred
from the data.

Parameters:
**values: Iterable**
The values to infer the parameters from.

**params: dict**
Additional parameters to pass to the widget.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
