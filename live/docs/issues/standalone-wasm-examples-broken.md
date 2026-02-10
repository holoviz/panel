# Standalone WASM examples in docs are broken

The examples at https://panel.holoviz.org/how_to/wasm/standalone.html have several issues that prevent them from working.

## 1. PyScript examples fail due to missing explicit dependencies

The PyScript example uses `packages` config to install wheels:

```html
<script type="py" config='{"packages": ["...bokeh-3.8.2-py3-none-any.whl", "...panel-1.8.7-py3-none-any.whl"]}'>
```

Unlike micropip (used in the Pyodide example), PyScript's `packages` config does not resolve transitive dependencies from wheels. This causes `ModuleNotFoundError: No module named 'param'` at runtime.

**Fix:** Add explicit dependencies:

```html
<script type="py" config='{"packages": ["...bokeh-3.8.2-py3-none-any.whl", "...panel-1.8.7-py3-none-any.whl", "param", "pyyaml", "numpy", "xyzservices"]}'>
```

## 2. PyScript examples missing `interpreter` config

Without an explicit `interpreter` URL, PyScript uses whatever Pyodide version it bundles. This may not be compatible with Panel (see related issue: Panel does not work with Pyodide v0.29.x). The Pyodide example explicitly pins v0.28.2, but the PyScript examples do not.

**Fix:** Add the interpreter URL:

```html
<script type="py" config='{"interpreter": "https://cdn.jsdelivr.net/pyodide/v0.28.2/full/pyodide.mjs", "packages": [...]}'>
```

## 3. py-editor example has wrong wheel URLs

The raw source template for the py-editor example is:

```html
<script type="py-editor" config='{"packages": [
  "https://cdn.holoviz.org/panel/wheels/bokeh-{{BOKEH_VERSION}}-py3-none-any.whl",
  "https://cdn.holoviz.org/panel/{{PANEL_VERSION}}/dist/wheels/{{PANEL_VERSION}}-py3-none-any.whl"
]}'>
```

Two bugs:
- **Bokeh wheel URL** uses `/panel/wheels/` instead of `/panel/{{PANEL_VERSION}}/dist/wheels/` (inconsistent with the other examples and likely 404s)
- **Panel wheel filename** is `{{PANEL_VERSION}}-py3-none-any.whl` instead of `panel-{{PANEL_VERSION}}-py3-none-any.whl` (missing `panel-` prefix)

**Fix:**

```
"https://cdn.holoviz.org/panel/{{PANEL_VERSION}}/dist/wheels/bokeh-{{BOKEH_VERSION}}-py3-none-any.whl",
"https://cdn.holoviz.org/panel/{{PANEL_VERSION}}/dist/wheels/panel-{{PANEL_VERSION}}-py3-none-any.whl"
```

## 4. py-editor example cannot work (fundamental limitation)

PyScript's `<script type="py-editor">` runs code in a **Web Worker**, which is isolated from the main thread DOM. The example uses `.servable(target='simple_app')`, but Panel's rendering pipeline requires main-thread DOM access via Bokeh's `embed_items()`.

This means the py-editor example **will never render interactive Panel widgets** — it will fail silently or error with something like `Unable to use window or document`.

This should either be documented as a known limitation or the py-editor example should be removed/replaced with a note explaining the constraint.

## 5. Admonition box has incorrect micropip syntax

The "warn" admonition recommends:

```javascript
await micropip.install(bk_whl, pn_whl);
```

`micropip.install()` takes a list, not positional args:

```javascript
await micropip.install([bk_whl, pn_whl]);
```

## Working examples

For reference, these versions work together:

| Component | Version |
|-----------|---------|
| Pyodide   | v0.28.2 |
| Bokeh JS  | 3.8.2   |
| Panel JS  | 1.8.7   |
| PyScript  | 2025.8.1 |

Pyodide example (works as-is from the docs):
```javascript
await micropip.install([
  "https://cdn.holoviz.org/panel/1.8.7/dist/wheels/bokeh-3.8.2-py3-none-any.whl",
  "https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl"
]);
```

PyScript example (needs interpreter + explicit deps):
```html
<script type="py" config='{
  "interpreter": "https://cdn.jsdelivr.net/pyodide/v0.28.2/full/pyodide.mjs",
  "packages": [
    "https://cdn.holoviz.org/panel/1.8.7/dist/wheels/bokeh-3.8.2-py3-none-any.whl",
    "https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl",
    "param", "pyyaml", "numpy", "xyzservices"
  ]
}'>
```

## Environment

- Panel 1.8.7
- Tested in Chrome on Linux
