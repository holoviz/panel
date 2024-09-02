# Widgets with ReactiveHTML

In this guide we will show you how to efficiently implement custom widgets using `ReactiveHTML` to get input from the user.

## Image Button

This example we will show you to create an `ImageButton`.

```{pyodide}
import panel as pn
import param

from panel.custom import ReactiveHTML, WidgetBase

pn.extension()

class ImageButton(ReactiveHTML, WidgetBase):

    clicks = param.Integer(default=0)

    image = param.String()

    value = param.Event()

    _template = """\
<button id="button" class="pn-container center-content" onclick="${script('click')}">
    <img id="image" class="image-size" src="${image}"></img>
</button>
"""

    _stylesheets = ["""
.pn-container {
    height: 100%;
    width: 100%;
}
.center-content {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1em;
}
.image-size {
    width: 100%;
    max-height: 100%;
    object-fit: contain;
}
"""]

    _scripts = {'click': 'data.clicks += 1'}

    @param.depends('clicks', watch=True)
    def _on__click(self):
        self.param.trigger('value')

button = ImageButton(
    image="https://raw.githubusercontent.com/holoviz/holoviz/25ac96dbc09f789612eb8e03a5deb36c5cd74393/examples/assets/panel.png",
    styles={"border": "2px solid lightgray"},
    width=400, height=200
)
pn.Column(button, button.param.clicks).servable()
```

If you don't want the *button* styling, you can change the `<button>` tag to a `<div>` tag.

## SVG Input

