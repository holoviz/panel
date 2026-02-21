# AnyWidget Pane: Research Summary

This document summarizes findings from 8 research tracks investigating how to implement a native `AnyWidget` pane in Panel that renders third-party anywidget objects without `ipywidgets_bokeh`.

## Reports

| Track | Report | Summary |
|-------|--------|---------|
| 1 | [traitlet-mapping.md](traitlet-mapping.md) | Complete traitlet-to-param type mapping with edge cases |
| 2 | [detection.md](detection.md) | `applies()` duck-typing strategy and priority=0.8 |
| 3 | [architecture.md](architecture.md) | Dynamic `AnyWidgetComponent` subclass approach validated |
| 4 | [sync.md](sync.md) | Bidirectional traitlet <-> param <-> Bokeh sync with guard pattern |
| 5 | [pane-design.md](pane-design.md) | Complete class skeleton with lifecycle flows |
| 6 | [esm-handling.md](esm-handling.md) | ESM/import map compatibility analysis |
| 7 | [ux-reactivity.md](ux-reactivity.md) | UX design for param reactivity via `pane.component` |
| 8 | [external-issues.md](external-issues.md) | External issues from marimo and ipywidgets_bokeh; risk assessment |

## Overall Architecture

```
pn.pane.AnyWidget(some_anywidget_instance)
    |
    +-- Detection: duck-typing (traits + comm + _esm) at priority 0.8
    |
    +-- Dynamic class: type('Name', (AnyWidgetComponent,), {_esm, params...})
    |       Triggers ReactiveESMMetaclass -> construct_data_model()
    |       Cached per anywidget class in _COMPONENT_CACHE
    |
    +-- Component instance: DynClass(**current_traitlet_values)
    |       Exposed as pane.component for user reactivity
    |
    +-- Three-way sync:
    |       traitlets <-> component.param <-> Bokeh model <-> browser
    |       Guard: _trait_changing list prevents recursion
    |
    +-- ESM pipeline: AnyWidgetComponent's existing TS adapter
            AnyWidgetModelAdapter provides get/set/save_changes/on/off
```

## Key Decisions

### 1. Detection & Priority

- **`priority = 0.8`** — wins over `IPyWidget` (0.6) and `IPyLeaflet` (0.7)
- **Duck-typing**: `hasattr(obj, 'traits') and hasattr(obj, 'comm') and hasattr(type(obj), '_esm')`
- No false positives: Panel's `Viewable` subclasses are caught by the `isinstance(obj, Viewable)` short-circuit before pane resolution runs
- See [detection.md](detection.md) for full conflict analysis

### 2. Architecture: Dynamic AnyWidgetComponent Subclass

**Validated** — Option A (dynamic subclass) is the recommended approach:

- `type('Name', (AnyWidgetComponent,), {...})` triggers `ReactiveESMMetaclass.__init__` which calls `construct_data_model()` — confirmed via code trace
- `_esm` as string or `pathlib.Path` on the dynamic class works via `_render_esm()` fallback path
- CSS injected via `_stylesheets` class attribute
- React in the import map does not affect non-React anywidgets (only loaded if imported)
- Frontend module caching shares compiled ESM across instances of the same class
- Alternative approaches (new Bokeh model, instance manipulation) were evaluated and rejected
- See [architecture.md](architecture.md) for detailed validation

### 3. Traitlet-to-Param Mapping

Complete mapping covering all traitlet types used by popular anywidgets:

