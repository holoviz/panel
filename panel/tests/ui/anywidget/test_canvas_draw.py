"""
Playwright test for the canvas_draw anywidget example.

Tests:
    1. Widget renders (canvas element appears)
    2. No unexpected console errors
    3. Browser -> Python sync (draw on canvas, stroke_count increments)
    4. Python -> Browser sync (clear strokes from Python, canvas resets)
"""
import anywidget
import pytest
import traitlets

import panel as pn

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.tests.util import serve_component, wait_until

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui


# --- Widget definition (same as research/anywidget/examples/canvas_draw.py) ---

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
                    if (stroke.length === 1) {
                        const [x, y] = stroke[0];
                        ctx.beginPath();
                        ctx.arc(x, y, 2, 0, Math.PI * 2);
                        ctx.fill();
                    } else {
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

    strokes = traitlets.List([], help="List of strokes").tag(sync=True)
    stroke_count = traitlets.Int(0, help="Total number of strokes drawn").tag(sync=True)


def test_canvas_renders(page):
    """Widget renders and the canvas element appears."""
    widget = CanvasWidget(strokes=[], stroke_count=0)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    canvas = page.locator("canvas.draw-canvas")
    expect(canvas).to_be_visible()

    assert_no_console_errors(msgs)


def test_canvas_draw_stroke(page):
    """Drawing on the canvas increments stroke_count (browser -> Python sync)."""
    widget = CanvasWidget(strokes=[], stroke_count=0)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    canvas = page.locator("canvas.draw-canvas")
    expect(canvas).to_be_visible()

    # Simulate a mouse drag (draw a stroke) on the canvas
    box = canvas.bounding_box()
    start_x = box["x"] + 50
    start_y = box["y"] + 50
    end_x = box["x"] + 150
    end_y = box["y"] + 150

    page.mouse.move(start_x, start_y)
    page.mouse.down()
    page.mouse.move(end_x, end_y, steps=5)
    page.mouse.up()

    # Wait for Python-side stroke_count to update
    wait_until(lambda: widget.stroke_count == 1, page)
    assert pane.component.stroke_count == 1
    assert len(widget.strokes) == 1

    assert_no_console_errors(msgs)


def test_canvas_multiple_strokes(page):
    """Drawing multiple strokes increments stroke_count correctly."""
    widget = CanvasWidget(strokes=[], stroke_count=0)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    canvas = page.locator("canvas.draw-canvas")
    box = canvas.bounding_box()

    # Draw first stroke
    page.mouse.move(box["x"] + 50, box["y"] + 50)
    page.mouse.down()
    page.mouse.move(box["x"] + 100, box["y"] + 100, steps=3)
    page.mouse.up()

    wait_until(lambda: widget.stroke_count == 1, page)

    # Draw second stroke
    page.mouse.move(box["x"] + 200, box["y"] + 50)
    page.mouse.down()
    page.mouse.move(box["x"] + 250, box["y"] + 150, steps=3)
    page.mouse.up()

    wait_until(lambda: widget.stroke_count == 2, page)
    assert len(widget.strokes) == 2

    assert_no_console_errors(msgs)


def test_canvas_clear_from_python(page):
    """Clearing strokes from Python resets the widget state (Python -> browser sync)."""
    widget = CanvasWidget(strokes=[], stroke_count=0)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    canvas = page.locator("canvas.draw-canvas")
    box = canvas.bounding_box()

    # Draw a stroke first
    page.mouse.move(box["x"] + 50, box["y"] + 50)
    page.mouse.down()
    page.mouse.move(box["x"] + 150, box["y"] + 150, steps=5)
    page.mouse.up()

    wait_until(lambda: widget.stroke_count == 1, page)

    # Clear from Python side
    pane.component.strokes = []
    pane.component.stroke_count = 0

    wait_until(lambda: widget.stroke_count == 0, page)
    assert widget.strokes == []

    assert_no_console_errors(msgs)
