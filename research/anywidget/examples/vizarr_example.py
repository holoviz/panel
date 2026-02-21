"""
vizarr Example — Zarr-based Image Viewer in Panel
==================================================

This example demonstrates using vizarr (a minimal Zarr-based image viewer)
with Panel's AnyWidget pane.

vizarr provides a purely client-side viewer for zarr-based images, supporting
2D slices of n-dimensional arrays with channel compositing. It uses the Viv
library for GPU-accelerated rendering.

Key traitlets:
    - _configs (List): Image layer configurations
    - view_state (Dict): Current viewer state (zoom, position, etc.)
    - height (Unicode): Viewer height as CSS string (default "500px")

KNOWN LIMITATION: vizarr requires zarr stores (local or remote) with
image data. This example uses a public OME-NGFF sample from the
Bio-Formats community. If the remote store is unavailable, the viewer
will render but show no image.

Required packages:
    pip install vizarr zarr

Run with:
    panel serve research/anywidget/examples/vizarr_example.py
"""

import panel as pn

try:
    import vizarr
except ImportError as e:
    raise ImportError(
        "This example requires vizarr. "
        "Please install it with: pip install vizarr"
    ) from e

try:
    import zarr
except ImportError as e:
    raise ImportError(
        "This example requires zarr. "
        "Please install it with: pip install zarr"
    ) from e

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

anywidget_pane = pn.pane.AnyWidget(viewer)

# ---------------------------------------------------------------------------
# 3. Panel controls for viewer height
# ---------------------------------------------------------------------------

component = anywidget_pane.component

height_select = pn.widgets.Select(
    name="Viewer Height",
    options=["400px", "500px", "600px", "700px", "800px"],
    value="600px",
    width=200,
)

height_select.param.watch(
    lambda e: setattr(component, "height", e.new), "value"
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
    header,
    pn.Row(height_select),
    anywidget_pane,
    pn.pane.Markdown("### Viewer State"),
    view_state_display,
    sizing_mode="stretch_width",
    max_width=1000,
).servable()
