# ESM & Import Map Handling

This document details how anywidget ESM code will be loaded by Panel's `AnyWidgetComponent` pipeline, covering inline vs file-based ESM, import maps, React injection, and CDN imports.

## 1. ESM Source Types: String vs Path

### Anywidget Convention

Anywidgets define their frontend code via the `_esm` class attribute, which can be:

1. **Inline string** -- JavaScript/TypeScript source code embedded directly:
   ```python
   class MyWidget(anywidget.AnyWidget):
       _esm = """
       export default { render({ model, el }) { ... } }
       """
   ```

2. **`pathlib.Path`** -- Reference to an external `.js` file:
   ```python
   class MyWidget(anywidget.AnyWidget):
       _esm = pathlib.Path(__file__).parent / "widget.js"
   ```

### Panel's `_render_esm()` Handling

Panel's `ReactiveESM._render_esm()` method at `panel/custom.py:375-393` handles both cases:

```python
@classmethod
def _render_esm(cls, compiled=True, server=False):
    esm_path = cls._esm_path(compiled=compiled is True)
    if esm_path:
        if esm_path == cls._bundle_path and cls.__module__ in sys.modules and server:
            # Generate relative path for server-served bundles
            esm = ('' if state.rel_path else './') + cls._component_resource_path(...)
        else:
            esm = esm_path.read_text(encoding='utf-8')
    else:
        esm = cls._esm
    # ...
    esm = textwrap.dedent(esm)
    return esm
```

The `_esm_path()` method at `panel/custom.py:342-362` resolves path-based ESM:
- If `_esm` is an `os.PathLike`, return it directly
- If `_esm` is a string ending in `.js`/`.jsx`/`.ts`/`.tsx`, resolve relative to the component's module path
- Otherwise return `None` (inline string mode)

### AnyWidget's Actual `_esm` Handling (from source analysis)

**Critical detail from source** (`/tmp/anywidget-src/anywidget/widget.py:40-52` and `_util.py:214-284`):

AnyWidget's `__init_subclass__` (line 65-74) automatically converts `_esm` strings that look like file paths into `FileContents` objects:

```python
def __init_subclass__(cls, **kwargs):
    for key in ('_esm', '_css') & cls.__dict__.keys():
        file_contents = try_file_contents(getattr(cls, key))
        if file_contents:
            setattr(cls, key, file_contents)
```

The `try_file_contents()` function (`_util.py:262-284`) checks if the value is:
- Already a path in `_VIRTUAL_FILES` (HMR virtual files)
- Coercible to a `pathlib.Path` via `try_file_path()` (single-line string with file extension, not a URL, not multiline)
- If it's a valid file path, wraps it in `FileContents(path, start_thread=...)` which reads the file and optionally watches for changes

Then in `__init__` (line 40-61), the `_esm`/`_css` values are converted to sync-tagged Unicode traits:
```python
anywidget_traits[key] = t.Unicode(str(value)).tag(sync=True)
```

So by the time the widget is instantiated, `_esm` is always a **string** (the inline JS or the file contents read into a string). The `str(value)` call on a `FileContents` object reads the file.

### Compatibility Assessment

**Fully compatible.** There are two integration approaches:

1. **From widget class (before instantiation)**: Read `_esm` from the class. If it's a `FileContents`/`VirtualFileContents`, call `str()` on it to get the content. If it's a raw string, check if `try_file_path()` would resolve it to a file and read that file, otherwise use it as inline ESM.

2. **From widget instance (after instantiation)**: Access the `_esm` trait value directly -- it's already a string (anywidget's `__init__` converts it).

For the AnyWidget pane, approach 1 is better because we may want to set up file watching for HMR support. Panel's `_render_esm()` handles both string and `os.PathLike` already.

**Key consideration**: When extracting `_esm` from an anywidget class, the value may be:
- A raw string (inline JS)
- A `FileContents` object (file watcher, `str()` returns contents)
- A `VirtualFileContents` object (in-memory, `str()` returns contents)
- A `pathlib.Path` (not yet wrapped by `__init_subclass__` if accessed before class finalization)

## 2. Bare Import Specifiers

### The Problem

Some anywidgets use bundled ESM with all dependencies included (self-contained). Others use **bare import specifiers** that rely on an import map:

```javascript
// Bare specifier -- needs import map resolution
import maplibregl from 'maplibre-gl'

// URL specifier -- resolved directly
import maplibregl from 'https://esm.sh/maplibre-gl@4.0.0'
```