| Common Traitlets | Param Type | Bokeh Property |
|-----------------|------------|----------------|
| `Int`, `CInt`, `Long` | `pm.Integer` | `bp.Int` |
| `Float`, `CFloat` | `pm.Number` | `bp.Either(bp.Float, bp.Bool)` |
| `Unicode`, `CUnicode` | `pm.String` | `bp.String` |
| `Bool`, `CBool` | `pm.Boolean` | `bp.Bool` |
| `Bytes`, `CBytes` | `pm.Bytes` | `bp.Nullable(bp.Bytes)` |
| `List` | `pm.List` | `bp.List(bp.Any)` |
| `Dict` | `pm.Dict` | `bp.Dict(bp.String, bp.Any)` |
| `Tuple` | `pm.Tuple` | `bp.Any` |
| `Enum` | `pm.Selector` | `bp.Any` (fallback) |
| Unknown / custom | `pm.Parameter` | `bp.Any` (fallback) |

- Custom traitlet subclasses resolved via MRO walking
- `traitlets.tag(sync=True)` enumerated via `widget.traits(sync=True)`
- Framework traits (`_esm`, `_css`, `_model_name`, etc.) excluded
- Binary data path (`pm.Bytes` -> `bp.Nullable(bp.Bytes)` -> `ArrayBuffer` -> `DataView`) works correctly
- See [traitlet-mapping.md](traitlet-mapping.md) for full mapping and edge cases

### 4. Bidirectional Sync

Three-layer sync with recursion guard:

```
anywidget traitlets  <-->  component params  <-->  Bokeh model
     (widget.observe)       (param.watch)      (_link_props)
              \____ _trait_changing guard ____/
```

- Layer 2 <-> 3 (param <-> Bokeh) handled by existing `Syncable` machinery
- Layer 1 <-> 2 (traitlet <-> param) uses `_trait_changing` list guard, same pattern as `create_linked_datamodel()`
- Cleanup: `widget.unobserve(handler)` on pane destruction or object change
- Thread safety: sufficient for single-threaded callback model (Jupyter main thread, Bokeh doc lock)
- See [sync.md](sync.md) for complete prototype

### 5. ESM & Import Map Compatibility

| Scenario | Status |
|----------|--------|
| Inline ESM string | Works |
| `pathlib.Path` ESM | Works |
| Bundled ESM (all deps included) | Works |
| CDN URL imports (`https://esm.sh/...`) | Works |
| Bare import specifiers | Partial — needs user-provided import map |
| React-based anywidgets | Works — React already in import map |
| Non-React anywidgets | Works — React not loaded unless imported |
| TypeScript / JSX ESM | Works — Sucrase compiles on the fly |

- `AnyWidgetComponent._render_code()` provides the anywidget adapter shim (`model.get/set/save_changes/on/off`)
- The adapter translates anywidget API calls to Bokeh model operations
- See [esm-handling.md](esm-handling.md) for full analysis

### 6. UX: Param Reactivity

**Recommended approach: Expose internal component via `pane.component`**

```python
widget = SomeAnyWidget(value=10)
pane = pn.pane.AnyWidget(widget)

# Full param/Panel reactivity via .component
pane.component.value                          # read
pane.component.value = 42                     # write (syncs everywhere)
pane.component.param.watch(cb, ['value'])     # watch
pn.bind(fn, pane.component.param.value)       # bind
pane.component.param.value.rx()               # reactive expression
pane.component.link(slider, value='value')    # link
```

**Why `.component` (Option F) over alternatives:**
- Options A (direct params on pane): name collisions with pane's Layoutable params
- Option B (proxy via .object): not Panel-idiomatic, no reactive primitives
- Option C (separate namespace): non-standard, verbose
- Option D (.rx only): not independently viable
- Option E (subclass with `_anywidget_class`): excellent for library authors, too heavy for ad-hoc use

**Name collision resolution:** Prefix conflicting trait names with `w_` (e.g., anywidget `width` trait -> `component.w_width`)

**Subclass pattern** (Option E) supported as an advanced secondary pattern:

```python
class MyMap(pn.pane.AnyWidget):
    _anywidget_class = lonboard.Map

map_widget = MyMap(center=[40.7, -74.0], zoom=10)
map_widget.component.param.watch(cb, ['zoom'])
```

See [ux-reactivity.md](ux-reactivity.md) for full evaluation and code examples.

