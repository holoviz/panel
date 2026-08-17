# panel.reactive module

Declares Syncable and Reactive classes which provides baseclasses for
Panel components which sync their state with one or more bokeh models
rendered on the frontend.

class panel.reactive.Reactive(refs=None, **params)
Bases: `Syncable`,
[Viewable](panel.viewable.md#panel.viewable.Viewable)

Reactive is a Viewable object that also supports syncing between the
objects parameters and the underlying bokeh model either via the defined
pyviz_comms.Comm type or using bokeh server.

In addition it defines various methods which make it easy to link the
parameters to other objects.

Methods

|  |  |
|----|----|
| [controls](#panel.reactive.Reactive.controls)(\[parameters, jslink\]) | Creates a set of widgets which allow manipulating the parameters on this instance. |
| [jscallback](#panel.reactive.Reactive.jscallback)(\[args\]) | Allows defining a JS callback to be triggered when a property changes on the source object. |
| [jslink](#panel.reactive.Reactive.jslink)(target\[, code, args, bidirectional\]) | Links properties on the this Reactive object to those on the target Reactive object in JS code. |
| [link](#panel.reactive.Reactive.link)(target\[, callbacks, bidirectional\]) | Links the parameters on this Reactive object to attributes on the target Parameterized object. |

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

controls(parameters: list\[str\] = \[\], jslink: bool = True, **kwargs) → BasePanel
Creates a set of widgets which allow manipulating the parameters on this
instance. By default all parameters which support linking are exposed,
but an explicit list of parameters can be provided.

Parameters:
**parameters: list(str)**
An explicit list of parameters to return controls for.

**jslink: bool**
Whether to use jslinks instead of Python based links. This does not
allow using all types of parameters.

**kwargs: dict**
Additional kwargs to pass to the Param pane(s) used to generate the
controls widgets.

Returns:
A layout of the controls

jscallback(args: dict\[str, t.Any\] = {}, **callbacks: str) → Callback
Allows defining a JS callback to be triggered when a property changes on
the source object. The keyword arguments define the properties that
trigger a callback and the JS code that gets executed.

Parameters:
**args: dict**
A mapping of objects to make available to the JS callback

**callbacks: dict**
A mapping between properties on the source model and the code to execute
when that property changes

Returns:
callback: Callback
The Callback which can be used to disable the callback.

jslink(target: JSLinkTarget, code: dict\[str, str\] \| None = None, args: dict \| None = None, bidirectional: bool = False, **links: str) → Link
Links properties on the this Reactive object to those on the target
Reactive object in JS code.

Supports two modes, either specify a mapping between the source and
target model properties as keywords or provide a dictionary of JS code
snippets which maps from the source parameter to a JS code snippet which
is executed when the property changes.

Parameters:
**target: panel.viewable.Viewable \| bokeh.model.Model \| holoviews.core.dimension.Dimensioned**
The target to link the value to.

**code: dict**
Custom code which will be executed when the widget value changes.

**args: dict**
A mapping of objects to make available to the JS callback

**bidirectional: boolean**
Whether to link source and target bi-directionally

**links: dict**
A mapping between properties on the source model and the target model
property to link it to.

Returns:
link: GenericLink
The GenericLink which can be used unlink the widget and the target
model.

link(target: param.Parameterized, callbacks: dict\[str, str \| Callable\] \| None = None, bidirectional: bool = False, **links: str) → Watcher
Links the parameters on this Reactive object to attributes on the target
Parameterized object.

Supports two modes, either specify a mapping between the source and
target object parameters as keywords or provide a dictionary of
callbacks which maps from the source parameter to a callback which is
triggered when the parameter changes.

Parameters:
**target: param.Parameterized**
The target object of the link.

**callbacks: dict \| None**
Maps from a parameter in the source object to a callback.

**bidirectional: bool**
Whether to link source and target bi-directionally

**links: dict**
Maps between parameters on this object to the parameters on the supplied
object.

class panel.reactive.ReactiveData(\*, selection, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: `SyncableData`

An extension of SyncableData which bi-directionally syncs a data
parameter between frontend and backend using a ColumnDataSource.

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
> `panel.reactive.SyncableData`: selection
>
>

class panel.reactive.ReactiveHTML(\*, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: `ReactiveCustomBase`

The ReactiveHTML class enables you to create custom Panel components
using HTML, CSS and/ or Javascript and without the complexities of
Javascript build tools.

A ReactiveHTML subclass provides bi-directional syncing of its
parameters with arbitrary HTML elements, attributes and properties. The
key part of the subclass is the \_template variable. This is the HTML
template that gets rendered and declares how to link parameters on the
subclass to HTML.

\>\>\>
import
panel
as
pn \>\>\>
import
param \>\>\>
class
CustomComponent(pn.reactive.ReactiveHTML):
... ...
index =
param.Integer(default=0)
... ...
\_template =
'\{index}"
onclick="\${\_img_click}"\>\</img\>'
... ...
def
\_img_click(self,
event):
...
self.index
+= 1
\>\>\>
CustomComponent(width=500,
height=200).servable()

## HTML templates

A ReactiveHTML component is declared by providing an HTML template on
the \_template attribute on the class. Parameters are synced by
inserting them as template variables of the form \${parameter_name},
e.g.:

>
>
> \\${parameter_2}\</div\>
>
>

will interpolate the parameter1 parameter on the class. In addition to
providing attributes we can also provide children to an HTML tag. By
default any parameter referenced as a child will be treated as a Panel
components to be rendered into the containing HTML. This makes it
possible to use ReactiveHTML to lay out other components.

## Children

As mentioned above parameters may be referenced as children of a DOM
node and will, by default, be treated as Panel components to insert on
the DOM node. However by declaring a \_child_config we can control how
the DOM nodes are treated. The \_child_config is indexed by parameter
name and may declare one of three rendering modes:

>
>
> - model (default): Create child and render child as a Panel component
>   into it.
>
> - literal: Create child and set child as its innerHTML.
>
> - template: Set child as innerHTML of the container.
>
>

If the type is ‘template’ the parameter will be inserted as is and the
DOM node’s innerHTML will be synced with the child parameter.

## DOM Events

In certain cases it is necessary to explicitly declare event listeners
on the DOM node to ensure that changes in their properties are synced
when an event is fired. To make this possible the HTML element in
question must be given a unique id, e.g.:

>
>
> \<input id=”input_el”\>\</input\>
>
>

Now we can use this name to declare set of \_dom_events to subscribe to.
The following will subscribe to change DOM events on the input element:

>
>
> {‘input_el’: \[‘change’\]}
>
>

Once subscribed the class may also define a method following the
\_{node}\_{event} naming convention which will fire when the DOM event
triggers, e.g. we could define a \_input_el_change method. Any such
callback will be given a DOMEvent object as the first and only argument.
The DOMEvent contains information about the event on the .data attribute
and declares the type of event on the .type attribute.

## Inline callbacks

Instead of declaring explicit DOM events Python callbacks can also be
declared inline, e.g.:

>
>
> \<input id=”input_el” onchange=”\${\_input_change}”\>\</input\>
>
>

will look for an \_input_change method on the ReactiveHTML component and
call it when the event is fired.

Additionally we can invoke pure JS scripts defined on the class, e.g.:

>
>
> \<input id=”input_el” onchange=”\${script(‘some_script’)}”\>\</input\>
>
>

This will invoke the following script if it is defined on the class:

>
>
> >
> >
> > \_scripts = {
> > ‘some_script’: ‘console.log(model, data, input_el, view)’
> >
> >
>
> }
>
>

## Scripts

In addition to declaring callbacks in Python it is also possible to
declare Javascript callbacks to execute when any synced attribute
changes. Let us say we have declared an input element with a synced
value parameter:

>
>
> \<input id=”input_el” value=”\${value}”\>\</input\>
>
>

We can now declare a set of \_scripts, which will fire whenever the
value updates:

>
>
> >
> >
> > \_scripts = {
> > ‘value’: ‘console.log(model, data, input_el)’
> >
> >
>
> }
>
>

The Javascript is provided multiple objects in its namespace including:

>
>
> - dataThe data model holds the current values of the synced
>   parameters, e.g. data.value will reflect the current value of the
>   input_el node.
>
> - model: The ReactiveHTML model which holds layout information
>   and information about the children and events.
>
> - state: An empty state dictionary which scripts can use to
>   store state for the lifetime of the view.
>
> - view: The Bokeh View class responsible for rendering the
>   component. This provides access to method like invalidate_layout and
>   run_script which allows invoking other scripts.
>
> - \<node\>: All named DOM nodes in the HTML template, e.g. the
>   input_el node in the example above.
>
>

Methods

|  |  |
|----|----|
| [on_event](#panel.reactive.ReactiveHTML.on_event)(node, event, callback) | Registers a callback to be executed when the specified DOM event is triggered on the named node. |

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

on_event(node: str, event: str, callback: Callable) → None
Registers a callback to be executed when the specified DOM event is
triggered on the named node. Note that the named node must be declared
in the HTML. To create a named node you must give it an id of the form
id=”name”, where name will be the node identifier.

Parameters:
**node: str**
Named node in the HTML identifiable via id of the form id=”name”.

**event: str**
Name of the DOM event to add an event listener to.

**callback: callable**
A callable which will be given the DOMEvent object.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
