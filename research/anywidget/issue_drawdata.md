# Bug: `circle_brush` ReferenceError breaks widget initialization in non-Jupyter environments

## Summary

`drawdata.ScatterWidget()` throws `Uncaught ReferenceError: Cannot access 'circle_brush' before initialization` when rendered in frameworks that use the anywidget ESM spec directly (e.g., Panel's `AnyWidget` pane, Marimo). This error breaks the widget's `model.on("change:...")` event handlers, preventing bidirectional sync between the frontend and Python.

## Reproduction

CANNOT RUN BEFORE RELEASE OF PANEL UPCOMING ANYWIDGET PANE. SEE https://github.com/holoviz/panel/pull/8428

### Minimal reproducible example (Panel)

```bash
pip install drawdata panel
```

```python
# drawdata_bug.py
import panel as pn
from drawdata import ScatterWidget

pn.extension()

widget = ScatterWidget()
pane = pn.pane.AnyWidget(widget)

# Try to sync brushsize changes
brushsize_display = pn.pane.Markdown(f"**Brush size:** {widget.brushsize}")
widget.observe(
    lambda change: setattr(brushsize_display, 'object', f"**Brush size:** {change['new']}"),
    names=['brushsize']
)

pn.Column(
    "# drawdata ScatterWidget — circle_brush bug",
    pane,
    brushsize_display,
).servable()
```

```bash
panel serve drawdata_bug.py
```

### Expected behavior

The ScatterWidget renders fully. Changing `brushsize` from Python updates the widget's brush size in the browser, and drawing points syncs back to Python via the `data` traitlet.

### Actual behavior

The widget partially renders (canvas and class buttons appear), but the browser console shows:

```
Uncaught ReferenceError: Cannot access 'circle_brush' before initialization
    at button.onclick (<esm>:9611:7)
    at <esm>:9616:14
    at Array.forEach (<anonymous>)
    at h.render (<esm>:9575:14)
```

Additionally:
```
Error: <svg> attribute height: Expected length, "auto".
```

Because the error occurs during the `render()` function, the `model.on("change:brushsize", ...)` and `model.on("change:n_classes", ...)` handlers may never be registered, which breaks bidirectional sync:

- **Widget -> Python:** Drawing does not sync `data` traitlet reliably
- **Python -> Widget:** Changing `widget.brushsize` from Python does not update the brush in the browser

## Root Cause Analysis

The `circle_brush` variable appears to be referenced before its declaration in the bundled ESM. This is likely a JavaScript variable hoisting issue in the build output — `circle_brush` is used in an `onclick` handler that executes during `render()`, but the variable declaration appears later in the bundle.

## Environment

- drawdata version: 0.5.0
- anywidget version: 0.9.x
- Panel version: 1.x (development branch with AnyWidget pane)
- Python: 3.12
- Browser: Chromium
- OS: Linux

## Notes

- The same widget works in JupyterLab because Jupyter's comm infrastructure handles initialization differently (the widget model is fully constructed before `render()` is called)
- Other anywidgets (e.g., wigglystuff, custom inline ESM widgets) render correctly in Panel, confirming this is a drawdata-specific issue
- The `<svg> attribute height: "auto"` error also suggests SVG sizing issues in the ESM bundle
