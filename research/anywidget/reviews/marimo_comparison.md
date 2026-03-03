# Marimo vs Panel: AnyWidget Implementation Comparison

**Research date:** 2026-03-02
**Marimo source:** `/workspaces/marimo`
**Panel source:** `/workspaces/panel`

## Key Files Examined

### Marimo
- `/workspaces/marimo/marimo/_plugins/ui/_impl/from_anywidget.py` — Python wrapper class
- `/workspaces/marimo/marimo/_plugins/ui/_impl/anywidget/init.py` — comm initialization
- `/workspaces/marimo/marimo/_plugins/ui/_impl/anywidget/utils.py` — buffer path extraction
- `/workspaces/marimo/marimo/_plugins/ui/_impl/anywidget/types.py` — type definitions
- `/workspaces/marimo/marimo/_plugins/ui/_impl/comm.py` — comm implementation
- `/workspaces/marimo/marimo/_messaging/notification.py` — wire protocol message types
- `/workspaces/marimo/frontend/src/plugins/impl/anywidget/model.ts` — frontend model with full protocol
- `/workspaces/marimo/frontend/src/plugins/impl/anywidget/widget-binding.ts` — ESM loading & AFM lifecycle
- `/workspaces/marimo/frontend/src/plugins/impl/anywidget/AnyWidgetPlugin.tsx` — React plugin component
- `/workspaces/marimo/frontend/src/plugins/impl/anywidget/serialization.ts` — binary buffer handling

### Panel
- `/workspaces/panel/panel/pane/anywidget.py` — Python pane
- `/workspaces/panel/panel/models/anywidget_component.ts` — TypeScript model adapter

---

## 1. Model Protocol Implementation (get/set/save_changes/send/on/off)

### Marimo Approach

Marimo implements the anywidget model protocol in a dedicated TypeScript `Model<T>` class in `model.ts`. The class uses **private class fields** (`#`) for encapsulation:

```typescript
export class Model<T extends ModelState> implements AnyModel<T> {
  #ANY_CHANGE_EVENT = "change";
  #dirtyFields: Map<keyof T, unknown>;   // tracks only changed fields
  #data: T;
  #comm: MarimoComm<T>;
  #listeners: Record<string, Set<EventHandler> | undefined> = {};
```

Key protocol method details:

**`set(key, value)` + `save_changes()`** — Marimo maintains a `#dirtyFields` Map that accumulates all `set()` calls. `save_changes()` only sends the dirty fields as a **partial update** and then clears the map:
```typescript
save_changes(): void {
  if (this.#dirtyFields.size === 0) { return; }
  const partialData = Object.fromEntries(this.#dirtyFields.entries()) as Partial<T>;
  this.#dirtyFields.clear();
  this.#comm.sendUpdate(partialData);
}
```

**`on(event, callback)` + `off(event, callback)`** — The on/off system uses a plain `Record<string, Set<EventHandler>>` map. `off()` accepts nullable arguments for broad cleanup:
```typescript
off(eventName?: string | null, callback?: EventHandler | null): void {
  if (!eventName) { this.#listeners = {}; return; }  // clear all
  if (!callback) { this.#listeners[eventName] = new Set(); return; }  // clear event
  this.#listeners[eventName]?.delete(callback);
}
```

**Generic `"change"` event** — In addition to `"change:fieldname"` events, Marimo emits a generic `"change"` event (debounced to one call per animation frame) whenever any field changes:
```typescript
#emitAnyChange = debounce(() => {
  const listeners = this.#listeners[this.#ANY_CHANGE_EVENT];
  for (const listener of listeners) { try { listener(); } catch (e) { Logger.error(...) } }
}, 0);
```

**`send(content, callbacks?, buffers?)`** — Fully supports binary buffers. ArrayBuffers and ArrayBufferViews are converted to `DataView`s and sent through the comm:
```typescript
send(content: any, callbacks?: any, buffers?: ArrayBuffer[] | ArrayBufferView[]): Promise<void> {
  const dataViews = (buffers ?? []).map((buf) =>
    buf instanceof ArrayBuffer ? new DataView(buf)
      : new DataView(buf.buffer, buf.byteOffset, buf.byteLength)
  );
  return this.#comm.sendCustomMessage(content, dataViews).then(() => callbacks?.());
}
```

**`widget_manager.get_model(model_id)`** — Marimo provides a real `widget_manager` API that allows widgets to look up other registered models asynchronously. This enables compound widgets (e.g. `model.widget_manager.get_model("abc123")`):
```typescript
widget_manager = {
  async get_model<TT extends ModelState>(model_id: WidgetModelId): Promise<AnyModel<TT>> {
    const model = await Model._modelManager.get(model_id);
    return model;
  },
};
```

**Internal API isolation** — Marimo uses a JavaScript `Symbol` (`marimoSymbol`) to hide internal methods from the public `AnyModel` interface, while still allowing trusted internal code to call them:
```typescript
[marimoSymbol]: MarimoInternalApi<T> = {
  updateAndEmitDiffs: (value: T) => this.#updateAndEmitDiffs(value),
  emitCustomMessage: (...) => this.#emitCustomMessage(...),
};
export function getMarimoInternal<T>(model: Model<T>): MarimoInternalApi<T> {
  return model[marimoSymbol];
}
```

