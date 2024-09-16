# Building `ReactiveHTML` Components

When you're working on custom applications and dashboards, there are times when you need to **extend Panel's capabilities to meet unique requirements**.

This page will walk you through using the `ReactiveHTML` class to craft custom components without the need for complex JavaScript build tools. You'll be able to leverage basic HTML, CSS, and JavaScript to tailor your components to your specific needs.

## Why Use `ReactiveHTML`?

`ReactiveHTML` empowers you to design and build custom components that seamlessly integrate with your Panel applications. These components can enhance your applications' interactivity and functionality, all while keeping the development process straightforward and free from the complexities of JavaScript build tools.

## A Basic Example

A *`ReactiveHTML` component* is essentially a class that you create by inheriting from the `ReactiveHTML` class. Within this custom class, you are required to define the `_template` attribute using HTML, which serves as the *design blueprint* for your custom component. You can use Javascript *template variables* `${...}` as well as Python [Jinja2](https://jinja.palletsprojects.com) syntax to make the template *dynamic*.

Here is a basic `Slideshow` component

```{pyodide}
import param
import panel as pn
from panel.reactive import ReactiveHTML

pn.extension()

class Slideshow(ReactiveHTML):

    index = param.Integer(default=0)

    _template = '<img id="slideshow_el" src="https://picsum.photos/800/300?image=${index}" onclick="${_img_click}"></img>'

    def _img_click(self, event):
        self.index += 1

Slideshow(width=800, height=300)
```

## Alternatives

If you're looking for **simpler** alternatives to `ReactiveHTML`, Panel provides a `Viewer` class that allows you to combine existing Panel components using Python only. This approach is a great choice if you want to quickly create custom components without the need for writing HTML, CSS, or JavaScript. You can learn more about creating custom `Viewer` components in our guide [How-to > Combine Existing Components](../../how_to/custom_components/custom_viewer).

On the other hand, if you're looking for a **more advanced** approach that gives you full control over the design and functionality of your custom components, you can use *Bokeh Models*. With Bokeh Models, you can leverage the full power of your IDE, TypeScript and modern JavaScript development tools to build advanced and performant custom components. Many of the built-in Panel components are built using this approach. It provides flexibility and extensibility, allowing you to create highly customized and interactive components tailored to your specific needs. We expect detailed documentation on writing custom Bokeh models will be added to the documentation in the future.

## The Name

`ReactiveHTML` is named for its ability to enable reactive programming in HTML. Unlike the static HTML content that the [`HTML`](../../reference/panes/HTML) pane displays, `ReactiveHTML` components can update their view dynamically in response to changes in parameter values and other events.

We could also have called the `ReactiveHTML` class for example `BaseComponent`, `HTMLComponent`, `SimpleComponent` or `AnyComponent` to give you the right associations.

It's worth noting that the name `ReactiveHTML` is not related to the JavaScript framework [React](https://react.dev/), although you can still use React with `ReactiveHTML` components.

## How-to Guides

To see `ReactiveHTML` in action and discover how to create your custom components, check out our detailed guide: [How-to > Create Custom Components with ReactiveHTML](../../how_to/custom_components/index.md#reactivehtml-components). It's packed with practical examples to help you get started quickly.

## API Guide

You can find it here [API > ReactiveHTML](../../api/panel.reactive.rst#panel.reactive.ReactiveHTML).

## Class Attributes

When creating a `ReactiveHTML` component, there are several class attributes that you can declare to customize its behavior.

The required attribute is:

- `_template` (str): This defines the blueprint for how your custom component should look and behave. It is defined using HTML and can use Javascript *template variables* `${...}` as well as Python [Jinja2](https://jinja.palletsprojects.com) syntax to make the template *dynamic*.

You can also declare the following optional attributes:

- `_child_config` (dict): This is a mapping that controls how children are rendered.
- `_ignored_refs` (tuple[str]): This is tuple of parameter names. Use this to render Panel components as Panel components and not their value or object.
- `_dom_events` (dict): This is a mapping of node IDs to DOM events to add event listeners to.
- `_extension_name` (str): This is the name used to import external CSS and JS dependencies via `pn.extension(_extension_name)` even if the component is not initially rendered.
- `_scripts` (dict): This is a mapping of JavaScript scripts that are automatically executed during the component's life cycle and on parameter changes.
- `_stylesheets` (list[str]): The _stylesheets attribute is a list of CSS instructions that define the visual appearance and styling of the component.

In addition, you can optionally declare the following attributes:

- `__css__` (list): This is a list of CSS dependencies required to style your component.
- `__javascript__` (list): This is a list of JavaScript dependencies that your component relies on.
- `__javascript_modules__` (list): This is a list of JavaScript module dependencies that your component relies on.

## `_template`

The `_template` attribute defines the blueprint of your component using HTML for the content and optionally CSS or JavaScript for styling and behavior.

For example, the following `_template` variable defines an image component that displays a slideshow:

```python
_template = '<img id="slideshow_el" src="https://picsum.photos/800/300?image=${index}" onclick="${_img_click}"></img>'
```

In this case, the `_template` variable consists of an HTML `img` tag that displays an image and includes a dynamic parameter `${index}` that changes the image displayed. It also includes an `onclick` event listener that triggers a Python method `_img_click` when the image is clicked.

### Template Variables

You can use JavaScript template variables of the form `${...}` to link the parameters of a component to the attributes of HTML elements.

For example, the following `_template` variable sets the `class` attribute of a `div` element to the value of the `some_parameter` parameter:

```python
_template = '<div id="custom_id" class="${some_parameter}"></div>'
```

In addition to providing attributes, you can also provide children to HTML elements using JavaScript template variables:

```python
_template = '<div id="custom_id">${some_parameter}</div>'
```

You can also use JavaScript template variables to trigger Python methods on the component:

```python
_template = '<div id="custom_id" onclick="${some_python_method}"></div>'
```

and to trigger JavaScript scripts defined in the `_scripts` attribute:

```python
_template = '<div id="custom_id" onclick="${script('some_javascript_script')}"></div>'
```

Note that you must declare an `id` on components that contain a template variable.

If the parameter is a list, each item in the list will be inserted in sequence unless declared otherwise. However, if you want to wrap each child in some custom HTML, you will have to use Jinja2 loop syntax:

```{pyodide}
class CustomComponent(ReactiveHTML):
    value = param.List(["value **1**", "value **2**", "value **3**"])

    _template = """
<div id="loop_el">
  {% for obj in value %}
  <div id="option_el">${obj}</div>
  {% endfor %}
</div>
"""
CustomComponent(width=500)
```

Note that you must wrap a `{% for ... %}` loop in an HTML element with an `id` attribute just as we do in the example.

### Jinja2 templating

You can use Jinja2 syntax to layout your template. When using Jinja2 syntax you can refer to parameters using `{{...}}` syntax. This will insert your parameter values as a literal string values.

For example, the following `CustomComponent` class uses Jinja2 syntax to insert the `value` literal value into a div element:

```{pyodide}
class CustomComponent(ReactiveHTML):
    value = param.String("A **value**")

    _template = """
<div>{{value}}</div>
"""
CustomComponent(width=500)
```

If the parameter is a list you can insert the children as *literal* values using the syntax:

```{pyodide}
class CustomComponent(ReactiveHTML):
    value = param.List(["value **1**", "value **2**", "value **3**"])

    _template = """
<div id="loop_el">
  {% for obj in value %}
  <div id="option">{{obj}}</div>
  {% endfor %}
</div>
"""

CustomComponent(width=500)
```

Note that you must wrap a `{% for ... %}` loop in an HTML element with an `id` attribute as shown in the example.

In addition you can use the following context variables:

- `param`: The param namespace object allows templating parameter names, labels, docstrings and other attributes.
- `__doc__`: The class docstring

For example, the following `CustomComponent` class uses Jinja2 syntax to insert the `value` parameter and display some information about it:

```{pyodide}
class CustomComponent(ReactiveHTML):
    """I'm a custom ReactiveHTML component"""
    value = param.String("My value", doc="My Documentation")

    _template = """
<p>value: {{value}} ({{ param.value.default }}, {{ param.value.doc }})</p>
<h2>List of parameters</p>
<p id="loop">
{% for object in param.params().values() %}{% if loop.index0 < 3 %}
<div>{{ loop.index0 }}. {{object.name}}: {{object.owner[object.name]}} ({{object.default}}, {{object.doc | replace("`", "'")}})</div><hr/>
{% endif %}{% endfor %}
</p>
"""

CustomComponent(value="A new value", width=500)
```

Check out the [How-to > Create Layouts With ReactiveHTML](../../how_to/custom_components/reactive_html/reactive_html_layout) guide for lots of Jinja2 examples.

### Template variables vs Jinja2

There are several differences between JavaScript template variables and Jinja2 templating.

- *Time of Rendering*: Jinja2 templating is rendered on the Python side during initial rendering, while JavaScript template variables are inserted later on the JavaScript side.
- *Type of Rendering*: Jinja2 templating provides literal string values, while JavaScript template variables provide Panel objects by default.
- *Element `id`s*: With Jinja2 templating, you don't need to add an id attribute except when using {% for ... %} loops. With JavaScript template variables, you must add an id attribute.
- *Parameter Linking*: Jinja2 `{{...}}` template variables are not dynamically linked, while JavaScript template variables `${...} are dynamically linked.

Here's an example that illustrates the differences. If you change the color, only the JavaScript template variable section will update:

```{pyodide}
class CustomComponent(ReactiveHTML):
    """I'm a custom component"""
    text = param.String("I'm **bold**")
    color = param.Color("silver", label="Select a color", doc="""The color of the component""")

    _template = """
<p style="background:{{ color }}">Jinja literal value. {{ text }}</p>
<p id="el" style="background:${color}">Javascript template variable. ${text}</p>
"""

component = CustomComponent(width=500)

pn.Column(component.param.color, component, )
```

## `_child_config`

The optional attribute `_child_config` attribute controls how template variables `${...}` will
be rendered when inserted as children into an HTML element.

The configuration can be one of

- `model` (default): Render as Panel component
- `literal`: Render as HTML string
- `template`: Render as string

For example:

```{pyodide}
import panel as pn
import param

class CustomComponent(ReactiveHTML):
    v_model = param.String(default="I'm a **model** value. <em>emphasize</em>")
    v_literal = param.String(default="I'm a **literal** value. <em>emphasize</em>")
    v_template = param.String(default="I'm a **template** value. <em>emphasize</em>")

    _child_config = {
        "v_model": "model",
        "v_literal": "literal",
        "v_template": "template",
    }

    _template = """
<div id="el_model">${v_model}</div>
<div id="el_literal">${v_literal}</div>
<div id="el_template">${v_template}</div>
"""

component = CustomComponent(width=500, height=200)
component
```

As you can see the parameters are rendered very differently.

If we change any of the parameter values the component is updated

```{pyodide}
component.v_model=component.v_model.replace("**", "*")
component.v_literal=component.v_model.replace("**", "*")
component.v_template=component.v_model.replace("**", "*")
```

Here is a another example illustrating the difference

```{pyodide}
svg = """<svg style="stroke: #e62f63;" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg" slot="collapsed-icon">
<path d="M15.2222 1H2.77778C1.79594 1 1 1.79594 1 2.77778V15.2222C1 16.2041 1.79594 17 2.77778 17H15.2222C16.2041 17 17 16.2041 17 15.2222V2.77778C17 1.79594 16.2041 1 15.2222 1Z" stroke-linecap="round" stroke-linejoin="round"></path>
<path d="M9 5.44446V12.5556" stroke-linecap="round" stroke-linejoin="round"></path>
<path d="M5.44446 9H12.5556" stroke-linecap="round" stroke-linejoin="round"></path></svg>"""

CustomComponent(v_literal=svg, v_template=svg, width=500, height=200)
```

Please note you cannot set `v_model=svg` because `ReactiveHTML` tries to set the `v_model` to a `pn.pane.SVG` pane.

```{pyodide}
try:
    CustomComponent(v_model=svg, v_literal=svg, v_template=svg, width=500, height=200)
except Exception as ex:
    print(ex)
```

For a complex object like `DataFrame` you can only use `model`. Using `literal` or `template`
will raise a `bokeh.core.serialization.SerializationError`.

## `_dom_events`

In certain cases it is necessary to explicitly declare event listeners on the HTML element to ensure that changes in their properties are synced when an event is fired.

To make this possible the HTML element in question must be given an `id` and the `id` + `event` name must be defined in `_dom_events`.

For example:

```{pyodide}
class CustomComponent(ReactiveHTML):
    value = param.String()

    _template = """
<input id="input_el" value="${value}"></input>
"""

    _dom_events = {'input_el': ['change']}

component=CustomComponent(width=500)
pn.Column(component, component.param.value)
```

Once subscribed, the class may also define a method following the `_{element-id}_{event}` naming convention, which will fire when the DOM event triggers. For example we could define a `_input_el_change` method. Any such callback will be given a `DOMEvent` object as the first and only argument.

The `DOMEvent` contains information about the event on the `.data` attribute, like declaring the type of event on `.data.type`.

For example:

```{pyodide}
class CustomComponent(ReactiveHTML):
    value = param.String()

    event = param.Parameter()

    _template = """
<input id="input_el" value="${value}"></input>
"""

    _dom_events = {"input_el": ["change"]}

    def _input_el_change(self, event):
        self.event = event.data


component = CustomComponent(width=500)
pn.Column(
    component, component.param.value, pn.pane.JSON(component.param.event)
)
```

## `_extension_name`

The `_extension_name` attribute allows you to easily import the CSS and JavaScript dependencies required by your custom component, even if the component is not initially rendered. By adding the `_extension_name` to the list of extensions in the `pn.extension` call, you ensure that the necessary resources are loaded when your component is used.

For example, if you have a custom component called `CustomComponent` and it requires specific CSS and JavaScript dependencies, you can define the `_extension_name` attribute in the class definition:

```python
class CustomComponent(ReactiveHTML):
    _extension_name = "custom-component"
    ...
```

Then, when you want to use the `CustomComponent` in your notebook or app, you simply include the `_extension_name` in the `pn.extension` call:

```python
import panel as pn
from my_components import CustomComponent

pn.extension("custom-component", ...)
```

This ensures that the necessary CSS and JavaScript dependencies are imported and available for your component to function correctly.

## `_scripts`

In addition to declaring callbacks in Python it is also possible to declare Javascript callbacks on the `_scripts` attribute of the `ReactiveHTML` class.

All callback scripts have a number of objects available in their namespace that allow accessing (and setting) the parameter values, store state, update the layout and access any named DOM nodes declared as part of the template. Specifically the following objects are declared in each callbacks namespace:

- `self`: A namespace model which provides access to all scripts on the class, e.g. `self.do_something()` will call the script named `do_something`.
- `data`:   The data model holds the current values of the synced parameters, e.g. `data.value` will reflect the current value of the parameter named `value`.
- `model`:  The `ReactiveHTML` model which declares the layout parameters (e.g. `width` and `height`) and the component definition.
- `state`:  An empty state dictionary which scripts can use to store state for the lifetime of the view.
- `view`: Bokeh View class responsible for rendering the component. This provides access to method like `view.resize_layout()` to signal to Bokeh that  it should recompute the layout of the element.
- `<node_el>`: All HTML elements given an id, e.g. the `slideshow_el` or `input_el` element found in the examples above.
- `state.event`: If the script is invoked via an [inline callback](#inline-callbacks) the corresponding event will be available as `state.event`.

Here is a small example illustrating some of the concepts

```python
class Counter(ReactiveHTML):
    count = param.Integer()

    _template = """
    <div>
        <p>Count: ${count}</p>
        <button id="increment_btn" onclick="${script('increment')}">Increment</button>
    </div>
    """

    _scripts = {
        "increment": "data.count += 1",
        "count": "if (data.count>=3){data.count=0}",
    }

counter = Counter()
pn.Column(counter, counter.param.count)
```

In this example, we have a `Counter` component that displays a count value and an *Increment* Button. The `_template` defines the HTML structure of the component, including the template variable `${count}` for the count value.

The `_scripts` attribute is used to define two JavaScript callbacks: `increment` and `count`. The `increment` callback increases the count value by 1, while the `count` callback resets the `count` value to 0 if the `count` value reaches 3 or higher. Each callback can access the `data` object, which holds the current values of synced parameters (in this case, the `count` parameter).

When the *Increment* button is clicked, the corresponding JavaScript callback is invoked, updating the count value.

When the `count` value is changed, the corresponding `count` JavaScript callback is invoked, optionally resetting the `count` value to zero.

By combining Python callbacks and JavaScript callbacks, you can create dynamic and interactive components that respond to user interactions.

### Parameter callbacks

If the key in the `_scripts` dictionary matches one of the parameters declared on the class the callback will automatically fire whenever the synced parameter value changes. As an example let's say we have a class which declares a `count` parameter

```python
    count = param.Integer()
```

We can now declare a `'count'` key in the `_scripts` dictionary, which will fire whenever the `count` is updated:

```python
   _scripts = {
     "count": "if (data.count>=3){data.count=0}",
   }
```

### Lifecycle callbacks

In addition to parameter callbacks there are a few reserved keys in the `_scripts` which are fired during rendering of the component:

- `"render"`: This callback is invoked during initial rendering of the component.
- `"after_layout"`: This callback is invoked after the component has been fully rendered and the layout is fully computed.
- `"remove"`: This callback is invoked when the component is removed from the document.

For example:

```{{pyodide}}
class Counter(ReactiveHTML):
    _template = """
    <p id="render_el"></p><p id="after_layout_el"></p>
    """

    _scripts = {
        "render": 'render_el.innerText=(new Date()).toISOString()',
        "after_layout": 'after_layout_el.innerText=(new Date()).toISOString()'
    }

Counter()
```

This example will show the timestamp when `"render"` and `"after_layout"` scripts are automatically invoked. You will notice the `"after_layout"` callback is automatically invoked a few milliseconds later.

### Explicit calls

It is also possible to explicitly invoke one script from the namespace of another script using the `self` object, e.g. we might define a `get_datetime` method that returns the current date and time in a
particular format:

```{{pyodide}}
class Counter(ReactiveHTML):
    _template = """
    <p id="render_el"></p><p id="after_layout_el"></p>
    """

    _scripts = {
        "render": "render_el.innerText=self.get_datetime()",
        "after_layout": "after_layout_el.innerText=self.get_datetime()",
        "get_datetime": "return (new Date()).toISOString()",
    }

Counter()
```

### Inline callbacks

We can invoke the Javascript code declared in the `_scripts` dictionary from an HTML element by
using the `script` function, e.g.:

```html
    <button id="increment_btn" onclick="${script('increment')}">Increment</button>
```

will invoke the `"increment"` script defined below when the button is clicked:

```python
    _scripts = {
        "increment": "data.count += 1",
   }
```

Note that the event that triggered the callback will be made available in the namespace via `state.event` value.

## External Dependencies

Often the components you build will have dependencies on some external Javascript or CSS files. To make this possible `ReactiveHTML` components may declare `__javascript__`, `__javascript_modules__` and `__css__` attributes, specifying the external dependencies to load. Note that in a notebook as long as the component is imported before the call to `pn.extension` all its dependencies will be loaded automatically. If you want to require users to load the components as an extension explicitly via a `pn.extension` call you can declare an `_extension_name`.

Below we will create a Material UI text field and declare the Javascript and CSS components to load:

```{pyodide}
import panel as pn
from panel.reactive import ReactiveHTML
import param

class MaterialTextField(ReactiveHTML):

    value = param.String(default='')

    _template = """
    <label id="text-field" class="mdc-text-field mdc-text-field--filled">
      <span class="mdc-text-field__ripple"></span>
      <span class="mdc-floating-label">Label</span>
      <input id="text-input" type="text" class="mdc-text-field__input" aria-labelledby="my-label" value="${value}"></input>
      <span class="mdc-line-ripple"></span>
    </label>
    """

    _dom_events = {'text-input': ['change']}

    # By declaring an _extension_name the component should be loaded explicitly with pn.extension('material-components')
    _extension_name = 'material-components'

    _scripts = {
        'render': "mdc.textField.MDCTextField.attachTo(text_field);"
    }

    __javascript__ = [
        'https://unpkg.com/material-components-web@latest/dist/material-components-web.min.js'
    ]

    __css__ = [
        'https://unpkg.com/material-components-web@latest/dist/material-components-web.min.css'
    ]

pn.extension('material-components') # for notebook

text_field = MaterialTextField(value="Some value")

pn.Column(text_field, text_field.param.value).servable()
```

In a notebook dependencies for this component will not be loaded unless the user explicitly loads them with a `pn.extension('material-components')`. In a server context you will also have to explicitly load this extension unless the component is rendered on initial page load, i.e. if the component is only added to the page in a callback you will also have to explicitly run `pn.extension('material-components')`.

### Bootstrap

[Bootstrap](https://getbootstrap.com/) is one of the most popular design frameworks. **We recommend not using [Bootstrap](https://getbootstrap.com/) with Panel**.

You can use its CSS to style your components, but in our experience its javascript does not work well with Panel. It simply cannot select and update HTML elements inside the *shadowroot* of `ReactiveHTML` components.

### Web Components

[Web Components](https://en.wikipedia.org/wiki/Web_Components) are custom HTML elements. Web components work really great with `ReactiveHTML` and in the same way as built in HTML elements like `button`, `div` and `img`.

Some web components that work well with Panels designs are

- [Shoelace](https://shoelace.style/): A large, mature collection of components that integrate well with the Bootstrap design.
- [Fast](https://explore.fast.design/): A relatively large and mature collection of components that integrate well with the Fast design.
- [Material](https://github.com/material-components/material-web): A growing collection of components that integrate well with the Material design.

For more inspiration check out the [awesome-web-components](https://github.com/web-padawan/awesome-web-components#components) list.

### React, Preact and Vue

`ReactiveHTML` can be used with [React](https://react.dev/), [Preact](https://preactjs.com/) and [Vue](https://vuejs.org/).

## `ReactiveHTML` vs `AnyWidget`

Both `ReactiveHTML` in the Panel ecosystem and `AnyWidget` in the Jupyter ipywidgets ecosystem allow you to develop custom components using HTML, CSS, and JavaScript. However, there are some differences in terms of parameter layout and event handling between the two.

### `AnyWidget`

- Parameter Layout: In `AnyWidget`, you use JavaScript in the `_esm` attribute to layout your parameter values.
- Event Handling: You configure event handlers using JavaScript code within the `_esm` attribute. You can listen for parameter changes and update the widget accordingly.

Here is an example of a `CounterWidget` using `AnyWidget`:

```python
import anywidget
import traitlets

class CounterWidget(anywidget.AnyWidget):
    value = traitlets.Int(0).tag(sync=True)

    _esm = """
    export function render({ model, el }) {
      let button = document.createElement("button");
      button.innerHTML = `count is ${model.get("value")}`;
      button.addEventListener("click", () => {
        model.set("value", model.get("value") + 1);
        model.save_changes();
      });
      model.on("change:value", () => {
        button.innerHTML = `count is ${model.get("value")}`;
      });
      el.appendChild(button);
    }
    """
```

### `ReactiveHTML`

- Parameter Layout: In `ReactiveHTML`, you typically use HTML, JavaScript template variables `${...}`, and Python Jinja2 syntax to layout your parameter values.
- Event Handling: You can configure event handlers using JavaScript code within the `_template` attribute. Additionally, you can use the `_scripts` attribute to define JavaScript callbacks that respond to events or parameter changes.

Here is an example of a `CounterWidget` using `ReactiveHTML`:

```{pyodide}
import param
from panel.reactive import ReactiveHTML

class CounterWidget(ReactiveHTML):
    value = param.Integer(default=0)

    _template = """
    <button id="button_el" class="styled-button" onclick="${script('click_handler')}"></button>
    """

    _scripts = {
        "render": "button_el.innerHTML = `count is ${data.value}`",
        "click_handler": "data.value += 1",
        "value": "button_el.innerHTML = `count is ${data.value}`"
    }
```

### Additional Notes

- Custom CSS and JavaScript files: `AnyWidget` allows you to easily develop CSS and JavaScript in separate files, providing a great developer experience with hot reload. `ReactiveHTML` does not currently have built-in support for separate files, but there are plans to add similar features in the future.
- Integration with other ecosystems: `AnyWidget` is part of the Jupyter ipywidgets ecosystem, while `ReactiveHTML` is part of the Panel ecosystem. There are ongoing efforts to make it easier for Panel users to integrate with the growing `AnyWidget` ecosystem.
