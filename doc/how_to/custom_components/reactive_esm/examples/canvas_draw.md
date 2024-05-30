# Build a Custom Canvas Component

```python
import param
import panel as pn

pn.extension()

class Canvas(pn.ReactiveESM):

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
    let start = null

    canvas.onmousedown = (event) => {
        start = event
        ctx.beginPath()
        ctx.moveTo(start.offsetX, start.offsetY)
    }
    canvas.onmousemove = (event) => {
        if (start == null)
            return
        ctx.lineTo(event.offsetX, event.offsetY)
        ctx.stroke()
    }
    canvas.onmouseup = () => {
        start = null
    }

    // Create clear button
    const clearButton = document.createElement('button');
    clearButton.textContent = 'Clear';
    clearButton.onclick = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        model.uri=""
    }

    // Create save button
    const saveButton = document.createElement('button');
    saveButton.textContent = 'Save';
    saveButton.onclick = () => {
        model.uri = canvas.toDataURL();
    };

    // Append elements to the parent element
    el.appendChild(canvas);
    el.appendChild(clearButton);
    el.appendChild(saveButton);
}
"""

canvas = Canvas(height=400, width=400)
html = pn.rx("<img src='{uri}'></img>").format(uri=canvas.param.uri)
png_view = pn.pane.HTML(html, height=400)

pn.Row(
    pn.Column(
        '# Drag on canvas to draw\n To export the drawing to a png click save.',
        pn.Row(
            canvas,
            png_view
        ),
    )
).servable()
```