### Panel Approach

Panel implements the protocol inside the `AnyWidgetModelAdapter` class in `anywidget_component.ts`. The adapter wraps the Bokeh model rather than maintaining its own data store:

```typescript
class AnyWidgetModelAdapter {
  declare model: AnyWidgetComponent
  model_changes: any   // accumulated setv calls
  data_changes: any    // accumulated data model changes
  _cb_map: Map<any, any>   // original cb → wrapped cb mapping
```

**`set(name, value)` + `save_changes()`** — Panel's `set()` routes to either `model_changes` or `data_changes` depending on whether the property lives on the Bokeh model or the data sub-model. `save_changes()` calls `this.model.setv(model_changes)` and handles nested `data` properties:
```typescript
save_changes() {
  this.model.setv(this.model_changes);
  this.model_changes = {};
  // ... complex nested data property walking ...
  this.data_changes = {};
}
```

**`on(event, cb)`** — Panel wraps all `"change:"` callbacks because Bokeh's `Signal0.emit()` passes `undefined` as the argument. The wrapper explicitly calls `this.get(trait_name)` to fetch the new value:
```typescript
const wrapped = () => {
  const value = this.get(trait_name);
  if (value !== undefined) { cb(value); }
}
this._cb_map.set(cb, wrapped);
this.model.watch(this.view, prop, wrapped);
```

**`off(event, cb)`** — Panel's `off()` requires both arguments. There is no support for `off()` with no arguments (clear all) or `off(event)` with only an event name (clear all for that event). This is a protocol gap.

**Generic `"change"` event** — Panel does **not** support the generic `"change"` event (without a field name suffix). Only `"change:fieldname"` events are routed.

**`widget_manager`** — Panel's adapter has **no `widget_manager` property**. This means compound widgets using `model.widget_manager.get_model()` will fail with "model.widget_manager is not defined".

**Binary data in `get()`** — Panel's `get()` converts `ArrayBuffer` to `DataView` at read time:
```typescript
if (value instanceof ArrayBuffer) { value = new DataView(value) }
```

---

## 2. Binary Data Transfer and Buffers

### Marimo Approach

Marimo uses a **dedicated wire format** with full round-trip support for binary buffers.

**Python side** — Uses ipywidgets' `_remove_buffers()` to extract `buffer_paths` from the widget state dict. Buffers are sent as raw `bytes` in the `ModelOpen`/`ModelUpdate` messages, then base64-encoded by `to_json_serializable()` for static export:
```python
# in comm.py
def _create_model_message(data: dict, buffers: list[Buffer]) -> Optional[ModelMessage]:
    bbuffers = [_ensure_bytes(b) for b in buffers]
    if method == "open":
        return ModelOpen(state=state, buffer_paths=buffer_paths, buffers=bbuffers)
```

The `_ensure_bytes()` helper handles non-standard buffer types (e.g. from `obstore`) that don't subclass `bytes`/`memoryview`/`bytearray` but implement `__buffer__` (Python 3.12+).

**Frontend side** — All incoming buffers are `base64ToDataView()`-decoded and stored in the `Model`'s state at the correct `buffer_paths`. The `decodeFromWire()` function handles both base64 strings and existing DataViews:
```typescript
export function decodeFromWire<T>(input: { state: T; bufferPaths?: Path[]; buffers?: (DataView | Base64String)[] }): T {
  for (const [i, bufferPath] of bufferPaths.entries()) {
    if (typeof buffer === "string") { set(out, bufferPath, base64ToDataView(buffer)); }
    else { set(out, bufferPath, buffer); }
  }
}
```

**Outgoing buffers (frontend → backend)** — `serializeBuffersToBase64()` dynamically discovers all `DataView` instances in the state object via `findDataViewPaths()` (recursive traversal). No need to pre-declare buffer paths:
```typescript
function findDataViewPaths(obj: unknown, currentPath: Path = []): Path[] {
  if (obj instanceof DataView) { paths.push(currentPath); }
  else if (Array.isArray(obj)) { for (const [i, e] of obj.entries()) ... }
  else if (typeof obj === "object") { for (const [key, v] of Object.entries(obj)) ... }
}
```

**Custom message buffers** — The `msg:custom` protocol (`model.send()`) natively carries `DataView[]` as a separate parameter. The buffers are base64-encoded for transport in `sendCustomMessage()`.

### Panel Approach

Panel uses a **manual base64 encoding strategy** layered on top of its JSON-only ESMEvent channel.

**State traits (Python → TypeScript)** — Panel inherits Bokeh's native `bp.Bytes` property type. When a `param.Bytes` parameter changes, Bokeh serializes it as an `ArrayBuffer`. The adapter's `get()` converts it to `DataView`:
```typescript
if (value instanceof ArrayBuffer) { value = new DataView(value) }
```

**State traits (TypeScript → Python)** — Panel's `set()` converts `DataView` and typed arrays back to `ArrayBuffer` before passing to `model_changes` / `data_changes`:
```typescript
if (value instanceof DataView) {
  value = value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength)
}
```

