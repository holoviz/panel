"""
Vitessce Example — Spatial Single-Cell Visualization with Panel AnyWidget Pane
===============================================================================

This example demonstrates rendering the Vitessce spatial single-cell data
viewer using Panel's AnyWidget pane. Vitessce is an interactive tool for
visual integration and exploration of spatial single-cell experiments.

The VitessceWidget is a genuine anywidget.AnyWidget subclass with synced
traitlets (_config, height, theme, proxy, etc.) and ESM that dynamically
loads the Vitessce React application from a CDN.

This demo uses the Codeluppi et al. 2018 Osmfish public dataset (mouse brain
somatosensory cortex) hosted on the Vitessce public S3 bucket. It includes:
- Spatial cell locations (tissue coordinates X, Y)
- t-SNE embedding (dimensionality reduction)
- Cluster / Subcluster annotations (excitatory, inhibitory neurons, etc.)

GitHub: https://github.com/vitessce/vitessce-python
Docs:   https://vitessce.github.io/vitessce-python/

KNOWN LIMITATIONS:
- Vitessce's ESM dynamically imports ~2-3 MB of JavaScript from unpkg.com
  CDN at runtime. First load may be slow (5-15s).
- The _config traitlet is prefixed with underscore, so the AnyWidget pane
  does not expose it as a user-facing param.
- The `height` trait collides with Panel's Layoutable.height and is renamed
  to `w_height` on the component.

Required package:
    pip install vitessce

Run with:
    panel serve research/anywidget/examples/ext_vitessce.py
"""

from vitessce import (
    CoordinationType as ct,
    FileType as ft,
    ViewType as vt,
    VitessceConfig,
)

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create a Vitessce configuration with public Codeluppi 2018 data
# ---------------------------------------------------------------------------

# The Codeluppi et al. 2018 Nature Methods dataset is a spatial
# transcriptomics dataset (osmFISH) of the mouse brain somatosensory cortex.
# CSV file columns: cell_id, TSNE_1, TSNE_2, PCA_1, PCA_2, Cluster,
#                   Subcluster, X, Y
DATA_BASE = "https://s3.amazonaws.com/vitessce-data/0.0.33/main/codeluppi-2018"

vc = VitessceConfig(
    schema_version="1.0.15",
    name="Codeluppi 2018 osmFISH — Panel AnyWidget Demo",
    description=(
        "Spatial transcriptomics (osmFISH) of the mouse brain somatosensory "
        "cortex. Data: Codeluppi et al., Nature Methods 2018."
    ),
)

ds = vc.add_dataset(name="Codeluppi 2018 osmFISH").add_file(
    url=f"{DATA_BASE}/codeluppi_2018_nature_methods.cells.csv",
    file_type=ft.OBS_LOCATIONS_CSV,
    options={"obsIndex": "cell_id", "obsLocations": ["X", "Y"]},
    coordination_values={"obsType": "cell"},
).add_file(
    url=f"{DATA_BASE}/codeluppi_2018_nature_methods.cells.csv",
    file_type=ft.OBS_EMBEDDING_CSV,
    options={"obsIndex": "cell_id", "obsEmbedding": ["TSNE_1", "TSNE_2"]},
    coordination_values={"obsType": "cell", "embeddingType": "t-SNE"},
).add_file(
    url=f"{DATA_BASE}/codeluppi_2018_nature_methods.cells.csv",
    file_type=ft.OBS_LABELS_CSV,
    options={"obsIndex": "cell_id", "obsLabels": "Cluster"},
    coordination_values={"obsType": "cell", "obsLabelsType": "Cluster"},
)

# Views: spatial map, t-SNE scatterplot, status
spatial = vc.add_view(vt.SPATIAL, dataset=ds)
scatterplot = vc.add_view(vt.SCATTERPLOT, dataset=ds)
status_view = vc.add_view(vt.STATUS, dataset=ds)

# Link scatterplot to t-SNE embedding
vc.link_views([scatterplot], [ct.EMBEDDING_TYPE], ["t-SNE"])

# Layout: spatial on left, scatterplot + status on right
vc.layout(spatial | (scatterplot / status_view))

# Create the widget
vitessce_widget = vc.widget(height=600, theme="dark")

# ---------------------------------------------------------------------------
# 2. Wrap with Panel's AnyWidget pane
# ---------------------------------------------------------------------------

anywidget_pane = pn.pane.AnyWidget(vitessce_widget, sizing_mode="stretch_width")

# ---------------------------------------------------------------------------
# 3. Wire Panel controls
# ---------------------------------------------------------------------------

component = anywidget_pane.component
component.height = 600
component.sizing_mode = "stretch_width"

# Theme selector
theme_select = pn.widgets.Select(
    name="Theme",
    options=["dark", "light"],
    value="dark",
    width=200,
)

if hasattr(component.param, "theme"):
    theme_select.param.watch(
        lambda e: setattr(component, "theme", e.new), "value"
    )

    def on_theme_change(*events):
        for event in events:
            if event.name == "theme":
                theme_select.value = event.new

    component.param.watch(on_theme_change, ["theme"])

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

banner = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
Vitessce loads ~2-3 MB of JavaScript from CDN on first render. Please wait
10-15 seconds for the viewer to appear. The <code>height</code> trait collides
with Panel's <code>height</code> and is renamed to <code>w_height</code>.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# Vitessce — Spatial Single-Cell Viewer

[GitHub](https://github.com/vitessce/vitessce-python) |
[Docs](https://vitessce.github.io/vitessce-python/) |
[Vitessce Web](http://vitessce.io/)

**Vitessce** is a framework for visual integration and exploration of spatial
single-cell experiments. This demo loads the **Codeluppi et al. 2018** osmFISH
dataset (mouse brain somatosensory cortex) from a public S3 bucket.

## What You See

- **Left panel (Spatial):** Physical tissue coordinates of cells (X, Y positions).
- **Right top (Scatterplot):** t-SNE dimensionality reduction of gene expression.
- **Right bottom (Status):** Viewer status and data loading progress.

## Interaction

- **Pan** by clicking and dragging
- **Zoom** with the scroll wheel
- **Hover** over cells to see annotations

## First Load

The viewer dynamically loads JavaScript from unpkg.com CDN. It may take
10-15 seconds to appear on first load. Then cell data (~3300 cells) loads
from S3.
""", sizing_mode="stretch_width")

pn.Column(
    banner,
    header,
    pn.Row(theme_select),
    anywidget_pane,
    sizing_mode="stretch_width",
    max_width=1200,
).servable()
