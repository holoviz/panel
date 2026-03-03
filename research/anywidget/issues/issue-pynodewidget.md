# pynodewidget: ReactDOM.render deprecation error with bundled React 18

## Summary

pynodewidget's ESM bundle includes React 18.3.1 but somewhere in its code (or ReactFlow dependency) calls the deprecated `ReactDOM.render()` API, causing a React error #185:

```
ReactDOM.render is no longer supported in React 18. Use createRoot instead.
```

This is **not** a Panel issue. Panel's AnyWidget pane does not interfere with anywidget ESM bundles' internal React usage.

## Context

We are testing Panel's `AnyWidget` pane ([PR #8428](https://github.com/holoviz/panel/pull/8428)) with various anywidget-based widgets. pynodewidget wraps ReactFlow as an anywidget for building interactive node graph editors.

## Minimal Reproducible Example

```python
from pynodewidget import NodeFlowWidget
import panel as pn

pn.extension()

widget = NodeFlowWidget(height="600px")
pn.pane.AnyWidget(widget).servable()
```

Running `panel serve example.py` produces the React error in the browser console. The ReactFlow canvas may render partially but React nodes fail to mount.

## Root Cause Analysis

pynodewidget's bundled ESM (`pynodewidget/static/index.js`) contains:

1. **A full bundled copy of React 18.3.1** (minified, inlined)
2. **Code that calls the deprecated `ReactDOM.render()` API** somewhere in the bundle or its ReactFlow dependency

React 18 deprecated `ReactDOM.render()` in favor of `createRoot()`. When the bundled React 18 encounters a `ReactDOM.render()` call, it throws error #185.

Key points:
- This is purely within pynodewidget's own bundled React — Panel does not provide or override React for anywidgets
- Panel's `AnyWidgetComponent` does NOT set up any React importmap for anywidgets
- The error would also occur in any environment loading this ESM bundle

## Environment

- pynodewidget: latest (pip install)
- Panel: development branch (enhancement/any-widget)
- React (bundled in pynodewidget): 18.3.1
- Browser: Chrome, Firefox (reproducible in both)

## Trait Collision

`height` (Unicode, e.g. "600px") collides with Panel's `height` param (int, pixels). Renamed to `w_height` on the Panel component automatically.

## Suggested Fix

Update the ESM bundle to use the React 18 `createRoot()` API instead of the deprecated `ReactDOM.render()`:

```javascript
// Before (deprecated)
ReactDOM.render(element, container)

// After (React 18)
const root = createRoot(container)
root.render(element)
```

## Upstream

- **Repo**: https://github.com/HenningScheufler/pynodewidget
- **Docs**: https://henningscheufler.github.io/pynodewidget/
