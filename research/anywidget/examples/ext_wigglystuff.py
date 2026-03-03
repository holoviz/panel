"""
wigglystuff Comprehensive Example -- All Widgets
=================================================

This example demonstrates ALL widgets from the wigglystuff library
rendered through Panel's AnyWidget pane.

Each widget has a status banner:
  - Green:  Works correctly with Panel
  - Yellow: Works with caveats (e.g., one-way sync only)
  - Red:    Does not work / requires external resources

GitHub: https://github.com/koaning/wigglystuff

Required package:
    pip install wigglystuff

Run with:
    panel serve research/anywidget/examples/ext_wigglystuff.py --port 6130
"""
import math
import random

import pandas as pd

from wigglystuff import (
    ColorPicker, CopyToClipboard, DiffViewer, EdgeDraw, KeystrokeWidget,
    Matrix, Paint, ParallelCoordinates, ProgressBar, PulsarChart,
    ScatterWidget, Slider2D, SortableList, SplineDraw, TangleChoice,
    TangleSelect, TangleSlider, TextCompare, ThreeWidget,
)

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def status_banner(color, title, detail=""):
    """Return a Markdown pane with a colored status banner."""
    colors = {
        "green":  ("#d4edda", "#155724", "#28a745"),
        "yellow": ("#fff3cd", "#856404", "#ffc107"),
        "red":    ("#f8d7da", "#721c24", "#dc3545"),
    }
    bg, fg, border = colors[color]
    detail_html = f'<p style="color: {fg}; font-size: 14px; margin: 6px 0 0 0;">{detail}</p>' if detail else ""
    return pn.pane.Markdown(f"""
<div style="background-color: {bg}; border: 2px solid {border}; border-radius: 8px; padding: 12px 16px; margin: 8px 0;">
<p style="color: {fg}; font-size: 18px; font-weight: bold; margin: 0;">{title}</p>
{detail_html}
</div>
""")


def section(title, description=""):
    """Return a section header."""
    parts = [pn.pane.Markdown(f"---\n## {title}")]
    if description:
        parts.append(pn.pane.Markdown(description))
    return parts


# ===========================================================================
# PAGE HEADER
# ===========================================================================

header = pn.pane.Markdown("""
# wigglystuff -- Comprehensive Widget Gallery

This page demonstrates **every widget** from the
[wigglystuff](https://github.com/koaning/wigglystuff) library, rendered
through Panel's `AnyWidget` pane. Each section includes a status banner,
usage instructions, and (where possible) bidirectional sync with Panel
controls.

**Total widgets in wigglystuff:** 35 classes.
This gallery covers the 19 that are self-contained and demonstrable
without external services, hardware, or Jupyter notebook context.

Widgets not demonstrated here require external services (Neo4j, WandB),
hardware (Gamepad, Webcam, Microphone), Jupyter cell context (CellTour,
DriverTour), network resources (ImageRefreshWidget, HTMLRefreshWidget),
or Altair charts (AltairWidget, ChartMultiSelect, ChartPuck, ChartSelect).
""")

# ===========================================================================
# 1. TangleSlider
# ===========================================================================

tangle_slider = TangleSlider(
    min_value=0, max_value=100, amount=50, step=1,
    prefix="Value: ", suffix=" units"
)
tangle_pane = pn.pane.AnyWidget(tangle_slider)
tangle_comp = tangle_pane.component

tangle_display = pn.pane.Markdown(pn.bind(
    lambda amount: f"**Current amount:** {amount:.1f}",
    tangle_comp.param.amount
))

panel_slider = pn.widgets.FloatSlider(
    name="Panel Slider (synced)", start=0, end=100, step=1, value=50
)
tangle_comp.param.watch(lambda e: setattr(panel_slider, 'value', e.new), ['amount'])
panel_slider.param.watch(lambda e: setattr(tangle_comp, 'amount', e.new), ['value'])

# ===========================================================================
# 2. TangleChoice
# ===========================================================================

