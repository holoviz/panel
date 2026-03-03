"""
weas-widget Example — Atomistic Structure Visualization
========================================================

This example demonstrates using weas-widget (Web Environment for Atomistic
Structure) with Panel's AnyWidget pane. weas-widget provides interactive 3D
visualization and editing of molecular and crystal structures.

WeasWidget is an ipywidgets HBox container whose first child is a BaseWidget
(the actual anywidget). Panel's AnyWidget pane wraps the BaseWidget directly.

GitHub: https://github.com/superstar54/weas-widget
Docs:   https://weas-widget.readthedocs.io/

Required packages:
    pip install weas-widget ase

Run with:
    panel serve research/anywidget/examples/ext_weaswidget.py

Testing instructions:
    1. Serve the app and open http://localhost:5006/ext_weaswidget
    2. The 3D viewer should render a water molecule (H2O) on load
    3. Use "Molecule" dropdown to switch between H2O, CH4, C2H6, NH3
    4. Use "Model Style" to switch between Space-filling / Ball-stick / Polyhedral
    5. Use "Color Scheme" to switch between JMOL / VESTA / CPK
    6. Toggle "Show Atom Labels" to display element symbols on atoms
    7. Rotate / zoom the 3D view with mouse (left-drag = rotate, scroll = zoom)
    8. The "Synced Trait Values" section should update when controls change

Trait name collisions:
    - `text` (List): Collides with Bokeh's `text` property name. However,
      since the weas-widget `text` trait is a List (for 3D text annotations)
      rather than a string, Panel maps it without issues — it becomes a
      `param.List` on the component.
"""

from ase.build import molecule

from weas_widget import WeasWidget

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# Molecule definitions
# ---------------------------------------------------------------------------
MOLECULES = {
    "H2O (Water)": "H2O",
    "CH4 (Methane)": "CH4",
    "C2H6 (Ethane)": "C2H6",
    "NH3 (Ammonia)": "NH3",
}

MODEL_STYLES = {
    "Space-filling": 0,
    "Ball-stick": 1,
    "Polyhedral": 2,
}

COLOR_SCHEMES = ["JMOL", "VESTA", "CPK"]
LABEL_TYPES = ["None", "Symbol", "Index"]

# ---------------------------------------------------------------------------
# Create the initial widget
# ---------------------------------------------------------------------------
atoms = molecule("H2O")
weas = WeasWidget(from_ase=atoms, guiConfig={"enabled": False})
# WeasWidget is an HBox; the actual anywidget is the first child (BaseWidget)
base_widget = weas.children[0]

# Wrap with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(base_widget, height=500, sizing_mode="stretch_width")
component = anywidget_pane.component

# ---------------------------------------------------------------------------
# Panel controls
# ---------------------------------------------------------------------------
molecule_select = pn.widgets.Select(
    name="Molecule",
    options=list(MOLECULES.keys()),
    value="H2O (Water)",
    width=250,
)

model_style_select = pn.widgets.Select(
    name="Model Style",
    options=list(MODEL_STYLES.keys()),
    value="Space-filling",
    width=250,
)

color_scheme_select = pn.widgets.Select(
    name="Color Scheme",
    options=COLOR_SCHEMES,
    value="JMOL",
    width=250,
)

label_type_select = pn.widgets.Select(
    name="Atom Labels",
    options=LABEL_TYPES,
    value="None",
    width=250,
)

show_bonds_toggle = pn.widgets.Checkbox(
    name="Show Bonded Atoms",
    value=False,
    width=250,
)

show_h_bonds_toggle = pn.widgets.Checkbox(
    name="Show Hydrogen Bonds",
    value=False,
    width=250,
)

# ---------------------------------------------------------------------------
# Synced trait display
# ---------------------------------------------------------------------------
trait_display = pn.pane.JSON(
    {
        "modelStyle": component.modelStyle,
        "colorType": component.colorType,
        "atomLabelType": component.atomLabelType,
        "showBondedAtoms": component.showBondedAtoms,
        "showHydrogenBonds": component.showHydrogenBonds,
        "ready": component.ready,
    },
    name="Synced Trait Values",
    depth=2,
    width=350,
)


