# Build Components from Scratch

This guide addresses how to build custom Panel components from scratch.

```{admonition} Prerequisites
1. As a how-to guide, the intent is to provide recipes for specific problems without a lot of discussion. However, this is an advanced topic so if you get stuck, please read the associated [Explanation > Building Custom Components](../../explanation/components/components_custom) for further explanation.
```

---

The `ReactiveHTML` class provides bi-directional syncing of arbitrary HTML attributes and DOM properties with parameters on the subclass. The key part of the subclass is the `_template` variable. This is the HTML template that gets rendered and declares how to link parameters on the class to HTML attributes.

## Callback Example

Let's declare a `Slideshow` component which subscribes to `click` events on an `<img>` element and advances the image `index` on each click:

```{pyodide}
import panel as pn
import param

from panel.reactive import ReactiveHTML

pn.extension()

class Slideshow(ReactiveHTML):

    index = param.Integer(default=0)

    _template = '<img id="slideshow" src="https://picsum.photos/800/300?image=${index}" onclick="${_img_click}"></img>'

    def _img_click(self, event):
        self.index += 1

print('run the code block above, then click on the image below')

Slideshow(width=500, height=200)
```

As we can see this approach lets us quickly build custom HTML components with complex interactivity. However if we do not need any complex computations in Python we can also construct a pure JS equivalent:

```{pyodide}
class JSSlideshow(ReactiveHTML):

    index = param.Integer(default=0)

    _template = """<img id="slideshow" src="https://picsum.photos/800/300?image=${index}" onclick="${script('click')}"></img>"""

    _scripts = {'click': 'data.index += 1'}

JSSlideshow(width=800, height=300)
```

## Child Template Example

If we want to provide a template for the children of an HTML node we have to use Jinja2 syntax to loop over the parameter. The component will insert the loop variable `option` into each of the tags:

```{pyodide}
class Select(ReactiveHTML):

    options = param.List(doc="Options to choose from.")

    value = param.String(doc="Current selected option")

    _template = """
    <select id="select" value="${value}" style="width: ${model.width}px">
      {% for option in options %}
      <option id="option">${option}</option>
      {% endfor %}
    </select>
    """

    _dom_events = {'select': ['change']}

select = Select(options=['A', 'B', 'C'])
select
```

The loop body can declare any number of HTML tags to add for each child object, e.g. to add labels or icons, however the child object (like the `{{option}}` or `${option}`) must always be wrapped by an HTML element (e.g. `<option>`) which must declare an `id`. Depending on your use case you can wrap each child in any HTML element you require, allowing complex nested components to be declared. Note that the example above inserted the `options` as child objects but since they are strings we could use literals instead:

```html
<select id="select" value="${value}" style="width: ${model.width}px">
  {% for option in options %}
  <option id="option-{{ loop.index0 }}">{{ option }}</option>
  {% endfor %}
</select>
```

When using child literals we have to ensure that each `<option>` DOM node has a unique ID manually by inserting the `loop.index0` value (which would otherwise be added automatically).

## Javascript Events Example

Next we will build a more complex example using pure Javascript events to draw on a canvas with configurable line width, color and the ability to clear and save the resulting drawing.

```{pyodide}
import panel as pn

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


## Related Resources
- Read the associated [Explanation > Building Custom Components](../../explanation/components/components_custom) for further explanation, including how to load external dependencies for your custom components.
