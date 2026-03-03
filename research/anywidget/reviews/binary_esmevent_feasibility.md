# Binary ESMEvent Channel: Feasibility Assessment

## Current State

The AnyWidget pane uses **base64 encoding** for all binary data transfer:
- Python-to-JS property sync: `memoryview` → `{'_pnl_bytes': base64_string}` in `_deep_serialize()`
- Python-to-JS messages: buffers base64-encoded under `_b64_buffers` key in `_send_override()`
- JS-to-Python messages: base64-encoded in TS `send()`, decoded in `_on_component_msg()`

## Bokeh's Existing Binary Infrastructure

Bokeh already has native binary WebSocket frame support:
- `Serializer(deferred=True)` extracts `bytes`/`memoryview` as `Buffer` objects
- Buffers sent as raw binary WebSocket frames (not base64)
- PATCH-DOC messages include `num_buffers` header and buffer_header/payload pairs
- ~33% transfer size reduction and significant CPU savings for large buffers

## Why Binary Is Not Working Today

Panel pre-encodes everything to base64 **before** the data reaches Bokeh's serializer, preventing Bokeh from ever seeing raw bytes.

## Recommended Phases

### Phase 1: Property-level binary transfer (LOW effort, HIGH impact)
- Stop pre-encoding `memoryview`/`bytes` as `_pnl_bytes` in `_deep_serialize()`
- Let Bokeh's serializer handle `bytes` natively via `bp.Bytes` properties
- **No Bokeh changes required**

### Phase 2: Python-to-JS message binary transfer (MEDIUM effort)
- Keep binary buffers as `bytes` in ESMEvent message dict
- Verify `MessageSentEvent.to_serializable()` extracts buffer references
- Verify BokehJS reconstitutes buffers in `MessageSent.msg_data`

### Phase 3: JS-to-Python message binary transfer (HIGH effort)
- Modify `DataEvent` serialization in TypeScript
- BokehJS Serializer needs to handle `ArrayBuffer` in generic event data
- May require upstream Bokeh changes

## Key Files

| File | Phase | Change |
|------|-------|--------|
| `panel/pane/anywidget.py` (`_deep_serialize`, `_send_override`) | 1, 2 | Remove base64 encoding |
| `panel/models/anywidget_component.ts` (`_decode_binary`, `send`) | 1, 2, 3 | Handle Bokeh's native BytesRep |
| `panel/models/esm.py` (`DataEvent`) | 2 | Buffer-aware serialization |
| `panel/models/reactive_esm.ts` (`DataEvent`) | 3 | Binary buffer extraction |

## Performance Impact

For 10 MB Arrow IPC buffer:
- **Current**: ~13.3 MB base64 + CPU encoding/decoding
- **Binary**: 10 MB raw + ~100 bytes header. Zero encoding overhead.
