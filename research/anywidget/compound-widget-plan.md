# Implementation Plan: `widget_manager.get_model()` for Compound AnyWidgets

## Goal

Support compound anywidgets (lonboard, higlass) in Panel's AnyWidget pane by implementing `widget_manager.get_model()` — the protocol that parent widgets use to resolve child widget references.

## Background

### The IPY_MODEL_ Protocol

In Jupyter, compound widgets reference child widgets via `"IPY_MODEL_<model_id>"` strings. Traits tagged with `**ipywidgets.widget_serialization` serialize Widget instances to these strings, and the widget manager resolves them back to model objects.

### Current State

Panel's `AnyWidgetModelAdapter.widget_manager` is a stub that rejects all `get_model()` calls. This blocks:

1. **Lonboard** — Map widget has 4 `widget_serialization` traits: `layers`, `controls`, `view`, `basemap`. Each is a child widget (or tuple of widgets). Layers themselves have `extensions` (also `widget_serialization`). The Map's ESM calls `widget_manager.get_model()` to load child models, then reads their state (Parquet tables, colors, etc.).

2. **HiGlass** — HiGlassWidget has `_tileset_client` (a plain `ipywidgets.Widget`). The ESM calls `widget_manager.get_model()` to get the tileset client, then uses `tModel.send()` / `tModel.on("msg:custom")` for data fetching.

### Reference Implementation

Marimo's `ModelManager` (in `model.ts`) uses a `Deferred` promise pattern: when `get_model(id)` is called before the model is registered, it creates a pending promise. When the model is later registered, the promise resolves. Timeout after 10s.

## Architecture

### Data Flow

```
Python                          WebSocket               JavaScript
──────                          ─────────               ──────────
Parent widget                                           Parent adapter
  ├─ trait: layers = (Layer1, Layer2)                      ├─ get("layers") → ["IPY_MODEL_abc", "IPY_MODEL_def"]
  │   to_json → ["IPY_MODEL_abc", "IPY_MODEL_def"]        │
  │                                                        ├─ widget_manager.get_model("abc")
  ├─ child: Layer1 (model_id="abc")                        │   └─ MODEL_REGISTRY.get("abc") → ChildModelAdapter
  │   ├─ table: Parquet bytes → base64                     │       ├─ get("table") → DataView[]
  │   ├─ get_fill_color: [255, 0, 0]                      │       ├─ on("change:table", cb)
  │   └─ extensions: (Ext1,) → ["IPY_MODEL_ghi"]          │       └─ widget_manager.get_model("ghi")
  │                                                        │
  └─ child: Layer2 (model_id="def")                        └─ widget_manager.get_model("def")
      └─ ...                                                   └─ ChildModelAdapter { ... }
```

### Two Types of Child Models

1. **Data-container children** (lonboard layers, controls, extensions): Hold state (traits), need `get()`, `set()`, `on("change:x")`, `save_changes()`. May themselves reference grandchild widgets.

2. **Message-only children** (HiGlass tileset client): Only need `send()` and `on("msg:custom")` for RPC-style communication. No trait reading needed.

Both types are handled by the same `ChildModelAdapter` class — message-only children simply have an empty state dict.

### Transport Mechanisms

| Channel | Mechanism | Direction |
|---------|-----------|-----------|
| Initial child state | `esm_constants._child_models` | Py → JS (once) |
| Child state updates | `component._send_msg()` (ESMEvent) | Py → JS (ongoing) |
| Child state save | `component.on_msg()` (DataEvent) | JS → Py |
| Child custom messages | Multiplexed through parent DataEvent/ESMEvent | Bidirectional |

All messages include a `_child_model_id` field for routing.

### Binary Data (Parquet/Arrow)

Lonboard serializes Arrow tables to Parquet bytes via custom `to_json` serializers. The existing pipeline handles this:

```
Python: Arrow Table → serialize_table_to_parquet() → list[bytes]
        → _deep_serialize() → [{"_pnl_bytes": "base64..."}, ...]
        → Bokeh JSON serialization → WebSocket

JS:     → ChildModelAdapter.get("table")
        → _decode_binary() → [DataView, DataView, ...]
        → lonboard's parseParquetBuffers() → Arrow Table
```

No new binary transport needed.

## Implementation Plan

### Phase 1: TypeScript — ModelRegistry + ChildModelAdapter

**File: `panel/models/anywidget_component.ts`** (~150 new lines)

#### 1.1 Deferred utility class

