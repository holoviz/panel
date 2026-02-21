# Feature Request: Reduce ESM bundle size or support external module loading

## Summary

The `anymap-ts` package bundles the entire MapLibre GL JS library into its ESM module (`_esm` traitlet), resulting in a ~17 MB JavaScript payload and ~231 KB of CSS. This makes it impractical for frameworks that inline ESM content, such as [Panel](https://panel.holoviz.org)'s `AnyWidget` pane.

## Problem

When Panel's `AnyWidget` pane renders an anywidget, it extracts the `_esm` string and transmits it via WebSocket to the browser for execution. For most anywidgets (which have small, self-contained ESM modules of a few KB), this works well. However, `anymap-ts`'s 17 MB ESM payload causes the WebSocket connection to close before transmission completes:

```
Error: Lost websocket connection, 1005 ()
```

This prevents `anymap-ts` from rendering in Panels future AnyWidget pane entirely.

## Suggested Solutions

### Option 1: Use `importShim` / CDN import (Preferred)

Instead of bundling MapLibre GL JS into the ESM, load it dynamically from a CDN:

```javascript
async function render({ model, el }) {
    // Load MapLibre GL JS from CDN (~200KB gzipped vs 17MB inline)
    const maplibregl = await import("https://esm.sh/maplibre-gl@4");
    // ... rest of render code
}
export default { render };
```

This keeps the ESM module small (~2-5 KB) while still loading the full MapLibre library at runtime. This pattern is used by many anywidgets.

### Option 2: Use `_esm` as a file path

If `_esm` is a `pathlib.Path` instead of an inline string, frameworks can handle large files differently (e.g., serving them as static assets rather than inlining). The anywidget spec supports both strings and paths.

### Option 3: Tree-shaking / code splitting

If the full MapLibre bundle is necessary, investigate whether the build process can be optimized to reduce the bundle size (tree-shaking unused features, code splitting, etc.).

## Impact

This change would make `anymap-ts` compatible with:
- **Panel** (`AnyWidget` pane) - currently fails due to WebSocket payload size
- **Marimo** and other frameworks that inline ESM
- Any environment with WebSocket message size limits like JupyterHub

## Environment

- anymap-ts version: latest
- Panel version: 1.x (development branch)
- Python: 3.12
- Browser: Chromium
