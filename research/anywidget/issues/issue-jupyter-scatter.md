# jupyter-scatter: WebGL canvas sizing crash in shadow DOM (transformMat4 null)

## Summary

When rendering jupyter-scatter's `JupyterScatter` widget inside a shadow DOM (as used by Panel's AnyWidget pane), `createScatterplot` crashes with:

```
TypeError: Cannot read properties of null (reading '0')
  at transformMat4 → getScatterGlPos → initCamera → init → createScatterplot
```

The crash occurs because `invert()` returns `null` for a singular projection matrix, which happens when the WebGL canvas has zero pixel dimensions inside the shadow DOM boundary. Even when the crash is silenced, the scatter plot does not render because the WebGL context is not properly initialized.

## Context

We are working on Panel's `AnyWidget` pane ([PR #8428](https://github.com/holoviz/panel/pull/8428)) which renders anywidget components inside a shadow DOM. jupyter-scatter is a popular anywidget for high-performance scatter plots using regl-scatterplot.

## Minimal Reproducible Example

```python
from jscatter.jscatter import Scatter
import numpy as np
import pandas as pd
import panel as pn

pn.extension()

df = pd.DataFrame({
    "x": np.random.randn(1000),
    "y": np.random.randn(1000),
})

scatter = Scatter(data=df, x="x", y="y", height=500)
pn.pane.AnyWidget(scatter.widget, width=600, height=500).servable()
```

## Root Cause Analysis

In `createScatterplot`, the `init()` function calls `updateViewAspectRatio()` and `initCamera()` BEFORE `set({height, width})`:

```javascript
const init = () => {
    updateViewAspectRatio();  // Uses currentWidth, currentHeight
    initCamera();              // Calls getScatterGlPos() which crashes
    // ... later ...
    set({ width, height });    // Would clamp to safe values, but too late
};
```

The `regl-scatterplot` library guards against zero dimensions with `Math.max(1, ...)` in `setCurrentHeight()`, but this guard is only applied during `set()`, not during the initial `updateViewAspectRatio()` call.

When the canvas is inside a shadow DOM and hasn't been fully laid out, the height/width values are zero at initialization time. The projection matrix becomes singular:

```javascript
viewAspectRatio = currentWidth / currentHeight;  // 0/0 = NaN
projectionLocal = fromScaling([], [1 / viewAspectRatio, 1, 1]);  // NaN
// ... invert() returns null for a matrix with NaN values
```

**Why explicit pane dimensions don't fix it:** Setting `width=600, height=500` on `pn.pane.AnyWidget()` sets the *outer* Bokeh view element size. The *inner* container element (`view.container`) inside the shadow DOM inherits its size from CSS flow, and at the time the ESM `render()` function runs, the browser has not yet completed CSS layout. The inner container still has 0×0 dimensions.

## Suggested Fix (regl-scatterplot upstream)

In `createScatterplot`, clamp `currentWidth` and `currentHeight` to a minimum of 1 before the initial `updateViewAspectRatio()`:

```javascript
const init = () => {
    currentWidth = Math.max(1, currentWidth);
    currentHeight = Math.max(1, currentHeight);
    updateViewAspectRatio();
    initCamera();
    // ...
};
```

Alternatively, defer WebGL initialization until the container has non-zero dimensions, e.g. using a `ResizeObserver`:

```javascript
const init = () => {
    if (canvas.clientWidth === 0 || canvas.clientHeight === 0) {
        const observer = new ResizeObserver((entries) => {
            if (canvas.clientWidth > 0 && canvas.clientHeight > 0) {
                observer.disconnect();
                actualInit();
            }
        });
        observer.observe(canvas);
        return;
    }
    actualInit();
};
```

## Workaround Attempts

| Approach | Result |
|----------|--------|
| Explicit `width=600, height=500` on pane | Silences crash but canvas still doesn't initialize |
| `sizing_mode="stretch_width"` | No effect |
| Adding CSS stylesheets to component | No effect on inner container at render time |
| Delaying render (20s wait) | No effect -- canvas never appears |

## Environment

- jupyter-scatter: latest
- regl-scatterplot: embedded in jupyter-scatter bundle (~951 KB)
- Panel: development branch (enhancement/any-widget)
- Browser: Chrome, Firefox (reproducible in both + headless)

## Classification

| Category | Details |
|----------|---------|
| Panel AnyWidget compatible | No -- WebGL init requires non-zero container at render time |
| Root cause | regl-scatterplot doesn't guard against 0×0 container at init |
| Fix location | Upstream (regl-scatterplot or jupyter-scatter) |
| Upstream repo | https://github.com/flekschas/jupyter-scatter |
| regl-scatterplot | https://github.com/flekschas/regl-scatterplot |
