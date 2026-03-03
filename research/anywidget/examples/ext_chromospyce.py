"""
ChromoSpyce Example — 3D Chromosome Visualization
===================================================

This example demonstrates using ChromoSpyce with Panel's AnyWidget pane.
ChromoSpyce renders 3D chromosome structure data in the browser using WebGL.

GitHub: https://github.com/nicheill/chromospyce

Key traitlets:
    - structure (Bytes): 3D structure data in Arrow format (from numpy or pandas)
    - viewconfig (Dict): Configuration for the 3D viewer

Required package:
    pip install chromospyce

Run with:
    panel serve research/anywidget/examples/ext_chromospyce.py
"""

import numpy as np

from chromospyce import Widget as ChromoWidget

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create 3D chromosome structure data
# ---------------------------------------------------------------------------

def make_helix(n_points=200, turns=6, radius=1.0, height=10.0):
    """Generate a helical 3D structure resembling a chromosome fiber."""
    t = np.linspace(0, turns * 2 * np.pi, n_points)
    x = radius * np.cos(t)
    y = radius * np.sin(t)
    z = np.linspace(0, height, n_points)
    return np.column_stack([x, y, z])


def make_double_helix(n_points=200, turns=6, radius=1.0, height=10.0, separation=0.3):
    """Generate a double helix structure."""
    t = np.linspace(0, turns * 2 * np.pi, n_points)
    x1 = radius * np.cos(t) + separation
    y1 = radius * np.sin(t)
    x2 = radius * np.cos(t + np.pi) - separation
    y2 = radius * np.sin(t + np.pi)
    z = np.linspace(0, height, n_points)
    # Interleave the two strands
    x = np.concatenate([x1, x2])
    y = np.concatenate([y1, y2])
    z = np.concatenate([z, z])
    return np.column_stack([x, y, z])


STRUCTURES = {
    "Single Helix": lambda: make_helix(200, turns=6),
    "Double Helix": lambda: make_double_helix(200, turns=6),
    "Compact (tight turns)": lambda: make_helix(300, turns=12, radius=0.5, height=5.0),
    "Extended (loose turns)": lambda: make_helix(150, turns=3, radius=1.5, height=15.0),
    "Random Walk": lambda: np.cumsum(np.random.randn(200, 3) * 0.3, axis=0),
}

# Create the initial widget
initial_structure = STRUCTURES["Single Helix"]()
widget = ChromoWidget(initial_structure)

# Wrap with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(widget, height=500, sizing_mode="stretch_width")
component = anywidget_pane.component

# ---------------------------------------------------------------------------
# 2. Panel controls
# ---------------------------------------------------------------------------

structure_select = pn.widgets.Select(
    name="Structure",
    options=list(STRUCTURES.keys()),
    value="Single Helix",
    width=250,
)

n_points_slider = pn.widgets.IntSlider(
    name="Number of Points",
    start=50,
    end=500,
    step=50,
    value=200,
    width=250,
)


def on_structure_change(event):
    """Update the 3D structure when selection changes."""
    structure_data = STRUCTURES[event.new]()
    new_widget = ChromoWidget(structure_data)
    component.structure = new_widget.structure


structure_select.param.watch(on_structure_change, "value")

# Display structure info
info_display = pn.pane.Markdown(
    pn.bind(
        lambda s: f"**Structure bytes:** {len(s):,}" if s else "No structure loaded",
        component.param.structure,
    ),
    sizing_mode="stretch_width",
)

# Viewconfig display
viewconfig_display = pn.pane.JSON(
    pn.bind(lambda vc: vc if vc else {}, component.param.viewconfig),
    name="View Config",
    depth=2,
    height=80,
)

# ---------------------------------------------------------------------------
# 3. Layout
# ---------------------------------------------------------------------------

status = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
ChromoSpyce renders 3D chromosome structure data using WebGL. The
<code>structure</code> trait (Arrow bytes from numpy arrays) syncs from Python
to browser. Different structural conformations can be loaded dynamically.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# ChromoSpyce — 3D Chromosome Visualization

[GitHub](https://github.com/nicheill/chromospyce)

ChromoSpyce provides interactive 3D visualization of chromosome structure data.
It accepts numpy arrays or pandas DataFrames with x, y, z coordinates and renders
them as a 3D point cloud / path in the browser.

## How to Test

1. **Select a structure** from the dropdown to load different 3D conformations.
2. **Rotate** the 3D view by left-clicking and dragging.
3. **Zoom** with the scroll wheel.
4. The structure bytes count updates when data changes.
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("### Controls"),
    structure_select,
    pn.pane.Markdown("### Structure Info"),
    info_display,
    viewconfig_display,
    width=350,
)

pn.Column(
    status,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### 3D Chromosome Viewer"),
            anywidget_pane,
            sizing_mode="stretch_width",
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=1200,
).servable()