In Jupyter, bare specifiers work because JupyterLab/Notebook provides an import map via the `@jupyter-widgets` infrastructure. Outside Jupyter, these bare specifiers will fail unless an import map is provided.

### Panel's Import Map System

Panel uses `es-module-shims` (loaded at `panel/models/esm.py:55-57`) to polyfill import maps. The import map is declared via `_declare_importmap()` in `panel/models/reactive_esm.ts:774-784`:

```typescript
protected _declare_importmap(): void {
    if (this.importmap) {
        const importMap = {...this.importmap}
        importShim.addImportMap(importMap)
    }
}
```

Each `ReactiveESM` component can provide its own `_importmap` class variable. For `ReactComponent`, this is enhanced at `panel/custom.py:854-887` to include React and optionally MUI dependencies.

### Handling Strategy for AnyWidgets

For anywidgets with bare import specifiers, there are several approaches:

1. **Widget provides its own import map**: Some anywidgets define an `_importmap` attribute. If present, pass it through directly.

2. **Fallback to esm.sh CDN**: For widgets that rely on Jupyter's import map, we could auto-generate an import map using `esm.sh`. This requires knowing the package name and version.

3. **Bundled ESM**: Many production anywidgets ship a bundled `.js` file with all dependencies inlined. These work without any import map. This is the most common case for published packages.

4. **User-provided import map**: Allow users to pass an `importmap` parameter to the AnyWidget pane, enabling manual resolution of bare specifiers.

**Recommendation**: Support approaches 1, 3, and 4 initially. Auto-generating import maps (approach 2) is complex and can be added later. Most published anywidgets either bundle their deps or use CDN URLs.

## 3. React Import Injection

### How `ReactComponent._process_importmap()` Works

`AnyWidgetComponent` inherits from `ReactComponent`, which injects React into the import map at `panel/custom.py:854-887`:

```python
@classmethod
def _process_importmap(cls):
    imports = cls._importmap.get('imports', {})
    v_react = cls._react_version
    imports_with_deps = {
        "react": f"https://esm.sh/react@{v_react}...",
        "react/": f"https://esm.sh/react@{v_react}.../",
        "react-dom": f"https://esm.sh/react-dom@{v_react}...",
        "react-dom/": f"https://esm.sh/react-dom@{v_react}.../"
    }
    # ... merge with user imports
    return {'imports': imports_with_deps, 'scopes': ...}
```

### Impact on Non-React AnyWidgets

The React imports (`react`, `react/`, `react-dom`, `react-dom/`) are added to the import map but are **only loaded when actually imported** by the ESM code. This is because:

1. `es-module-shims` uses dynamic imports -- entries in the import map are only fetched when a matching `import` statement is encountered
2. The import map merely provides URL resolution; it does not trigger downloads

**Assessment: No issue for non-React anywidgets.** The React entries in the import map will be silently ignored if the widget's ESM does not `import` from `react` or `react-dom`.

### `_react_version` Difference

Note that `AnyWidgetComponent` sets `_react_version = "19"` (at `panel/custom.py:939`) while `ReactComponent` uses `_react_version = '18.3.1'`. This is intentional as newer anywidgets may target React 19. This only matters for anywidgets that actually use React.

## 4. Test Scenario: Simple Inline ESM

### Setup

```python
class CounterWidget(pn.custom.AnyWidgetComponent):
    value = param.Integer(default=0)

    _esm = """
    function render({ model, el }) {
        let count = () => model.get("value");
        let btn = document.createElement("button");
        btn.innerHTML = `count is ${count()}`;
        btn.addEventListener("click", () => {
            model.set("value", count() + 1);
            model.save_changes();
        });
        model.on("change:value", () => {
            btn.innerHTML = `count is ${count()}`;
        });
        el.appendChild(btn);
    }
    export default { render };
    """
```

### Pipeline Trace

1. **ESM extraction**: `_render_esm()` returns the inline string (no path resolution needed)
2. **Compilation**: In `reactive_esm.ts:841-867`, the ESM is compiled via Sucrase with transforms `["typescript", "jsx"]` (set by `AnyWidgetComponent` TS class at line 159). For plain JS without JSX/TS, this is effectively a no-op pass-through.
3. **Import map**: `_process_importmap()` adds React entries (unused). `_declare_importmap()` registers them with `es-module-shims`.
4. **Module loading**: The compiled code is turned into a Blob URL and loaded via `importShim(url)` at `reactive_esm.ts:894`.
5. **Initialization**: If `mod.default.initialize` exists, it runs. For simple widgets, this is typically absent.
6. **Render module**: `init_module()` creates a render wrapper at `reactive_esm.ts:798-812`.
7. **Render execution**: The `_render_code()` override in `anywidget_component.ts:166-179` calls `render_fn` with `{view, model: view.adapter, data, el}` where `model` is an `AnyWidgetAdapter` instance.
8. **AnyWidgetAdapter shim**: The adapter provides `get()`, `set()`, `save_changes()`, `on()`, `off()` methods that translate anywidget API calls to Bokeh model operations.

