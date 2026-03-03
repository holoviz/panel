# CEV (Comparative Embedding Visualization) — Incompatibility with Panel's AnyWidget Pane

## Summary

CEV's `EmbeddingComparisonWidget` extends `ipywidgets.VBox`, not `anywidget.AnyWidget`. While CEV is listed in the anywidget gallery because it uses anywidget internally (via jupyter-scatter), the top-level widget class is a composite ipywidgets container without an `_esm` attribute or anywidget-style sync traitlets. Panel's AnyWidget pane cannot detect or render it.

## Environment
- Panel: latest (PR #8428)
- cev: 0.2.1
- Python: 3.10+

## Root Cause

Panel's AnyWidget pane identifies compatible widgets by checking for the `_esm` attribute and `traits()` method that are hallmarks of a direct `anywidget.AnyWidget` subclass. CEV's `EmbeddingComparisonWidget` inherits from `ipywidgets.VBox`, which means:

1. **No `_esm` attribute**: The widget has no ESM JavaScript module to extract and render.
2. **No anywidget-style traitlets**: Its traitlets are VBox children/layout traits, not embedding-specific data traits.
3. **Composite architecture**: The actual visualization lives inside nested jupyter-scatter widgets that are children of the VBox.

The widget's internal architecture is:

```
EmbeddingComparisonWidget (ipywidgets.VBox)
    children:
        MetricDropdown (ipywidgets widget)
        EmbeddingWidget (uses jupyter-scatter internally)
        EmbeddingWidget (uses jupyter-scatter internally)
        ControlWidgets (zoom, colormap, etc.)
```

The individual jupyter-scatter widgets inside CEV are genuine anywidgets, but they are deeply nested and not directly accessible for wrapping with the AnyWidget pane.

## Minimal Reproducible Example

```python
import pandas as pd
from cev.widgets import Embedding, EmbeddingComparisonWidget

import panel as pn

pn.extension()

# Create sample embeddings
umap = Embedding.from_ozette(pd.read_parquet("umap.pq"))
ozette = Embedding.from_ozette(pd.read_parquet("ozette.pq"))

widget = EmbeddingComparisonWidget(
    umap,
    ozette,
    titles=["Standard UMAP", "Annotation-Transformed UMAP"],
    metric="confusion",
    selection="synced",
    auto_zoom=True,
    row_height=320,
)

# This will fail — applies() returns False because there is no _esm
pn.pane.AnyWidget(widget).servable()
```

## Expected vs Actual
- **Expected:** Widget renders in Panel's AnyWidget pane
- **Actual:** The AnyWidget pane's `applies()` check returns `False` because `EmbeddingComparisonWidget` has no `_esm` attribute. The widget is an `ipywidgets.VBox`, not an `anywidget.AnyWidget`, so there is no ESM to extract and no anywidget-style traitlets to map to Param parameters.

## Context

This issue was discovered while testing compatibility of anywidget-based widgets with Panel's `pn.pane.AnyWidget` pane (PR [#8428](https://github.com/holoviz/panel/pull/8428)). The AnyWidget pane provides a Param-integrated wrapper for leaf anywidgets.

## Workaround

Use `pn.pane.IPyWidget` with `pn.extension("ipywidgets")` instead, which can render the entire ipywidgets.VBox tree:

```python
import pandas as pd
from cev.widgets import Embedding, EmbeddingComparisonWidget

import panel as pn

pn.extension("ipywidgets")

umap = Embedding.from_ozette(pd.read_parquet("umap.pq"))
ozette = Embedding.from_ozette(pd.read_parquet("ozette.pq"))

widget = EmbeddingComparisonWidget(
    umap, ozette,
    titles=["Standard UMAP", "Annotation-Transformed UMAP"],
    metric="confusion",
)

pn.pane.IPyWidget(widget).servable()
```

Alternatively, the underlying [jupyter-scatter](https://github.com/flekschas/jupyter-scatter) library is a direct anywidget and may work with Panel's AnyWidget pane for individual scatter plot visualizations.

## Suggested Fix

This is not a bug in CEV or Panel. CEV is architecturally a composite ipywidgets container, not a leaf anywidget. The recommended approach is to use `pn.pane.IPyWidget` for composite widget trees, or to use the individual jupyter-scatter anywidgets directly if only scatter plot functionality is needed.