tangle_choice = TangleChoice(choices=["red", "green", "blue"])
tangle_choice_pane = pn.pane.AnyWidget(tangle_choice)
tangle_choice_comp = tangle_choice_pane.component

choice_display = pn.pane.Markdown(pn.bind(
    lambda c: f"**Selected choice:** {c}",
    tangle_choice_comp.param.choice
))

# ===========================================================================
# 3. TangleSelect
# ===========================================================================

tangle_select = TangleSelect(choices=["apple", "banana", "cherry", "date"])
tangle_select_pane = pn.pane.AnyWidget(tangle_select)
tangle_select_comp = tangle_select_pane.component

select_display = pn.pane.Markdown(pn.bind(
    lambda c: f"**Selected option:** {c}",
    tangle_select_comp.param.choice
))

# ===========================================================================
# 4. ColorPicker
# ===========================================================================

color_picker = ColorPicker(color="#3b82f6", show_label=True)
color_picker_pane = pn.pane.AnyWidget(color_picker)
color_picker_comp = color_picker_pane.component

color_display = pn.pane.Markdown(pn.bind(
    lambda c: f'**Selected color:** <span style="background-color:{c}; padding: 2px 20px; border-radius: 4px;">&nbsp;</span> `{c}`',
    color_picker_comp.param.color
))

# ===========================================================================
# 5. Slider2D
# ===========================================================================

slider_2d = Slider2D(
    x=0.0, y=0.0,
    x_bounds=(-1.0, 1.0), y_bounds=(-1.0, 1.0),
    width=350, height=350
)
slider_2d_pane = pn.pane.AnyWidget(slider_2d)
slider_2d_comp = slider_2d_pane.component

slider_2d_display = pn.pane.Markdown(pn.bind(
    lambda x, y: f"**Position:** x={x:.3f}, y={y:.3f}",
    slider_2d_comp.param.x, slider_2d_comp.param.y
))

# ===========================================================================
# 6. Matrix
# ===========================================================================

matrix = Matrix(
    rows=3, cols=3, min_value=-10, max_value=10, step=1, digits=0,
    row_names=["Row A", "Row B", "Row C"],
    col_names=["Col 1", "Col 2", "Col 3"],
)
matrix_pane = pn.pane.AnyWidget(matrix)
matrix_comp = matrix_pane.component

matrix_display = pn.pane.Markdown(pn.bind(
    lambda m: f"**Matrix values:** `{m}`",
    matrix_comp.param.matrix
))

# ===========================================================================
# 7. SortableList
# ===========================================================================

sortable = SortableList(
    value=["Python", "JavaScript", "Rust", "Go", "TypeScript"],
    editable=True, removable=True, addable=True,
    label="Programming Languages"
)
sortable_pane = pn.pane.AnyWidget(sortable)
sortable_comp = sortable_pane.component

sortable_display = pn.pane.Markdown(pn.bind(
    lambda v: f"**Current order:** {v}",
    sortable_comp.param.value
))

# ===========================================================================
# 8. ProgressBar
# ===========================================================================

progress = ProgressBar(value=42, max_value=100)
progress_pane = pn.pane.AnyWidget(progress)
progress_comp = progress_pane.component

progress_slider = pn.widgets.IntSlider(
    name="Set Progress", start=0, end=100, step=1, value=42
)
progress_slider.param.watch(lambda e: setattr(progress_comp, 'value', e.new), ['value'])

progress_display = pn.pane.Markdown(pn.bind(
    lambda v: f"**Progress:** {v}%",
    progress_comp.param.value
))

# ===========================================================================
# 9. DiffViewer
# ===========================================================================

diff_viewer = DiffViewer(
    old_contents="def hello():\n    print('Hello, World!')\n    return None\n",
    new_contents="def hello(name: str = 'World'):\n    msg = f'Hello, {name}!'\n    print(msg)\n    return msg\n",
    old_name="hello_v1.py",
    new_name="hello_v2.py",
    diff_style="split",
    expand_unchanged=True,
)
diff_viewer_pane = pn.pane.AnyWidget(diff_viewer)

