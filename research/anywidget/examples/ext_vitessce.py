"""
Vitessce Example — Spatial Single-Cell Visualization with Panel AnyWidget Pane
===============================================================================

This example demonstrates rendering the Vitessce spatial single-cell data
viewer using Panel's AnyWidget pane. Vitessce is an interactive tool for
visual integration and exploration of spatial single-cell experiments.

The VitessceWidget is a genuine anywidget.AnyWidget subclass with synced
traitlets (_config, height, theme, proxy, etc.) and ESM that dynamically
loads the Vitessce React application from a CDN.

KNOWN LIMITATIONS:
- Vitessce's ESM dynamically imports React and the Vitessce library from
  unpkg.com CDN at runtime. This requires internet access and may take a
  moment to load on first render.
- The _config traitlet is prefixed with underscore, so the AnyWidget pane
  may not expose it as a user-facing param (it filters names starting with _).
  However, height and theme are exposed as regular synced traitlets.
- Complex data setups (AnnData, OME-TIFF, etc.) require additional packages
  and data preparation. This example uses a minimal remote JSON configuration.

Required package:
    pip install vitessce

Run with:
    panel serve research/anywidget/examples/ext_vitessce.py
"""

from vitessce import ViewType as vt, VitessceConfig

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create a Vitessce configuration
# ---------------------------------------------------------------------------

# Create a minimal Vitessce config with a scatterplot view
# This uses the view config API without any data -- it will show
# an empty viewer that demonstrates the widget rendering.
vc = VitessceConfig(schema_version="1.0.15", name="Panel AnyWidget Demo")

# Add an empty dataset
ds = vc.add_dataset(name="Demo Dataset")

# Add a description view
desc = vc.add_view(vt.DESCRIPTION, dataset=ds)

# Set up layout
vc.layout(desc)

# Create the widget -- this returns a VitessceWidget (anywidget.AnyWidget subclass)
# Synced traitlets: _config (Dict), height (Int), theme (Unicode),
#   proxy (Bool), js_package_version (Unicode), plugin_esm (List)
vitessce_widget = vc.widget(height=500, theme="light")

# ---------------------------------------------------------------------------
# 2. Wrap with Panel's AnyWidget pane
# ---------------------------------------------------------------------------

# NOTE: Vitessce's "height" trait (Int) collides with Panel's "height" param.
# The AnyWidget pane renames it to "w_height" on the component. The Vitessce
# ESM calls model.get("height") on the JS side, which does NOT resolve to
# "w_height" — this is a known framework limitation.  Set explicit sizing
# on the component to ensure the container has non-zero dimensions.
anywidget_pane = pn.pane.AnyWidget(vitessce_widget, sizing_mode="stretch_width")

# ---------------------------------------------------------------------------
# 3. Wire Panel controls for bidirectional sync
# ---------------------------------------------------------------------------

component = anywidget_pane.component

# Set explicit height on the component to give the container non-zero dimensions
component.height = 500
component.sizing_mode = "stretch_width"

# Height control
height_slider = pn.widgets.IntSlider(
    name="Widget Height",
    start=300,
    end=800,
    value=500,
    width=300,
)

# Theme selector
theme_select = pn.widgets.Select(
    name="Theme",
    options=["light", "dark"],
    value="light",
    width=200,
)

# Panel -> Widget sync
# NOTE: Vitessce's "height" trait is renamed to "w_height" due to collision
# with Panel's Layoutable.height.  We also update the Panel component height
# so the container resizes along with the Vitessce viewer.
def on_height_change(e):
    if hasattr(component.param, 'w_height'):
        component.w_height = e.new
    component.height = e.new  # Also resize the container

height_slider.param.watch(on_height_change, "value")

if hasattr(component.param, 'theme'):
    theme_select.param.watch(
        lambda e: setattr(component, 'theme', e.new), "value"
    )

# Widget -> Panel sync
def on_component_change(*events):
    for event in events:
        if event.name == "w_height":
            height_slider.value = event.new
        elif event.name == "theme":
            theme_select.value = event.new

watch_params = [p for p in ["w_height", "theme"] if hasattr(component.param, p)]
if watch_params:
    component.param.watch(on_component_change, watch_params)

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

header = pn.pane.Markdown("""
# Vitessce Spatial Single-Cell Viewer -- Panel AnyWidget Pane

This example renders the **Vitessce** viewer natively in Panel using the
`AnyWidget` pane. Vitessce is a visual integration tool for exploration of
spatial single-cell experiments.

## How It Works

The VitessceWidget loads the Vitessce React application dynamically from a
CDN (unpkg.com). The widget syncs configuration, height, and theme via
traitlets mapped to Panel params.

## Controls

- **Height:** Adjust the viewer height using the slider
- **Theme:** Switch between light and dark themes

## About Vitessce

[Vitessce](http://vitessce.io) supports visualization of:
- Spatial transcriptomics data
- Single-cell RNA-seq embeddings (UMAP, t-SNE)
- Cell segmentation and spatial coordinates
- Gene expression heatmaps
- Multi-modal data coordination

## Known Limitations

- The Vitessce ESM dynamically imports ~2-3 MB of JavaScript from CDN at
  runtime. First load may be slow.
- The `_config` traitlet is underscore-prefixed and may not be exposed as
  a user-facing param by the AnyWidget pane.
- For full-featured usage with actual data (AnnData, Zarr, OME-TIFF),
  additional packages are needed: `pip install 'vitessce[all]'`
""")

controls = pn.Column(
    pn.pane.Markdown("### Controls"),
    height_slider,
    theme_select,
    width=350,
)

pn.Column(
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### Vitessce Viewer"),
            anywidget_pane,
            sizing_mode="stretch_width",
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=1200,
).servable()