**Custom message buffers** — Panel has no native binary channel for `ESMEvent`. Instead, the Python `_send_override()` function manually base64-encodes buffers into `_b64_buffers` inside the JSON message:
```python
def _send_override(content, buffers=None):
    if buffers:
        encoded = [base64.b64encode(buf).decode('ascii') for buf in buffers]
        content = {**content, '_b64_buffers': encoded}
    component._send_msg(content)
```
The TypeScript adapter then manually decodes them with `atob()`:
```typescript
const wrapped = (data: any) => {
  if (data && data._b64_buffers) {
    buffers = data._b64_buffers.map((b64) => { /* atob decode */ return new DataView(...) })
    const {_b64_buffers, ...clean} = data;
    data = clean;
  }
  cb(data, buffers);
}
```

**Key Gap:** Panel does not support nested buffer paths from `buffer_paths`. Marimo supports buffers at arbitrary nested paths (e.g. `["nested", "arr", 0, "bytes"]`). Panel only supports top-level `bytes` traits via Bokeh's `bp.Bytes`.

---

## 3. Render Lifecycle

### Marimo Approach

Marimo implements the full [AFM (anywidget Framework Manifest) spec](https://anywidget.dev/en/afm) lifecycle with clear separation:

1. **`initialize({model, experimental})`** — called once per model lifetime (shared across all views of the same model). The return value is a cleanup function, registered on a per-binding `AbortController`.

2. **`render({model, el, experimental})`** — called once per view (one DOM element). The return value is another cleanup function, registered on a combined signal (view unmount OR binding destruction).

```typescript
class WidgetBinding<T extends ModelState = ModelState> {
  async bind(widgetDef: AnyWidget<T>, model: Model<T>): Promise<RenderFn> {
    const cleanup = await widget.initialize?.({ model, experimental });
    if (cleanup) { bindingSignal.addEventListener("abort", cleanup); }

    this.#render = async (el, viewSignal) => {
      const renderCleanup = await widget.render?.({ model, el, experimental });
      if (renderCleanup) {
        const combined = abortSignalAny([viewSignal, bindingSignal]);
        combined.addEventListener("abort", renderCleanup);
      }
    };
    return this.#render;
  }
}
```

**AbortSignal composition** — Marimo includes a polyfill for `AbortSignal.any()` to support older environments:
```typescript
function abortSignalAny(signals: AbortSignal[]): AbortSignal {
  if (typeof AbortSignal.any === "function") { return AbortSignal.any(signals); }
  const controller = new AbortController();
  for (const signal of signals) {
    if (signal.aborted) { controller.abort(signal.reason); return controller.signal; }
    signal.addEventListener("abort", () => controller.abort(signal.reason), { once: true });
  }
  return controller.signal;
}
```

**Model manager timeout** — If the frontend is waiting for a model that never arrives (race condition), the `ModelManager` rejects after 10 seconds:
```typescript
constructor(timeout = 10_000) { this.#timeout = timeout; }
get(key: WidgetModelId): Promise<Model<any>> {
  // ...
  setTimeout(() => {
    if (entry.deferred.status !== "pending") { return; }
    entry.deferred.reject(new Error(`Model not found for key: ${key}`));
  }, this.#timeout);
}
```

**Model/view race handling** — The `"open"` message handler checks for an existing model before creating a new one (handles case where the React component renders before the `"open"` message arrives):
```typescript
const existingModel = modelManager.getSync(modelId);
if (existingModel) {
  getMarimoInternal(existingModel).updateAndEmitDiffs(stateWithBuffers);
  return;  // do not create duplicate
}
```

**Widget def as factory function** — The `WidgetBinding.bind()` method handles both object and factory function widget definitions:
```typescript
const widget = typeof widgetDef === "function" ? await widgetDef() : widgetDef;
```

**Lifecycle on model close** — When a `"close"` message arrives, both the `BindingManager` binding AND the `ModelManager` entry are destroyed. The model's `AbortSignal` is aborted, which clears all listeners registered on it:
```typescript
case "close":
  BINDING_MANAGER.destroy(modelId);   // aborts binding signal → initialize cleanup
  modelManager.delete(modelId);       // aborts model signal → clears all listeners
  return;
```

**Python lifecycle** — A `CommLifecycleItem` is registered with the marimo cell lifecycle registry. When the cell is re-executed or deleted, the comm is closed, which sends a `ModelClose` to the frontend:
```python
class CommLifecycleItem(CellLifecycleItem):
  def dispose(self, context: RuntimeContext, deletion: bool) -> bool:
    self._comm.close()
    return True
```

### Panel Approach

Panel's lifecycle is driven by the Bokeh view lifecycle:

1. **`initialize()`** — Panel calls `_run_initializer()` once per model, passing an `AnyWidgetModelAdapter` (not the view-specific adapter).

2. **`render()`** — Panel's `_render_code()` creates a render module that wraps the anywidget's `render()` function. The `destroyer` Promise holds the cleanup function returned by `render()`:
```typescript
const out = Promise.resolve(view.render_fn({ view, model: view.adapter, ... }) || null)
view.destroyer = out
```

3. **Cleanup** — On `remove()`, the adapter calls `destroyer.then(d => d({model, el}))`. This correctly handles the case where `render()` returns a cleanup function.

**Key Gaps:**
- Panel does not use `AbortSignal` for lifecycle management. Cleanup is entirely dependent on the `destroyer` Promise pattern, which does not compose well for multiple views.
- The `initialize()` lifecycle spec says its return cleanup should fire when the model is destroyed (not just when a single view is removed). Panel fires the cleanup on each view's `remove()`, which violates the spec for multi-view scenarios.
- No model manager timeout — if the Bokeh model creation is delayed, there is no timeout error.

---

## 4. Traitlet to Internal State Mapping

### Marimo Approach

Marimo does **not** map traitlets to an internal state system. Instead, it uses a `MarimoComm` object that replaces the widget's `comm` attribute. The comm shims the ipywidgets comm protocol (`open`, `send`, `close`, `on_msg`) using marimo's own messaging infrastructure.

The widget's traitlets remain the source of truth. When a traitlet changes, the widget's existing `_handle_msg` mechanism calls `comm.send()` which broadcasts a `ModelUpdate` notification. When the frontend sends an update, `handle_msg()` is called, which calls `_handle_msg` on the widget, which updates the traitlet values.

**Filtering ignored traits** — Marimo filters 17 system traits from state before sending to the frontend:
```python
ignored_traits = {
  "comm", "layout", "log", "tabbable", "tooltip", "keys",
  "_esm", "_css", "_anywidget_id", "_msg_callbacks", "_dom_classes",
  "_model_module", "_model_module_version", "_model_name",
  "_property_lock", "_states_to_send", "_view_count",
  "_view_module", "_view_module_version", "_view_name",
}
```

**State sync (frontend → Python)** — When the frontend sends `method: "update"`, `MarimoCommManager.receive_comm_message()` calls `comm.handle_msg(payload)`, which calls `w._handle_msg(msg)` — the standard ipywidgets message handler that calls `widget.set_state(state)`.

**Partial state updates** — The `receive_comm_message()` method returns `(ui_element_id, state)` from update messages to trigger cell re-execution with just the changed fields.

### Panel Approach

Panel maps each synced traitlet to a `param.Parameter` on a dynamically generated `AnyWidgetComponent` subclass. This gives Panel the full Param ecosystem (watchers, bind, rx):

```python
TRAITLET_MAP = {
  traitlets.Bool:    param.Boolean,
  traitlets.Int:     param.Integer,
  traitlets.Float:   param.Number,
  traitlets.Unicode: param.String,
  traitlets.Bytes:   param.Bytes,
  traitlets.List:    param.List,
  traitlets.Tuple:   param.Tuple,
  traitlets.Dict:    param.Dict,
  # ...
}
```

**Bidirectional sync** — Panel uses `widget.observe()` for traitlet → param updates and `component.param.watch()` for param → traitlet updates. A `_trait_changing` set prevents infinite loops.

**Deep serialization** — Non-JSON-safe values (dataclasses, msgspec Structs, pydantic models, pandas DataFrames) are recursively serialized. DataFrames are converted to records format.

**Instance trait handling** — `traitlets.Instance` is mapped to `param.Dict` because Bokeh cannot serialize arbitrary Python objects. The sync layer converts between the instance type and dict using `from_dict`, `msgspec.convert`, `model_validate`, or `klass(**value)`.

**Key advantage of Panel's approach:** Full Param reactivity — users can do `pn.bind(my_func, pane.component.param.value)` or `pane.component.rx.value` on any trait. Marimo does not offer this (access is through the widget instance directly).

---

## 5. Name Collision Handling

### Marimo Approach

Marimo does not rename traits. The `Model<T>` stores all state under the original trait names. No collision handling needed because marimo uses its own state store and does not integrate with a UI framework that has reserved property names.

### Panel Approach

Panel maps traitlet names to param names, renaming any that collide with:
1. Existing params on `AnyWidgetComponent` or its parent classes (e.g. `height`, `width`, `margin`)
2. BokehJS reserved attribute names (e.g. `name`, `type`, `id`, `get`, `set`, `destroy`)

The renaming convention is `w_<name>` (e.g. `height` → `w_height`). A `_trait_name_map` dict is passed to the TypeScript adapter via `esm_constants`, which uses it for transparent translation:

```typescript
get _trait_name_map(): Record<string, string> {
  const constants = this.model.data?.attributes?.esm_constants;
  return (constants && constants._trait_name_map) ? constants._trait_name_map : {};
}
_to_param_name(trait_name: string): string {
  return this._trait_name_map[trait_name] || trait_name;
}
```

This is a significant feature that Marimo doesn't need (because it uses its own state dict and doesn't integrate with a Bokeh model), but it's necessary for Panel because Bokeh's data model has many reserved names.