# ===========================================================================
# 10. TextCompare
# ===========================================================================

text_compare = TextCompare(
    text_a="The quick brown fox jumps over the lazy dog. "
           "Panel is a great library for building dashboards.",
    text_b="The fast brown fox leaps over the lazy dog. "
           "Panel is a great library for building interactive dashboards.",
    min_match_words=3,
)
text_compare_pane = pn.pane.AnyWidget(text_compare)
text_compare_comp = text_compare_pane.component

text_compare_display = pn.pane.Markdown(pn.bind(
    lambda m: f"**Matches found:** {len(m)} common phrases",
    text_compare_comp.param.matches
))

# ===========================================================================
# 11. EdgeDraw
# ===========================================================================

edge_draw = EdgeDraw(
    names=["A", "B", "C", "D", "E"],
    directed=True,
    width=500, height=350,
)
edge_draw_pane = pn.pane.AnyWidget(edge_draw)
edge_draw_comp = edge_draw_pane.component

edge_display = pn.pane.Markdown(pn.bind(
    lambda links: f"**Edges:** {links}" if links else "**Edges:** (none drawn yet)",
    edge_draw_comp.param.links
))

# ===========================================================================
# 12. Paint
# ===========================================================================

paint = Paint(width=600, height=350)
paint_pane = pn.pane.AnyWidget(paint)
paint_comp = paint_pane.component

paint_display = pn.pane.Markdown(pn.bind(
    lambda b: f"**Canvas data:** {'Has content' if b else 'Empty'} ({len(b)} chars base64)",
    paint_comp.param.base64
))

# ===========================================================================
# 13. ScatterWidget
# ===========================================================================

scatter_data = [
    {"x": random.gauss(0.3, 0.08), "y": random.gauss(0.3, 0.08), "c": 0}
    for _ in range(30)
] + [
    {"x": random.gauss(0.7, 0.08), "y": random.gauss(0.7, 0.08), "c": 1}
    for _ in range(30)
]

scatter = ScatterWidget(
    data=scatter_data, n_classes=4, brushsize=30,
    width=500, height=400,
)
scatter_pane = pn.pane.AnyWidget(scatter)
scatter_comp = scatter_pane.component

scatter_display = pn.pane.Markdown(pn.bind(
    lambda d: f"**Points:** {len(d)} total",
    scatter_comp.param.data
))

# ===========================================================================
# 14. SplineDraw
# ===========================================================================

import numpy as np


def simple_spline(x, y):
    """Linear interpolation spline: return evenly spaced points along the line."""
    if len(x) < 2:
        return x, y
    order = np.argsort(x)
    x_sorted, y_sorted = x[order], y[order]
    x_curve = np.linspace(x_sorted.min(), x_sorted.max(), 200)
    y_curve = np.interp(x_curve, x_sorted, y_sorted)
    return x_curve, y_curve


spline = SplineDraw(
    spline_fn=simple_spline,
    n_classes=2, brushsize=30,
    width=500, height=350,
)
spline_pane = pn.pane.AnyWidget(spline)
spline_comp = spline_pane.component


def _format_spline_info(data, curve, curve_error):
    """Format drawn points and computed spline for display."""
    if not data:
        return "**Drawn points:** (click on the canvas to add points)"

    # Group points by color class
    groups = {}
    for pt in data:
        color = pt.get("color", "unknown")
        groups.setdefault(color, []).append(pt)

    lines = [f"**Drawn points:** {len(data)} total across {len(groups)} class(es)\n"]

    for color, pts in groups.items():
        xs = [f'{p["x"]:.1f}' for p in pts[:8]]
        ys = [f'{p["y"]:.1f}' for p in pts[:8]]
        suffix = ", ..." if len(pts) > 8 else ""
        lines.append(f"- **{color}** ({len(pts)} pts): x=[{', '.join(xs)}{suffix}], y=[{', '.join(ys)}{suffix}]")

    if curve:
        lines.append(f"\n**Computed spline:** {len(curve)} curve(s)")
        for c in curve:
            n_pts = len(c.get("points", []))
            lines.append(f"- **{c['color']}**: {n_pts} interpolated points")

    if curve_error:
        lines.append(f"\n**Spline error:** {curve_error}")

    return "\n".join(lines)