```typescript
class Deferred<T> {
  promise: Promise<T>
  resolve!: (value: T) => void
  reject!: (reason?: any) => void
  status: "pending" | "resolved" | "rejected" = "pending"
  value?: T

  constructor() {
    this.promise = new Promise((resolve, reject) => {
      this.resolve = (v: T) => { this.status = "resolved"; this.value = v; resolve(v) }
      this.reject = (r?: any) => { this.status = "rejected"; reject(r) }
    })
  }
}
```

#### 1.2 ModelRegistry (global, page-scoped)

```typescript
class ModelRegistry {
  _entries: Map<string, { deferred: Deferred<ChildModelAdapter> }> = new Map()
  _timeout: number = 10_000  // 10s timeout (matches marimo)

  get(model_id: string): Promise<ChildModelAdapter> {
    let entry = this._entries.get(model_id)
    if (!entry) {
      entry = { deferred: new Deferred() }
      this._entries.set(model_id, entry)
      // Timeout to prevent hanging
      setTimeout(() => {
        if (entry!.deferred.status === "pending") {
          entry!.deferred.reject(new Error(`Child model ${model_id} not found (timeout)`))
          this._entries.delete(model_id)
        }
      }, this._timeout)
    }
    return entry.deferred.promise
  }

  register(model_id: string, adapter: ChildModelAdapter): void {
    let entry = this._entries.get(model_id)
    if (!entry) {
      entry = { deferred: new Deferred() }
      this._entries.set(model_id, entry)
    }
    entry.deferred.resolve(adapter)
  }

  delete(model_id: string): void {
    this._entries.delete(model_id)
  }
}

const MODEL_REGISTRY = new ModelRegistry()
```

#### 1.3 ChildModelAdapter

A lightweight model adapter for child widgets. Implements the same anywidget/ipywidgets model interface.

```typescript
class ChildModelAdapter {
  model_id: string
  state: Record<string, any>
  parent_adapter: AnyWidgetModelAdapter
  _listeners: Record<string, Set<(...args: any[]) => void>> = {}
  _dirty: Record<string, any> = {}

  constructor(model_id: string, state: Record<string, any>, parent: AnyWidgetModelAdapter) {
    this.model_id = model_id
    this.state = state
    this.parent_adapter = parent
  }

  get(name: string): any {
    let value = this.state[name]
    return this._decode_binary(value)
  }

  set(name: string, value: any): void {
    if (value === undefined) return
    const old = this.state[name]
    this.state[name] = value
    this._dirty[name] = value
    this._emit(`change:${name}`, value)
    if (old !== value) this._emit("change")
  }

  save_changes(): void {
    if (Object.keys(this._dirty).length === 0) return
    // Route through parent to Python
    this.parent_adapter.send({
      _child_save_changes: { model_id: this.model_id, changes: this._dirty }
    })
    this._dirty = {}
  }

  on(event: string, cb: (...args: any[]) => void, _context?: any): void {
    if (!this._listeners[event]) this._listeners[event] = new Set()
    // Support Backbone.js context binding (lonboard passes `this` as context)
    const bound = _context ? cb.bind(_context) : cb
    this._listeners[event].add(bound)
    // Store original → bound mapping for off()
    if (_context) (cb as any).__bound = bound
  }

  off(event?: string | null, cb?: ((...args: any[]) => void) | null): void {
    if (!event) { this._listeners = {}; return }
    if (!cb) { this._listeners[event] = new Set(); return }
    const bound = (cb as any).__bound || cb
    this._listeners[event]?.delete(bound)
  }

  send(data: any, _callbacks?: any, _buffers?: any[]): void {
    // Multiplex through parent with model_id tag
    this.parent_adapter.send(
      { _child_model_id: this.model_id, ...(typeof data === "object" ? data : { _data: data }) },
      _callbacks, _buffers
    )
  }

  get widget_manager(): any {
    return {
      get_model: (model_id: string) => MODEL_REGISTRY.get(model_id)
    }
  }

  // Reuse parent's binary decoding
  _decode_binary(value: any): any {
    return this.parent_adapter._decode_binary(value)
  }

  _emit(event: string, value?: any): void {
    const listeners = this._listeners[event]
    if (!listeners) return
    for (const cb of listeners) {
      try { cb(value) } catch (e) { console.error(`ChildModel ${this.model_id} event error:`, e) }
    }
  }

  // Update state from Python and fire change events
  _update_state(key: string, value: any): void {
    const old = this.state[key]
    this.state[key] = value
    if (old !== value) {
      this._emit(`change:${key}`, this._decode_binary(value))
      this._emit("change")
    }
  }
}
```

