"""
ipyniivue Example -- Neuroimaging Viewer
=========================================

This example demonstrates using ipyniivue's NiiVue widget with
Panel's AnyWidget pane. NiiVue is a WebGL-based neuroimaging viewer
for NIfTI volumes, meshes, and tractography data.

NiiVue renders a canvas-based 3D/2D viewer entirely in the browser.
Without loaded volumes, it displays a dark canvas with crosshair
controls. Volumes can be loaded from URLs or binary data.

GitHub: https://github.com/niivue/ipyniivue
NiiVue: https://niivue.github.io/niivue/

Key traitlets:
    - volumes (List): List of volume specifications (URL or data)
    - meshes (List): List of mesh specifications
    - opts (Instance[ConfigOptions]): Rendering options (crosshair color, etc.)
    - height (Int): Canvas height in pixels -- COLLIDES with Panel -> renamed to w_height
    - draw_opacity (Float): Drawing overlay opacity
    - overlay_alpha_shader (Float): Overlay alpha blending
    - background_masks_overlays (Int): Background mask setting

Required package:
    pip install ipyniivue

Run with:
    panel serve research/anywidget/examples/ext_ipyniivue.py

Testing Instructions:
    1. Run the app with the command above
    2. Verify the NiiVue canvas renders (dark canvas with crosshairs)
    3. Adjust the draw_opacity slider -- the value should sync
    4. Adjust the overlay_alpha_shader slider
    5. Try loading the sample MNI brain volume using the "Load Sample" button
       (requires internet access to fetch from niivue.github.io)
    6. Check the browser console for errors (F12)

Trait Name Collisions:
    - height -> renamed to w_height (collides with Panel's height param)
"""

from ipyniivue import NiiVue

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create the NiiVue widget
# ---------------------------------------------------------------------------

nv = NiiVue(height=450)

# Wrap with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(nv, height=500, sizing_mode="stretch_width")
component = anywidget_pane.component

# ---------------------------------------------------------------------------
# 2. Panel controls for bidirectional sync
# ---------------------------------------------------------------------------

draw_opacity_slider = pn.widgets.FloatSlider(
    name="Draw Opacity",
    start=0.0,
    end=1.0,
    step=0.05,
    value=component.draw_opacity,
    width=280,
)

overlay_alpha_slider = pn.widgets.FloatSlider(
    name="Overlay Alpha Shader",
    start=0.0,
    end=1.0,
    step=0.05,
    value=component.overlay_alpha_shader,
    width=280,
)

outline_width_slider = pn.widgets.FloatSlider(
    name="Overlay Outline Width",
    start=0.0,
    end=5.0,
    step=0.1,
    value=component.overlay_outline_width,
    width=280,
)

# Sync Panel -> Widget
draw_opacity_slider.param.watch(
    lambda e: setattr(component, 'draw_opacity', e.new), ['value']
)
overlay_alpha_slider.param.watch(
    lambda e: setattr(component, 'overlay_alpha_shader', e.new), ['value']
)
outline_width_slider.param.watch(
    lambda e: setattr(component, 'overlay_outline_width', e.new), ['value']
)

# Sync Widget -> Panel
component.param.watch(
    lambda e: setattr(draw_opacity_slider, 'value', e.new), ['draw_opacity']
)
component.param.watch(
    lambda e: setattr(overlay_alpha_slider, 'value', e.new), ['overlay_alpha_shader']
)
component.param.watch(
    lambda e: setattr(outline_width_slider, 'value', e.new), ['overlay_outline_width']
)

# Note: Loading NIfTI volumes from Python via component.volumes = [{"url": ...}]
# does not work because NiiVue's ESM expects volumes to be NVImage instances
# with internal data buffers (.slice()), not plain dicts.
# Volumes should be loaded via ipyniivue's Python API before wrapping:
#   nv = NiiVue()
#   nv.load_volumes([{"url": "https://niivue.github.io/niivue/images/mni152.nii.gz"}])
# This requires Jupyter kernel messaging which Panel doesn't provide.

# Trait display
trait_display = pn.pane.JSON(
    {
        "draw_opacity": nv.draw_opacity,
        "overlay_alpha_shader": nv.overlay_alpha_shader,
        "overlay_outline_width": nv.overlay_outline_width,
        "w_height": getattr(component, 'w_height', nv.height),
    },
    name="Synced Traits",
    depth=2,
    width=280,
)


def on_trait_change(*events):
    trait_display.object = {
        "draw_opacity": component.draw_opacity,
        "overlay_alpha_shader": component.overlay_alpha_shader,
        "overlay_outline_width": component.overlay_outline_width,
        "w_height": getattr(component, 'w_height', 'N/A'),
    }


component.param.watch(
    on_trait_change,
    ["draw_opacity", "overlay_alpha_shader", "overlay_outline_width"],
)

# ---------------------------------------------------------------------------
# 3. Layout
# ---------------------------------------------------------------------------

status_banner = pn.pane.Markdown("""
<div style="background-color: #fff3cd; border: 2px solid #ffc107; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #856404; font-size: 20px; font-weight: bold; margin: 0;">
WORKS WITH CAVEATS
</p>
<p style="color: #856404; font-size: 15px; margin: 8px 0 0 0;">
NiiVue's WebGL canvas renders and scalar rendering parameters
(<code>draw_opacity</code>, <code>overlay_alpha_shader</code>, etc.) sync
bidirectionally. However, <strong>loading volumes is not supported</strong>:
NiiVue volumes are compound child ipywidgets (<code>IPY_MODEL_</code> references)
that require Jupyter's widget manager to resolve. Panel's AnyWidget pane only
supports leaf anywidgets with flat traits. For full NiiVue functionality with
volumes, use <code>pn.pane.IPyWidget</code> in a Jupyter environment.
The <code>height</code> trait collides with Panel and is renamed to
<code>w_height</code>.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# ipyniivue -- Neuroimaging Viewer

**[ipyniivue](https://github.com/niivue/ipyniivue)** is an anywidget wrapper
around [NiiVue](https://niivue.github.io/niivue/), a WebGL-based viewer for
neuroimaging data (NIfTI volumes, meshes, tractography).

## How to Use

1. **View the canvas:** The NiiVue viewer starts with an empty dark canvas
   and crosshair controls.
2. **Adjust rendering:** Use the sliders to modify draw opacity and overlay
   settings. These sync in real time.

## Trait Collision Note

The `height` traitlet collides with Panel's built-in `height` parameter.
It is automatically renamed to `w_height` on the component.
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("## Rendering Controls"),
    draw_opacity_slider,
    overlay_alpha_slider,
    outline_width_slider,
    pn.pane.Markdown("## Synced Traits"),
    trait_display,
    width=320,
)

pn.Column(
    status_banner,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### NiiVue Viewer"),
            anywidget_pane,
            min_width=500,
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=1100,
).servable()
