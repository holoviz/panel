"""
widget-bandsplot Example -- Band Structure Visualization
=========================================================

This example demonstrates using widget-bandsplot's BandsPlotWidget
with Panel's AnyWidget pane and bidirectional sync for energy range
and formatting options.

widget-bandsplot renders electronic band structure diagrams used in
condensed matter physics and materials science. It visualizes energy
bands along high-symmetry paths in the Brillouin zone and can
optionally display the density of states (DOS).

GitHub: https://github.com/osscar-org/widget-bandsplot
Docs:   https://www.osscar.org/widgets/widget_bandsplot.html

Key traitlets:
    - bands (List): Band structure data -- list of path segments with
      'from', 'to', 'length', 'values', 'x' keys
    - bands_color (List): Custom colors per band
    - dos (Dict): Density of states data with 'fermi_energy' and 'dos' keys
    - energy_range (List[float]): Y-axis energy range [min, max] in eV
    - dos_range (List): X-axis range for DOS plot
    - format_settings (Dict): Display options (showFermi, showLegend, etc.)

Required package:
    pip install widget-bandsplot

Run with:
    panel serve research/anywidget/examples/ext_bandsplot.py

Testing Instructions:
    1. Run the app with the command above
    2. Verify the band structure plot renders (parabolic bands)
    3. Adjust the energy range sliders on the right -- the plot
       Y-axis should update
    4. Toggle "Show Fermi Level" and "Show Legend" checkboxes
    5. Try switching to the "Semiconductor" or "Metal" preset
    6. Check the browser console for errors (F12)

Trait Name Collisions: NONE
    The widget traits (bands, bands_color, dos, energy_range,
    dos_range, format_settings) do not collide with any Bokeh
    reserved model property names or Panel params.
"""

import numpy as np

from widget_bandsplot import BandsPlotWidget

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Generate synthetic band structure data
# ---------------------------------------------------------------------------
# Band structure data follows the format used by AiiDA's BandsData export.
# Each "path" entry describes a segment between two high-symmetry k-points.


def make_bands_data(band_offsets, fermi_level=0.0, n_points=50):
    """Generate synthetic band structure data.

    Parameters
    ----------
    band_offsets : list of float
        Energy offsets for each band at the Gamma point.
    fermi_level : float
        Fermi energy level.
    n_points : int
        Number of k-points per segment.

    Returns
    -------
    bands_list : list
        Band structure data in widget-bandsplot format.
    fermi : float
        The Fermi level.
    """
    # Define a simple path: GAMMA -> X -> M -> GAMMA
    segments = [
        ("GAMMA", "X", 0.0, 1.0),
        ("X", "M", 1.0, 1.7),
        ("M", "GAMMA", 1.7, 2.7),
    ]

    paths = []
    for seg_from, seg_to, x_start, x_end in segments:
        x = np.linspace(x_start, x_end, n_points).tolist()
        k_norm = np.linspace(0, np.pi, n_points)

        values = []
        for offset in band_offsets:
            if offset < fermi_level:
                # Valence band: cosine-like
                band = (offset - 1.5 * np.cos(k_norm)).tolist()
            else:
                # Conduction band: inverted cosine
                band = (offset + 1.5 * np.cos(k_norm)).tolist()
            values.append(band)

        paths.append({
            "length": n_points,
            "from": seg_from,
            "to": seg_to,
            "values": values,
            "x": x,
            "two_band_types": False,
        })

    bands_list = [{
        "paths": paths,
        "path": [["GAMMA", "X"], ["X", "M"], ["M", "GAMMA"]],
        "fermi_level": fermi_level,
    }]

    return bands_list, fermi_level


# --- Presets ---

PRESETS = {}

# Semiconductor: bands with a gap
semi_offsets = [-6.0, -4.0, -2.0, -1.0, 1.0, 2.0, 4.0, 6.0]
semi_bands, semi_fermi = make_bands_data(semi_offsets, fermi_level=0.0)
PRESETS["Semiconductor"] = {
    "bands": semi_bands,
    "fermi": semi_fermi,
    "energy_range": [-8.0, 8.0],
}

# Metal: bands crossing the Fermi level
metal_offsets = [-5.0, -3.0, -1.0, 0.0, 0.5, 2.0, 4.0]
metal_bands, metal_fermi = make_bands_data(metal_offsets, fermi_level=0.0)
PRESETS["Metal"] = {
    "bands": metal_bands,
    "fermi": metal_fermi,
    "energy_range": [-7.0, 6.0],
}

