# panel.custom module

class panel.custom.AnyWidgetComponent(\*, use_shadow_dom, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: [ReactComponent](#panel.custom.ReactComponent)

The AnyWidgetComponent allows you to create custom Panel components in
the style of an AnyWidget component. Specifically this component type
creates shims that make it possible to reuse AnyWidget ESM code as is,
without having to adapt the callbacks to use Bokeh APIs.

Reference: [https://panel.holoviz.org/reference/custom_components/AnyWidgetComponent.html](https://panel.holoviz.org/reference/custom_components/AnyWidgetComponent.html)

Example:

import
param
import
panel
as
pn
pn.extension()
class
CounterWidget(pn.custom.AnyWidgetComponent):
\_esm =
"""  function render({ model,
el }) {  let count = () =\>
model.get("value");  let btn =
document.createElement("button");  btn.innerHTML
= \`count is \${count()}\`;
btn.addEventListener("click", () =\> {
model.set("value", count() + 1);
model.save_changes();  });
 model.on("change:value", () =\> {
 btn.innerHTML = \`count is \${count()}\`;
 });
el.appendChild(btn);  }
export default { render };  """
value =
param.Integer()
CounterWidget().servable()

Methods

|  |  |
|----|----|
| [send](#panel.custom.AnyWidgetComponent.send)(msg) | Sends a custom event containing the provided message to the frontend. |

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
> [title="panel.custom.ReactComponent"> class="sourceCode python xref py py-class docutils literal notranslate">panel.custom.ReactComponent](#panel.custom.ReactComponent):
> use_shadow_dom
>
>

send(msg: dict)
Sends a custom event containing the provided message to the frontend.

Parameters:
**msg: dict**

class panel.custom.JSComponent(\*, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: [ReactiveESM](#panel.custom.ReactiveESM)

The JSComponent allows you to create custom Panel components using
Javascript and CSS without the complexities of Javascript build tools.

A JSComponent subclass provides bi-directional syncing of its parameters
with arbitrary HTML elements, attributes and properties. The key part of
the subclass is the \_esm variable. Use this to define a render function
as shown in the example below.

Reference: [https://panel.holoviz.org/reference/custom_components/JSComponent.html](https://panel.holoviz.org/reference/custom_components/JSComponent.html)

Example:

import
panel
as
pn
import
param
pn.extension()
class
CounterButton(pn.custom.JSComponent):
value =
param.Integer()
\_esm =
"""  export function render({
model }) {  let btn =
document.createElement("button");  btn.innerHTML
= \`count is
\${model.value}\`;
 btn.addEventListener("click", () =\> {
 model.value += 1  });
 model.on('value', () =\> {
btn.innerHTML = \`count is
\${model.value}\`;
 })  return btn
 }  """
CounterButton().servable()

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

class panel.custom.PyComponent(\*, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: [Viewable](panel.viewable.md#panel.viewable.Viewable),
[Layoutable](panel.viewable.md#panel.viewable.Layoutable)

The PyComponent combines the convenience of Viewer components that allow
creating custom components by declaring a \_\_panel\_\_ method with the
ability of controlling layout and styling related parameters directly on
the class. Internally the PyComponent will forward layout parameters to
the underlying object, which is created lazily on render.

Reference: [https://panel.holoviz.org/reference/custom_components/PyComponent.html](https://panel.holoviz.org/reference/custom_components/PyComponent.html)

Example:

import
panel
as
pn
import
param
pn.extension()
class
CounterButton(pn.custom.PyComponent,
pn.widgets.WidgetBase):
value =
param.Integer(default=0)
def
\_\_panel\_\_(self):
return
pn.widgets.Button(
name=self.\_button_name,
on_click=self.\_on_click
) def
\_on_click(self,
event):
self.value
+= 1
@param.depends("value")
def
\_button_name(self):
return
f"count is
{self.value}"
CounterButton().servable()

Methods

|  |  |
|----|----|
| [select](#panel.custom.PyComponent.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

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

select(selector: type \| Callable\[\[Viewable\], bool\] \| None = None) → list\[Viewable\]
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

class panel.custom.ReactComponent(\*, use_shadow_dom, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: [ReactiveESM](#panel.custom.ReactiveESM)

The ReactComponent allows you to create custom Panel components using
React without the complexities of Javascript build tools.

A ReactComponent subclass provides bi-directional syncing of its
parameters with arbitrary HTML elements, attributes and properties. The
key part of the subclass is the \_esm variable. Use this to define a
render function as shown in the example below.

Reference: [https://panel.holoviz.org/reference/custom_components/ReactComponent.html](https://panel.holoviz.org/reference/custom_components/ReactComponent.html)

Example:

import
panel
as
pn
import
param
class
CounterButton(pn.custom.ReactComponent):
value =
param.Integer()
\_esm =
"""  export function
render({model}) {
 const \[value, setValue\] =
model.useState("value");  return (
 \<button onClick={e =\> setValue(value+1)}\>
 count is {value}
 \</button\>  )
 }  """
CounterButton().servable()

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

`use_shadow_dom`` ``=`` ``Boolean(constant=True,`` ``default=True,`` ``label='Use`` ``shadow`` ``dom')`
Whether to render component into a shadow root. This may optionally be
disabled but will only take effect if the parent is also a React
component. If disabled the component will be rendered into the parent’s
React DOM tree.

class panel.custom.ReactiveESM(\*, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: `ReactiveCustomBase`

The ReactiveESM classes allow you to create custom Panel components
using HTML, CSS and/ or Javascript and without the complexities of
Javascript build tools.

A ReactiveESM subclass provides bi-directional syncing of its parameters
with arbitrary HTML elements, attributes and properties. The key part of
the subclass is the \_esm variable. Use this to define a render function
as shown in the example below.

Example:

import
panel
as
pn
import
param
pn.extension()
class
CounterButton(pn.custom.ReactiveESM):
value =
param.Integer()
\_esm =
"""  export function render({
model }) {  let btn =
document.createElement("button");  btn.innerHTML
= \`count is
\${model.value}\`;
 btn.addEventListener("click", () =\> {
 model.value += 1  });
 model.on('value', () =\> {
btn.innerHTML = \`count is
\${model.value}\`;
 })  return btn
 }  """
CounterButton().servable()

Methods

|  |  |
|----|----|
| [on_event](#panel.custom.ReactiveESM.on_event)(event, callback) | Registers a callback to be executed when the specified DOM event is triggered. |
| [on_msg](#panel.custom.ReactiveESM.on_msg)(callback) | Registers a callback to be executed when a message event containing arbitrary data is received. |
| [select](#panel.custom.ReactiveESM.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

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

on_event(event: str, callback: Callable) → None
Registers a callback to be executed when the specified DOM event is
triggered.

Parameters:
**event: str**
Name of the DOM event to add an event listener to.

**callback: callable**
A callable which will be given the DOMEvent object.

on_msg(callback: Callable) → None
Registers a callback to be executed when a message event containing
arbitrary data is received.

Parameters:
**event: str**
Name of the DOM event to add an event listener to.

**callback: callable**
A callable which will be given the msg data.

select(selector: type \| Callable\[\[Viewable\], bool\] \| None = None) → list\[Viewable\]
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

class panel.custom.ReactiveESMMetaclass(name: str, bases: tuple\[type, ...\], dict\_: Mapping\[str, t.Any\])
Bases: `ReactiveMetaBase`

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