**Assessment: This scenario works correctly** with the existing `AnyWidgetComponent` pipeline. The key shim is the `AnyWidgetAdapter` class which provides the `model.get()` / `model.set()` / `model.save_changes()` / `model.on("change:...")` API that anywidgets expect.

## 5. Test Scenario: CDN Imports

### Setup

```python
class MapWidget(pn.custom.AnyWidgetComponent):
    center = param.List(default=[0, 0])
    zoom = param.Number(default=2)

    _esm = """
    import maplibregl from 'https://esm.sh/maplibre-gl@4.0.0'

    function render({ model, el }) {
        const map = new maplibregl.Map({
            container: el,
            center: model.get("center"),
            zoom: model.get("zoom"),
        });
    }
    export default { render };
    """
```

### How `es-module-shims` Handles This

`es-module-shims` (loaded from `panel/models/esm.py:55-57`) intercepts all module loads. When it encounters `import ... from 'https://esm.sh/...'`, it:

1. Recognizes this as an absolute URL (not a bare specifier)
2. Fetches the module directly from the CDN URL
3. Resolves any further imports within that module using its own resolution algorithm

**Assessment: CDN imports work correctly.** `es-module-shims` handles absolute URL imports natively. No import map entry is needed for these.

### Potential Issues

1. **CORS**: CDN URLs must serve modules with appropriate CORS headers. `esm.sh` and other major CDN providers do this by default.
2. **Nested bare imports**: If the CDN module itself uses bare specifiers internally, `esm.sh` rewrites those to absolute URLs. Other CDNs may not.
3. **Offline environments**: CDN imports will fail without network access. Bundled widgets are preferable for offline use.

## 6. Module Loading Flow (Complete)

```
Python                          TypeScript
------                          ----------
_esm (str or Path)
    |
    v
_render_esm()
    |
    v
_get_properties(doc)
  -> esm: str
  -> importmap: dict
    |
    v
    [Bokeh sync]  ============> ReactiveESM model
                                    |
                                    v
                                recompile()
                                    |
                                    v
                                compile() [Sucrase: TS+JSX -> JS]
                                    |
                                    v
                                _declare_importmap() [es-module-shims]
                                    |
                                    v
                                Blob URL or server URL
                                    |
                                    v
                                importShim(url) -> module
                                    |
                                    v
                                mod.default?.initialize?.(...)
                                    |
                                    v
                                init_module() -> render_module
                                    |
                                    v
                                render_module.default.render(id)
                                    |
                                    v
                                AnyWidgetComponentView.render_fn({
                                    view, model: adapter, data, el
                                })
```

## 7. Key Differences: AnyWidget API vs Panel ESM API

| Feature | AnyWidget API | Panel ReactiveESM API |
|---|---|---|
| Model access | `model.get(name)` / `model.set(name, val)` | `model.name` / `model.name = val` |
| Save changes | `model.save_changes()` required | Automatic on property set |
| Change events | `model.on("change:name", cb)` | `model.on("name", cb)` |
| Render signature | `render({ model, el })` | `render({ model, view, data, el })` |
| Return value | Cleanup function (optional) | DOM element or void |
| Export format | `export default { render }` | `export function render(...)` |

The `AnyWidgetAdapter` class in `anywidget_component.ts:6-98` bridges these API differences, translating anywidget-style calls to Bokeh model operations.

## 8. Bundled ESM (`_bundle_path`)

Panel supports pre-bundled ESM via `_bundle_path` (defined at `panel/custom.py:277-328`). When a `.bundle.js` file exists alongside the component, Panel:

1. Serves it as a static file (in server mode)
2. Reads it inline (in notebook mode)
3. Skips Sucrase compilation (the bundle is already JS)

For anywidgets that ship bundled JS, the `_bundle` class variable can be set to point to the bundled file. This bypasses Sucrase compilation and import map resolution, since the bundle is self-contained.

## 9. `_esm_shared` for Shared Modules