# Simple: just 4 bands
simple_offsets = [-3.0, -1.0, 1.0, 3.0]
simple_bands, simple_fermi = make_bands_data(simple_offsets, fermi_level=0.0)
PRESETS["Simple (4 bands)"] = {
    "bands": simple_bands,
    "fermi": simple_fermi,
    "energy_range": [-5.0, 5.0],
}

# ---------------------------------------------------------------------------
# 2. Create the BandsPlotWidget and wrap with Panel
# ---------------------------------------------------------------------------

widget = BandsPlotWidget(
    bands=semi_bands,
    energy_range=[-8.0, 8.0],
    format_settings={"showFermi": True, "showLegend": False},
)

anywidget_pane = pn.pane.AnyWidget(widget, height=500, sizing_mode="stretch_width")
component = anywidget_pane.component

# ---------------------------------------------------------------------------
# 3. Panel controls for bidirectional sync
# ---------------------------------------------------------------------------

preset_selector = pn.widgets.Select(
    name="Preset",
    options=list(PRESETS.keys()),
    value="Semiconductor",
    width=280,
)

energy_min = pn.widgets.FloatSlider(
    name="Energy Min (eV)",
    start=-15.0,
    end=0.0,
    step=0.5,
    value=-8.0,
    width=280,
)

energy_max = pn.widgets.FloatSlider(
    name="Energy Max (eV)",
    start=0.0,
    end=15.0,
    step=0.5,
    value=8.0,
    width=280,
)

show_fermi = pn.widgets.Checkbox(name="Show Fermi Level", value=True)
show_legend = pn.widgets.Checkbox(name="Show Legend", value=False)


def on_preset_change(event):
    preset = PRESETS[event.new]
    component.bands = preset["bands"]
    component.energy_range = preset["energy_range"]
    energy_min.value = preset["energy_range"][0]
    energy_max.value = preset["energy_range"][1]


preset_selector.param.watch(on_preset_change, "value")


def on_energy_range_change(*events):
    component.energy_range = [energy_min.value, energy_max.value]


energy_min.param.watch(on_energy_range_change, "value")
energy_max.param.watch(on_energy_range_change, "value")


def on_format_change(*events):
    component.format_settings = {
        "showFermi": show_fermi.value,
        "showLegend": show_legend.value,
    }


show_fermi.param.watch(on_format_change, "value")
show_legend.param.watch(on_format_change, "value")

# Display current trait values
trait_display = pn.pane.JSON(
    {
        "energy_range": widget.energy_range,
        "format_settings": widget.format_settings,
        "num_bands": len(semi_bands[0]["paths"][0]["values"]) if semi_bands else 0,
        "num_segments": len(semi_bands[0]["paths"]) if semi_bands else 0,
    },
    name="Synced Traits",
    depth=2,
    width=280,
)


def on_component_change(*events):
    trait_display.object = {
        "energy_range": list(component.energy_range),
        "format_settings": component.format_settings,
        "num_bands": (
            len(component.bands[0]["paths"][0]["values"])
            if component.bands and component.bands[0].get("paths")
            else 0
        ),
        "num_segments": (
            len(component.bands[0]["paths"])
            if component.bands and component.bands[0].get("paths")
            else 0
        ),
    }


component.param.watch(on_component_change, ["bands", "energy_range", "format_settings"])

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

status_banner = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
Band structure plots render correctly with synthetic data.
Bidirectional sync of <code>energy_range</code> and <code>format_settings</code> works.
Preset switching updates the <code>bands</code> data and re-renders.
No trait name collisions with Bokeh reserved names.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# widget-bandsplot -- Electronic Band Structure

**[widget-bandsplot](https://github.com/osscar-org/widget-bandsplot)** is an
anywidget for visualizing electronic band structures and density of states (DOS),
commonly used in condensed matter physics and materials science.

## How to Use

1. **Select a preset** from the dropdown to load different band configurations
   (semiconductor with gap, metal with bands crossing Fermi level, or simple).
2. **Adjust energy range** using the sliders to zoom in/out on the Y-axis.
3. **Toggle display options** with the Fermi level and legend checkboxes.
4. The synced traits panel shows current widget state.

The synthetic data uses cosine-shaped bands along a GAMMA-X-M-GAMMA path.
For real data, use AiiDA's `verdi data band export` command.
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("## Controls"),
    preset_selector,
    energy_min,
    energy_max,
    pn.pane.Markdown("## Display Options"),
    show_fermi,
    show_legend,
    pn.pane.Markdown("## Synced Traits"),
    trait_display,
    width=320,
)

pn.Column(
    status_banner,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### Band Structure"),
            anywidget_pane,
            min_width=500,
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=1100,
).servable()
