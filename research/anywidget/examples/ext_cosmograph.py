"""
Cosmograph Example -- GPU-Accelerated Graph Visualization
============================================================

This example demonstrates using the cosmograph-widget with Panel's
AnyWidget pane. Cosmograph provides GPU-accelerated graph/network
visualization with force-directed layout simulation powered by WebGL.

GitHub: https://github.com/cosmograph-org/cosmograph
Docs:   https://cosmograph.app/

Key traitlets (subset of 103 total):
    - points (Any): DataFrame of node data (converted to IPC binary internally)
    - links (Any): DataFrame of edge data (converted to IPC binary internally)
    - point_color (Union): Default point color (hex string)
    - point_size (Float): Default point size in pixels
    - point_color_by (Unicode): Column name to color points by
    - point_size_by (Unicode): Column name to size points by
    - point_label_by (Unicode): Column name for point labels
    - point_id_by (Unicode): Column name for point IDs
    - link_source_by (Unicode): Column name for link source IDs
    - link_target_by (Unicode): Column name for link target IDs
    - link_color (Union): Default link color
    - link_width (Float): Default link width
    - background_color (Union): Canvas background color
    - selected_point_indices (List): Currently selected point indices
    - clicked_point_index (Int): Index of the last clicked point
    - simulation_gravity (Float): Gravity force strength
    - simulation_repulsion (Float): Repulsion force strength
    - disable_simulation (Bool): Disable force-directed simulation
    - fit_view_on_init (Bool): Auto-fit view on initialization

Note: ``points`` and ``links`` are Any traits that get serialized to IPC
binary (``_ipc_points``, ``_ipc_links``). They do NOT appear as params on
the Panel component. To update graph data, set them on the original widget
object directly.

Required package:
    pip install cosmograph-widget

Run with:
    panel serve research/anywidget/examples/ext_cosmograph.py
"""

import pandas as pd
from cosmograph_widget import Cosmograph

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create sample graph data
# ---------------------------------------------------------------------------

# Social network-like graph with groups
nodes = pd.DataFrame({
    "id": [f"node_{i}" for i in range(20)],
    "label": [f"Person {i}" for i in range(20)],
    "group": (
        ["Engineering"] * 5
        + ["Marketing"] * 5
        + ["Sales"] * 5
        + ["Research"] * 5
    ),
})

# Edges: intra-group chains + cross-group bridges
edges_data = []
for group_start in range(0, 20, 5):
    for i in range(group_start, group_start + 4):
        edges_data.append({
            "source": f"node_{i}",
            "target": f"node_{i + 1}",
        })
cross_links = [
    (0, 5), (0, 10), (0, 15),
    (5, 10), (10, 15), (5, 15),
    (2, 7), (7, 12), (12, 17),
    (3, 8), (8, 13), (13, 18),
]
for s, t in cross_links:
    edges_data.append({"source": f"node_{s}", "target": f"node_{t}"})

edges = pd.DataFrame(edges_data)

# ---------------------------------------------------------------------------
# 2. Create the Cosmograph widget
# ---------------------------------------------------------------------------

widget = Cosmograph(
    points=nodes,
    links=edges,
    point_color="#4a90d9",
    point_size=8,
    point_label_by="label",
    point_id_by="id",
    link_source_by="source",
    link_target_by="target",
    link_color="#cccccc",
    link_width=1,
    show_labels=True,
    show_dynamic_labels=True,
    fit_view_on_init=True,
    simulation_gravity=0.25,
    simulation_repulsion=1.0,
    background_color="#222222",
)

# Wrap with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(widget, height=500, sizing_mode="stretch_width")
component = anywidget_pane.component

# ---------------------------------------------------------------------------
# 3. Panel controls for graph properties
# ---------------------------------------------------------------------------

point_color_picker = pn.widgets.ColorPicker(
    name="Point Color",
    value="#4a90d9",
    width=200,
)

point_size_slider = pn.widgets.FloatSlider(
    name="Point Size",
    start=1,
    end=30,
    value=8,
    step=1,
    width=250,
)

link_width_slider = pn.widgets.FloatSlider(
    name="Link Width",
    start=0.1,
    end=5,
    value=1,
    step=0.1,
    width=250,
)

gravity_slider = pn.widgets.FloatSlider(
    name="Simulation Gravity",
    start=0,
    end=2,
    value=0.25,
    step=0.05,
    width=250,
)

repulsion_slider = pn.widgets.FloatSlider(
    name="Simulation Repulsion",
    start=0,
    end=5,
    value=1.0,
    step=0.1,
    width=250,
)

show_labels_toggle = pn.widgets.Toggle(
    name="Show Labels",
    value=True,
    button_type="primary",
    width=200,
)

background_color_picker = pn.widgets.ColorPicker(
    name="Background Color",
    value="#222222",
    width=200,
)