#### 1.4 Update AnyWidgetModelAdapter.widget_manager

Replace the stub:
```typescript
get widget_manager(): any {
  return {
    get_model: (model_id: string) => MODEL_REGISTRY.get(model_id)
  }
}
```

#### 1.5 Child model initialization in AnyWidgetComponentView

In `initialize()`, after creating the adapter:
```typescript
override initialize(): void {
  super.initialize()
  this.adapter = new AnyWidgetAdapter(this)
  // ... existing code ...

  // Initialize child models from esm_constants
  const constants = this.model.data?.attributes?.esm_constants
  if (constants && constants._child_models) {
    for (const [model_id, info] of Object.entries(constants._child_models as Record<string, any>)) {
      const child = new ChildModelAdapter(model_id, info.state || {}, this.adapter)
      MODEL_REGISTRY.register(model_id, child)
    }
  }
}
```

#### 1.6 Handle incoming child state updates

Listen for ESMEvent messages tagged with `_child_state_update`:
```typescript
// In the view's event handling (or adapter's msg:custom handler):
// When receiving {_child_state_update: {model_id, key, value}} from Python:
const child = MODEL_REGISTRY._entries.get(msg.model_id)?.deferred.value
if (child) child._update_state(msg.key, msg.value)
```

#### 1.7 Handle incoming child custom messages

When Python sends a custom message for a child model:
```typescript
// {_child_msg_custom: {model_id, content, buffers?}}
const child = MODEL_REGISTRY._entries.get(msg.model_id)?.deferred.value
if (child) child._emit("msg:custom", msg.content)
```

### Phase 2: Python — Child Widget Detection + Serialization

**File: `panel/pane/anywidget.py`** (~120 new lines)

#### 2.1 Detect widget_serialization traits

```python
def _is_widget_serialization(trait):
    """Check if a trait uses ipywidgets.widget_serialization."""
    to_json = trait.metadata.get('to_json')
    from_json = trait.metadata.get('from_json')
    return to_json is not None and from_json is not None
```

#### 2.2 Collect child widgets recursively

```python
def _collect_child_widgets(widget, _seen=None):
    """
    Recursively collect all child widgets referenced via widget_serialization.
    Returns dict mapping model_id -> widget instance.
    """
    if _seen is None:
        _seen = set()
    widget_id = id(widget)
    if widget_id in _seen:
        return {}
    _seen.add(widget_id)

    import ipywidgets
    children = {}

    for name, trait in widget.traits(sync=True).items():
        if name in _FRAMEWORK_TRAITS:
            continue
        if not _is_widget_serialization(trait):
            continue
        value = getattr(widget, name)
        # Handle single widget, list/tuple of widgets
        widgets_to_process = []
        if isinstance(value, ipywidgets.Widget):
            widgets_to_process.append(value)
        elif isinstance(value, (list, tuple)):
            for item in value:
                if isinstance(item, ipywidgets.Widget):
                    widgets_to_process.append(item)

        for child in widgets_to_process:
            if child.model_id not in children:
                children[child.model_id] = child
                children.update(_collect_child_widgets(child, _seen))

    return children
```

#### 2.3 Serialize child widget state

```python
def _serialize_child_state(child_widget):
    """Serialize a child widget's sync-tagged traits for JS transport."""
    state = {}
    for name, trait in child_widget.traits(sync=True).items():
        if name in _FRAMEWORK_TRAITS:
            continue
        value = getattr(child_widget, name)
        state[name] = _serialize_trait(child_widget, name, value)
    return state
```

#### 2.4 Update `_create_component()` to handle children

In `_create_component()`, after building the component:

```python
# Collect child widgets
children = _collect_child_widgets(widget)
if children:
    # Add child model data to constants
    child_models = {}
    for model_id, child in children.items():
        child_models[model_id] = {
            'state': _serialize_child_state(child),
        }
    # Merge into existing constants
    component_cls._constants = {
        **getattr(component_cls, '_constants', {}),
        '_child_models': child_models,
    }
    # Wire up child trait sync and message routing
    self._setup_child_sync(children, component)
```

#### 2.5 Wire up child trait observation

