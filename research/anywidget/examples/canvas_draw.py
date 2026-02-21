"""
Drawing canvas anywidget demonstrating complex interaction with List traitlet.

This example demonstrates:
- Defining a custom anywidget with List and Int traitlets
- Handling mouse events for drawing on a canvas element
- Complex state management with stroke coordinates
- Bidirectional synchronization with Panel widgets

Run with: panel serve research/anywidget/examples/canvas_draw.py
"""
import anywidget
import traitlets

import panel as pn

pn.extension()


class CanvasWidget(anywidget.AnyWidget):
    """A drawing canvas widget that tracks strokes."""

    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "canvas-container";

        let canvas = document.createElement("canvas");
        canvas.width = 400;
        canvas.height = 300;
        canvas.className = "draw-canvas";
        canvas.style.backgroundColor = "white";
        canvas.style.border = "2px solid #333";
        canvas.style.cursor = "crosshair";

        let ctx = canvas.getContext("2d");
        ctx.strokeStyle = "#333";
        ctx.lineWidth = 2;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";
        ctx.fillStyle = "#333";

        let isDrawing = false;
        let currentStroke = [];

        canvas.addEventListener("mousedown", (e) => {
            isDrawing = true;
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            currentStroke = [[x, y]];
            ctx.beginPath();
            ctx.moveTo(x, y);

            // Draw a small dot at the click position for visual feedback
            ctx.arc(x, y, 2, 0, Math.PI * 2);
            ctx.fill();
        });

        canvas.addEventListener("mousemove", (e) => {
            if (!isDrawing) return;
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            currentStroke.push([x, y]);
            ctx.lineTo(x, y);
            ctx.stroke();
        });

        canvas.addEventListener("mouseup", () => {
            if (isDrawing && currentStroke.length > 0) {
                isDrawing = false;
                ctx.closePath();

                // IMPORTANT: Create a NEW array (immutable update) so change detection works.
                // Mutating in-place (e.g. strokes.push()) means the reference stays the same,
                // and the framework won't detect a change.
                let strokes = model.get("strokes") || [];
                model.set("strokes", [...strokes, currentStroke]);
                model.set("stroke_count", (model.get("stroke_count") || 0) + 1);

                model.save_changes();
            }
        });

        canvas.addEventListener("mouseleave", () => {
            isDrawing = false;
        });

        container.appendChild(canvas);
        el.appendChild(container);

        // Listen for changes to strokes (e.g., clear from Python)
        model.on("change:strokes", () => {
            let strokes = model.get("strokes") || [];
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.strokeStyle = "#333";
            ctx.lineWidth = 2;
            ctx.lineCap = "round";
            ctx.lineJoin = "round";
            ctx.fillStyle = "#333";

            strokes.forEach((stroke) => {
                if (stroke.length > 0) {
                    // Handle single-point clicks (draw a dot)
                    if (stroke.length === 1) {
                        const [x, y] = stroke[0];
                        ctx.beginPath();
                        ctx.arc(x, y, 2, 0, Math.PI * 2);
                        ctx.fill();
                    } else {
                        // Handle multi-point strokes (draw lines)
                        ctx.beginPath();
                        ctx.moveTo(stroke[0][0], stroke[0][1]);
                        for (let i = 1; i < stroke.length; i++) {
                            ctx.lineTo(stroke[i][0], stroke[i][1]);
                        }
                        ctx.stroke();
                    }
                    ctx.closePath();
                }
            });
        });
    }
    export default { render };
    """

    _css = """
    .canvas-container {
        padding: 20px;
        display: flex;
        justify-content: center;
    }

    .draw-canvas {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        background-color: white;
    }
    """

    strokes = traitlets.List([], help="List of strokes, each stroke is a list of [x, y] coordinates").tag(sync=True)
    stroke_count = traitlets.Int(0, help="Total number of strokes drawn").tag(sync=True)


# Create the anywidget instance and wrap it with Panel
widget = CanvasWidget(strokes=[], stroke_count=0)
pane = pn.pane.AnyWidget(widget)

# pane.component is available immediately — use param API
component = pane.component

# Create widgets to display stroke count and clear canvas
stroke_count_display = pn.pane.Markdown(pn.bind(
    lambda n: f"**Strokes:** {n}", component.param.stroke_count
))
clear_button = pn.widgets.Button(name="Clear Canvas", button_type="danger")


def clear_canvas(event):
    component.strokes = []
    component.stroke_count = 0


clear_button.on_click(clear_canvas)

# Layout
header = pn.pane.Markdown("""
# Drawing Canvas Example — AnyWidget Pane + Complex Interaction

This example demonstrates **complex mouse interaction** with List and Int
traitlets.  The canvas is an anywidget rendered via ESM.  Each stroke is
stored as a list of `[x, y]` coordinates in the `strokes` List traitlet.

**Try it:**
1. **Draw on the canvas** — stroke count updates on the Python side.
2. **Click "Clear Canvas"** — the Panel button resets the traitlets, and
   the anywidget canvas clears via bidirectional sync.

**API used:** `pn.bind(func, component.param.stroke_count)` for reactive display,
and direct `component.strokes = []` for clear. No `widget.observe()` needed!
""")

pn.Column(
    header,
    pn.pane.Markdown("### Anywidget (browser-side canvas)"),
    pane,
    pn.pane.Markdown("### Panel Widgets (Python-side controls)"),
    pn.Row(stroke_count_display, clear_button),
).servable()
