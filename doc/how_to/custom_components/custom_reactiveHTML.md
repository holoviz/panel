# Build Components from Scratch



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