```python
def _setup_child_sync(self, children, component):
    """Watch child widget traits and push updates to JS via ESMEvent."""
    for model_id, child in children.items():
        trait_names = [
            name for name in child.traits(sync=True)
            if name not in _FRAMEWORK_TRAITS
        ]

        def _on_child_change(change, _mid=model_id, _child=child):
            name = change['name']
            value = _serialize_trait(_child, name, change['new'])
            component._send_msg({
                '_child_state_update': {
                    'model_id': _mid, 'key': name, 'value': value
                }
            })

        child.observe(_on_child_change, names=trait_names)
        self._trait_watchers.append(('traitlet', child, _on_child_change, trait_names))
```

#### 2.6 Wire up child custom message routing

For HiGlass's tileset client and similar message-passing patterns:

```python
def _setup_child_msg_routing(self, children, component):
    """Bridge custom messages between JS child models and Python child widgets."""

    # JS child → Python child: demultiplex by _child_model_id
    def _on_child_msg(event):
        data = getattr(event, 'data', event)
        if not isinstance(data, dict):
            return
        child_id = data.get('_child_model_id')
        if not child_id:
            return
        child = children.get(child_id)
        if not child or not hasattr(child, '_handle_custom_msg'):
            return
        # Decode base64 buffers
        buffers = []
        if '_b64_buffers' in data:
            import base64
            for b64 in data['_b64_buffers']:
                buffers.append(base64.b64decode(b64))
            data = {k: v for k, v in data.items() if k not in ('_b64_buffers', '_child_model_id')}
        else:
            data = {k: v for k, v in data.items() if k != '_child_model_id'}
        child._handle_custom_msg(data, buffers)

    component.on_msg(_on_child_msg)

    # Python child → JS child: override send() on each child widget
    for model_id, child in children.items():
        original_send = getattr(child, 'send', None)

        def _child_send(content, buffers=None, _mid=model_id):
            msg = {'_child_msg_custom': {'model_id': _mid, 'content': content}}
            if buffers:
                import base64
                encoded = []
                for buf in buffers:
                    if isinstance(buf, memoryview):
                        buf = bytes(buf)
                    encoded.append(base64.b64encode(buf).decode('ascii'))
                msg['_child_msg_custom']['_b64_buffers'] = encoded
            component._send_msg(msg)

        child.send = _child_send
        self._trait_watchers.append(('child_send', child, original_send))
```

#### 2.7 Update `_teardown_trait_sync()` to clean up child state

```python
# In _teardown_trait_sync, also handle 'child_send' entries:
if entry[0] == 'child_send':
    _, child, original_send = entry
    if original_send:
        child.send = original_send
```

### Phase 3: TypeScript — ESMEvent Routing for Child Models

**File: `panel/models/anywidget_component.ts`** (~40 new lines)

In `AnyWidgetComponentView`, handle child-related ESMEvents:

```typescript
// In the view's event handler (connected during initialize):
_handle_child_event(data: any): boolean {
  // Child state update from Python
  if (data._child_state_update) {
    const { model_id, key, value } = data._child_state_update
    const entry = MODEL_REGISTRY._entries.get(model_id)
    if (entry?.deferred.status === "resolved" && entry.deferred.value) {
      entry.deferred.value._update_state(key, value)
    }
    return true
  }
  // Child custom message from Python
  if (data._child_msg_custom) {
    const { model_id, content, _b64_buffers } = data._child_msg_custom
    const entry = MODEL_REGISTRY._entries.get(model_id)
    if (entry?.deferred.status === "resolved" && entry.deferred.value) {
      let buffers: DataView[] = []
      if (_b64_buffers) {
        buffers = _b64_buffers.map((b64: string) => {
          const binary = atob(b64)
          const bytes = new Uint8Array(binary.length)
          for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
          return new DataView(bytes.buffer)
        })
      }
      entry.deferred.value._emit("msg:custom", content, buffers)
    }
    return true
  }
  return false
}
```

### Phase 4: Update _render_code for Child Message Routing

In `_render_code()`, connect child message event routing so that ESMEvents from Python can reach child models. The existing `on_event` handler on the view needs to check for child-related messages.

### Phase 5: Testing

#### 5.1 Unit tests (`panel/tests/pane/test_anywidget.py`)

- Test `_collect_child_widgets()` with mock compound widgets
- Test `_serialize_child_state()` for various trait types
- Test child model constants are correctly populated
- Test child trait observation fires updates
- Test child custom message routing (both directions)
- Test recursive child discovery (grandchildren)
- Test cleanup/teardown

#### 5.2 Integration tests (lonboard example)

```python
# research/anywidget/examples/ext_lonboard.py
import lonboard
import geopandas as gpd
# ... create map with ScatterplotLayer ...
pn.pane.AnyWidget(m, height=600).servable()
```

