# Building Custom Components

When building custom applications and dashboards it is frequently useful to extend Panel with custom components to fit a specialized need. Panel provides multiple mechanisms to extend and compose different components or even add entirely new components.

This Background page will focus on the building of entirely new components. Making full new components can be straightforward in the simplest cases, but it does require knowledge of web technologies like HTML, CSS, and JavaScript. Alternatively, to learn how to compose existing Panel components into an easily reusable unit that behaves like a native Panel component, see the [How-to > Combine Existing Components](../../how_to/custom_components/custom_viewer.md) page.

## ReactiveHTML components

The `ReactiveHTML` provides bi-directional syncing of arbitrary HTML attributes and DOM properties with parameters on the subclass. This kind of component must declare a HTML template written using Javascript template variables (`${}`) and optionally Jinja2 syntax:

- `_template`: The HTML template to render declaring how to link parameters on the class to HTML attributes.

Additionally the component may declare some additional attributes providing further functionality

- `_child_config` (optional): Optional mapping that controls how children are rendered.
- `_dom_events` (optional): Optional mapping of named nodes to DOM events to add event listeners to.
- `_scripts` (optional): Optional mapping of Javascript to execute on specific parameter changes.

### HTML templates

A ReactiveHTML component is declared by providing an HTML template on the `_template` attribute on the class. Parameters are synced by inserting them as template variables of the form `${parameter}`, e.g.:

```html
    _template = '<div id="custom_id" class="${div_class}" onclick="${some_method}">${children}</div>'
```

will interpolate the `div_class` parameter on the `class` attribute of the HTML element.

In addition to providing attributes we can also provide children to an HTML tag. Any child parameter will be treated as other Panel components to render into the containing HTML. This makes it possible to use `ReactiveHTML` to lay out other components. Lastly the `${}` syntax may also be used to invoke Python methods and JS scripts. Note that you must declare an `id` on components which have linked parameters, methods or children.