---

## 6. ESM Loading Strategy

### Marimo Approach

Marimo uses **native ES module `import()`** via Vite's `/* @vite-ignore */` hint:
```typescript
async #doImport(jsUrl: string): Promise<any> {
  let url = asRemoteURL(jsUrl).toString();
  if (isStaticNotebook()) { url = resolveVirtualFileURL(url); }
  return import(/* @vite-ignore */ url);
}
```

**Deduplication by content hash** — The `WidgetDefRegistry` caches imports by `jsHash` (a hash of the ESM contents, NOT the URL). This means:
- Multiple widget instances of the same type share one import
- Re-loading with a different URL (but same contents) reuses the cached module
- If the ESM changes (hot reload), the hash changes, so a new import is triggered

```typescript
class WidgetDefRegistry {
  getModule(jsUrl: string, jsHash: string): Promise<any> {
    const cached = this.#cache.get(jsHash);
    if (cached) { return cached; }
    const promise = this.#doImport(jsUrl).catch((error) => {
      this.#cache.delete(jsHash);  // clear on failure to allow retry
      throw error;
    });
    this.#cache.set(jsHash, promise);
    return promise;
  }
  invalidate(jsHash: string): void { this.#cache.delete(jsHash); }
}
```

**Error recovery** — If an import fails (e.g. network error or invalid URL), the cache entry is removed so the next call with a new URL can retry.

