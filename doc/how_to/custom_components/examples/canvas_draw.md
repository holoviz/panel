# Build a Custom Canvas Component

```{pyodide}
import param
import panel as pn

from panel.reactive import ReactiveHTML

pn.extension(template='bootstrap')
```

This example shows how to use the `ReactiveHTML` component to develop a **Drawable Canvas**.

```{pyodide}
class Canvas(ReactiveHTML):

    color = param.Color(default='#000000')

    line_width = param.Number(default=1, bounds=(0.1, 10))

    uri = param.String()

    _template = """
    <canvas
      id="canvas"
      style="border: 1px solid"
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

canvas = Canvas(width=400, height=400)

# We create a separate HTML element which syncs with the uri parameter of the Canvas

png_view = pn.pane.HTML(height=400)

canvas.jslink(png_view, code={'uri': "target.text = `<img src='${source.uri}'></img>`"})

pn.Row(
    canvas.controls(['color', 'line_width']).servable(target='sidebar'),
    pn.Column(
        '# Drag on canvas to draw\n To export the drawing to a png click save.',
        pn.Row(
            canvas,
            png_view
        ),
    ).servable()
)
```