The HTML templates also support [Jinja2](https://jinja.palletsprojects.com/en/2.11.x/) syntax to template parameter variables and child objects. The Jinja2 templating engine is automatically given a few context variables:

- `param`: The param namespace object allows templating parameter names, labels, docstrings and other attributes.
- `__doc__`: The class docstring

The difference between Jinja2 literal templating and the JS templating syntax is important to note. While literal values are inserted during the initial rendering step they are not dynamically linked.

### Children

In order to template other parameters as child objects there are a few options. By default all parameters referenced using `${child}` syntax are treated as if they were Panel components, e.g.:

```html
<div id="custom_id">${parameter}</div>
```

will render the contents of the `parameter` as a Panel object. If you want to render it as a literal string instead you can use the regular Jinja templating syntax instead, i.e. `{{ parameter }}` or you can use the `_child_config` to declare you want to treat `parameter` as a literal:

```python
_child_config = {'parameter': 'literal'}
```

If the parameter is a list each item in the list will be inserted in sequence unless declared otherwise. However if you want to wrap each child in some custom HTML you will have to use Jinja2 loop syntax:

```html
<select>
  {% for obj in parameter %}
  <option id="option">${obj}</option>
  {% endfor %}
</select>
```

This will insert the children as Panel components. If you want to insert the children as *literal* values, you can use the syntax:

```html
<select>
  {% for obj in parameter %}
  <option id="option-{{ loop.index0 }}">{{ obj }}</option>
  {% endfor %}
</select>
```

### DOM Events

In certain cases it is necessary to explicitly declare event listeners on the DOM node to ensure that changes in their properties are synced when an event is fired. To make this possible the HTML element in question must be given an `id`, e.g.:

```html
    _template = '<input id="custom_id"></input>'
```

Now we can use this name to declare set of `_dom_events` to subscribe to. The following will subscribe to change DOM events on the input element:

```python
    _dom_events = {'custom_id': ['change']}
```

Once subscribed the class may also define a method following the `_{node-id}_{event}` naming convention which will fire when the DOM event triggers, e.g. we could define a `_custom_id_change` method. Any such callback will be given a `DOMEvent` object as the first and only argument.

The `DOMEvent` contains information about the event on the `.data` attribute, like declaring the type of event on `.data.type`.

### Scripts

In addition to declaring callbacks in Python it is also possible to declare Javascript callbacks on the `_scripts` attribute of the `ReactiveHTML` class. There are a few ways to trigger such callbacks.

All scripts have a number of objects available in their namespace that allow accessing (and setting) the parameter values, store state, update the layout and access any named DOM nodes declared as part of the template. Specifically the following objects are declared in each callbacks namespace:

* `self`: A namespace model which provides access to all scripts on the class, e.g. `self.value()` will call the 'value' script defined above.
* `data`:   The data model holds the current values of the synced parameters, e.g. `data.value` will reflect the current value of the input node.
* `model`:  The `ReactiveHTML` model which declares the layout parameters (e.g. `width` and `height`) and the component definition.
* `state`:  An empty state dictionary which scripts can use to store state for the lifetime of the view.
* `view`: Bokeh View class responsible for rendering the component. This provides access to method like `view.resize_layout()` to signal to Bokeh that  it should recompute the layout of the element.
* `<node>`: All named DOM nodes in the HTML template, e.g. the `input` node in the example above.
* `event`: If the script is invoked via an [inline callback](#inline-callbacks) the corresponding event will be in the namespace

#### Parameter callbacks

If the key in the `_scripts` dictionary matches one of the parameters declared on the class the callback will automatically fire whenever the synced parameter value changes. As an example let's say we have a class which declares a `value` parameter, linked to the `value` attribute of an `<input>` HTML tag:

```python
    value = param.String()

    _template = '<input id="custom_id" value="${value}"></input>'
```

We can now declare a `'value'` key in the `_scripts` dictionary, which will fire whenever the `value` is updated:

```python
   _scripts = {
     'value': 'console.log(self, input, data.value)'
   }
```

#### Lifecycle callbacks

In addition to parameter callbacks there are a few reserved keys in the `_scripts` which are fired during rendering of the component:

- `'render'`: This callback is invoked during initial rendering of the component.
- `'after_layout'`: This callback is invoked after the component has been fully rendered and the layout is fully computed.
- `'remove'`: This callback is invoked when the component is removed.

#### Explicit calls

It is also possible to explicitly invoke one script from the namespace of another script using the `self` object, e.g. we might define a `get_data` method that returns the data in a particular format:

```python
    _scripts = {
      'get_data': 'return [data.x, data.y]'
      'render'  : 'console.log(self.get_data())'
    }
```

### Inline callbacks

Instead of declaring explicit DOM events Python callbacks can also be declared inline, e.g.:

```html
    _template = '<input id="custom_id" onchange="${_input_change}"></input>'
```

will look for an `_input_change` method on the `ReactiveHTML` component and call it when the event is fired.

Additionally we can invoke the Javascript code declared in the `_scripts` dictionary by name using the `script` function, e.g.:

```html
    <input id="custom_id" onchange="${script('some_script')}"></input>
```

will invoke the following script if it is defined on the class:

```python
    _scripts = {
        'some_script': 'console.log(self.state.event)'
   }
```

Note that the event that triggered the callback will be made available in the namespace of the callback

### Examples

#### Callbacks

To see all of this in action we declare a `Slideshow` component which subscribes to `click` events on an `<img>` element and advances the image `index` on each click:

```{pyodide}
import param
from panel.reactive import ReactiveHTML
import panel as pn
pn.extension() # for notebook

class Slideshow(ReactiveHTML):

    index = param.Integer(default=0)

    _template = '<img id="slideshow" src="https://picsum.photos/800/300?image=${index}" onclick="${_img_click}"></img>'

    def _img_click(self, event):
        self.index += 1

Slideshow(width=800, height=300)
```

As we can see this approach lets us quickly build custom HTML components with complex interactivity. However if we do not need any complex computations in Python we can also construct a pure JS equivalent:

```{pyodide}
class JSSlideshow(ReactiveHTML):

    index = param.Integer(default=0)

    _template = """<img id="slideshow" src="https://picsum.photos/800/300?image=${index}" onclick="${script('click')}"></img>"""

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

The loop body can declare any number of HTML tags to add for each child object, e.g. to add labels or icons, however the child object (like the `{{item}}` or `${item}`) must always be wrapped by an HTML element (e.g. `<option>`) which must declare an `id`. Depending on your use case you can wrap each child in any HTML element you require, allowing complex nested components to be declared. Note that the example above inserted the `items` as child objects (i.e. as full Panel objects) but since they are strings we could use literals instead:

```html
<div id="cards" class="cards">
{% for item in items -%}
    <div id="card" class="card">{{item}}</div>
{%- endfor %}
</div>
```

When using child literals we have to ensure that each `<option>` DOM node has a unique ID manually by inserting the `loop.index0` value (which would otherwise be added automatically).

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
pn.extension('material-components')

text_field = MaterialTextField()

text_field
```

In a notebook dependencies for this component will not be loaded unless the user explicitly loads them with a `pn.extension('material-components')`. In a server context you will also have to explicitly load this extension unless the component is rendered on initial page load, i.e. if the component is only added to the page in a callback you will also have to explicitly run `pn.extension('material-components')`.

## Building custom Bokeh models

The last approach to extending Panel with new components is to write custom Bokeh models. This involves writing, compiling and distributing custom Javascript and therefore requires considerably more effort than the other approaches. Detailed documentation on writing such components will be coming to the developer guide in the future.