def update_trait_display():
    trait_display.object = {
        "modelStyle": component.modelStyle,
        "colorType": component.colorType,
        "atomLabelType": component.atomLabelType,
        "showBondedAtoms": component.showBondedAtoms,
        "showHydrogenBonds": component.showHydrogenBonds,
        "ready": component.ready,
    }


# ---------------------------------------------------------------------------
# Callbacks: Panel controls -> component
# ---------------------------------------------------------------------------
def on_molecule_change(event):
    mol_key = MOLECULES[event.new]
    new_atoms = molecule(mol_key)
    new_weas = WeasWidget(from_ase=new_atoms)
    new_base = new_weas.children[0]
    # Update the atoms trait on the component
    component.atoms = new_base.atoms
    update_trait_display()


def on_model_style_change(event):
    component.modelStyle = MODEL_STYLES[event.new]
    update_trait_display()


def on_color_scheme_change(event):
    component.colorType = event.new
    update_trait_display()


def on_label_type_change(event):
    component.atomLabelType = event.new
    update_trait_display()


def on_show_bonds_change(event):
    component.showBondedAtoms = event.new
    update_trait_display()


def on_show_h_bonds_change(event):
    component.showHydrogenBonds = event.new
    update_trait_display()


molecule_select.param.watch(on_molecule_change, "value")
model_style_select.param.watch(on_model_style_change, "value")
color_scheme_select.param.watch(on_color_scheme_change, "value")
label_type_select.param.watch(on_label_type_change, "value")
show_bonds_toggle.param.watch(on_show_bonds_change, "value")
show_h_bonds_toggle.param.watch(on_show_h_bonds_change, "value")

# ---------------------------------------------------------------------------
# Widget -> Panel sync (component param.watch)
# ---------------------------------------------------------------------------
def on_component_change(*events):
    for event in events:
        if event.name == "modelStyle":
            # Reverse-lookup the style name
            for label, val in MODEL_STYLES.items():
                if val == event.new:
                    model_style_select.value = label
                    break
        elif event.name == "colorType":
            if event.new in COLOR_SCHEMES:
                color_scheme_select.value = event.new
        elif event.name == "atomLabelType":
            if event.new in LABEL_TYPES:
                label_type_select.value = event.new
    update_trait_display()


component.param.watch(
    on_component_change,
    ["modelStyle", "colorType", "atomLabelType", "ready"],
)

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
status_banner = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS — Widget renders and trait sync is functional
</p>
<p style="color: #155724; font-size: 14px; margin: 8px 0 0 0;">
weas-widget's BaseWidget is a standard anywidget with <code>_esm</code> and
<code>_css</code> traits. Panel wraps it directly. The 3D WebGL viewer renders
correctly and trait changes (model style, colors, labels) propagate via the
component param interface.
</p>
</div>
""")

header = pn.pane.Markdown("""
# weas-widget — Atomistic Structure Viewer

[GitHub](https://github.com/superstar54/weas-widget) |
[Docs](https://weas-widget.readthedocs.io/)

**weas-widget** provides interactive 3D visualization for molecular and crystal
structures. It supports ASE and Pymatgen data formats, multiple rendering
styles, and interactive editing (rotate, select, measure atoms).

## How to Use

- **Rotate**: Left-click and drag on the 3D viewer
- **Zoom**: Scroll wheel
- **Pan**: Right-click and drag
- **Select atoms**: Click on atoms (indices appear in synced traits)
- Use the controls on the right to change visualization settings
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("### Visualization Controls"),
    molecule_select,
    model_style_select,
    color_scheme_select,
    label_type_select,
    show_bonds_toggle,
    show_h_bonds_toggle,
    pn.pane.Markdown("### Synced Trait Values"),
    trait_display,
    width=350,
)

pn.Column(
    status_banner,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### 3D Structure Viewer"),
            anywidget_pane,
            sizing_mode="stretch_width",
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=1200,
).servable()
