"""
Jupyter Scatter Example -- WebGL Scatter Plot (DOES NOT RENDER)
===============================================================

This example attempts to use jupyter-scatter's JupyterScatter widget
with Panel's AnyWidget pane.

STATUS: DOES NOT RENDER -- WebGL initialization fails inside Panel's
shadow DOM because the container has 0x0 pixel dimensions when
``createScatterplot`` (regl-scatterplot) runs.

Root cause
----------
jupyter-scatter uses `regl-scatterplot`, a WebGL-based renderer that
requires its container element to have **non-zero CSS pixel dimensions**
at the instant `createScatterplot()` is called. Inside Panel's Bokeh
shadow DOM, the ESM render function runs before CSS layout has sized the
container, so the canvas starts at 0x0 pixels.  This causes
``getScatterGlPos`` → ``transformMat4`` to compute a singular projection
matrix, crashing with:

    TypeError: Cannot read properties of null (reading '0') at transformMat4

Even with explicit ``width`` and ``height`` on the AnyWidget pane, the
inner shadow DOM container may still have 0x0 at render time.  Setting
explicit dimensions sometimes silences the crash but the canvas still
fails to initialize -- no scatter plot appears.

This is NOT a binary data issue -- the ``_pnl_bytes`` base64 encoding
correctly delivers the point data.  It is a **container sizing / WebGL
init timing** issue specific to shadow DOM rendering.

GitHub: https://github.com/flekschas/jupyter-scatter
Docs:   https://jupyter-scatter.dev/

NOTE: If both ``jscatter`` (scientific computing) and ``jupyter-scatter``
are installed, the top-level ``jscatter`` namespace may be shadowed.
Import from ``jscatter.jscatter`` to ensure the correct ``Scatter``
class is used.

NOTE: The ``Scatter`` class is a wrapper, not the anywidget itself.
The actual anywidget is ``scatter.widget`` (a ``JupyterScatter`` instance).

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

# Wrap the underlying anywidget with Panel's AnyWidget pane.
# Explicit width/height are set but do NOT fix the WebGL init issue --
# the inner shadow DOM container still has 0×0 at createScatterplot time.
anywidget_pane = pn.pane.AnyWidget(scatter_widget, width=600, height=500)

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

status = pn.pane.Markdown("""
<div style="background-color: #f8d7da; border: 2px solid #dc3545; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #721c24; font-size: 20px; font-weight: bold; margin: 0;">
DOES NOT RENDER -- WebGL initialization fails in shadow DOM
</p>
<p style="color: #721c24; font-size: 14px; margin: 8px 0 0 0;">
jupyter-scatter uses <code>regl-scatterplot</code>, a WebGL renderer that requires
its container to have <strong>non-zero CSS pixel dimensions</strong> when
<code>createScatterplot()</code> runs. Inside Panel's Bokeh shadow DOM, the ESM
render function executes before the browser has laid out the container, so it
starts at 0&times;0 pixels. This causes <code>transformMat4</code> to compute a
singular projection matrix, crashing with
<code>TypeError: Cannot read properties of null (reading '0')</code>.
<br/><br/>
<strong>This is a container sizing / WebGL init timing issue</strong>, not a data
or binary serialization problem. Even explicit <code>width</code>/<code>height</code>
on the pane do not resolve it because the <em>inner</em> shadow DOM container may
still be unsized at render time.
<br/><br/>
<strong>Possible fix (upstream):</strong> regl-scatterplot could defer WebGL init until
the container has non-zero dimensions (e.g. via ResizeObserver), or Panel could
provide a &ldquo;deferred render&rdquo; hook that waits for layout to complete.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown(f"""
# Jupyter Scatter -- Interactive Cluster Explorer

A scatter plot of **{n:,} points** in 4 color-coded clusters, rendered with
high-performance WebGL.

## How to Interact (if rendering works)

- **Zoom:** Scroll to zoom in and out
- **Pan:** Click and drag to move the view
- **Select points:** Click and drag to draw a **lasso** around points.
  Selected point indices appear in the "Selection" readout on the right.
  Click on empty space to clear the selection.
- **Hover:** Move your mouse over a point to see its coordinates and
  cluster label in the "Hovering" readout.

## Display Controls

Use the sliders on the right to adjust **point size**, **opacity**, and
**background color**. Changes update the chart in real time.
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
    status,
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