**Hot reload** — When `jsHash` changes (ESM contents changed), `WidgetDefRegistry.invalidate()` is called and `WidgetBinding.bind()` detects the different `widgetDef` object and re-initializes, calling the old binding's cleanup first.

**Static notebook** — For static exports, virtual file URLs are resolved to blob URLs via `resolveVirtualFileURL()`.

### Panel Approach

Panel uses **sucrase transpilation** followed by a blob URL import inside the Bokeh framework. The `AnyWidgetComponent.compile()` method:
1. Tries sucrase TypeScript+JSX transpilation
2. Falls back to raw ESM if sucrase fails with a `SyntaxError` (handles pre-bundled modules like tldraw, quak)

```typescript
override compile(): string | null {
  if (this.bundle != null) { return this.esm; }
  try {
    const result = super.compile();
    if (result !== null) { return result; }
    this.compile_error = null;
    return this.esm;  // fallback to raw ESM
  } catch (e) {
    if (e instanceof SyntaxError) { return this.esm; }
    throw e;
  }
}
```

**No content hashing for deduplication** — Panel caches the render module by a static key `"anywidget_component"`, not by ESM content hash. All instances of different widget types share the same render module (which is the generic render glue, not the widget-specific ESM). The widget-specific ESM is loaded separately by ReactiveESM.

**Import maps** — Panel uses the `_importmap` class variable to support import map entries for resolving module specifiers.

**Key difference:** Marimo imports the ESM URL directly as a native ES module and caches by content hash. Panel transpiles the ESM with sucrase and loads it as a blob URL. Panel does not support the `jsHash`-based deduplication that prevents redundant imports across multiple instances of the same widget.

---

## 7. `msg:custom` Protocol

### Marimo Approach

The `msg:custom` protocol is handled as a first-class citizen in Marimo's comm system.

**Python → Frontend** — When Python calls `widget.send(content, buffers)`, the `MarimoComm.send()` method broadcasts a `ModelCustom` notification:
```python
class ModelCustom(msgspec.Struct, tag="custom", tag_field="method"):
  content: Any
  buffers: list[bytes]
```

**Frontend handling** — The `handleWidgetMessage` function dispatches `"custom"` messages to `model.emitCustomMessage()`, which notifies all `"msg:custom"` listeners with `(content, buffers)` where `buffers` is a `DataView[]`:
```typescript
case "custom": {
  const model = await modelManager.get(modelId);
  getMarimoInternal(model).emitCustomMessage(
    { method: "custom", content: msg.content },
    buffers,  // already decoded from base64 to DataViews
  );
}
```

**Frontend → Python** — `model.send(content, callbacks, buffers)` calls `comm.sendCustomMessage(content, dataViews)` which sends:
```typescript
await getRequestClient().sendModelValue({
  modelId,
  message: { method: "custom", content },
  buffers: buffers.map(dataViewToBase64),
});
```

The Python backend receives this as a comm message with `method: "custom"` and calls `w._handle_msg` which dispatches to `_handle_custom_msg`.

**Key feature:** Buffers are natively transmitted (as base64 in the JSON) in both directions. The `msg:custom` listener signature `(content, buffers: DataView[])` is correctly implemented.

### Panel Approach

Panel's `msg:custom` support is implemented via a workaround over the JSON-only `ESMEvent` channel.

**Python → Frontend** — Python's `widget.send()` is monkey-patched to base64-encode buffers into the JSON message body under `_b64_buffers`:
```python
def _send_override(content, buffers=None):
  if buffers:
    encoded = [base64.b64encode(buf).decode('ascii') for buf in buffers]
    content = {**content, '_b64_buffers': encoded}
  component._send_msg(content)
```
The TypeScript adapter's `on("msg:custom", cb)` wraps the listener to decode `_b64_buffers` back to `DataView[]`:
```typescript
const wrapped = (data: any) => {
  if (data && data._b64_buffers) {
    buffers = data._b64_buffers.map(b64 => { /* atob */ return new DataView(...) });
    const {_b64_buffers, ...clean} = data;
    data = clean;
  }
  cb(data, buffers);
};
```

**Frontend → Python** — The `model.send(data)` in the Panel adapter triggers a `DataEvent`, which the Python component's `on_msg` handler receives. Buffers are not natively supported in this direction (no `DataView[]` parameter handling in `send()`).

**Key Gap:** Panel's `send()` method in the adapter (`AnyWidgetModelAdapter.send()`) calls `this.model.trigger_event(new DataEvent(data))` without accepting the `buffers` parameter from the anywidget protocol. The signature should be `send(content, callbacks?, buffers?)` but Panel only handles `data`.

---

## 8. Edge Cases Marimo Handles That Panel Doesn't

