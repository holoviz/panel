# Building `ReactiveHTML` Components

When you're working on custom applications and dashboards, there are times when you need to **extend Panel's capabilities to meet unique requirements**.

This page will walk you through using the `ReactiveHTML` class to craft custom components without the need for complex JavaScript build tools. You'll be able to leverage basic HTML, CSS, and JavaScript to tailor your components to your specific needs.

## Why Use `ReactiveHTML`?

`ReactiveHTML` empowers you to design and build custom components that seamlessly integrate with your Panel applications. These components can enhance your applications' interactivity and functionality, all while keeping the development process straightforward and free from the complexities of JavaScript build tools.

## What are the alternatives to `ReactiveHTML`?

If you're looking for simpler alternatives to `ReactiveHTML`, Panel provides a `Viewer` class that allows you to combine existing Panel components using Python only. This approach is a great choice if you want to quickly create custom components without the need for writing HTML, CSS, or JavaScript. You can learn more about creating custom `Viewer` components in our guide [How-to > Combine Existing Components](../../how_to/custom_components/custom_viewer.md).

On the other hand, if you're looking for a more advanced approach that gives you full control over the design and functionality of your custom components, you can use *Bokeh Models*. With Bokeh Models, you can leverage the power of your IDE and modern JavaScript development tools to build advanced and performant custom components. Many of the built-in Panel components are built using this approach. It provides flexibility and extensibility, allowing you to create highly customized and interactive components tailored to your specific needs.

## What is a `ReactiveHTML` component?