spline_display = pn.pane.Markdown(pn.bind(
    _format_spline_info,
    spline_comp.param.data,
    spline_comp.param.curve,
    spline_comp.param.curve_error,
))

# Show the raw data as a JSON pane so users can see the exact structure
spline_json = pn.pane.JSON(
    pn.bind(lambda d, c: {"drawn_points": d, "spline_curves": c}, spline_comp.param.data, spline_comp.param.curve),
    depth=2, name="SplineDraw Data (live)", height=200,
)

# ===========================================================================
# 15. CopyToClipboard
# ===========================================================================

copy_widget = CopyToClipboard(text_to_copy="Hello from Panel + wigglystuff!")
copy_pane = pn.pane.AnyWidget(copy_widget)

# ===========================================================================
# 16. KeystrokeWidget
# ===========================================================================

keystroke = KeystrokeWidget()
keystroke_pane = pn.pane.AnyWidget(keystroke)
keystroke_comp = keystroke_pane.component

keystroke_display = pn.pane.Markdown(pn.bind(
    lambda k: f"**Last key:** `{k}`" if k else "**Last key:** (press a key)",
    keystroke_comp.param.last_key
))

# ===========================================================================
# 17. ThreeWidget (3D scatter)
# ===========================================================================

three_data = []
for i in range(80):
    t = i / 80 * 2 * math.pi
    three_data.append({
        "x": math.cos(t) * (1 + 0.3 * math.sin(3 * t)),
        "y": math.sin(t) * (1 + 0.3 * math.sin(3 * t)),
        "z": 0.5 * math.sin(2 * t),
        "r": int(127 + 127 * math.cos(t)),
        "g": int(127 + 127 * math.sin(t)),
        "b": 180,
    })

three_widget = ThreeWidget(
    data=three_data,
    width=500, height=400,
    auto_rotate=True,
    auto_rotate_speed=2.0,
    show_axes=True,
    show_grid=True,
)
three_pane = pn.pane.AnyWidget(three_widget)

# ===========================================================================
# 18. PulsarChart
# ===========================================================================

n_rows = 12
n_points = 80
x_vals = [i / n_points for i in range(n_points)]
pulsar_rows = {}
for row in range(n_rows):
    phase = row / n_rows * 2 * math.pi
    pulsar_rows[f"Signal {row+1}"] = [
        0.3 * math.sin(2 * math.pi * x + phase) +
        0.5 * math.exp(-((x - 0.5) ** 2) / 0.01) * (1 + 0.5 * math.sin(row))
        for x in x_vals
    ]

pulsar_df = pd.DataFrame(pulsar_rows, index=x_vals).T

pulsar = PulsarChart(
    df=pulsar_df,
    overlap=0.6,
    peak_scale=1.0,
    fill_opacity=0.8,
    stroke_width=1.5,
    width=500, height=400,
    x_label="Frequency",
    y_label="Signal",
)
pulsar_pane = pn.pane.AnyWidget(pulsar)
pulsar_comp = pulsar_pane.component

pulsar_display = pn.pane.Markdown(pn.bind(
    lambda idx: f"**Selected row:** {idx}" if idx is not None else "**Selected row:** (click a row)",
    pulsar_comp.param.selected_index
))

# ===========================================================================
# 19. ParallelCoordinates
# ===========================================================================