#### 5.3 Integration tests (higlass example)

```python
# research/anywidget/examples/ext_higlass.py
import higlass as hg
# ... create HiGlassWidget with tilesets ...
pn.pane.AnyWidget(widget, height=600).servable()
```

#### 5.4 Playwright UI tests

- test_lonboard.py: Renders, layers visible, bidirectional sync
- test_higlass.py: Renders, tileset data loads, genomic tracks visible

#### 5.5 Regression

- Verify all 82 existing unit tests pass
- Verify leaf widget examples still work (sample of 5-10)

## Key Design Decisions

### 1. Global ModelRegistry vs Per-Widget

**Decision: Global (page-scoped)**

Like marimo's `MODEL_MANAGER`, a single global registry per page. Model IDs are ipywidgets UUIDs, which are globally unique within a session. If Panel serves multiple sessions, each has its own page/JS context.

### 2. Initial State via esm_constants vs Dynamic Properties

**Decision: esm_constants for initial state, ESMEvent for updates**

`esm_constants` is the simplest mechanism for one-time delivery of child state. Ongoing updates use the existing ESMEvent channel (message-based). No new Bokeh property types needed.

### 3. Backbone.js context parameter in on()

**Decision: Support via Function.prototype.bind()**

Lonboard's TS code passes a context parameter to `model.on("change:x", callback, this)`. The ChildModelAdapter binds the callback to the context. This is a minor addition but critical for lonboard compatibility.

### 4. Child save_changes() routing

**Decision: Route through parent DataEvent**

When JS child adapters call `save_changes()`, the changes are sent as a DataEvent message tagged with the child model_id. Python demultiplexes and applies to the correct child widget.

### 5. Binary data handling

**Decision: Reuse existing base64 pipeline**

No new binary transport needed. Lonboard's Parquet bytes → base64 → JSON → WebSocket → atob() → DataView. The ChildModelAdapter's `get()` calls `_decode_binary()` to restore DataView objects.

## File Changes Summary

| File | Lines Added | Description |
|------|-------------|-------------|
| `panel/models/anywidget_component.ts` | ~200 | Deferred, ModelRegistry, ChildModelAdapter, child event routing |
| `panel/pane/anywidget.py` | ~150 | Child detection, serialization, sync, message routing |
| `panel/tests/pane/test_anywidget.py` | ~100 | Unit tests for compound widget support |
| `panel/tests/ui/anywidget/test_lonboard.py` | ~60 | Playwright tests for lonboard |
| `panel/tests/ui/anywidget/test_higlass.py` | ~60 | Playwright tests for higlass |
| `research/anywidget/examples/ext_lonboard.py` | ~50 | Updated lonboard example |
| `research/anywidget/examples/ext_higlass.py` | ~50 | Updated higlass example |

**Total: ~670 new/modified lines**

## Risks and Mitigations

1. **Large Parquet data through esm_constants**: Base64 encoding inflates size by ~33%. For multi-MB datasets, this could be slow. Mitigation: Works for typical datasets; optimize with streaming/chunked transfer later if needed.

2. **Timing — child models must be registered before parent's render()**: If `render()` calls `widget_manager.get_model()` before `initialize()` registers child models, it would hang (Deferred pattern handles this — the Promise resolves when the model is later registered). But we register in `initialize()` which runs before `render()`, so this should be fine.

3. **Recursive depth**: Lonboard layers → extensions is 2 levels. Deeply nested widget trees could be slow to serialize. Mitigation: Add depth limit (e.g., 5 levels).

4. **Leaf widget regression**: Adding child model logic could interfere with existing leaf widgets. Mitigation: Child model code only activates when `widget_serialization` traits are detected. Leaf widgets have no such traits.

## Implementation Order

1. TypeScript: Deferred + ModelRegistry + ChildModelAdapter (testable independently)
2. TypeScript: Update widget_manager stub → use registry
3. Python: `_collect_child_widgets()` + `_serialize_child_state()`
4. Python: Update `_create_component()` to populate `_child_models` in constants
5. TypeScript: Initialize child models in `AnyWidgetComponentView.initialize()`
6. Python: `_setup_child_sync()` — trait observation
7. TypeScript: Handle `_child_state_update` ESMEvents
8. Python: `_setup_child_msg_routing()` — custom messages
9. TypeScript: Handle `_child_msg_custom` and child `send()` routing
10. Test with lonboard (data-container children)
11. Test with higlass (message-only children)
12. Run full regression suite