A *`ReactiveHTML` component* is essentially a class that you create by inheriting from the `ReactiveHTML` class. Within this custom class, you are required to define the `_template` attribute using HTML, which serves as the *design blueprint* for your custom component. You can use Javascript *template variables* `${...}` as well as Python [Jinja2](https://jinja.palletsprojects.com) syntax to make the template *dynamic*.

Here is a basic example

```{pyodide}
import param
import panel as pn

pn.extension()

class Slideshow(pn.reactive.ReactiveHTML):

    index = param.Integer(default=0)

    _template = '<img id="slideshow_el" src="https://picsum.photos/800/300?image=${index}" onclick="${_img_click}"></img>'

    def _img_click(self, event):
        self.index += 1

Slideshow(width=800, height=300)
```

## Why is it called ReactiveHTML?

`ReactiveHTML` is named for its ability to enable reactive programming in HTML. Unlike the static HTML content that the [`HTML`](../../../examples/reference/panes/HTML.ipynb) pane displays, `ReactiveHTML` components can update their view in response to changes in the class parameters.

It's worth noting that the name `ReactiveHTML` is not related to the JavaScript framework [React](https://react.dev/), although you can still use React with `ReactiveHTML` components.

## Where do I find practical examples?

To see `ReactiveHTML` in action and discover **how to** create your custom components, check out our detailed guide: [How-to > Create Custom Components with ReactiveHTML](../../how_to/custom_components/reactive_html/index.md). It's packed with practical examples to help you get started quickly.

## Where do I find the full API description?

You can find it here [API > ReactiveHTML](../../api/panel.reactive.html#panel.reactive.ReactiveHTML).

## What class attributes should a component declare?

When creating a `ReactiveHTML` component, there are several class attributes that you can declare to customize its behavior.

The required attribute is:

- `_template` (str): This defines the blueprint for how your custom component should look and behave. It is defined using HTML and can use Javascript *template variables* `${...}` as well as Python [Jinja2](https://jinja.palletsprojects.com) syntax to make the template *dynamic*.

You can also declare the following optional attributes:

- `_child_config` (dict): This is a mapping that controls how children are rendered.
- `_dom_events` (dict): This is a mapping of node IDs to DOM events to add event listeners to.
- `_extension_name` (str): This is the name used to import external CSS and JS dependencies via `pn.extension(_extension_name)`.
- `_scripts` (dict): This is a mapping of JavaScript scripts that are automatically executed during the component's life cycle and on parameter changes.
- `_stylesheets` (list[str]): The _stylesheets attribute is a list of CSS instructions that define the visual appearance and styling of the component.

In addition, you can optionally declare the following attributes:

- `__css__` (list): This is a list of CSS dependencies required to style your component.
- `__javascript__` (list): This is a list of JavaScript dependencies that your component relies on.
- `__javascript_modules__` (list): This is a list of JavaScript module dependencies that your component relies on.

### What does the `_template` attribute define?

The `_template` attribute defines the blueprint of your component using HTML for the content and optionally CSS or JavaScript for styling and behavior.

For example, the following `_template` variable defines an image component that displays a slideshow:

```python
_template = '<img id="slideshow_el" src="https://picsum.photos/800/300?image=${index}" onclick="${_img_click}"></img>'
```

In this case, the `_template` variable consists of an HTML `img` tag that displays an image and includes a dynamic parameter `${index}` that changes the image displayed. It also includes an `onclick` event listener that triggers a Python method `_img_click` when the image is clicked.

#### What can I use JavaScript Template Variables for?

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
class CustomComponent(pn.reactive.ReactiveHTML):
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

Note that you must wrap a `{% for ... %}` loop in a HTML element with an `id` attribute just as we do in the example.

#### What can I use Jinja2 templating for?

You can use Jinja2 syntax to layout your template. When using Jinja2 syntax you can refer to parameters using `{{...}}` syntax. This will insert your parameter values as a literal string values.

For example, the following `CustomComponent` class uses Jinja2 syntax to insert the value parameter into a div element:

```{pyodide}
class CustomComponent(pn.reactive.ReactiveHTML):
    value = param.String("A **value**")

    _template = """
<div>{{value}}</div>
"""
CustomComponent(width=500)
```

If the parameter is a list you can insert the children as *literal* values using the syntax:

```{pyodide}
class CustomComponent(pn.reactive.ReactiveHTML):
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
class CustomComponent(pn.reactive.ReactiveHTML):
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

Check out the [How-to > Create Layouts With ReactiveHTML](../../how_to/custom_components/reactive_html/reactive_html_layout.md) guide for lots of Jinja2 examples.

#### What are the differences between Javascript template variables and Jinja2 templating?

There are several differences between JavaScript template variables and Jinja2 templating.

- *Time of Rendering*: Jinja2 templating is rendered on the Python side during initial rendering, while JavaScript template variables are inserted later on the JavaScript side.
- *Type of Rendering*: Jinja2 templating provides literal string values, while JavaScript template variables provide Panel objects by default.
- *Element IDs*: With Jinja2 templating, you don't need to add an id attribute except when using {% for ... %} loops. With JavaScript template variables, you must add an id attribute.
- *Parameter Linking*: Jinja2 templating is not dynamically linked, while JavaScript template variables are dynamically linked.

Here's an example that illustrates the differences. If you change the color, only the JavaScript template variable section will update:

```{pyodide}
class CustomComponent(pn.reactive.ReactiveHTML):
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

## What does the `_child_config` attribute do?

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

class CustomComponent(pn.reactive.ReactiveHTML):
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

## What does the `_dom_events` do?

In certain cases it is necessary to explicitly declare event listeners on the HTML element to ensure that changes their properties are synced when an event is fired.

To make this possible the HTML element in question must be given an `id` and the `id` + `event` name must be defined in `_dom_events`.

For example:

```{pyodide}
class CustomComponent(pn.reactive.ReactiveHTML):
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
class CustomComponent(pn.reactive.ReactiveHTML):
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

The `_extension_name` enables you to get the css and javascript dependencies imported in your notebook or app - even if the component is not rendered initially.

It simple to use as you just add the `_extension_name` to `pn.extension` in the same way as you would do when using the Plotly or Tabulator components.

```python
import panel as pn
from my_components import CustomComponent

pn.extension("custom-component", "plotly", "tabulator")
```

## What does the `_extension_name` do?

The `_extension_name` attribute allows you to easily import the CSS and JavaScript dependencies required by your custom component, even if the component is not initially rendered. By adding the `_extension_name` to the list of extensions in the `pn.extension` call, you ensure that the necessary resources are loaded when your component is used.

For example, if you have a custom component called `CustomComponent` and it requires specific CSS and JavaScript dependencies, you can define the `_extension_name` attribute in the class definition:

```python
class CustomComponent(pn.reactive.ReactiveHTML):
    _extension_name = "custom-component"
    ...
```

Then, when you want to use the `CustomComponent` in your notebook or app, you simply include the `_extension_name` in the `pn.extension` call:

```python
import panel as pn
from my_components import CustomComponent

pn.extension("custom-component", "tabulator", ...)
```

This ensures that the necessary CSS and JavaScript dependencies are imported and available for your component to function correctly.

### Scripts

In addition to declaring callbacks in Python it is also possible to declare Javascript callbacks on the `_scripts` attribute of the `ReactiveHTML` class.

All scripts have a number of objects available in their namespace that allow accessing (and setting) the parameter values, store state, update the layout and access any named DOM nodes declared as part of the template. Specifically the following objects are declared in each callbacks namespace:

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

#### Parameter callbacks

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

#### Lifecycle callbacks

In addition to parameter callbacks there are a few reserved keys in the `_scripts` which are fired during rendering of the component:

- `"render"`: This callback is invoked during initial rendering of the component.
- `"after_layout"`: This callback is invoked after the component has been fully rendered and the layout is fully computed.
- `"remove"`: This callback is invoked when the component is removed from the document.

For example:

```{{pyodide}}
class Counter(pn.reactive.ReactiveHTML):
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

#### Explicit calls

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

#### Inline callbacks

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

### Examples

Below you will see some more examples to help explain how the `ReactiveHTML` class can be utilized.

#### Python vs Javascript Callbacks

To see all of this in action we declare a `Slideshow` component which subscribes to `click` events on an `<img>` element and advances the image `index` on each click:

```{pyodide}
class Slideshow(ReactiveHTML):

    index = param.Integer(default=0)

    _template = '<img id="slideshow_el" src="https://picsum.photos/800/300?image=${index}" onclick="${_img_click}"></img>'

    def _img_click(self, event):
        self.index += 1

Slideshow(width=800, height=300).servable()
```

As we can see this approach lets us quickly build custom HTML components with complex interactivity. However if we do not need any complex computations in Python we can also construct a pure JS equivalent:

```{pyodide}
class JSSlideshow(ReactiveHTML):

    index = param.Integer(default=0)

    _template = """<img id="slideshow_el" src="https://picsum.photos/800/300?image=${index}" onclick="${script('click')}"></img>"""

    _scripts = {'click': 'data.index += 1'}

JSSlideshow(width=800, height=300)
```

#### Child templates

If we want to provide a template for the children of an HTML node we have to use Jinja2 syntax to loop over the parameter. The component will insert the loop variable `item` into each of the tags:

```{pyodide}
class Cards(ReactiveHTML):

    items = param.List(doc="Items to render into cards.")

    _template = """
    <div id="cards" class="cards">
      {% for item in items -%}
        <div id="card" class="card">${item}</div>
      {%- endfor %}
    </div>
    """

    _stylesheets = ["""
        .cards { display: flex; }
        .card {
          box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
          border-radius: 5px;
          margin: 5px
        }
    """]

cards = Cards(items=['Foo', 'Bar', 'Baz'])

cards
```

The loop body can declare any number of HTML tags to add for each child object, e.g. to add labels or icons, however the child object (like the `{{item}}` or `${item}`) must always be wrapped by an HTML element (e.g. `<div>`) which must declare an `id`. Depending on your use case you can wrap each child in any HTML element you require, allowing complex nested components to be declared. Note that the example above inserted the `items` as child objects (i.e. as full Panel objects) but since they are strings we could use literals instead:

```html
<div id="cards" class="cards">
{% for item in items -%}
    <div id="card" class="card">{{item}}</div>
{%- endfor %}
</div>
```

#### Pure Javascript events

Next we will build a more complex example using pure Javascript events to draw on a canvas with configurable line width, color and the ability to clear and save the resulting drawing.

```{pyodide}
class Canvas(ReactiveHTML):

    color = param.Color(default='#000000')

    line_width = param.Number(default=1, bounds=(0.1, 10))

    uri = param.String()

    _template = """
    <canvas
      id="canvas"
      style="border: 1px solid;"
      width="${model.width}"
      height="${model.height}"
      onmousedown="${script('start')}"
      onmousemove="${script('draw')}"
      onmouseup="${script('end')}"
    >
    </canvas>
    <button id="clear" onclick='${script("clear")}'>Clear</button>
    <button id="save" onclick='${script("save")}'>Save</button>
    """

    _scripts = {
        'render': """
          state.ctx = canvas.getContext("2d")
        """,
        'start': """
          state.start = event
          state.ctx.beginPath()
          state.ctx.moveTo(state.start.offsetX, state.start.offsetY)
        """,
        'draw': """
          if (state.start == null)
            return
          state.ctx.lineTo(event.offsetX, event.offsetY)
          state.ctx.stroke()
        """,
        'end': """
          delete state.start
        """,
        'clear': """
          state.ctx.clearRect(0, 0, canvas.width, canvas.height);
        """,
        'save': """
          data.uri = canvas.toDataURL();
        """,
        'line_width': """
          state.ctx.lineWidth = data.line_width;
        """,
        'color': """
          state.ctx.strokeStyle = data.color;
        """
    }

canvas = Canvas(width=300, height=300)

# We create a separate HTML element which syncs with the uri parameter of the Canvas
png_view = pn.pane.HTML()
canvas.jslink(png_view, code={'uri': "target.text = `<img src='${source.uri}'></img>`"})

pn.Column(
    '# Drag on canvas to draw\n To export the drawing to a png click save.',
    pn.Row(
        canvas.controls(['color', 'line_width']),
        canvas,
        png_view
    )
)
```

This example leverages all three ways a script is invoked:

1. `'render'` is called on initialization
2. `'start'`, `'draw'` and `'end'` are explicitly invoked using the `${script(...)}` syntax in inline callbacks
3. `'line_width'` and `'color'` are invoked when the parameters change (i.e. when a widget is updated)

It also makes extensive use of the available objects in the namespace:

- `'render'`: Uses the `state` object to easily access the canvas rendering context in subsequent callbacks and accesses the `canvas` DOM node by name.
- `'start'`, `'draw'`:  Use the `event` object provided by the `onmousedown` and `onmousemove` inline callbacks
- `'save'`, `'line_width'`, `'color'`: Use the `data` object to get and set the current state of the parameter values

## External dependencies

Often the components you build will have dependencies on some external Javascript or CSS files. To make this possible `ReactiveHTML` components may declare `__javascript__`, `__javascript_modules__` and `__css__` attributes, specifying the external dependencies to load. Note that in a notebook as long as the component is imported before the call to `pn.extension` all its dependencies will be loaded automatically. If you want to require users to load the components as an extension explicitly via a `pn.extension` call you can declare an `_extension_name`.

Below we will create a Material UI text field and declare the Javascript and CSS components to load:

```python
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
```

```python
pn.extension('material-components') # for notebook

text_field = MaterialTextField(value="Some value")

pn.Column(text_field, text_field.param.value).servable()
```

In a notebook dependencies for this component will not be loaded unless the user explicitly loads them with a `pn.extension('material-components')`. In a server context you will also have to explicitly load this extension unless the component is rendered on initial page load, i.e. if the component is only added to the page in a callback you will also have to explicitly run `pn.extension('material-components')`.