parallel_data = []
for i in range(50):
    parallel_data.append({
        "Sepal Length": round(random.gauss(5.8, 0.8), 1),
        "Sepal Width": round(random.gauss(3.0, 0.4), 1),
        "Petal Length": round(random.gauss(3.7, 1.5), 1),
        "Petal Width": round(random.gauss(1.2, 0.7), 1),
        "Species": random.choice(["setosa", "versicolor", "virginica"]),
    })

parallel = ParallelCoordinates(
    data=parallel_data,
    color_by="Species",
    width=800,
    height=400,
)
parallel_pane = pn.pane.AnyWidget(parallel)
parallel_comp = parallel_pane.component

parallel_display = pn.pane.Markdown(pn.bind(
    lambda f: f"**Filtered indices:** {len(f)} rows" if f else "**Filtered indices:** (drag axes to filter)",
    parallel_comp.param.filtered_indices
))


# ===========================================================================
# ASSEMBLY
# ===========================================================================

page = pn.Column(
    header,
    max_width=900,
    styles={"margin": "0 auto"},
)

# --- 1. TangleSlider ---
page.extend(section(
    "1. TangleSlider",
    "An inline draggable number. **Click and drag left/right** on the number to change it."
))
page.append(status_banner(
    "yellow", "ONE-WAY SYNC (Widget -> Panel)",
    "TangleSlider reads <code>amount</code> once at render and does not listen for external updates. "
    "Dragging updates Panel, but Panel slider changes do not update the TangleSlider display."
))
page.extend([
    pn.Row(pn.Spacer(width=20), tangle_pane),
    tangle_display, panel_slider,
])

# --- 2. TangleChoice ---
page.extend(section(
    "2. TangleChoice",
    "An inline text widget that cycles through choices on click."
))
page.append(status_banner("green", "WORKS"))
page.extend([tangle_choice_pane, choice_display])

# --- 3. TangleSelect ---
page.extend(section(
    "3. TangleSelect",
    "A dropdown-style inline selector. Click to show choices."
))
page.append(status_banner("green", "WORKS"))
page.extend([tangle_select_pane, select_display])

# --- 4. ColorPicker ---
page.extend(section(
    "4. ColorPicker",
    "A color picker widget. Click to open the color palette."
))
page.append(status_banner("green", "WORKS"))
page.extend([color_picker_pane, color_display])

# --- 5. Slider2D ---
page.extend(section(
    "5. Slider2D",
    "A 2D slider pad. **Click and drag** inside the box to set X/Y coordinates."
))
page.append(status_banner("green", "WORKS"))
page.extend([slider_2d_pane, slider_2d_display])

# --- 6. Matrix ---
page.extend(section(
    "6. Matrix",
    "An editable matrix of numbers. **Click a cell** and type to change values, "
    "or **drag left/right** on a cell to adjust."
))
page.append(status_banner("green", "WORKS"))
page.extend([matrix_pane, matrix_display])

# --- 7. SortableList ---
page.extend(section(
    "7. SortableList",
    "A drag-and-drop sortable list. **Drag items** to reorder. "
    "Use the + button to add, x to remove, and pencil to edit."
))
page.append(status_banner("green", "WORKS"))
page.extend([sortable_pane, sortable_display])

# --- 8. ProgressBar ---
page.extend(section(
    "8. ProgressBar",
    "A simple progress bar. Use the Panel slider below to change the value."
))
page.append(status_banner("green", "WORKS"))
page.extend([progress_pane, progress_display, progress_slider])

# --- 9. DiffViewer ---
page.extend(section(
    "9. DiffViewer",
    "A side-by-side diff viewer for comparing text. Shows additions, deletions, and unchanged lines."
))
page.append(status_banner("green", "WORKS"))
page.append(diff_viewer_pane)

# --- 10. TextCompare ---
page.extend(section(
    "10. TextCompare",
    "Highlights common phrases between two texts. Matched phrases are highlighted."
))
page.append(status_banner("green", "WORKS"))
page.extend([text_compare_pane, text_compare_display])

