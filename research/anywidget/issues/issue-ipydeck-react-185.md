# ipydeck: React Error #185 — Does Not Render

## Status: DOES NOT RENDER

## Error
```
Uncaught Error: Minified React error #185;
visit https://react.dev/errors/185 for the full message
```

## Root Cause

ipydeck's ESM bundles React 18 and uses `ReactDOM.render()` or `ReactDOM.createRoot()` to mount
its deck.gl component. When Panel renders the anywidget inside a shadow DOM container, the React
root container argument is either missing or invalid from React's perspective.

React error #185 typically means: "It looks like you called `ReactDOM.render()` without a valid
container element" — the shadow DOM host may not satisfy React's container validation.

## Reproducibility
- **Panel AnyWidget pane**: Always fails — blank map area, uncaught React error
- **JupyterLab**: Works (standard DOM, Jupyter widget manager provides real DOM nodes)

## Possible Solutions
1. **Upstream**: ipydeck could check if `el` is a shadow root and adapt its React mounting
2. **Panel**: Provide a real DOM node (not shadow DOM) for React-based anywidgets
3. **Workaround**: None currently — ipydeck requires React DOM mounting that Panel's
   shadow DOM container doesn't support

## Trait Name Collisions
- `height` → `w_height`
- `width` → `w_width`
