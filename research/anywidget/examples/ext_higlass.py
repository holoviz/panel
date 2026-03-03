"""
HiGlass — Genomic Data Viewer with Compound AnyWidget Support
==============================================================

Renders the HiGlass genomic data viewer using Panel's AnyWidget pane.
HiGlass is a compound widget — its ``_tileset_client`` trait uses
``widget_serialization`` to reference a JupyterTilesetClient child widget
that handles RPC data fetching.  Panel's compound widget support resolves
this through ``widget_manager.get_model(id)`` on the JS side.

GitHub: https://github.com/higlass/higlass-python
Docs:   https://docs.higlass.io/

Required package:
    higlass-python

Run with:
    panel serve research/anywidget/examples/ext_higlass.py --dev

KNOWN LIMITATIONS:
- Local tilesets (hg.cooler()) are not supported — only remote server
  tilesets work because the JupyterTilesetClient uses comm messages for
  local data fetching, which Panel does not implement.
- The HiGlass ESM bundles the React-based viewer (~11 KB compressed).
"""

import higlass as hg

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create a HiGlass view configuration with a remote tileset
# ---------------------------------------------------------------------------

tileset = hg.remote(
    uid="CQMd6V_cRw6iCI_-Unl3PQ",
    server="https://higlass.io/api/v1/",
    name="Rao et al. (2014) GM12878 MboI (allreps) 1kb",
)

track = tileset.track("heatmap")

view = hg.view(
    hg.track("top-axis"),
    track,
)

higlass_widget = view.widget()

# ---------------------------------------------------------------------------
# 2. Wrap with Panel's AnyWidget pane
# ---------------------------------------------------------------------------

anywidget_pane = pn.pane.AnyWidget(
    higlass_widget, height=700, sizing_mode="stretch_width",
)

# ---------------------------------------------------------------------------
# 3. Wire Panel controls for bidirectional sync
# ---------------------------------------------------------------------------

component = anywidget_pane.component

location_display = pn.pane.JSON({}, name="Current Location", width=400, depth=3)


def on_location_change(*events):
    for event in events:
        if event.name == "location":
            location_display.object = {"location": event.new} if event.new else {}


if hasattr(component.param, "location"):
    component.param.watch(on_location_change, ["location"])

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

header = pn.pane.Markdown("""
# HiGlass Genomic Data Viewer — Compound AnyWidget

[GitHub](https://github.com/higlass/higlass-python) |
[Docs](https://docs.higlass.io/)

This example renders **HiGlass** — a genomic data visualization tool — using
Panel's AnyWidget pane. HiGlass is a *compound widget* — its
``_tileset_client`` trait references a JupyterTilesetClient child widget.

The viewer displays a Hi-C contact matrix heatmap from the Rao et al. (2014)
dataset hosted on the public HiGlass server.

**Interact:** Scroll to zoom, click and drag to pan.
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
