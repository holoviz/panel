"""
vizarr Example — Zarr-based Image Viewer in Panel
==================================================

This example demonstrates using vizarr (a minimal Zarr-based image viewer)
with Panel's AnyWidget pane.

vizarr provides a purely client-side viewer for zarr-based images, supporting
2D slices of n-dimensional arrays with channel compositing. It uses the Viv
library for GPU-accelerated rendering.

GitHub: https://github.com/hms-dbmi/vizarr
Docs:   https://github.com/hms-dbmi/vizarr#readme

Key traitlets:
    - _configs (List): Image layer configurations
    - view_state (Dict): Current viewer state (zoom, position, etc.)
    - height (Unicode): Viewer height as CSS string (default "500px")
      NOTE: vizarr's `height` trait (Unicode) collides with Panel's `height`
      param (Integer). The AnyWidget pane renames it to `w_height`.

KNOWN LIMITATION: vizarr requires zarr stores (local or remote) with
image data. This example uses a public OME-NGFF sample from the
Bio-Formats community. If the remote store is unavailable, the viewer
will render but show no image.

Required packages:
    pip install vizarr zarr

Run with:
    panel serve research/anywidget/examples/ext_vizarr.py
"""

import vizarr
import zarr

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create the vizarr Viewer with a public OME-NGFF dataset
# ---------------------------------------------------------------------------

viewer = vizarr.Viewer(height="600px")

# Add a public OME-NGFF sample image from the BioFormats community
# This is a remote zarr store served over HTTP
try:
    store = zarr.open(
        "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.4/idr0062A/6001240.zarr",
        mode="r",
    )
    viewer.add_image(source=store)
    image_loaded = True
except Exception:
    image_loaded = False

# ---------------------------------------------------------------------------
# 2. Wrap with AnyWidget pane
# ---------------------------------------------------------------------------

# NOTE: vizarr's "height" trait (Unicode, e.g. "600px") collides with Panel's
# integer "height" param. The AnyWidget pane renames it to "w_height" on the
# component. However, vizarr's ESM calls model.get("height") on the JS side,
# which currently does NOT resolve to "w_height" — this is a known framework
# limitation (the trait_name_map is not exposed to the TypeScript adapter).
# As a workaround, set explicit sizing on the component so the container
# element has non-zero dimensions.
anywidget_pane = pn.pane.AnyWidget(viewer, sizing_mode="stretch_width")

# ---------------------------------------------------------------------------
# 3. Panel controls for viewer height
# ---------------------------------------------------------------------------

component = anywidget_pane.component

# Set explicit height on the component so the Bokeh container element has
# a non-zero height. This uses Panel's integer height (pixels).
component.height = 600
component.sizing_mode = "stretch_width"

# Fix vizarr layer controller text visibility: the viewer has a black
# background but MUI components use dark text by default. Inject CSS to
# force light text colors on the controls sidebar.
component._stylesheets = ["""
/* vizarr layer controller: force light text on black background */
.MuiTypography-root,
.MuiTypography-caption,
.MuiTypography-body2,
.MuiAccordionSummary-content p,
.MuiAccordionDetails-root span,
.MuiFormLabel-root,
.MuiInputBase-root,
.MuiInput-root input {
    color: #e0e0e0 !important;
}
.MuiIconButton-root {
    color: #e0e0e0 !important;
}
.MuiSvgIcon-root {
    fill: #e0e0e0 !important;
}
.MuiSlider-rail {
    background-color: #555 !important;
}
.MuiAccordion-root {
    background-color: rgba(30, 30, 30, 0.85) !important;
}
"""]

height_select = pn.widgets.Select(
    name="Viewer Height",
    options=["400px", "500px", "600px", "700px", "800px"],
    value="600px",
    width=200,
)

height_select.param.watch(
    lambda e: setattr(component, "w_height", e.new), "value"
)

# Display view state reactively
view_state_display = pn.pane.JSON(
    viewer.view_state if viewer.view_state else {},
    name="View State",
    depth=2,
)

component.param.watch(
    lambda *events: setattr(
        view_state_display, "object",
        {e.name: e.new for e in events if e.name == "view_state"}.get("view_state", view_state_display.object)
    ),
    ["view_state"],
)

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

status_msg = (
    "Image loaded from public OME-NGFF store."
    if image_loaded
    else "**Warning:** Could not load the remote zarr store. "
    "The viewer is rendered but no image is displayed."
)

status = pn.pane.Markdown("""
<div style="background-color: #fff3cd; border: 2px solid #ffc107; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #856404; font-size: 20px; font-weight: bold; margin: 0;">
WORKS WITH CAVEATS
</p>
<p style="color: #856404; font-size: 15px; margin: 8px 0 0 0;">
<strong>Limitations:</strong> (1) Requires a remote zarr store &mdash; if the store is
unavailable, the viewer renders but shows no image.
(2) The <code>height</code> trait (Unicode, e.g. "600px") collides with Panel's
integer <code>height</code> and is renamed to <code>w_height</code>.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown(f"""
# vizarr — Zarr Image Viewer in Panel

**vizarr** is a minimal, client-side viewer for zarr-based images.
It supports 2D slices of n-dimensional arrays with channel compositing,
powered by GPU-accelerated rendering via the [Viv](https://github.com/hms-dbmi/viv) library.

{status_msg}

## How It Works

The `vizarr.Viewer()` widget is an anywidget. Panel wraps it with
`pn.pane.AnyWidget()` for native rendering. The `view_state` traitlet
tracks the current zoom and position, displayed below.

## Interaction

- **Pan** by clicking and dragging
- **Zoom** with the scroll wheel
- Use the layer controls (top-left) to toggle channels
""", sizing_mode="stretch_width")

pn.Column(
    status,
    header,
    pn.Row(height_select),
    anywidget_pane,
    pn.pane.Markdown("### Viewer State"),
    view_state_display,
    sizing_mode="stretch_width",
    max_width=1000,
).servable()
