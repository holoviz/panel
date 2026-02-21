"""
Jupyter Scatter Example with Bidirectional Sync
================================================

This example demonstrates using jupyter-scatter's JupyterScatter widget
with Panel's AnyWidget pane and bidirectional sync between the widget
and Panel controls.

Jupyter Scatter is built on anywidget.AnyWidget and uses regl-scatterplot
for high-performance WebGL rendering. It can handle millions of points.
The widget's ESM is loaded from a bundled `bundle.js` file.

The JupyterScatter widget (accessed via `scatter.widget`) exposes many
traitlets for appearance (color, size, opacity), interaction (selection,
hovering, lasso), camera state, and data encoding. The high-level
`jscatter.Scatter` class wraps this widget with a convenient API.

NOTE: If both `jscatter` (scientific computing) and `jupyter-scatter` are
installed, the top-level `jscatter` namespace may be shadowed. Import from
`jscatter.jscatter` to ensure the correct `Scatter` class is used.

NOTE: The `Scatter` class is a wrapper, not the anywidget itself.
The actual anywidget is `scatter.widget` (a `JupyterScatter` instance).
We must pass `scatter.widget` to pn.pane.AnyWidget(), not `scatter`.

Required packages:
    pip install jupyter-scatter pandas numpy

Run with:
    panel serve research/anywidget/examples/ext_jupyter_scatter.py
"""

import numpy as np
import pandas as pd

from jscatter.jscatter import Scatter

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create sample data
# ---------------------------------------------------------------------------

np.random.seed(42)
n = 5000

# Create clustered scatter data
clusters = []
centers = [(0, 0), (3, 3), (-3, 3), (3, -3)]
labels = ["Cluster A", "Cluster B", "Cluster C", "Cluster D"]

for i, (cx, cy) in enumerate(centers):
    cluster_n = n // len(centers)
    clusters.append(pd.DataFrame({
        "x": np.random.randn(cluster_n) * 0.8 + cx,
        "y": np.random.randn(cluster_n) * 0.8 + cy,
        "category": labels[i],
        "value": np.random.uniform(0, 100, cluster_n),
    }))

df = pd.concat(clusters, ignore_index=True)

# ---------------------------------------------------------------------------
# 2. Create the Scatter plot and extract the anywidget
# ---------------------------------------------------------------------------

scatter = Scatter(
    data=df,
    x="x",
    y="y",
    color_by="category",
    size=3,
    height=500,
)

# The actual anywidget is scatter.widget (JupyterScatter instance)
scatter_widget = scatter.widget

# Wrap the underlying anywidget with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(scatter_widget)

# ---------------------------------------------------------------------------
# 3. Wire up Panel controls for bidirectional sync
# ---------------------------------------------------------------------------

component = anywidget_pane.component

# --- Point size control ---
size_slider = pn.widgets.IntSlider(
    name="Point Size", start=1, end=20, value=3, width=250
)

def on_size_change(event):
    component.size = event.new

size_slider.param.watch(on_size_change, "value")
component.param.watch(lambda e: setattr(size_slider, "value", e.new), ["size"])

# --- Opacity control ---
opacity_slider = pn.widgets.FloatSlider(
    name="Opacity", start=0.1, end=1.0, value=1.0, step=0.1, width=250
)

def on_opacity_change(event):
    component.opacity = event.new

opacity_slider.param.watch(on_opacity_change, "value")
component.param.watch(lambda e: setattr(opacity_slider, "value", e.new), ["opacity"])

# --- Background color ---
bg_color = pn.widgets.ColorPicker(
    name="Background Color", value="#ffffff", width=250
)

def on_bg_change(event):
    component.background_color = event.new

bg_color.param.watch(on_bg_change, "value")

# --- Selection display ---
selection_display = pn.pane.Markdown(
    "**Selection:** None (use lasso or click to select points)",
    sizing_mode="stretch_width",
)

def on_selection_change(*events):
    for event in events:
        if event.name == "selection":
            sel = event.new
            if sel is not None and len(sel) > 0:
                n_sel = len(sel)
                preview = list(sel[:10])
                text = f"**Selection:** {n_sel} points selected"
                if n_sel > 10:
                    text += f" (showing first 10: {preview}...)"
                else:
                    text += f" (indices: {preview})"
                selection_display.object = text
            else:
                selection_display.object = "**Selection:** None"

component.param.watch(on_selection_change, ["selection"])

# --- Hovering display ---
hover_display = pn.pane.Markdown(
    "**Hovering:** Move mouse over points",
    sizing_mode="stretch_width",
)

def on_hover_change(*events):
    for event in events:
        if event.name == "hovering":
            idx = event.new
            if idx is not None and idx >= 0:
                row = df.iloc[idx]
                hover_display.object = (
                    f"**Hovering:** Point {idx} — "
                    f"({row['x']:.2f}, {row['y']:.2f}) "
                    f"[{row['category']}]"
                )
            else:
                hover_display.object = "**Hovering:** None"

component.param.watch(on_hover_change, ["hovering"])

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

header = pn.pane.Markdown(f"""
# Jupyter Scatter — AnyWidget Pane Demo

This example renders **jupyter-scatter's JupyterScatter** widget (an anywidget)
natively in Panel using the `AnyWidget` pane with bidirectional sync.

**{n} points** in 4 clusters are rendered via WebGL (regl-scatterplot).

## Interaction

- **Pan/Zoom:** Scroll to zoom, drag to pan
- **Lasso Select:** Click and drag to lasso-select points
- **Hover:** Move the mouse over points to see details

## Bidirectional Sync

- **Panel to Widget:** Adjust the sliders and color picker to change the widget
- **Widget to Panel:** Selection and hover info update in real-time from the widget
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("### Display Controls"),
    size_slider,
    opacity_slider,
    bg_color,
    pn.pane.Markdown("### Interaction Feedback"),
    hover_display,
    selection_display,
    width=350,
)

pn.Column(
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### Scatter Plot"),
            anywidget_pane,
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=1000,
).servable()