### 8.1 Generic `"change"` Event (No Field Suffix)

Marimo supports `model.on("change", callback)` — a generic change event that fires (debounced to once per frame) whenever **any** field changes. Panel only supports `model.on("change:fieldname", callback)`.

Some widgets (e.g., widgets from the `ipywidgets` ecosystem) use generic change listeners as a simple "anything changed" hook. Panel would silently ignore these.

**Marimo:**
```typescript
#ANY_CHANGE_EVENT = "change";
#emitAnyChange = debounce(() => {
  const listeners = this.#listeners[this.#ANY_CHANGE_EVENT];
  for (const listener of listeners) { listener(); }
}, 0);
```

**Panel:** No equivalent. `on()` silently logs an error for unrecognized events:
```typescript
console.error(`Event of type '${event}' not recognized.`)
```

### 8.2 `off()` with No Arguments (Clear All Listeners)

Marimo's `off()` signature is `off(eventName?, callback?)` — all parameters optional. With no arguments, it clears all listeners. This is the standard backbone.js/ipywidgets convention. Panel requires both `event` and `cb`.

**Marimo:**
```typescript
off(eventName?: string | null, callback?: EventHandler | null): void {
  if (!eventName) { this.#listeners = {}; return; }     // clear all
  if (!callback) { this.#listeners[eventName] = new Set(); return; }  // clear event
  this.#listeners[eventName]?.delete(callback);
}
```

**Panel:** `off(event: string, cb: (...args) => void)` — both required.

### 8.3 `widget_manager.get_model()` for Compound Widgets

Marimo provides `model.widget_manager.get_model(model_id)` which returns a `Promise<AnyModel>` for any registered model. This supports compound widgets where the ESM needs to reference another model (e.g. via `IPY_MODEL_` prefix):

```typescript
// From marimo smoke test: anywidget_smoke_tests/multiple_models.py
let fooModel = await model.widget_manager.get_model(
  model.get("foo").slice("IPY_MODEL_".length)
)
fooModel.on("change:value", () => { button.innerText = fooModel.get("value"); });
```

Panel's adapter has **no `widget_manager` property**. This means compound widgets will fail with `TypeError: Cannot read properties of undefined (reading 'get_model')`.

### 8.4 Model Manager Race Condition Handling

Marimo's `ModelManager` supports the case where the React component renders **before** the `"open"` message arrives. The `getSync()` method returns `undefined` if not yet resolved, and `get()` returns a Promise that resolves when the model arrives (with a 10-second timeout to avoid hanging).

The `"open"` message handler detects an already-resolved model (component created first) and updates it instead of creating a duplicate:
```typescript
const existingModel = modelManager.getSync(modelId);
if (existingModel) {
  getMarimoInternal(existingModel).updateAndEmitDiffs(stateWithBuffers);
  return;
}
```

Panel does not have a model manager concept. Bokeh guarantees model creation before rendering, so this race condition does not arise. However, if Panel is ever used in an asynchronous context, this could become relevant.

### 8.5 `_repr_mimebundle_()` Sync for Third-Party Widgets

Marimo calls `_repr_mimebundle_()` on the widget before rendering, to force Plotly's `FigureWidget` (and plotly-resampler) to sync their internal state to traitlets:

```python
def _sync_widget_state(widget: AnyWidget) -> None:
  repr_mimebundle = getcallable(widget, "_repr_mimebundle_")
  if repr_mimebundle is not None:
    try: repr_mimebundle()
    except Exception: LOGGER.debug("Failed to call _repr_mimebundle_ on %s", ...)
```

This is done lazily (once, on first render) via `_ensure_widget_synced()`. Panel does not do this, which means Plotly's `FigureWidget` displayed via Panel's AnyWidget pane might show stale data.

### 8.6 WeakCache for Widget-to-UIElement Mapping

Marimo uses a custom `WeakCache` that uses `weakref.finalize()` to automatically remove cached entries when the widget object is garbage collected:

```python
class WeakCache(Generic[K, V]):
  def __init__(self) -> None:
    self._data: dict[int, V] = {}
    self._finalizers: dict[int, weakref.finalize[[int], K]] = {}
  def add(self, k: K, v: V) -> None:
    oid: int = id(k)
    self._data[oid] = v
    self._finalizers[oid] = weakref.finalize(k, self._cleanup, oid)
```

This ensures that when a user creates many widget instances without explicitly cleaning them up, the cache does not grow unboundedly.

Panel uses an `OrderedDict` with LRU eviction capped at 256 entries (`_CACHE_MAX_SIZE`). This is simpler but can keep stale component classes alive even after all widget instances are garbage collected.

### 8.7 `echo_update` Message Handling

Marimo explicitly handles and silently ignores `echo_update` messages (used for multi-client sync acknowledgment in Jupyter):
```python
elif method == "echo_update":
  return None  # skip
```

The TypeScript schema also lists `echo_update` as a valid message type, so it doesn't error on unexpected messages. Panel does not handle this message type.

### 8.8 Non-Standard Buffer Types in `_ensure_bytes()`

Marimo's `_ensure_bytes()` helper handles custom buffer types from libraries like `obstore` that hold binary data but don't subclass `bytes`/`memoryview`/`bytearray`:
```python
def _ensure_bytes(buf: object) -> bytes:
  if isinstance(buf, bytes): return buf
  return bytes(buf)  # handles __buffer__ protocol (Python 3.12+)
```

