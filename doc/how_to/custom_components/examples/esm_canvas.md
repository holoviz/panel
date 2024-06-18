# Build a Custom Canvas Component

```{pyodide}
import param
import panel as pn

from panel.custom import JSComponent

pn.extension()

class Canvas(JSComponent):

    color = param.Color(default='#000000')

    line_width = param.Number(default=1, bounds=(0.1, 10))

    uri = param.String()

    _esm = """
export function render({model, el}){
    // Create canvas
    const canvas = document.createElement('canvas');
    canvas.style.border = '1px solid';
    canvas.width = model.width;
    canvas.height = model.height;
    const ctx = canvas.getContext("2d")

    // Set up drawing handlers
    let start = null
    canvas.addEventListener('mousedown', (event) => {
      start = event
      ctx.beginPath()
      ctx.moveTo(start.offsetX, start.offsetY)
    })
    canvas.addEventListener('mousemove', (event) => {
      if (start == null)
        return
      ctx.lineTo(event.offsetX, event.offsetY)
      ctx.stroke()
    })
    canvas.addEventListener('mouseup', () => {
      start = null
    })

    // Update styles
    model.watch(() => {
      ctx.lineWidth = model.line_width;
      ctx.strokeStyle = model.color;
    }, ['color', 'line_width'])

    // Create clear button
    const clearButton = document.createElement('button');
    clearButton.textContent = 'Clear';
    clearButton.addEventListener('click', () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      model.uri = ""
    })
    // Create save button
    const saveButton = document.createElement('button');
    saveButton.textContent = 'Save';
    saveButton.addEventListener('click', () => {
      model.uri = canvas.toDataURL();
    })
    // Append elements to the parent element
    el.appendChild(canvas);
    el.appendChild(clearButton);
    el.appendChild(saveButton);
}
"""

canvas = Canvas(height=400, width=400)
png_view = pn.pane.HTML(
    pn.rx("<img src='{uri}'></img>").format(uri=canvas.param.uri),
    height=400
)

pn.Column(
    '# Drag on canvas to draw\n To export the drawing to a png click save.',
    pn.Param(
        canvas.param,
        default_layout=pn.Row,
        parameters=['color', 'line_width'],
        show_name=False
    ),
    pn.Row(
        canvas,
        png_view
    ),
).servable()
```
