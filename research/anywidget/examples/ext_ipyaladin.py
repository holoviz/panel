"""
ipyaladin Example — Aladin Lite Sky Viewer in Panel
====================================================

This example demonstrates using ipyaladin (Aladin Lite astronomical
sky viewer) with Panel's AnyWidget pane.

ipyaladin brings Aladin Lite into notebooks via anywidget, providing
interactive visualization of HiPS (Hierarchical Progressive Surveys)
sky maps with support for 550+ surveys, catalogue overlays, and
coordinate-based navigation.

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
    target="M42",       # Orion Nebula
    fov=1.0,             # 1 degree field of view
    survey="https://alaskybis.unistra.fr/DSS/DSSColor",
)

# ---------------------------------------------------------------------------
# 2. Wrap with AnyWidget pane
# ---------------------------------------------------------------------------

anywidget_pane = pn.pane.AnyWidget(aladin, height=500)

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

header = pn.pane.Markdown("""
# ipyaladin — Aladin Lite Sky Viewer in Panel

**ipyaladin** brings [Aladin Lite](https://aladin.cds.unistra.fr/AladinLite/)
into Panel via anywidget, enabling interactive visualization of astronomical
sky surveys directly in your data app.

## Features

- Browse **550+ HiPS sky surveys** (optical, infrared, X-ray, radio)
- Navigate to any **deep sky object** by name (M42, NGC 1234, etc.)
- **Zoom** with scroll wheel, **pan** by dragging
- Change **coordinate frames** (ICRS equatorial, Galactic)

## Controls

Use the controls below to navigate the sky. Select a target object,
adjust the field of view, or switch between different sky surveys.
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.Row(target_select, survey_select),
    pn.Row(fov_slider, coo_frame_select),
)

pn.Column(
    header,
    controls,
    anywidget_pane,
    sizing_mode="stretch_width",
    max_width=1000,
).servable()
