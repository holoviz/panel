# AnyWidget Protocol Comparison: Native vs Panel Implementation

**Research date:** 2026-03-02
**Source repositories:** `/workspaces/anywidget` (native), `/workspaces/panel` (Panel)

## Executive Summary

Panel's `AnyWidgetComponent` / `AnyWidget` pane implements the anywidget model protocol with high fidelity. Most features work correctly. There are a few gaps in protocol conformance and one intentional deviation around the `change:` callback argument ordering.

## Feature Parity Matrix

| Feature | Native anywidget | Panel | Status |
|---|---|---|---|
| `model.get(name)` | Backbone Model.get | Bokeh attribute lookup + type coercion | DONE |
| `model.set(name, value)` | Backbone Model.set | Deferred to `save_changes()` batch | DONE |
| `model.save_changes()` | Backbone sync to Python | Bokeh setv() | DONE |
| `model.send(content, cb?, buffers?)` | 3-arg: comm.send() | 3-arg: DataEvent + b64 encoding | FIXED |
| `model.on("change:x", cb)` | 2-arg: `(context, value)` | 1-arg: `(value)` only | INTENTIONAL |
| `model.on("change", cb)` | Generic change event | Generic change event | FIXED |
| `model.on("msg:custom", cb)` | 2-arg: `(msg, DataView[])` | 2-arg: decoded from b64 | DONE |
| `model.off(event, cb)` | Backbone off, w/ wrapped cb | Bokeh disconnect | DONE |
| `model.off(null)` | Backbone bulk cleanup | Clears all listeners | FIXED |
| `model.widget_manager` | DOMWidgetModel.widget_manager | Stub with warning | FIXED |
| `experimental.invoke(name, msg)` | Full RPC via msg:custom | Full RPC implementation | FIXED |
| Trait→param type mapping | N/A (JS only) | Comprehensive TRAITLET_MAP | DONE |
| Trait name collision handling | N/A | `w_` prefix + `_trait_name_map` | DONE |
| Bokeh reserved name collision | N/A | `_BOKEH_RESERVED` frozenset (69 names) | FIXED |
| Bytes/ArrayBuffer traits | Native binary channel | Bokeh bp.Bytes + DataView | DONE |
| `msg:custom` binary buffers | Native binary | Base64 encode/decode round-trip | DONE |
| `_esm` file watching / HMR | watchfiles thread + solid-js | Read-once (intentional) | BY DESIGN |
| `_css` scoped loading | `<style id=_anywidget_id>` | `_stylesheets` param | DONE |
| Widget state embed/snapshot | `AnyModel.serialize()` + structuredClone | Not applicable | BY DESIGN |

## Key Protocol Details

### `change:` Callback Argument Ordering

The official anywidget/Backbone protocol calls callbacks as `cb(context, value)` with two arguments. Panel intentionally passes `cb(value)` with one argument, putting the value as the first arg.

**Rationale**: In practice, the vast majority of real widgets use either:
- The 0-arg form: `model.on("change:value", () => { model.get("value"); })`
- The 1-arg form: `model.on("change:_params", (new_params) => { Object.entries(new_params); })` (Altair)

Both patterns work correctly with Panel's 1-arg convention. The 2-arg form `(_, value)` would receive `value = undefined` with Panel, but no widely-used widget relies on this.

### `send()` Signature

Native: `send(content: any, callbacks?: any, buffers?: ArrayBuffer[] | ArrayBufferView[])`
Panel: `send(data: any, _callbacks_or_options?: any, _buffers?: any[])`

Panel accepts both:
1. Native 3-positional: `send(content, undefined, buffers)` — used by `@anywidget/signals`
2. Options-style: `send(data, {buffers: [...]})` — legacy/alternative

### Binary Data Transfer

Panel uses base64 encoding for `msg:custom` binary data because Bokeh's DataEvent only supports JSON. This adds ~33% overhead but is functionally correct.

For trait-level binary data (`traitlets.Bytes`), Bokeh's native `bp.Bytes` property handles binary serialization directly — no base64 overhead.

### `experimental.invoke()` RPC

Panel implements the full invoke protocol:
1. JS sends: `{id, kind: "anywidget-command", name, msg}` via `send()`
2. Python receives via `_handle_custom_msg` (dispatched by anywidget's `@command` decorator)
3. Python responds via `widget.send({id, kind: "anywidget-command-response", response})`
4. JS resolves the Promise when matching response arrives

Supports `AbortSignal` for cancellation and binary buffers in both directions.

## Remaining Gaps

### Low Priority

1. **No content-hash ESM deduplication** — Marimo deduplicates ESM imports by content hash. Panel caches by widget class (which is sufficient for most use cases).

2. **No `echo_update` handling** — Multi-client sync messages may need special handling in future.

3. **No `_repr_mimebundle_()` sync** — Plotly `FigureWidget` may show stale data (edge case).

### By Design (Not Planned)

1. **No HMR support** — Panel doesn't support hot module reload. Development reloading uses `--autoreload`.

2. **No widget state embed/snapshot** — Panel uses its own document model, not Jupyter's widget state protocol.

3. **Full `widget_manager`** — Panel provides a stub. Full implementation would require exposing Panel's internal component registry, which is architecturally different from Jupyter's widget manager.