## Pane Class Skeleton

The complete class skeleton is in [pane-design.md](pane-design.md). Key points:

- **File**: `panel/pane/anywidget.py`
- **Base class**: `Pane` (provides `object`, `_rerender_params`, `_update_pane`, `_update_object`)
- **`_updates = False`**: full model rebuild on object change
- **`component`**: `param.ClassSelector(class_=AnyWidgetComponent, constant=True)` — the internal component
- **`_get_model()`**: delegates to `self.component._get_model()`
- **`_cleanup()`**: tears down trait sync when last root is cleaned up
- **Registration**: import in `panel/pane/__init__.py`, add to `__all__`

## Environments

The architecture works across all target environments:

- **Panel server** (`panel serve`): Bokeh document handles model sync; ESM loaded via `es-module-shims`
- **Jupyter notebooks**: `pyviz_comms` handles model sync; same ESM pipeline
- **Pyodide**: ESM pipeline works in browser; Bokeh model sync via in-browser document

## Verification Checklist

- [x] Traitlet-to-param mapping covers types used by lonboard, mosaic, drawdata, jupyter-scatter
- [x] Architecture recommendation (dynamic subclass) validated with concrete metaclass code trace
- [x] Sync strategy has working prototype pattern with loop guards
- [x] Pane skeleton addresses all environments (server, notebook, Pyodide)
- [x] Detection strategy has no false positives (verified 5 scenarios)
- [x] ESM pipeline handles inline, file-based, bundled, and CDN imports
- [x] UX design provides full param reactivity via `pane.component`
- [x] Name collision strategy defined (w_ prefix)
- [x] Cleanup lifecycle handles observer teardown

## Future Considerations

1. **Pydantic Parameterized wrapper**: Same architecture pattern (foreign type -> param mapping -> bidirectional sync) could be reused for wrapping Pydantic `BaseModel` instances. See [todo.md](todo.md) for details.
2. **`__getattr__` forwarding**: Optional ergonomic enhancement to allow `pane.value` as shortcut for `pane.component.value`. Deferred to avoid confusion with pane params.
3. **HMR support**: Anywidget's `FileContents` change signal could be connected to Panel's `_watch_esm()` for hot module replacement.
4. **`send()` / custom messages**: `AnyWidgetComponent` already supports `_send_msg()`. The pane should expose `pane.send(msg)` for custom message passing.

### 5. External Issues Findings (Track 8)

Research into marimo and ipywidgets_bokeh issues ([external-issues.md](external-issues.md)) identified 17 relevant issues across both projects. Key findings:

- **Shadow DOM is the highest new risk**: marimo issues #6026 and #2196 show that anywidgets designed for Jupyter break when rendered inside Shadow DOM (CSS isolation strips styles, `document.getSelection()` and other APIs fail). **Recommendation**: default `use_shadow_dom=False` on the dynamic component class created by the AnyWidget pane, since anywidgets do not expect shadow DOM isolation.
- **Binary data handling is well-addressed**: Panel's Bokeh binary websocket frames and the `AnyWidgetAdapter.get()` DataView conversion handle the binary path correctly, avoiding the JSON encoding bugs that affected marimo (#2506).
- **ipywidgets_bokeh dependency elimination is strongly motivated**: The project has 25 open issues, no PyPI releases in 12+ months, and fundamental architectural limitations (requireJS dependency, ArrayBuffer serialization failures, widget protocol version errors). Panel's native AnyWidget pane bypasses all of these issues.
- **Callback signature follows the AFM spec**: Panel's `AnyWidgetAdapter.on()` uses zero-argument callbacks, matching the anywidget specification. Widgets using the Backbone three-argument convention will fail (same as marimo), which is acceptable per the spec.
- **Overall risk level: LOW to MEDIUM** -- no architectural changes needed, only minor adjustments (Shadow DOM default, additional tests for binary edge cases).