This example will show you have to turn a [SVG](https://en.wikipedia.org/wiki/SVG) image into a clickable and hoverable input widget.

This can for example be used to make a technical drawing interactive.

```{pyodide}
import panel as pn
import param

from panel.custom import ReactiveHTML, WidgetBase

pn.extension()

class SVGInput(ReactiveHTML, WidgetBase):
    value = param.String(default="")

    clicks = param.Integer()
    click = param.String()
    hover = param.String()

    _child_config = {"value": "literal"}

    _template = """\
    <div id="container" class="pn-container"
      onclick="${script('click_handler')}" onmouseover="${script('mouseover_handler')}"
    >
      {{ value }}
    </div>
    """

    _stylesheets = ["""
      .pn-container { height: 100%; width: 100%; position:relative;}
      .pn-container svg {position: relative; height:100%; width:100%}
    """]

    _scripts = {
        "click_handler": """
          const name = state.event.target.getAttribute("data-name")
          if (name != null) {
            data.click = name
            data.clicks += 1
          }
        """,
        "mouseover_handler": """
          const name = state.event.target.getAttribute("data-name")
          data.hover = name || ""
        """
    }

SVG = """
<svg viewBox="0 35 300 300">
    <rect data-name="foot" x="130" y="270" width="40" height="30" fill="brown"/>
    <polygon data-name="bottom" points="150,150 230,270 70,270" fill="#234236"/>
    <polygon data-name="middle" points="150,110 210,210 90,210" fill="#0C5C4C"/>
    <polygon data-name="top" points="150,70 190,150 110,150" fill="#38755B"/>
</svg>
"""

button = SVGInput(
    value=SVG,
    styles={"border": "2px solid lightgray"},
    height=400, sizing_mode="stretch_width", max_width=1000
)

pn.Column(button, button.param.clicks, button.param.click, button.param.hover).servable()
```

If you want to use your own SVG `value`, you must make sure that

- the `viewBox` is set on the SVG
- the `data-name` is set on the SVG child elements, that you want to make clickable and hoverable.

In this example its tempting to call the `onclick` event handler `click` instead of `click_handler`.
But if you do, the `clicks` value will be incremented twice because a parameter called `click` also exists and when its value changes, the associated `click` script will be executed!

## Select Widget

Lets see how to create a basic `Select` widget.

```{pyodide}
import panel as pn
import param

from panel.custom import ReactiveHTML, WidgetBase

pn.extension()

class Select(ReactiveHTML, WidgetBase):

    options = param.List(doc="Options to choose from.")

    value = param.String(default="", doc="Current selected option")

    _template = """
    <select id="select_el" class="pn-container style" value="${value}">
      {% for option in options %}
      <option id="option_el">{{option}}</option>
      {% endfor %}
    </select>
    """

    stylesheets=["""
      .pn-container {height: 100%;width: 100%;position:relative;}
      .style {border: 2px dashed lightgray;border-radius:20px}
    """]

    _dom_events = {'select_el': ['change']}

select = Select(
    value="B",
    options=['A', 'B', 'C'], height=50, width=300,
)
pn.Column(select, select.param.value).servable()
```

Note how we used a {% for ... %}` loop to loop over the options.

In this example we inserted the options as literal `str` values via `{{option}}`.

Note that the example above inserted the `options` as child objects but since they are strings we could use literals instead:

```html
<select id="select_el" class="pn-container style" value="${value}" >
  {% for option in options %}
  <option id="option_el">{{ option }}</option>
  {% endfor %}
</select>
```

## Drawable Canvas

Next we will build a more complex widget to draw on a canvas with a
configurable line width, color and the ability to clear and save the resulting drawing.

```{pyodide}
import panel as pn
import param

from panel.custom import ReactiveHTML, WidgetBase

pn.extension()


class Canvas(ReactiveHTML, WidgetBase):
    value = param.String(default="")

    color = param.Color(default="#000000")
    line_width = param.Number(default=1, bounds=(0.1, 10))

    save = param.Event()
    clear = param.Event()

    _template = """
    <canvas
      id="canvas_el" style="border: 1px solid;"
      width="${model.width}" height="${model.height}"
      onmousedown="${script('start')}" onmousemove="${script('draw')}" onmouseup="${script('end')}"
    ></canvas>
    """

    _scripts = {
        "render": "state.ctx = canvas_el.getContext('2d')",
        "start": """
          state.start = event
          state.ctx.beginPath()
          state.ctx.moveTo(state.start.offsetX, state.start.offsetY)""",
        "draw": """
          if (state.start == null)
            return
          state.ctx.lineTo(event.offsetX, event.offsetY)
          state.ctx.stroke()""",
        "end": "delete state.start",
        "save": "data.value = canvas_el.toDataURL()",
        "clear": """
          state.ctx.clearRect(0, 0, canvas_el.width, canvas_el.height)
          data.value = ""
        """,
        "line_width": "state.ctx.lineWidth = data.line_width",
        "color": "state.ctx.strokeStyle = data.color",
    }

canvas = Canvas(width=300, height=300,)

def png_element(value):
    if not value:
       return "<p style='padding:10px;'>Click <em>Save</em> to show the image here.<p>"
    return f"<img src='{value}'></img>"

png_view = pn.pane.HTML(
    pn.bind(png_element, canvas),
	width=canvas.width,
	height=canvas.height+2,
	margin=(0, 10),
    styles={"border": "1px solid black"},
)

pn.Column(
    "# Drag on the left canvas to draw\n To export the drawing to a `png` image click *Save*.",
    pn.Row(
        pn.Param(
		    canvas.param,
			parameters=['color', 'line_width', 'save', 'clear'],
			show_name=False
		),
        canvas,
        png_view,
    ),
).servable()
```

This example invokes *scripts* in 3 ways:

1. `'render'` is called on initialization
2. `'start'`, `'draw'` and `'end'` are explicitly invoked using the `${script(...)}` syntax in inline callbacks
3. `'line_width'`, `'color'`, `'save'` and `'clear'` are invoked when the parameters change

It also makes extensive use of the available objects in the namespace:

- `'render'`: Accesses the `canvas_el` DOM node by name and saves it to the `state` object to easily access the `canvas_el` in subsequent scripts
- `'start'`, `'draw'`:  Use the `event` object provided by the `onmousedown` and `onmousemove` inline callbacks
- `'save'`, `'clear'`, `'line_width'`, `'color'`: Use the `data` object to get and set the current state of the `value`
