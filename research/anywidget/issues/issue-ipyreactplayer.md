# ipyreactplayer — Incompatibility with Panel's AnyWidget Pane

## Summary

ipyreactplayer's ESM exports a **React component function** (`export default App`) instead of an anywidget `render({model, el})` function. Panel's Sucrase transpiler successfully compiles the JSX, but the resulting component expects React props (`{url, width, height, ...}`) instead of the anywidget render signature (`{model, el, experimental}`), causing a runtime error.

## Environment
- Panel: latest (PR #8428)
- ipyreactplayer: 0.0.1
- Python: 3.10+

## Root Cause

ipyreactplayer wraps [react-player](https://github.com/cookpete/react-player) as an anywidget. Its ESM has two issues:

### 1. Exports a React component, not an anywidget `render()` function

```javascript
// What ipyreactplayer exports:
const App = ({ url, width, height, playing, ... }) => {
  return <ReactPlayer url={url} ... />
};
export default App;  // ← React component

// What anywidget expects:
export function render({ model, el }) { ... }
```

Panel calls `view.render_fn({ model, el, ... })` on the default export. Since `App` destructures `{ url, ... }` from its argument, and `url` is not present in `{ model, el, ... }`, the browser throws:

```
TypeError: Cannot destructure property 'url' of 'undefined' as it is undefined.
```

### 2. Bare `import React from "react"` specifier

The ESM uses `import React from "react"` — a bare specifier that requires React in an import map or bundled. Panel does not provide React by default in the AnyWidget pane.

**Note:** Panel's Sucrase transpiler now successfully compiles the JSX to `React.createElement()` calls, so the original `SyntaxError: Unexpected token '<'` no longer occurs. The failure is now at runtime due to the export format mismatch.

## Minimal Reproducible Example

```python
from ipyreactplayer import VideoPlayer

import panel as pn

pn.extension()

widget = VideoPlayer(
    url="https://www.youtube.com/watch?v=aqz-KE-bpKQ",
    controls=True,
    width="640px",
    height="360px",
)

# This will fail — default export is a React component, not render()
pn.pane.AnyWidget(widget, height=400, width=660).servable()
```

## Expected vs Actual
- **Expected:** Widget renders in Panel's AnyWidget pane
- **Actual:** Console shows `TypeError: Cannot destructure property 'url' of 'undefined' as it is undefined`. Panel calls the default export with `{model, el, ...}` but the React component `App` expects `{url, width, height, ...}` as props. The widget does not render. Python-side trait creation succeeds; the failure is at browser-side runtime.

## Context

This issue was discovered while testing compatibility of anywidget-based widgets with Panel's `pn.pane.AnyWidget` pane (PR [#8428](https://github.com/holoviz/panel/pull/8428)). The AnyWidget pane provides a Param-integrated wrapper for leaf anywidgets.

## Workaround

Use `pn.pane.IPyWidget` with `pn.extension("ipywidgets")` instead:

```python
from ipyreactplayer import VideoPlayer

import panel as pn

pn.extension("ipywidgets")

widget = VideoPlayer(
    url="https://www.youtube.com/watch?v=aqz-KE-bpKQ",
    controls=True,
    width="640px",
    height="360px",
)

pn.pane.IPyWidget(widget).servable()
```

## Suggested Fix

**Upstream (ipyreactplayer):** Refactor the ESM to use the standard anywidget `render({model, el})` signature instead of exporting a bare React component. Use `@anywidget/react` or bundle React + ReactDOM and call `ReactDOM.render()` / `createRoot().render()` inside the `render()` function:

```javascript
// Option 1: Use @anywidget/react (recommended)
import * as React from "@anywidget/react";
export default function App({ model }) {
  const [url] = model.useModelState("url");
  // ... render with react-player
}

// Option 2: Bundle React and use standard render()
import React from "react";
import { createRoot } from "react-dom/client";
export function render({ model, el }) {
  const root = createRoot(el);
  root.render(<App url={model.get("url")} ... />);
  return () => root.unmount();
}
```

The JSX transpilation itself now works (Panel's Sucrase handles it). The remaining issue is purely the export format — `export default App` vs `export function render`.
