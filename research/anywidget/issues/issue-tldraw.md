# tldraw v3 ESM incompatibility with es-module-shims

## Summary

tldraw v3's ESM bundle uses Sucrase-generated `_asyncOptionalChain` helper functions that cause a `SyntaxError` in `es-module-shims` when loaded dynamically via `importShim()`. This prevents tldraw from rendering in environments that use `es-module-shims` for ESM loading (including Panel's AnyWidget pane).

## Context

We are working on Panel's `AnyWidget` pane ([PR #8428](https://github.com/holoviz/panel/pull/8428)) which renders anywidget-based components inside Panel applications. The pane loads widget ESM code using `es-module-shims` (`importShim()`). Most anywidget ESM bundles work correctly, but tldraw v3's bundle fails due to the helper function issue described below.

## Minimal Reproducible Example

```python
import tldraw
import panel as pn

pn.extension()

widget = tldraw.TldrawWidget()
pn.pane.AnyWidget(widget).servable()
```

Running with `panel serve example.py` and opening in a browser produces:

```
SyntaxError: Unexpected token '_asyncOptionalChain'
```

in the browser console when `es-module-shims` tries to parse the ESM bundle.

## Root Cause

tldraw v3's ESM bundle is compiled with Sucrase, which transforms optional chaining (`?.`) into helper function calls:

```javascript
// Original code
const result = await obj?.method?.()

// Sucrase output
const result = await _asyncOptionalChain([obj, 'optionalAccess', _ => _.method, 'optionalCall', _ => _()])
```

The `_asyncOptionalChain` and `_optionalChain` helper functions are declared at the top of the bundle. When `es-module-shims` parses the ESM, it encounters these function declarations in a context where they're not expected, causing a `SyntaxError`.

## Attempted Workarounds

1. **Sucrase fallback detection**: Panel detects when a bundle contains `_optionalChain` or `_asyncOptionalChain` helpers and falls back to using the raw ESM without Sucrase transformation. This avoids double-transformation but doesn't fix the `es-module-shims` parsing issue.

2. **Native `import()`**: Using native `import()` instead of `importShim()` might work but loses import map support.

## Environment

- tldraw: v3.x
- es-module-shims: 1.x (used by Panel/Bokeh for ESM loading)
- Browser: Chrome, Firefox (reproducible in both)

## Expected Behavior

The tldraw ESM bundle should be loadable by standard ESM loading mechanisms including `es-module-shims`.

## Possible Solutions

1. Ship a pre-bundled ESM that doesn't use Sucrase helper functions (use native optional chaining instead, which is supported in all modern browsers)
2. Use a different transpiler that preserves optional chaining syntax
3. Provide an alternative bundle format that avoids the helper function pattern
