"""
HiGlass Example — Genomic Data Viewer with Panel AnyWidget Pane
================================================================

This example demonstrates rendering the HiGlass genomic data viewer
using Panel's AnyWidget pane. HiGlass is an interactive tool for
exploring genomic contact matrices and other genomic data types.

The HiGlassWidget is a genuine anywidget.AnyWidget subclass with
synced traitlets (_viewconf, _options, location, etc.) and a bundled
ESM module. This example uses a remote tileset from the HiGlass
public server to display a Hi-C contact matrix heatmap.

KNOWN LIMITATIONS:
- The HiGlass ESM bundles the entire React-based HiGlass viewer. If the
  ESM is very large, it may hit WebSocket payload limits (similar to
  anymap-ts). If that happens, you will see "Lost websocket connection".
- The widget uses a custom JupyterTilesetClient for data fetching via
  comm messages. Panel does not implement the comm protocol, so only
  remote tilesets (server-hosted) are expected to work. Local tilesets
  (hg.cooler()) will not work.
- The `location` trait is read-only from the widget side.

Required package:
    pip install higlass-python

Run with:
    panel serve research/anywidget/examples/higlass_example.py
"""

import panel as pn

try:
    import higlass as hg
except ImportError as e:
    raise ImportError(
        "This example requires higlass-python. "
        "Please install it with: pip install higlass-python"
    ) from e

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create a HiGlass view configuration with a remote tileset
# ---------------------------------------------------------------------------

# Remote tileset from the public HiGlass server
tileset = hg.remote(
    uid="CQMd6V_cRw6iCI_-Unl3PQ",
    server="https://higlass.io/api/v1/",
    name="Rao et al. (2014) GM12878 MboI (allreps) 1kb",
)

# Create a heatmap track from the remote tileset
track = tileset.track("heatmap")

# Create a view with a top axis and the heatmap
view = hg.view(
    hg.track("top-axis"),
    track,
)

# The view object is a HiGlassWidget (anywidget.AnyWidget subclass)
# It has synced traitlets: _viewconf (Dict), location (List), _options (Dict)

# ---------------------------------------------------------------------------
# 2. Wrap with Panel's AnyWidget pane
# ---------------------------------------------------------------------------

anywidget_pane = pn.pane.AnyWidget(view, height=500, sizing_mode="stretch_width")

# ---------------------------------------------------------------------------
# 3. Wire Panel controls for bidirectional sync
# ---------------------------------------------------------------------------

component = anywidget_pane.component

# Display the current location (read-only from widget)
location_display = pn.pane.JSON({}, name="Current Location", width=400)


def on_location_change(*events):
    for event in events:
        if event.name == "location":
            location_display.object = {"location": event.new} if event.new else {}


# Watch the location trait (updated when user navigates)
if hasattr(component.param, 'location'):
    component.param.watch(on_location_change, ["location"])

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

header = pn.pane.Markdown("""
# HiGlass Genomic Data Viewer -- Panel AnyWidget Pane

This example renders the **HiGlass** genomic visualization tool natively
in Panel using the `AnyWidget` pane. The viewer displays a Hi-C contact
matrix heatmap from the Rao et al. (2014) dataset hosted on the public
HiGlass server.

## How to Interact

- **Zoom:** Scroll to zoom in/out on the heatmap
- **Pan:** Click and drag to navigate
- **Location:** The current genomic location is displayed below (if sync works)

## About HiGlass

[HiGlass](https://higlass.io) is a tool for exploring genomic contact
matrices, genome interaction profiles, and other types of multiscale
genomic data. It uses the anywidget framework to provide a Jupyter-native
widget with a React-based viewer.

## Known Limitations

- The HiGlass ESM may be large (bundles React + HiGlass viewer). If the
  WebSocket disconnects, the ESM payload may exceed transmission limits.
- Local tilesets (hg.cooler) are not supported -- only remote server tilesets work
  because Panel does not implement the Jupyter comm protocol used for local data fetching.
""")

location_section = pn.Column(
    pn.pane.Markdown("### Navigation State"),
    location_display,
    width=400,
)

pn.Column(
    header,
    anywidget_pane,
    location_section,
    sizing_mode="stretch_width",
    max_width=1000,
).servable()