Panel does not have this wrapper and relies on Bokeh's serializer to handle buffer types natively.

### 8.9 Static/WASM Export with No-Op Comm

Marimo creates a static no-op comm in static notebook mode that silently swallows all network calls:
```typescript
const comm: MarimoComm<ModelState> = isStaticNotebook()
  ? {
      sendUpdate: async () => undefined,
      sendCustomMessage: async () => undefined,
    }
  : { /* real comm */ };
```

Panel handles this at the Panel/Bokeh level (the document is not connected to a server in static mode).

---

## 9. Feature-by-Feature Comparison Table

| Feature | Marimo | Panel | Gap |
|---------|--------|-------|-----|
| `model.get(key)` | Full implementation, returns DataView for binary | Full implementation, ArrayBuffer → DataView at read time | None significant |
| `model.set(key, value)` | Full, batches in dirtyFields Map | Full, batches in model_changes dict | None significant |
| `model.save_changes()` | Only sends dirty fields (partial update) | Sends all accumulated changes | None significant |
| `model.send(content, callbacks, buffers)` | Full: buffers as native DataView[], callbacks invoked | Partial: no buffers parameter in TS adapter `send()` | **Panel missing buffer parameter** |
| `model.on("change:key", cb)` | Full, `cb` receives new value | Full, cb wrapped to explicitly fetch value | None (both correct) |
| `model.on("change", cb)` | Supported (generic any-change, debounced) | **Not supported** | **Panel missing generic `change` event** |
| `model.on("msg:custom", cb)` | Full: `cb(content, DataView[])` | Workaround: buffers base64 in JSON body | Works but inelegant |
| `model.off(event, cb)` | Full | Full | None |
| `model.off(event)` | Clears all for that event | **Not supported** | **Panel `off` signature incomplete** |
| `model.off()` | Clears all listeners | **Not supported** | **Panel `off` signature incomplete** |
| `model.widget_manager.get_model()` | Full async, with timeout | **Not implemented** | **Panel missing widget_manager** |
| `initialize({ model, experimental })` | Full AFM spec, once per model | Called once per model | None |
| `initialize` cleanup | Fires on model close | Fires on each view remove (spec violation) | **Panel cleanup fires too early/often** |
| `render({ model, el, experimental })` | Full AFM spec, once per view | Once per view | None |
| `render` cleanup | AbortSignal composition (view unmount OR model close) | `destroyer` Promise (fires on remove) | None significant |
| `experimental.invoke` | Returns error (not supported) | **Not passed to initialize/render** | **Panel missing `experimental` object** |
| ESM loading | Native `import()`, cached by content hash | sucrase transpile → blob URL | Different approach |
| ESM hot reload | Hash-based invalidation, re-initialize | No native support | **Panel no hot reload** |
| ESM deduplication | By content hash across instances | Per-class cache via LRU OrderedDict | Marimo more efficient |
| Binary buffers (state) | `buffer_paths` at arbitrary nested paths | Top-level `bp.Bytes` only | **Panel no nested buffer paths** |
| Binary buffers (msg:custom Python→TS) | Natively carried as `buffers: list[bytes]` | Base64 in JSON via `_b64_buffers` | Works but inelegant |
| Binary buffers (msg:custom TS→Python) | Natively carried as `DataView[]` | **No buffer support in send() direction** | **Panel missing outgoing buffers** |
| `_repr_mimebundle_()` sync | Yes, for Plotly FigureWidget compat | **Not done** | **Panel may show stale Plotly data** |
| `echo_update` handling | Silently ignored | **Not handled** | **Panel may error on echo_update** |
| Non-standard buffer types | `_ensure_bytes()` handles `__buffer__` | Relies on Bokeh defaults | Minor |
| WeakRef-based caching | `WeakCache` auto-removes dead entries | LRU OrderedDict with size cap | Different approach |
| Static/WASM export | No-op comm in static mode | Handled by Bokeh layer | None |
| Model manager timeout | 10-second timeout on pending models | N/A (no model manager) | N/A |
| Race condition (component before open) | `getSync()` + deferred model update | N/A (Bokeh guarantees order) | N/A |
| CSS injection | `adoptedStyleSheets` with `<style>` fallback into shadow root | `_stylesheets` list on Bokeh model | Different approach |
| Compound widgets | `widget_manager.get_model()` | **Not supported** | **Critical gap** |
| Traitlet → param mapping | Passes through to widget directly | Full mapping with Param ecosystem | Panel has more reactivity |
| Name collision renaming | Not needed (own state dict) | `w_<name>` renaming | Panel-specific concern |
| `off()` with 0 args no-op | Clears all | Error / no-op | **Panel missing** |

---

## 10. Recommendations for Panel Improvements

### Priority 1 (Critical): `widget_manager.get_model()`

Compound widgets (e.g. from the ipywidgets ecosystem using `IPY_MODEL_` serialization) call `model.widget_manager.get_model(model_id)`. Panel's adapter is missing this property entirely.

