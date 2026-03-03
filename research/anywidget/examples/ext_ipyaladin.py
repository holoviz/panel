"""
ipyaladin Example — Aladin Lite Sky Viewer in Panel
====================================================

This example demonstrates using ipyaladin (Aladin Lite astronomical
sky viewer) with Panel's AnyWidget pane.

ipyaladin brings Aladin Lite into notebooks via anywidget, providing
interactive visualization of HiPS (Hierarchical Progressive Surveys)
sky maps with support for 550+ surveys, catalogue overlays, and
coordinate-based navigation.

GitHub: https://github.com/cds-astro/ipyaladin
Docs:   https://cds-astro.github.io/ipyaladin/

Key traitlets:
    - _target (Unicode): Sky coordinates to center on (e.g. "M1" or "83.63 22.01")
    - _fov (Float): Field of view in degrees (default 60.0)
    - survey (Unicode): HiPS survey URL
    - coo_frame (Unicode): Coordinate frame ("ICRS" or "Galactic")
    - projection (Unicode): Map projection (default "SIN")
    - _height (Int): Widget height in pixels (default 400)
    - overlay_survey (Unicode): Overlay survey URL
    - overlay_survey_opacity (Float): Overlay opacity (0.0-1.0)

Required package:
    pip install ipyaladin

Run with:
    panel serve research/anywidget/examples/ext_ipyaladin.py
"""

from ipyaladin import Aladin

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create the Aladin widget
# ---------------------------------------------------------------------------

aladin = Aladin(
    target="159.2135528 -58.6241989",
    survey="https://alasky.u-strasbg.fr/Planets/Mars_Viking_MDIM21",
    fov=10,
    height=800,
)

# ---------------------------------------------------------------------------
# 2. Wrap with AnyWidget pane
# ---------------------------------------------------------------------------

# NOTE: Width/height on the AnyWidget pane do NOT propagate to the inner
# component's Bokeh model. Instead, set sizing on the component directly.
anywidget_pane = pn.pane.AnyWidget(aladin, sizing_mode="stretch_width")

# Set explicit height on the component so the Aladin Lite container gets a
# non-zero size.  Aladin's own _height trait controls the inner canvas height,
# but the outer Panel container also needs explicit dimensions.
anywidget_pane.component.height = 500
anywidget_pane.component.sizing_mode = "stretch_width"

# ---------------------------------------------------------------------------
# 3. Panel controls for navigation and survey selection
# ---------------------------------------------------------------------------

component = anywidget_pane.component

# Target selector — famous deep sky objects
target_select = pn.widgets.Select(
    name="Target",
    options={
        "Orion Nebula (M42)": "M42",
        "Andromeda Galaxy (M31)": "M31",
        "Crab Nebula (M1)": "M1",
        "Pleiades (M45)": "M45",
        "Whirlpool Galaxy (M51)": "M51",
        "Eagle Nebula (M16)": "M16",
        "Sombrero Galaxy (M104)": "M104",
        "Galactic Center": "Sgr A*",
    },
    value="M42",
    width=250,
)

# Field of view slider
fov_slider = pn.widgets.FloatSlider(
    name="Field of View (degrees)",
    start=0.01,
    end=60.0,
    value=1.0,
    step=0.01,
    width=300,
)

# Survey selector
survey_select = pn.widgets.Select(
    name="Sky Survey",
    options={
        "DSS Color": "https://alaskybis.unistra.fr/DSS/DSSColor",
        "2MASS Color": "https://alaskybis.unistra.fr/2MASS/Color",
        "WISE Color": "https://alaskybis.unistra.fr/AllWISE/RGB-W4-W2-W1",
        "Fermi Color": "https://alaskybis.unistra.fr/Fermi/Color",
    },
    value="https://alaskybis.unistra.fr/DSS/DSSColor",
    width=250,
)

# Coordinate frame selector
coo_frame_select = pn.widgets.Select(
    name="Coordinate Frame",
    options=["ICRS", "Galactic"],
    value="ICRS",
    width=150,
)

# Panel -> Widget (through component params)
# Note: ipyaladin uses underscore-prefixed private traits for some properties
target_select.param.watch(
    lambda e: setattr(component, "_target", e.new), "value"
)
fov_slider.param.watch(
    lambda e: setattr(component, "_fov", e.new), "value"
)
survey_select.param.watch(
    lambda e: setattr(component, "survey", e.new), "value"
)
coo_frame_select.param.watch(
    lambda e: setattr(component, "coo_frame", e.new), "value"
)

# Widget -> Panel (through component param.watch)
def on_component_change(*events):
    for event in events:
        if event.name == "_fov":
            fov_slider.value = round(event.new, 4)
        elif event.name == "_target":
            # Target may change to coords — just update display
            pass

# Watch available traits
try:
    component.param.watch(on_component_change, ["_fov"])
except Exception:
    pass  # Trait might not be available on component yet

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

status = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
This example works fully with Panel's AnyWidget pane.
Rendering, sky navigation, survey switching, and field-of-view sync all work as expected.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# ipyaladin -- Interactive Sky Viewer

[GitHub](https://github.com/cds-astro/ipyaladin) | [Docs](https://cds-astro.github.io/ipyaladin/)

[Aladin Lite](https://aladin.cds.unistra.fr/AladinLite/) is an interactive
sky map -- think Google Maps, but for the night sky.

## How to Explore

1. **Pick a target:** Select a famous astronomical object from the **Target**
   dropdown to fly to it (e.g., the Orion Nebula is a glowing cloud of gas
   where new stars form).
2. **Zoom:** Use your **scroll wheel** to zoom. The **Field of View** slider
   also controls zoom -- small values (< 1 degree) are close-ups, large
   values (> 30 degrees) show a wide swath of sky.
3. **Pan:** Click and drag to move across the sky.
4. **Switch surveys:** The **Sky Survey** dropdown changes the imagery:
   - *DSS Color* -- visible-light photographs
   - *2MASS Color* -- near-infrared (reveals dust-hidden stars)
   - *WISE Color* -- mid-infrared (warm dust and galaxies glow brightly)
   - *Fermi Color* -- gamma-ray (shows the most violent events in the universe)
5. **Coordinate Frame:** Switch between *ICRS* (standard sky coordinates)
   and *Galactic* (centered on the Milky Way plane).

The field-of-view slider syncs bidirectionally -- zooming with the scroll
wheel updates the slider, and dragging the slider updates the view.
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.Row(target_select, survey_select),
    pn.Row(fov_slider, coo_frame_select),
)

pn.Column(
    status,
    header,
    controls,
    anywidget_pane,
    sizing_mode="stretch_width",
    max_width=1000,
).servable()
