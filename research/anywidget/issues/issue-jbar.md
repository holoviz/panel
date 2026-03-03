# jbar: Shadow DOM getElementById — Does Not Render

## Status: DOES NOT RENDER

## Error
```
D3 selects an empty node — no SVG bar chart is created
```

## Root Cause

jbar's ESM uses `d3.select("#my_dataviz")` (a document-level CSS ID selector query) to locate its container div. Panel renders AnyWidget components inside a shadow DOM, and `document.querySelector("#my_dataviz")` cannot penetrate shadow DOM boundaries.

As a result, D3 returns an empty selection and the SVG bar chart is never created. The widget element is present in the DOM, but the bars are invisible.

Panel's `anywidget_component.ts` patches `document.getElementById` to search open shadow roots as a fallback, but jbar's D3 code may use `d3.select()` which calls `document.querySelector()` internally, bypassing the patched `getElementById`.

## Reproducibility
- **Panel AnyWidget pane**: Always fails — widget element is present but bars are invisible
- **JupyterLab**: Works (standard DOM, no shadow DOM)

## Possible Solutions
1. **Upstream**: jbar could use the `el` reference provided by anywidget's `render()` function instead of querying by global CSS ID
2. **Panel**: Extend shadow DOM query patching to also intercept `document.querySelector` / `document.querySelectorAll` — but this would be a broad monkey-patch with potential side effects
3. **Workaround**: None currently — this is a fundamental incompatibility between D3 widgets that use document-level ID selectors and shadow DOM encapsulation

## Trait Name Collisions
None — `data`, `x`, `exclude`, `selection` do not collide with Panel/Bokeh reserved names.
