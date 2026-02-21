"""
Rerun SDK Viewer — Size Issue (Minimal Reproducible Example)
=============================================================

This file documents the limitation of using the Rerun SDK viewer widget
with Panel's AnyWidget pane. The rerun-notebook package bundles the entire
Rerun Viewer compiled to WebAssembly (~31 MiB for re_viewer_bg.wasm) plus
JavaScript glue code that loads it.

The Problem
-----------
The Rerun viewer's ESM stub is small (~54 bytes), but it dynamically loads
a very large WASM bundle (~31 MiB). The asset loading relies on anywidget's
internal file serving mechanism (via _esm file path resolution), which Panel's
AnyWidget pane does not support. Panel inlines the ESM as a string, bypassing
the file-based asset serving that rerun-notebook depends on.

As a result:
1. The ESM is extracted and sent over WebSocket (this works -- it's small)
2. The ESM tries to load the WASM bundle from a relative path
3. The WASM bundle cannot be found because Panel does not serve the assets
4. The viewer fails to initialize

See also: ext_rerun.py for the full documentation example.

Required packages:
    pip install "rerun-sdk[notebook]"

Run with:
    panel serve research/anywidget/examples/issue_rerun_sdk_viewer.py
"""

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# Minimal Reproducible Example
# ---------------------------------------------------------------------------
# The following code demonstrates the issue. Uncomment to attempt rendering
# (will fail with asset loading errors in the browser).

# from rerun_notebook import Viewer
# viewer = Viewer(width=800, height=600)
# anywidget_pane = pn.pane.AnyWidget(viewer)

# ---------------------------------------------------------------------------
# What happens when you try
# ---------------------------------------------------------------------------
# 1. Panel extracts the ESM from the Viewer widget (a short loader stub)
# 2. The ESM is sent to the browser via WebSocket
# 3. The browser executes the ESM, which tries to fetch the WASM bundle
#    from a relative URL (e.g., ./re_viewer_bg.wasm)
# 4. The fetch fails because Panel's server does not serve the WASM file
# 5. The viewer shows a blank area or errors in the console

# ---------------------------------------------------------------------------
# Information display
# ---------------------------------------------------------------------------

try:
    from rerun_notebook import Viewer
    viewer = Viewer(width=800, height=600)
    esm_length = len(getattr(viewer, '_esm', '') or '')
    traits_info = [(n, type(t).__name__) for n, t in viewer.traits(sync=True).items()
                   if not n.startswith('_model') and not n.startswith('_view')]
    widget_info = f"""
- **rerun-notebook Viewer** is an anywidget.AnyWidget subclass
- **ESM stub size:** {esm_length} bytes (small loader, not the actual viewer)
- **WASM bundle:** ~31 MiB (`re_viewer_bg.wasm`) -- loaded dynamically by ESM
- **Synced traits:** {', '.join(f'`{n}` ({t})' for n, t in traits_info)}
"""
except Exception as e:
    widget_info = f"Could not inspect Viewer: {e}"

header = pn.pane.Markdown(f"""
# Rerun SDK Viewer -- Size Issue

## Minimal Reproducible Example

```python
from rerun_notebook import Viewer
import panel as pn

pn.extension()

viewer = Viewer(width=800, height=600)
pn.pane.AnyWidget(viewer).servable()
```

Running this will fail because the WASM bundle cannot be served.

## Widget Details

{widget_info}

## Root Cause

The Rerun viewer's ESM is a small loader stub that dynamically fetches
`re_viewer_bg.wasm` (~31 MiB) from a relative path. Panel's AnyWidget pane
inlines the ESM as a string and does not serve companion asset files, so the
WASM fetch fails.

## Potential Fixes

1. **Asset proxy**: Panel could proxy the anywidget's static file directory
   through its Tornado server, allowing relative WASM/JS fetches to resolve.
2. **External ESM URL**: Support loading ESM from a URL instead of inlining,
   so the viewer can use its CDN mode (`RERUN_NOTEBOOK_ASSET` env var).
3. **Use ipywidgets_bokeh bridge** as a workaround (if available).
""")

pn.Column(
    header,
    sizing_mode="stretch_width",
    max_width=900,
).servable()