# --- 11. EdgeDraw ---
page.extend(section(
    "11. EdgeDraw",
    "Draw directed edges between nodes. **Click a source node, then a target node** to create an edge."
))
page.append(status_banner("green", "WORKS"))
page.extend([edge_draw_pane, edge_display])

# --- 12. Paint ---
page.extend(section(
    "12. Paint",
    "A freehand drawing canvas. Use the toolbar to select brush, color, and size."
))
page.append(status_banner("green", "WORKS"))
page.extend([paint_pane, paint_display])

# --- 13. ScatterWidget ---
page.extend(section(
    "13. ScatterWidget",
    "An interactive scatter plot for labeling data. **Click** to paint points with "
    "the selected class. Use the class buttons to switch classes."
))
page.append(status_banner("green", "WORKS"))
page.extend([scatter_pane, scatter_display])

# --- 14. SplineDraw ---
page.extend(section(
    "14. SplineDraw",
    "Draw spline curves on a canvas. **Click** to add points. "
    "The widget fits a smooth spline through your points.\n\n"
    "This example demonstrates **browser → Python data sync**: drawn points and "
    "computed spline curves are sent back to Panel in real time. "
    "The JSON pane below shows the raw data structure."
))
page.append(status_banner("green", "WORKS — Full data sync to Python"))
page.extend([spline_pane, spline_display, spline_json])

# --- 15. CopyToClipboard ---
page.extend(section(
    "15. CopyToClipboard",
    "A button that copies text to the clipboard. Click the button to copy."
))
page.append(status_banner("green", "WORKS"))
page.append(copy_pane)

# --- 16. KeystrokeWidget ---
page.extend(section(
    "16. KeystrokeWidget",
    "Captures keyboard events. **Click inside the widget area, then press any key.**"
))
page.append(status_banner("green", "WORKS"))
page.extend([keystroke_pane, keystroke_display])

# --- 17. ThreeWidget ---
page.extend(section(
    "17. ThreeWidget (3D Scatter)",
    "A 3D scatter plot using Three.js. **Click and drag** to rotate, scroll to zoom."
))
page.append(status_banner("green", "WORKS"))
page.append(three_pane)

# --- 18. PulsarChart ---
page.extend(section(
    "18. PulsarChart",
    "A joy-plot / ridgeline chart. **Click a row** to select it."
))
page.append(status_banner("green", "WORKS"))
page.extend([pulsar_pane, pulsar_display])

# --- 19. ParallelCoordinates ---
page.extend(section(
    "19. ParallelCoordinates",
    "A parallel coordinates chart for multivariate data. "
    "**Drag on an axis** to create a filter range."
))
page.append(status_banner("green", "WORKS"))
page.extend([parallel_pane, parallel_display])

# --- Not Demonstrated ---
page.extend(section("Widgets Not Demonstrated"))
page.append(pn.pane.Markdown("""
The following wigglystuff widgets are **not demonstrated** because they require
external services, hardware, or Jupyter notebook context:

| Widget | Reason |
|--------|--------|
| **AltairWidget** | Requires an Altair chart spec |
| **ApiDoc** | Requires a Python module doc dict |
| **CellTour / DriverTour** | Requires Jupyter notebook cell context |
| **ChartMultiSelect** | Requires a base64-encoded chart image |
| **ChartPuck** | Requires a base64-encoded chart image |
| **ChartSelect** | Requires a base64-encoded chart image |
| **EnvConfig** | Requires environment variable configuration |
| **GamepadWidget** | Requires a physical gamepad controller |
| **HTMLRefreshWidget** | Requires a URL to fetch HTML from |
| **ImageRefreshWidget** | Requires a URL to fetch images from |
| **ModuleTreeWidget** | Requires a module tree dict |
| **Neo4jWidget** | Requires a Neo4j database connection |
| **WandbChart** | Requires a Weights & Biases API key |
| **WebcamCapture** | Requires camera hardware access |
| **WebkitSpeechToTextWidget** | Requires microphone + WebKit browser |
"""))

page.servable()
