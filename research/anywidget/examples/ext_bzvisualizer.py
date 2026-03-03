"""
BZ Visualizer Example — Brillouin Zone Visualization
=====================================================

This example demonstrates using widget-bzvisualizer with Panel's AnyWidget pane.
The widget renders interactive 3D Brillouin zones for crystal structures.

GitHub: https://github.com/osscar-org/widget-bzvisualizer

Key traitlets:
    - cell (List): Unit cell vectors [[a1x,a1y,a1z], [a2x,a2y,a2z], [a3x,a3y,a3z]]
    - rel_coords (List): Relative atomic coordinates
    - atom_numbers (List): Atomic numbers
    - show_axes (Bool): Show coordinate axes
    - show_bvectors (Bool): Show reciprocal lattice vectors
    - show_pathpoints (Bool): Show high-symmetry k-points
    - height (Unicode): Widget height (collides with Bokeh → w_height)
    - width (Unicode): Widget width (collides with Bokeh → w_width)

Trait name collisions:
    - height → w_height (Unicode, e.g. '400px')
    - width → w_width (Unicode, e.g. '100%')

Required packages:
    pip install widget-bzvisualizer

Run with:
    panel serve research/anywidget/examples/ext_bzvisualizer.py
"""

import widget_bzvisualizer

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Crystal structure definitions
# ---------------------------------------------------------------------------

STRUCTURES = {
    "Simple Cubic (Polonium)": {
        "cell": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        "rel_coords": [[0, 0, 0]],
        "atom_numbers": [84],
    },
    "FCC (Copper)": {
        "cell": [[0, 0.5, 0.5], [0.5, 0, 0.5], [0.5, 0.5, 0]],
        "rel_coords": [[0, 0, 0]],
        "atom_numbers": [29],
    },
    "BCC (Iron)": {
        "cell": [[-0.5, 0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, -0.5]],
        "rel_coords": [[0, 0, 0]],
        "atom_numbers": [26],
    },
    "Hexagonal (Graphite)": {
        "cell": [[1, 0, 0], [-0.5, 0.866, 0], [0, 0, 2.0]],
        "rel_coords": [[0, 0, 0], [0.333, 0.667, 0]],
        "atom_numbers": [6, 6],
    },
}

# Create initial widget
initial = STRUCTURES["FCC (Copper)"]
widget = widget_bzvisualizer.BZVisualizer(
    cell=initial["cell"],
    rel_coords=initial["rel_coords"],
    atom_numbers=initial["atom_numbers"],
)

# Wrap with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(widget, height=500, sizing_mode="stretch_width")
component = anywidget_pane.component

# ---------------------------------------------------------------------------
# 2. Panel controls
# ---------------------------------------------------------------------------

structure_select = pn.widgets.Select(
    name="Crystal Structure",
    options=list(STRUCTURES.keys()),
    value="FCC (Copper)",
    width=250,
)

show_axes = pn.widgets.Checkbox(name="Show Axes", value=True, width=200)
show_bvectors = pn.widgets.Checkbox(name="Show Reciprocal Vectors", value=True, width=200)
show_pathpoints = pn.widgets.Checkbox(name="Show High-Symmetry Points", value=False, width=200)


def on_structure_change(event):
    """Load a new crystal structure."""
    s = STRUCTURES[event.new]
    component.cell = s["cell"]
    component.rel_coords = s["rel_coords"]
    component.atom_numbers = s["atom_numbers"]


structure_select.param.watch(on_structure_change, "value")

# Toggle controls → component
show_axes.param.watch(lambda e: setattr(component, 'show_axes', e.new), 'value')
show_bvectors.param.watch(lambda e: setattr(component, 'show_bvectors', e.new), 'value')
show_pathpoints.param.watch(lambda e: setattr(component, 'show_pathpoints', e.new), 'value')

# Component → toggle controls
component.param.watch(lambda e: setattr(show_axes, 'value', e.new), 'show_axes')
component.param.watch(lambda e: setattr(show_bvectors, 'value', e.new), 'show_bvectors')
component.param.watch(lambda e: setattr(show_pathpoints, 'value', e.new), 'show_pathpoints')

# Trait display
trait_display = pn.pane.JSON(
    pn.bind(
        lambda *_: {
            "show_axes": component.show_axes,
            "show_bvectors": component.show_bvectors,
            "show_pathpoints": component.show_pathpoints,
            "cell": component.cell,
        },
        component.param.show_axes,
        component.param.show_bvectors,
        component.param.show_pathpoints,
        component.param.cell,
    ),
    name="Synced Traits",
    depth=2,
    height=150,
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
The BZ Visualizer renders interactive 3D Brillouin zones using WebGL. Crystal
structure traits (<code>cell</code>, <code>rel_coords</code>,
<code>atom_numbers</code>) and display toggles sync bidirectionally.
Note: <code>height</code>/<code>width</code> traits are renamed to
<code>w_height</code>/<code>w_width</code> due to Bokeh name collisions.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# widget-bzvisualizer — Brillouin Zone Viewer

[GitHub](https://github.com/osscar-org/widget-bzvisualizer)

Interactive 3D visualization of Brillouin zones for different crystal structures.
Part of the OSSCAR (Open Software Services for Classrooms and Research) project.

## How to Test

1. **Select a crystal structure** from the dropdown to load different Brillouin zones.
2. **Toggle display options** (axes, reciprocal vectors, high-symmetry points).
3. **Rotate** the 3D view by left-clicking and dragging.
4. **Zoom** with the scroll wheel.
5. The synced traits panel shows current state.
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("### Controls"),
    structure_select,
    show_axes,
    show_bvectors,
    show_pathpoints,
    pn.pane.Markdown("### Synced Traits"),
    trait_display,
    width=350,
)

pn.Column(
    status,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### 3D Brillouin Zone"),
            anywidget_pane,
            sizing_mode="stretch_width",
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=1200,
).servable()
