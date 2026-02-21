"""
CEV (Comparative Embedding Visualization) — Not a Direct anywidget (ipywidgets.VBox)
=====================================================================================

This example documents why the CEV (Comparative Embedding Visualization)
widget cannot be used with Panel's AnyWidget pane.

CEV's EmbeddingComparisonWidget extends ipywidgets.VBox, NOT
anywidget.AnyWidget. While CEV is listed in the anywidget gallery
because it is "implemented with anywidget and builds upon jupyter-scatter",
the top-level widget class is a composite ipywidgets container, not a
direct anywidget.

Panel's AnyWidget pane works by extracting an anywidget's _esm source
and traitlets, then rendering them through Panel's ReactiveESM pipeline.
Since EmbeddingComparisonWidget does not have _esm or sync-tagged
traitlets in the anywidget sense, the pane cannot render it.

Required package:
    pip install cev

Run with:
    panel serve research/anywidget/examples/ext_cev.py
"""

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# Document why CEV cannot work with Panel's AnyWidget pane
# ---------------------------------------------------------------------------

header = pn.pane.Markdown("""
# CEV (Comparative Embedding Visualization) -- Not Compatible

## The Problem

**CEV's `EmbeddingComparisonWidget`** extends `ipywidgets.VBox`, NOT
`anywidget.AnyWidget`. While CEV is listed in the
[anywidget gallery](https://anywidget.dev/en/community/) because it
uses anywidget internally (via jupyter-scatter), the top-level widget
class is a **composite ipywidgets container**.

Panel's `AnyWidget` pane detects widgets by checking for `_esm` and
`traits()` — the hallmarks of a direct `anywidget.AnyWidget` subclass.
Since `EmbeddingComparisonWidget` is an `ipywidgets.VBox`:

- It has **no `_esm`** attribute (no ESM JavaScript module)
- Its traitlets are VBox children/layout traits, not embedding-specific data
- The actual visualization lives inside nested jupyter-scatter widgets

## What Works vs. What Doesn't

| Feature | Status |
|---------|--------|
| Python-side widget creation | Works |
| AnyWidget pane detection (`applies()`) | **Fails** (no `_esm`) |
| ESM extraction | **N/A** (no ESM to extract) |
| Panel rendering | **Not possible** |

## Widget Architecture

```
EmbeddingComparisonWidget (ipywidgets.VBox)
    children:
        MetricDropdown (ipywidgets widget)
        EmbeddingWidget (uses jupyter-scatter internally)
        EmbeddingWidget (uses jupyter-scatter internally)
        ControlWidgets (zoom, colormap, etc.)
```

The individual `jupyter-scatter` widgets inside CEV ARE anywidgets, but
they are deeply nested and not directly accessible for wrapping.

## Alternative Approaches

1. **Use jupyter-scatter directly:** The underlying
   [jupyter-scatter](https://github.com/flekschas/jupyter-scatter) library
   IS a direct anywidget and may work with Panel's AnyWidget pane for
   individual scatter plot visualizations.

2. **Use ipywidgets_bokeh:** For the full CEV composite widget, the
   traditional `ipywidgets_bokeh` approach would be needed to render
   the entire ipywidgets.VBox tree in Panel.

3. **Rebuild in Panel:** The comparison visualization could be recreated
   using Panel's native components with jupyter-scatter or hvplot for the
   individual scatter plots.

## Example Usage (Jupyter Only)

For reference, here is how CEV is used in a Jupyter environment:

```python
import pandas as pd
from cev.widgets import Embedding, EmbeddingComparisonWidget

# Load two embeddings from parquet files
umap = Embedding.from_ozette(pd.read_parquet("umap.pq"))
ozette = Embedding.from_ozette(pd.read_parquet("ozette.pq"))

# Create comparison widget (ipywidgets.VBox, not anywidget)
widget = EmbeddingComparisonWidget(
    umap,
    ozette,
    titles=["Standard UMAP", "Annotation-Transformed UMAP"],
    metric="confusion",
    selection="synced",
    auto_zoom=True,
    row_height=320,
)
widget  # displays in Jupyter
```

## CEV Package Info

- **Package:** `pip install cev`
- **Repository:** [OzetteTech/comparative-embedding-visualization](https://github.com/OzetteTech/comparative-embedding-visualization)
- **Widget class:** `cev.widgets.EmbeddingComparisonWidget` (extends `ipywidgets.VBox`)
- **Internal dependencies:** jupyter-scatter (anywidget), Rust-compiled metrics
- **Quick demo:** `uvx --python 3.11 cev demo` (launches in JupyterLab)
""")

pn.Column(
    header,
    sizing_mode="stretch_width",
    max_width=900,
).servable()