Panel's `_esm_shared` class variable (at `panel/custom.py:246`) allows declaring shared ESM modules that are loaded once and reused across component instances. This could be useful for anywidgets that share large dependency bundles.

## 10. Summary and Recommendations

| Scenario | Compatibility | Notes |
|---|---|---|
| Inline ESM string | Full | Works via existing `_render_esm()` pipeline |
| `pathlib.Path` ESM | Full | `_esm_path()` resolves and reads the file |
| Bundled ESM (all deps included) | Full | Most common for published anywidgets |
| CDN URL imports (`https://esm.sh/...`) | Full | `es-module-shims` handles natively |
| Bare import specifiers | Partial | Needs import map; user must provide or widget must bundle |
| React-based anywidgets | Full | React already in import map via `ReactComponent` |
| Non-React anywidgets | Full | React imports in map but not loaded unless used |
| TypeScript ESM | Full | Sucrase compiles TS+JSX on the fly |
| CSS in `_css` attribute | Needs work | Current `AnyWidgetComponent` does not handle `_css`; needs extraction |

### Open Issues

1. **`_css` attribute**: Anywidgets can define `_css` for styling (as a string or file path, handled identically to `_esm`). Panel's `AnyWidgetComponent` does not currently extract and apply this. From the anywidget source (`widget.py:41-44`), `_css` is converted to a sync-tagged Unicode trait containing CSS text. The AnyWidget pane should:
   - Extract `_css` from the widget class (similar to `_esm`)
   - Inject it as a `<style>` element in the component's shadow DOM or as an `ImportedStyleSheet`
   - Panel already has `css_bundle` support in `ReactiveESM` -- this could potentially be reused

2. **HMR (Hot Module Replacement)**: Anywidget supports HMR via `FileContents` objects that watch files using `watchfiles` (same library Panel uses). The `FileContents.changed` signal (psygnal-based) triggers when the file changes. Panel's `config.autoreload` provides similar functionality. When wrapping an anywidget, the pane could:
   - If `_esm` is a `FileContents`, connect to its `changed` signal
   - Update the component's ESM when changes are detected
   - This integrates naturally with Panel's existing `_watch_esm()` mechanism

3. **Binary buffer protocol**: In ipywidgets, binary buffers are separated from state via `remove_buffers()` and sent as separate websocket frames. Panel's Bokeh protocol also sends `bp.Bytes` as binary frames. The encoding/decoding is handled transparently -- Panel does NOT need to implement `remove_buffers`.

4. **`send()` / custom messages**: AnyWidget supports `widget.send(msg)` for custom messages from Python to JS, and `model.on("msg:custom", cb)` for receiving them. Panel's `AnyWidgetComponent` already supports this via:
   - Python: `self._send_msg(msg)` (inherited from `ReactiveESM`)
   - TS: `model.on("msg:custom", cb)` handled by `AnyWidgetAdapter.on()` at `anywidget_component.ts:82-83`
   - The AnyWidget pane should expose a `send(msg)` method that delegates to `_send_msg()`

## 11. AnyWidget Render Function Signature

### Standard AnyWidget Render Signature

From the anywidget source and documentation, the render function receives:

```javascript
// ESM module structure:
export default {
    render({ model, el }) {
        // model: AnyWidgetAdapter (get/set/save_changes/on/off)
        // el: HTMLElement container
        // Return: optional cleanup function
    },
    initialize({ model }) {
        // Optional initialization, called once
        // model: adapter with get/set/save_changes/on/off
        // Return: optional cleanup function
    }
}
```

### Panel's AnyWidgetComponentView Render Call

From `anywidget_component.ts:165-179`, the render code passes:

```typescript
view.render_fn({
    view,                    // AnyWidgetComponentView
    model: view.adapter,     // AnyWidgetAdapter (provides get/set/save_changes/on/off)
    data: view.model.data,   // Bokeh DataModel (direct property access)
    el: view.container       // HTMLDivElement
})
```

The `AnyWidgetAdapter` (`anywidget_component.ts:100-124`) provides the standard anywidget model API:
- `get(name)` -- reads from Bokeh data model attributes, converts ArrayBuffer to DataView
- `set(name, value)` -- stages changes
- `save_changes()` -- applies staged changes to the Bokeh model
- `on(event, cb)` -- watches for property changes ("change:prop") and custom messages ("msg:custom")
- `off(event, cb)` -- unregisters watchers
- `get_child(name)` -- gets child element(s) for Panel's Children support

This matches the standard anywidget API, so existing anywidget ESM code should work without modification.