**Recommendation:** Implement `widget_manager` on `AnyWidgetModelAdapter` using a global registry of Bokeh models. When a widget has `traitlets.Instance` traits tagged with `ipywidgets.widget_serialization`, the serialized value is `"IPY_MODEL_<uuid>"`. Panel would need to:
1. Maintain a `MODEL_REGISTRY` mapping `model_id → AnyWidgetComponent`
2. Register each created component
3. Return a proxy that wraps the other component's model

### Priority 2 (High): Generic `"change"` Event

Add support for `model.on("change", callback)` in `AnyWidgetModelAdapter.on()`. This requires tracking "any change" listeners separately and debouncing them:

```typescript
// In AnyWidgetModelAdapter
#changeCallbacks: Set<() => void> = new Set()

on(event: string, cb: (...args: any[]) => void) {
  if (event === "change") {
    this.#changeCallbacks.add(cb)
    // Hook into Bokeh's property change notifications
    // ...
    return;
  }
  // existing logic...
}
```

### Priority 3 (High): `off()` Signature Compliance

Extend `off()` to support the full anywidget protocol signature:
```typescript
off(event?: string | null, cb?: ((...args: any[]) => void) | null) {
  if (!event) { /* clear all listeners */ return; }
  if (!cb) { /* clear all listeners for this event */ return; }
  // existing logic
}
```

### Priority 4 (High): `send()` Buffer Parameter

Add the `buffers` parameter to the TypeScript adapter's `send()` method:
```typescript
send(data: any, _callbacks?: any, buffers?: ArrayBuffer[] | DataView[]) {
  // If buffers present, encode and include them
  if (buffers && buffers.length > 0) {
    const encoded = buffers.map(b => { /* base64 */ });
    data = { ...data, _b64_buffers: encoded };
  }
  this.model.trigger_event(new DataEvent(data))
}
```

### Priority 5 (Medium): `experimental` Object in `initialize`/`render`

Pass an `experimental` object when calling `initialize()` and `render()`. Marimo provides an `experimental` object with an `invoke` stub. This prevents TypeScript type errors in widgets that reference `experimental`:

```typescript
const experimental = {
  invoke: async () => { console.warn("anywidget.invoke not supported in Panel"); throw new Error("..."); }
};
// In _run_initializer:
const props = { model: new AnyWidgetModelAdapter(this), experimental };
initialize(props);
```

### Priority 6 (Medium): `_repr_mimebundle_()` Sync for Plotly

Before rendering a widget, call `_repr_mimebundle_()` if it exists. This ensures Plotly's `FigureWidget` (and plotly-resampler) syncs its internal data to widget traits. In Panel's Python `_create_component()`:

```python
def _create_component(self) -> AnyWidgetComponent | None:
  widget = self.object
  # Sync widget state before reading traits
  repr_mimebundle = getattr(widget, '_repr_mimebundle_', None)
  if callable(repr_mimebundle):
    try: repr_mimebundle()
    except Exception: pass
  # ... rest of creation
```

### Priority 7 (Low): `echo_update` Handling

Add explicit handling for `echo_update` method to prevent errors:

```python
elif method == "echo_update":
  return None  # Silently skip multi-client sync acknowledgment
```

### Priority 8 (Low): ESM Content Hash Deduplication

Consider using a content hash (e.g. SHA-256 of `_esm`) as the cache key instead of the class object. This would:
- Share the compiled module across instances of the same widget class
- Enable proper hot reload when the ESM changes

```python
esm_hash = hashlib.sha256(esm.encode('utf-8')).hexdigest()[:16] if esm else ''
# Pass to frontend as js_hash for cache keying
```

### Priority 9 (Low): `AbortSignal.any()` Polyfill

Add a polyfill for `AbortSignal.any()` to support older browsers/environments where it's not natively available:

```typescript
function abortSignalAny(signals: AbortSignal[]): AbortSignal {
  if (typeof AbortSignal.any === "function") { return AbortSignal.any(signals); }
  const controller = new AbortController();
  for (const signal of signals) {
    if (signal.aborted) { controller.abort(signal.reason); return controller.signal; }
    signal.addEventListener("abort", () => controller.abort(signal.reason), { once: true });
  }
  return controller.signal;
}
```

---

## Summary of Architecture Differences

**Marimo's approach** is a complete re-implementation of the Jupyter widget comm protocol using their own messaging infrastructure. They use a dedicated `MarimoComm` that replaces ipywidgets' kernel-based comm, maintaining the traitlet-driven widget unchanged on the Python side. The frontend has a fully typed `Model<T>` class that cleanly implements the AFM spec with proper lifecycle (initialize once, render many), AbortSignal-based cleanup, and a `widget_manager` for compound widgets. Binary data flows through dedicated buffer paths channels.

**Panel's approach** is a translation layer: traitlets are converted to Param parameters, which are synced bidirectionally. This gives Panel users native Param reactivity (`param.watch`, `pn.bind`, `.rx`) on any anywidget — a major advantage. The TypeScript adapter wraps the Bokeh model and translates the anywidget protocol API into Bokeh property changes. The tradeoffs are: the implementation is more complex (name collision handling, deep serialization), binary data handling is a workaround over JSON, and some protocol methods (`off()` variants, `widget_manager`, generic `change` event) are incomplete.

The most impactful improvements Panel can make are: `widget_manager.get_model()` support for compound widgets, generic `"change"` event support, and the full `off()` signature (no-argument and single-argument forms).