disable_sim_toggle = pn.widgets.Toggle(
    name="Disable Simulation",
    value=False,
    button_type="warning",
    width=200,
)

# Panel -> Widget sync
point_color_picker.param.watch(
    lambda e: setattr(component, 'point_color', e.new), ['value']
)
point_size_slider.param.watch(
    lambda e: setattr(component, 'point_size', e.new), ['value']
)
link_width_slider.param.watch(
    lambda e: setattr(component, 'link_width', e.new), ['value']
)
background_color_picker.param.watch(
    lambda e: setattr(component, 'background_color', e.new), ['value']
)
gravity_slider.param.watch(
    lambda e: setattr(component, 'simulation_gravity', e.new), ['value']
)
repulsion_slider.param.watch(
    lambda e: setattr(component, 'simulation_repulsion', e.new), ['value']
)
show_labels_toggle.param.watch(
    lambda e: setattr(component, 'show_labels', e.new), ['value']
)
disable_sim_toggle.param.watch(
    lambda e: setattr(component, 'disable_simulation', e.new), ['value']
)

# Display selected and clicked points
selected_display = pn.pane.Markdown(
    pn.bind(
        lambda sel: f"**Selected point indices:** {sel}" if sel else "**Selected points:** (none)",
        component.param.selected_point_indices,
    ),
    sizing_mode="stretch_width",
)

clicked_display = pn.pane.Markdown(
    pn.bind(
        lambda idx: f"**Clicked point index:** {idx}" if idx is not None else "**Clicked point:** (none)",
        component.param.clicked_point_index,
    ),
    sizing_mode="stretch_width",
)

# --- Dataset switcher ---
# Note: points/links are not synced as Panel params (they are Any traits
# serialized to IPC binary). We set them on the original widget object.

DATASETS = {
    "Social Network (20 nodes)": (nodes, edges),
    "Ring Graph (12 nodes)": (
        pd.DataFrame({
            "id": [f"r{i}" for i in range(12)],
            "label": [f"Node {i}" for i in range(12)],
        }),
        pd.DataFrame({
            "source": [f"r{i}" for i in range(12)],
            "target": [f"r{(i + 1) % 12}" for i in range(12)],
        }),
    ),
    "Star Graph (10 nodes)": (
        pd.DataFrame({
            "id": ["center"] + [f"leaf_{i}" for i in range(9)],
            "label": ["Center"] + [f"Leaf {i}" for i in range(9)],
        }),
        pd.DataFrame({
            "source": ["center"] * 9,
            "target": [f"leaf_{i}" for i in range(9)],
        }),
    ),
}

dataset_selector = pn.widgets.Select(
    name="Graph Dataset",
    options=list(DATASETS.keys()),
    value="Social Network (20 nodes)",
    width=250,
)


def on_dataset_change(event):
    pts, lks = DATASETS[event.new]
    # Data must be set through the original widget object, not the component,
    # because `points` and `links` are Python properties that serialize to
    # binary `_ipc_points` / `_ipc_links` traits internally.
    widget.points = pts
    widget.links = lks


dataset_selector.param.watch(on_dataset_change, "value")

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

status = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
Cosmograph renders GPU-accelerated graph visualizations with force-directed layout.
Visual properties (<code>point_color</code>, <code>point_size</code>, <code>link_width</code>,
<code>background_color</code>) and simulation parameters all sync correctly via Panel
controls. Click and selection events propagate back to Python. Dataset switching updates
the graph by setting <code>points</code>/<code>links</code> on the original widget object
(these are IPC-serialized Any traits, not Panel component params).
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# Cosmograph -- GPU-Accelerated Graph Visualization

[GitHub](https://github.com/cosmograph-org/cosmograph) |
[Cosmograph.app](https://cosmograph.app/)

Interactive graph/network visualization with force-directed layout,
powered by WebGL for high-performance rendering of large graphs.

## How to Test

1. **Pan and zoom** the graph canvas (scroll to zoom, drag to pan).
2. **Click a node** to see the clicked point index update below.
3. **Switch datasets** using the selector to load different graph topologies.
4. **Adjust appearance** -- change point color, size, link width, and
   background color with the controls on the right.
5. **Tune the simulation** -- adjust gravity and repulsion to change
   the force-directed layout behavior.
6. **Disable simulation** to freeze nodes in their current positions.
7. **Toggle labels** to show/hide node labels on the canvas.
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("### Dataset"),
    dataset_selector,
    pn.pane.Markdown("### Appearance"),
    point_color_picker,
    point_size_slider,
    link_width_slider,
    background_color_picker,
    show_labels_toggle,
    pn.pane.Markdown("### Simulation"),
    gravity_slider,
    repulsion_slider,
    disable_sim_toggle,
    pn.pane.Markdown("### Interaction"),
    clicked_display,
    selected_display,
    width=350,
)

pn.Column(
    status,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### Graph"),
            anywidget_pane,
            sizing_mode="stretch_width",
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=1200,
).servable()
