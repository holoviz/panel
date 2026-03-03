"""
ipymolstar Example — PDBe Molecular Viewer
============================================

This example demonstrates using the ipymolstar PDBeMolstar widget (a 3D
molecular structure viewer powered by Mol*) with Panel's AnyWidget pane.

PDBeMolstar is a Jupyter widget wrapping the PDBe implementation of the
Mol* (MolStar) viewer. It can display 3D molecular structures from the
Protein Data Bank (PDB) by ID, with controls for visual style, spin,
background color, and more.

GitHub: https://github.com/Jhsmit/ipymolstar
Docs:   https://ipymolstar.readthedocs.io/

Key traitlets:
    - molecule_id (Unicode): PDB ID to display (e.g. "1cbs")
    - height (Unicode): Height string like "500px" (COLLIDES with Panel -> w_height)
    - width (Unicode): Width string like "100%" (COLLIDES with Panel -> w_width)
    - bg_color (Unicode): Background color
    - visual_style (Enum): 'cartoon', 'ball-and-stick', etc.
    - spin (Bool): Whether to spin the molecule
    - hide_controls (Bool): Hide the control panel
    - lighting (Enum): Lighting mode
    - hide_water (Bool): Hide water molecules
    - click_event (Dict): Click event data
    - mouseover_event (Dict): Mouseover event data

NOTE: height and width traits collide with Panel's Layoutable parameters,
so they are renamed to w_height and w_width on the component. The dimension
forwarding logic ensures the pane is sized correctly.

Required package:
    pip install ipymolstar

Run with:
    panel serve research/anywidget/examples/ext_ipymolstar.py
"""

from ipymolstar import PDBeMolstar

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create the PDBeMolstar widget and wrap with AnyWidget pane
# ---------------------------------------------------------------------------

widget = PDBeMolstar(molecule_id="1cbs", height="500px", width="100%", subscribe_events=True)
anywidget_pane = pn.pane.AnyWidget(widget, sizing_mode="stretch_width", height=550)

# ---------------------------------------------------------------------------
# 2. Panel controls for bidirectional sync
# ---------------------------------------------------------------------------

component = anywidget_pane.component

# Molecule ID input — load different proteins by PDB ID
molecule_input = pn.widgets.TextInput(
    name="PDB Molecule ID",
    value="1cbs",
    placeholder="Enter a PDB ID (e.g. 1cbs, 2hbs, 4hhb)",
    width=300,
)

# Visual style selector
# Note: visual_style defaults to None (Mol* picks the best style automatically)
style_select = pn.widgets.Select(
    name="Visual Style",
    options=[None, "cartoon", "ball-and-stick", "gaussian-surface", "molecular-surface", "spacefill", "putty", "point"],
    value=widget.visual_style,
    width=300,
)

# Spin toggle
spin_toggle = pn.widgets.Toggle(
    name="Spin Molecule",
    value=False,
    width=150,
)

# Background color picker
bg_color_picker = pn.widgets.ColorPicker(
    name="Background Color",
    value="#F7F7F7",
    width=150,
)

# Panel -> Widget (through component params)
molecule_input.param.watch(
    lambda e: setattr(component, "molecule_id", e.new), "value"
)
style_select.param.watch(
    lambda e: setattr(component, "visual_style", e.new), "value"
)
spin_toggle.param.watch(
    lambda e: setattr(component, "spin", e.new), "value"
)
bg_color_picker.param.watch(
    lambda e: setattr(component, "bg_color", e.new), "value"
)

# Widget -> Panel (through component param.watch)
def on_component_change(*events):
    for event in events:
        if event.name == "molecule_id":
            molecule_input.value = event.new
        elif event.name == "visual_style":
            style_select.value = event.new
        elif event.name == "spin":
            spin_toggle.value = event.new

component.param.watch(on_component_change, ["molecule_id", "visual_style", "spin"])

# ---------------------------------------------------------------------------
# 3. Click and mouseover event display
# ---------------------------------------------------------------------------

click_display = pn.pane.JSON(
    {},
    name="Click Event",
    depth=3,
)

mouseover_display = pn.pane.JSON(
    {},
    name="Mouseover Event",
    depth=3,
)

def on_event_change(*events):
    for event in events:
        if event.name == "click_event" and event.new:
            click_display.object = event.new
        elif event.name == "mouseover_event" and event.new:
            mouseover_display.object = event.new

component.param.watch(on_event_change, ["click_event", "mouseover_event"])

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

header = pn.pane.Markdown("""
# PDBe Mol* Viewer -- Panel AnyWidget Example

**ipymolstar** wraps the PDBe implementation of the [Mol\\*](https://molstar.org/)
molecular viewer. Enter any PDB ID to load a 3D structure.

## How to Interact

- **Rotate:** Click and drag on the 3D view
- **Zoom:** Scroll to zoom in and out
- **Pan:** Right-click and drag
- **Select atoms:** Click on atoms to see click event data
- **Hover:** Move mouse over atoms to see mouseover events

## Testing Instructions

1. Change the PDB ID in the text input (try: `2hbs`, `4hhb`, `1bna`)
2. Toggle the Spin switch to rotate the molecule
3. Change the Visual Style dropdown
4. Click on atoms in the 3D view and check the Click Event display

## Renamed Traits

The `height` and `width` traitlets collide with Panel's layout parameters
and are automatically renamed to `w_height` and `w_width` on the component.
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("### Controls"),
    molecule_input,
    style_select,
    pn.Row(spin_toggle, bg_color_picker),
    pn.pane.Markdown("### Click Event"),
    click_display,
    pn.pane.Markdown("### Mouseover Event"),
    mouseover_display,
    width=400,
)

status = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
3D molecular viewer renders correctly. PDB structures load from the Protein Data Bank.
Visual style, spin, and background color sync from Python to browser.
Click and mouseover events sync back to Python via <code>subscribe_events=True</code>.
The <code>height</code> and <code>width</code> traits are renamed to <code>w_height</code> / <code>w_width</code>.
</p>
</div>
""", sizing_mode="stretch_width")

pn.Column(
    status,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### 3D Molecular Viewer"),
            anywidget_pane,
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=1200,
).servable()
