import type * as p from "@bokehjs/core/properties"
import type {Transform} from "sucrase"

import {DataEvent, ReactiveESM, ReactiveESMView} from "./reactive_esm"

// ---------------------------------------------------------------------------
// AnyWidgetModelAdapter / AnyWidgetAdapter
// ---------------------------------------------------------------------------
// These classes implement the **anywidget model protocol** that ESM widget
// code expects.  The protocol requires: get, set, save_changes, send, on, off.
//
// Two key differences from the base ReactiveESM model_proxy:
//
// 1. **Callback wrapping (on/off)** — Bokeh's Signal0.emit() passes
//    `undefined` as the first argument to callbacks (confirmed in
//    bokeh/core/signaling: Signal0.emit → super.emit(undefined)).
//    The anywidget protocol specifies that change callbacks receive the
//    *new value*.  We wrap every "change:" callback to fetch the current
//    value via get() and pass it explicitly.  Without this, widgets like
//    **Altair JupyterChart** crash because their callbacks destructure
//    the argument (e.g. `Object.entries(new_params)` on undefined).
//
// 2. **Trait name translation** — When a traitlet name collides with
//    Panel's Layoutable params (e.g. `height`, `width`), the Python side
//    renames the param (e.g. `height` → `w_height`).  The ESM code still
//    uses the original traitlet name, so the adapter translates between
//    them using `_trait_name_map` (sent via esm_constants).  Affects
//    widgets like **vizarr**, **Vitessce**, and **ipyaladin**.
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Deferred<T> — Promise with exposed resolve/reject
// ---------------------------------------------------------------------------

export class Deferred<T> {
  promise: Promise<T>
  resolve!: (value: T) => void
  reject!: (reason?: any) => void

  constructor() {
    this.promise = new Promise<T>((resolve, reject) => {
      this.resolve = resolve
      this.reject = reject
    })
  }
}

// ---------------------------------------------------------------------------
// ModelRegistry — page-scoped registry for child widget models
// ---------------------------------------------------------------------------
// Enables get_model(id) to be called before or after child model registration.
// If get_model is called first, a pending Deferred is created and resolved
// when register() is called later.

export class ModelRegistry {
  private _deferreds: Map<string, Deferred<any>> = new Map()
  private _resolved: Map<string, any> = new Map()

  get(id: string): Promise<any> {
    const existing = this._resolved.get(id)
    if (existing) {
      return Promise.resolve(existing)
    }
    let deferred = this._deferreds.get(id)
    if (!deferred) {
      deferred = new Deferred<any>()
      this._deferreds.set(id, deferred)
      // Timeout after 10 seconds to avoid hanging indefinitely
      setTimeout(() => {
        if (!this._resolved.has(id)) {
          deferred!.reject(new Error(`[Panel AnyWidget] get_model('${id}') timed out after 10s`))
          this._deferreds.delete(id)
        }
      }, 10000)
    }
    return deferred.promise
  }

  register(id: string, adapter: any): void {
    this._resolved.set(id, adapter)
    const deferred = this._deferreds.get(id)
    if (deferred) {
      deferred.resolve(adapter)
      this._deferreds.delete(id)
    }
  }

  delete(id: string): void {
    this._resolved.delete(id)
    this._deferreds.delete(id)
  }

  get_resolved(id: string): any | null {
    return this._resolved.get(id) || null
  }
}

export const MODEL_REGISTRY = new ModelRegistry()

// ---------------------------------------------------------------------------
// ChildModelAdapter — lightweight model for child widgets
// ---------------------------------------------------------------------------
// Implements the anywidget/ipywidgets model interface for child widgets
// referenced via IPY_MODEL_ strings in compound widgets (lonboard, higlass).

export class ChildModelAdapter {
  model_id: string
  private _state: Record<string, any>
  private _parent: AnyWidgetModelAdapter
  private _listeners: Map<string, Array<{cb: (...args: any[]) => void, context?: any}>>
  private _dirty: Set<string>
  // Cached widget_manager object — must be stable (same reference) across accesses
  // because React hooks use it in useEffect dependency arrays with Object.is comparison.
  widget_manager: {get_model: (model_id: string) => Promise<any>}

  constructor(model_id: string, state: Record<string, any>, parent: AnyWidgetModelAdapter) {
    this.model_id = model_id
    this._state = {...state}
    this._parent = parent
    this._listeners = new Map()
    this._dirty = new Set()
    this.widget_manager = {
      get_model: (mid: string) => MODEL_REGISTRY.get(mid),
    }
  }

  get(name: string): any {
    let value = this._state[name]
    value = this._parent._decode_binary(value)
    return value
  }

  set(name: string, value: any): void {
    this._state[name] = value
    this._dirty.add(name)
  }

  save_changes(): void {
    if (this._dirty.size === 0) { return }
    const changes: Record<string, any> = {}
    for (const key of this._dirty) {
      let value = this._state[key]
      // Convert DataView/TypedArray back to ArrayBuffer for transport
      if (value instanceof DataView) {
        value = value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength)
      } else if (ArrayBuffer.isView(value) && !(value instanceof DataView)) {
        value = value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength)
      }
      changes[key] = value
    }
    this._dirty.clear()
    // Route through parent's DataEvent
    this._parent.model.trigger_event(new DataEvent({
      _child_save_changes: {model_id: this.model_id, changes},
    }))
  }

  on(event: string, cb: (...args: any[]) => void, context?: any): void {
    let listeners = this._listeners.get(event)
    if (!listeners) {
      listeners = []
      this._listeners.set(event, listeners)
    }
    listeners.push({cb, context})
  }

  off(event?: string | null, cb?: ((...args: any[]) => void) | null): void {
    if (!event) {
      this._listeners.clear()
      return
    }
    if (!cb) {
      this._listeners.delete(event)
      return
    }
    const listeners = this._listeners.get(event)
    if (listeners) {
      const filtered = listeners.filter(entry => entry.cb !== cb)
      if (filtered.length > 0) {
        this._listeners.set(event, filtered)
      } else {
        this._listeners.delete(event)
      }
    }
  }

  send(data: any, _callbacks?: any, buffers?: any[]): void {
    // Base64-encode binary buffers for JSON transport
    let payload: any = data
    if (buffers && buffers.length > 0) {
      const encoded: string[] = []
      for (const buf of buffers) {
        let bytes: Uint8Array
        if (buf instanceof ArrayBuffer) {
          bytes = new Uint8Array(buf)
        } else if (buf instanceof DataView) {
          bytes = new Uint8Array(buf.buffer, buf.byteOffset, buf.byteLength)
        } else if (buf instanceof Uint8Array) {
          bytes = buf
        } else if (ArrayBuffer.isView(buf)) {
          bytes = new Uint8Array(buf.buffer, buf.byteOffset, buf.byteLength)
        } else {
          bytes = new Uint8Array(buf as ArrayBuffer)
        }
        let binary = ""
        for (let i = 0; i < bytes.length; i++) {
          binary += String.fromCharCode(bytes[i])
        }
        encoded.push(btoa(binary))
      }
      if (typeof data === "object" && data !== null) {
        payload = {...data, _b64_buffers: encoded}
      } else {
        payload = {_data: data, _b64_buffers: encoded}
      }
    }
    // Route through parent DataEvent with child model ID
    this._parent.model.trigger_event(new DataEvent({
      _child_model_id: this.model_id,
      ...((typeof payload === "object" && payload !== null) ? payload : {_data: payload}),
    }))
  }

  // Called by event routing when Python sends a state update for this child
  _update_state(key: string, value: any): void {
    this._state[key] = value
    // Fire change:key listeners
    const specific = this._listeners.get(`change:${key}`)
    if (specific) {
      const decoded = this.get(key)  // decode binary if needed
      for (const {cb, context} of specific) {
        try { cb.call(context, decoded) } catch (e) { console.error("Error in child change callback:", e) }
      }
    }
    // Fire generic "change" listeners
    const generic = this._listeners.get("change")
    if (generic) {
      for (const {cb, context} of generic) {
        try { cb.call(context) } catch (e) { console.error("Error in child generic change callback:", e) }
      }
    }
  }

  // Called by event routing when Python sends a custom message for this child
  _emit_custom_msg(content: any, buffers: DataView[]): void {
    const listeners = this._listeners.get("msg:custom")
    if (listeners) {
      for (const {cb, context} of listeners) {
        try { cb.call(context, content, buffers) } catch (e) { console.error("Error in child msg:custom callback:", e) }
      }
    }
  }
}

export class AnyWidgetModelAdapter {
  declare model: AnyWidgetComponent
  declare model_changes: any
  declare data_changes: any
  declare view: AnyWidgetComponentView | null
  // Maps original callbacks to their wrapped versions for "change:" events.
  // Needed so off() can unregister the *wrapped* version that on() actually
  // connected to Bokeh's signal system.
  _cb_map: Map<any, any>
  // Generic "change" event listeners (fire on ANY property change)
  _generic_change_cbs: Set<(...args: any[]) => void>
  // Per-callback watchers for generic "change" — needed for cleanup in off()
  _generic_change_watchers: Map<(...args: any[]) => void, Array<{prop: string, wrapped: () => void}>>
  // Cached name maps (built lazily from esm_constants._trait_name_map)
  _cached_trait_name_map: Record<string, string> | null
  _cached_param_name_map: Record<string, string> | null
  // Cached widget_manager object — must be stable (same reference) across accesses
  // because React hooks use it in useEffect dependency arrays with Object.is comparison.
  widget_manager: {get_model: (model_id: string) => Promise<any>}
  // Cached widget_serialization values — must return the SAME reference for the
  // same trait on repeated get() calls.  React's useSyncExternalStore compares
  // getSnapshot() results with Object.is; returning a new array/object each time
  // triggers an infinite re-render loop (e.g. lonboard controls/layers).
  _cached_ws_values: Record<string, any>

  constructor(model: AnyWidgetComponent) {
    this.view = null
    this.model = model
    this.model_changes = {}
    this.data_changes = {}
    this._cb_map = new Map()
    this._generic_change_cbs = new Set()
    this._generic_change_watchers = new Map()
    this._cached_trait_name_map = null
    this._cached_param_name_map = null
    this._cached_ws_values = {}
    this.widget_manager = {
      get_model: (model_id: string) => MODEL_REGISTRY.get(model_id),
    }
  }

  // ---- Trait ↔ param name translation ------------------------------------
  // The Python side builds a mapping from traitlet names to Bokeh param
  // names and ships it as esm_constants._trait_name_map.  For example,
  // if a widget has a `height` traitlet that collides with Layoutable's
  // `height`, the map contains {"height": "w_height"}.

  // traitlet name → param name  (e.g. "height" → "w_height")
  get _trait_name_map(): Record<string, string> {
    let result = this._cached_trait_name_map
    if (result === null) {
      const constants = this.model.data?.attributes?.esm_constants
      result = (constants && constants._trait_name_map) ? constants._trait_name_map as Record<string, string> : {}
      this._cached_trait_name_map = result
    }
    return result
  }

  // param name → traitlet name  (e.g. "w_height" → "height")
  get _param_name_map(): Record<string, string> {
    let result = this._cached_param_name_map
    if (result === null) {
      result = {}
      for (const [trait, param] of Object.entries(this._trait_name_map)) {
        result[param] = trait
      }
      this._cached_param_name_map = result
    }
    return result
  }

  _to_param_name(trait_name: string): string {
    return this._trait_name_map[trait_name] || trait_name
  }

  _to_trait_name(param_name: string): string {
    return this._param_name_map[param_name] || param_name
  }

  // ---- anywidget model protocol ------------------------------------------

  get(name: any) {
    const param_name = this._to_param_name(name)
    let value
    const propPath = param_name.split(".")
    let targetModel: any = this.model.data

    for (let i = 0; i < propPath.length - 1; i++) {
      if (targetModel && targetModel.attributes && propPath[i] in targetModel.attributes) {
        targetModel = targetModel.attributes[propPath[i]]
      } else {
        targetModel = null
        break
      }
    }

    if (targetModel && targetModel.attributes && propPath[propPath.length - 1] in targetModel.attributes) {
      value = targetModel.attributes[propPath[propPath.length - 1]]
    } else {
      value = this.model.attributes[param_name]
    }

    // For widget_serialization traits (compound widgets like lonboard, higlass),
    // the values are stored as "IPY_MODEL_<id>" strings in esm_constants.
    // Return them as-is — the widget's own JS code will parse the strings
    // (e.g. value.slice("IPY_MODEL_".length)) and call widget_manager.get_model()
    // to resolve child models.
    //
    // CRITICAL: Return the SAME cached reference on repeated calls.  Lonboard
    // uses React's useSyncExternalStore whose getSnapshot() compares with
    // Object.is.  A new array/object reference would trigger an infinite
    // re-render → useEffect → get() → new reference → re-render loop.
    if (value === undefined || value === null) {
      const constants = this.model.data?.attributes?.esm_constants
      if (constants && constants._widget_serialization_values) {
        const raw = constants._widget_serialization_values[name]
        if (raw !== undefined) {
          if (!(name in this._cached_ws_values)) {
            this._cached_ws_values[name] = raw
          }
          return this._cached_ws_values[name]
        }
      }
    }

    if (value instanceof ArrayBuffer) {
      value = new DataView(value)
    }

    // Decode base64-encoded binary data produced by Python's _serialize_trait.
    // Traits that use ipywidgets binary serialization (e.g. jupyter-scatter's
    // array_to_binary) produce {view: memoryview, dtype, shape} on the Python
    // side.  Panel base64-encodes memoryview values as {_pnl_bytes: string}.
    // Here we decode them back to DataView so ESM deserializers work correctly.
    value = this._decode_binary(value)

    return value
  }

  // Recursively decode {_pnl_bytes: base64_string} markers into DataView objects.
  _decode_binary(value: any): any {
    if (value === null || value === undefined || typeof value !== "object") {
      return value
    }
    // DataView and ArrayBuffer instances are already decoded binary data
    // (e.g. from the ArrayBuffer → DataView conversion in get()).
    // Passing them through Object.entries() would destroy them — DataView
    // has no enumerable own properties, so it would become {}.
    if (value instanceof DataView || value instanceof ArrayBuffer) {
      return value
    }
    if ("_pnl_bytes" in value && typeof value._pnl_bytes === "string") {
      const binary = atob(value._pnl_bytes)
      const bytes = new Uint8Array(binary.length)
      for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i)
      }
      return new DataView(bytes.buffer)
    }
    // IMPORTANT: Preserve reference identity when no decoding is needed.
    // React's useSyncExternalStore compares getSnapshot() results with
    // Object.is — a new array/object reference triggers infinite re-renders
    // (e.g. lonboard selected_bounds after bbox selection).
    if (Array.isArray(value)) {
      let changed = false
      const mapped = value.map((v: any) => {
        const decoded = this._decode_binary(v)
        if (decoded !== v) { changed = true }
        return decoded
      })
      return changed ? mapped : value
    }
    let changed = false
    const result: Record<string, any> = {}
    for (const [k, v] of Object.entries(value)) {
      const decoded = this._decode_binary(v)
      result[k] = decoded
      if (decoded !== v) { changed = true }
    }
    return changed ? result : value
  }

  set(name: string, value: any) {
    const param_name = this._to_param_name(name)
    // Skip undefined values — Bokeh's serializer cannot handle them.
    // Some ESM widgets (e.g. Vitessce) set traits to undefined during
    // internal state updates.  undefined has no JSON representation;
    // if the widget intends to clear a value it should use null.
    if (value === undefined) {
      return
    }
    // Convert DataView/TypedArray back to ArrayBuffer for Bokeh's bp.Bytes
    if (value instanceof DataView) {
      value = value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength)
    } else if (ArrayBuffer.isView(value) && !(value instanceof DataView)) {
      // TypedArray (Uint8Array, etc.)
      value = value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength)
    }
    if (param_name.split(".")[0] in this.model.data.attributes) {
      this.data_changes = {...this.data_changes, [param_name]: value}
    } else if (param_name in this.model.attributes) {
      this.model_changes = {...this.model_changes, [param_name]: value}
    }
  }

  save_changes() {
    this.model.setv(this.model_changes)
    this.model_changes = {}
    for (const key in this.data_changes) {
      const propPath = key.split(".")
      let targetModel: any = this.model.data
      for (let i = 0; i < propPath.length - 1; i++) {
        if (targetModel && targetModel.attributes && propPath[i] in targetModel.attributes) {
          targetModel = targetModel.attributes[propPath[i]]
        } else {
          console.warn(`Skipping '${key}': '${propPath[i]}' does not exist.`)
          targetModel = null
          break
        }
      }
      if (targetModel && targetModel.attributes && propPath[propPath.length - 1] in targetModel.attributes) {
        targetModel.setv({[propPath[propPath.length - 1]]: this.data_changes[key]})
      } else {
        console.warn(`Skipping '${key}': Final property '${propPath[propPath.length - 1]}' not found.`)
      }
    }
    this.data_changes = {}
  }

  // send() is part of the anywidget protocol — used by widgets like
  // **Mosaic** to send query messages to the Python backend.
  // When binary buffers are provided (e.g. Arrow IPC data), they are
  // base64-encoded into the JSON message under `_b64_buffers` for
  // transport via Panel's DataEvent (which only supports JSON).
  // The Python side decodes them in _on_component_msg().
  //
  // Supports TWO calling conventions:
  //   1. Native anywidget: send(content, callbacks?, buffers?)
  //      Used by @anywidget/signals invoke(), which calls
  //      model.send(content, undefined, buffers) with 3 positional args.
  //   2. Legacy: send(data, {buffers: [...]})
  //      Used by some widgets that pass buffers in an options object.
  send(data: any, _callbacks_or_options?: any, _buffers?: any[]) {
    // Normalize: extract buffers from either calling convention
    let buffers: any[] | undefined = _buffers
    if (!buffers && _callbacks_or_options && _callbacks_or_options.buffers) {
      buffers = _callbacks_or_options.buffers
    }
    if (buffers && buffers.length > 0) {
      const encoded: string[] = []
      for (const buf of buffers) {
        let bytes: Uint8Array
        if (buf instanceof ArrayBuffer) {
          bytes = new Uint8Array(buf)
        } else if (buf instanceof DataView) {
          bytes = new Uint8Array(buf.buffer, buf.byteOffset, buf.byteLength)
        } else if (buf instanceof Uint8Array) {
          bytes = buf
        } else if (ArrayBuffer.isView(buf)) {
          // Other TypedArrays (Int32Array, Float64Array, etc.)
          bytes = new Uint8Array(buf.buffer, buf.byteOffset, buf.byteLength)
        } else {
          bytes = new Uint8Array(buf as ArrayBuffer)
        }
        let binary = ""
        for (let i = 0; i < bytes.length; i++) {
          binary += String.fromCharCode(bytes[i])
        }
        encoded.push(btoa(binary))
      }
      if (typeof data === "object" && data !== null) {
        data = {...data, _b64_buffers: encoded}
      } else {
        data = {_data: data, _b64_buffers: encoded}
      }
    }
    this.model.trigger_event(new DataEvent(data))
  }

  on(event: string, cb: (...args: any[]) => void) {
    if (event === "change") {
      // Generic "change" event — fires when ANY property changes.
      // Some widgets (e.g. those using @anywidget/signals) rely on this.
      //
      // We register Bokeh watchers on every data attribute so the callback
      // fires regardless of whether any specific "change:<trait>" listener
      // exists.  Without this, generic change callbacks would only fire as
      // a side-effect of specific change:x wrappers.
      this._generic_change_cbs.add(cb)
      const data_attrs = this.model.data?.attributes || {}
      const watchers: Array<{prop: string, wrapped: () => void}> = []
      for (const prop of Object.keys(data_attrs)) {
        if (prop === "esm_constants") {
          continue
        }
        const wrapped = () => {
          try { cb() } catch (e) { console.error("Error in generic change callback:", e) }
        }
        this.model.watch(this.view, prop, wrapped)
        watchers.push({prop, wrapped})
      }
      this._generic_change_watchers.set(cb, watchers)
    } else if (event.startsWith("change:")) {
      const trait_name = event.slice("change:".length)
      const prop = this._to_param_name(trait_name)
      // Wrap the callback to explicitly fetch and pass the current value.
      //
      // Why this is necessary:
      //   Bokeh's Signal0.emit() calls `super.emit(undefined)`, so the raw
      //   callback would receive `undefined` as its first argument.  The
      //   anywidget protocol requires the *new value* to be passed.
      //
      // Without this wrapping, **Altair JupyterChart** crashes on its
      // `change:_params` callback (it does `Object.entries(new_params)`
      // where new_params is undefined), and **Altair** selection sync
      // via `change:_vl_selections` also breaks.
      const wrapped = () => {
        // Use the original trait_name for get() (not the translated prop)
        // because get() internally calls _to_param_name().
        const value = this.get(trait_name)
        if (value !== undefined) {
          cb(value)
        }
      }
      this._cb_map.set(cb, wrapped)
      this.model.watch(this.view, prop, wrapped)
    } else if (event === "msg:custom") {
      // The anywidget protocol specifies that "msg:custom" callbacks
      // receive two arguments: (msg, buffers) where buffers is a
      // DataView[].  Panel's ESMEvent carries JSON only — no native
      // binary channel.
      //
      // To support widgets like **Mosaic** that send binary data
      // (Arrow IPC query results), the Python side base64-encodes
      // buffers into `msg._b64_buffers`.  We decode them here back
      // into DataView objects before calling the ESM callback.
      //
      // Without buffer support, **Mosaic** crashes with:
      //   "Cannot read properties of undefined (reading '0')"
      // because it accesses buffers[0] to read Arrow IPC data.
      const wrapped = (data: any) => {
        // Skip child-directed messages to prevent them leaking to the
        // parent ESM's msg:custom handler.  These are routed to child
        // models separately via the view's event routing.
        if (data && (data._child_state_update || data._child_msg_custom)) {
          return
        }
        let buffers: DataView[] = []
        if (data && data._b64_buffers) {
          const encoded: string[] = data._b64_buffers
          buffers = encoded.map((b64: string) => {
            const binary = atob(b64)
            const bytes = new Uint8Array(binary.length)
            for (let i = 0; i < binary.length; i++) {
              bytes[i] = binary.charCodeAt(i)
            }
            return new DataView(bytes.buffer)
          })
          // Remove the transport key so the ESM sees a clean message
          const {_b64_buffers, ...clean} = data
          data = clean
        }
        cb(data, buffers)
      }
      this._cb_map.set(cb, wrapped)
      // Try to connect to the view's event system.  The view may be:
      //   1. this.view (set on AnyWidgetAdapter, used during render())
      //   2. this.model._anywidget_view (set during view init, used when
      //      _run_initializer calls ESM initialize() asynchronously after
      //      the view already exists)
      //   3. null (neither exists yet — queue for later)
      const target_view = this.view || this.model._anywidget_view
      if (target_view) {
        target_view.on_event(wrapped)
      } else {
        // No view yet — queue on the model for later flush
        if (!this.model._pending_msg_handlers) {
          this.model._pending_msg_handlers = []
        }
        this.model._pending_msg_handlers.push(wrapped)
      }
    } else {
      console.error(`Event of type '${event}' not recognized.`)
    }
  }

  // ---- experimental.invoke() RPC ------------------------------------------
  // The anywidget protocol provides an `experimental.invoke(name, msg, opts)`
  // RPC pattern.  The JS side sends a request via `model.send()` and listens
  // for a matching response on `msg:custom`.
  //
  // Protocol: JS sends {id, kind: "anywidget-command", name, msg}
  //           Python responds {id, kind: "anywidget-command-response", response}
  //
  // The Python side dispatches to methods decorated with
  // `anywidget.experimental.command`.
  invoke(name: string, msg?: any, options?: {buffers?: any[], signal?: AbortSignal}): Promise<[any, DataView[]]> {
    const id = crypto.randomUUID()
    const buffers = options?.buffers ?? []
    const signal = options?.signal

    return new Promise<[any, DataView[]]>((resolve, reject) => {
      if (signal?.aborted) {
        reject(signal.reason ?? new DOMException("Aborted", "AbortError"))
        return
      }

      const handler = (response_data: any, response_buffers: DataView[]) => {
        if (
          response_data &&
          response_data.id === id &&
          response_data.kind === "anywidget-command-response"
        ) {
          this.off("msg:custom", handler)
          resolve([response_data.response, response_buffers])
        }
      }

      if (signal) {
        signal.addEventListener("abort", () => {
          this.off("msg:custom", handler)
          reject(signal.reason ?? new DOMException("Aborted", "AbortError"))
        }, {once: true})
      }

      this.on("msg:custom", handler)
      this.send(
        {id, kind: "anywidget-command", name, msg},
        undefined,
        buffers,
      )
    })
  }

  // off() supports the full anywidget protocol:
  //   off()              — remove ALL listeners (cleanup)
  //   off("change")      — remove all generic change listeners
  //   off("change", cb)  — remove specific generic change listener
  //   off("change:x")    — remove all listeners for trait x
  //   off("change:x", cb) — remove specific listener for trait x
  //   off("msg:custom")  — remove all custom message listeners
  //   off("msg:custom", cb) — remove specific custom message listener
  off(event?: string | null, cb?: ((...args: any[]) => void) | null) {
    // off() with no args — clear everything
    if (!event) {
      this._generic_change_cbs.clear()
      for (const [, watchers] of this._generic_change_watchers) {
        for (const {prop, wrapped} of watchers) {
          this.model.unwatch(this.view, prop, wrapped)
        }
      }
      this._generic_change_watchers.clear()
      this._cb_map.clear()
      return
    }
    if (event === "change") {
      if (cb) {
        this._generic_change_cbs.delete(cb)
        const watchers = this._generic_change_watchers.get(cb)
        if (watchers) {
          for (const {prop, wrapped} of watchers) {
            this.model.unwatch(this.view, prop, wrapped)
          }
          this._generic_change_watchers.delete(cb)
        }
      } else {
        this._generic_change_cbs.clear()
        for (const [, watchers] of this._generic_change_watchers) {
          for (const {prop, wrapped} of watchers) {
            this.model.unwatch(this.view, prop, wrapped)
          }
        }
        this._generic_change_watchers.clear()
      }
    } else if (event.startsWith("change:")) {
      const trait_name = event.slice("change:".length)
      const prop = this._to_param_name(trait_name)
      if (cb) {
        // Retrieve the wrapped callback that on() registered with Bokeh,
        // falling back to the original in case on() was never called.
        const wrapped = this._cb_map.get(cb) || cb
        this._cb_map.delete(cb)
        this.model.unwatch(this.view, prop, wrapped)
      }
      // If no cb, we'd need to remove all watchers for this prop,
      // but Bokeh's signal system doesn't easily support that.
      // Skip for now — specific cb removal covers the common case.
    } else if (event === "msg:custom" && this.view) {
      if (cb) {
        const wrapped = this._cb_map.get(cb) || cb
        this._cb_map.delete(cb)
        this.view.remove_on_event(wrapped)
      }
    }
  }
}

// AnyWidgetAdapter extends the model adapter with view-specific features
// (get_child for nested Panel components within anywidget layouts).
export class AnyWidgetAdapter extends AnyWidgetModelAdapter {
  declare view: AnyWidgetComponentView

  constructor(view: AnyWidgetComponentView) {
    super(view.model)
    this.view = view
  }

  get_child(name: any): HTMLElement | HTMLElement[] | undefined {
    const child_model = this.model.data[name]
    if (Array.isArray(child_model)) {
      const subchildren = []
      for (const subchild of child_model) {
        const subview = this.view.get_child_view(subchild)
        if (subview) {
          subchildren.push(subview.el)
        }
      }
      return subchildren
    } else {
      return this.view.get_child_view(child_model)?.el
    }
  }

}

export class AnyWidgetComponentView extends ReactiveESMView {
  declare model: AnyWidgetComponent
  adapter: AnyWidgetAdapter
  destroyer: Promise<((props: any) => void) | null>
  // Track child model IDs registered by this view for cleanup
  _child_model_ids: string[] = []

  override initialize(): void {
    super.initialize()
    this.adapter = new AnyWidgetAdapter(this)
    // Store view reference on model so model-level adapters can connect events
    this.model._anywidget_view = this
    // Flush any msg:custom handlers queued before view existed
    if (this.model._pending_msg_handlers) {
      for (const handler of this.model._pending_msg_handlers) {
        this.on_event(handler)
      }
      this.model._pending_msg_handlers = null
    }
    // Initialize child models from esm_constants._child_models
    const constants = this.model.data?.attributes?.esm_constants
    if (constants && constants._child_models) {
      for (const [model_id, info] of Object.entries(constants._child_models as Record<string, any>)) {
        const child = new ChildModelAdapter(model_id, info.state || {}, this.adapter)
        MODEL_REGISTRY.register(model_id, child)
        this._child_model_ids.push(model_id)
      }
    }
  }

  override connect_signals(): void {
    super.connect_signals()
    // Route child-directed ESMEvent messages to the appropriate child model
    this.on_event((data: any) => {
      if (!data || typeof data !== "object") { return }
      // Child state update: {_child_state_update: {model_id, key, value}}
      if (data._child_state_update) {
        const {model_id, key, value} = data._child_state_update
        const child = MODEL_REGISTRY.get_resolved(model_id)
        if (child && child._update_state) {
          child._update_state(key, value)
        }
        return
      }
      // Child custom message: {_child_msg_custom: {model_id, content, _b64_buffers?}}
      if (data._child_msg_custom) {
        const {model_id, content} = data._child_msg_custom
        const child = MODEL_REGISTRY.get_resolved(model_id)
        if (child && child._emit_custom_msg) {
          // Decode base64 buffers if present
          let buffers: DataView[] = []
          if (data._child_msg_custom._b64_buffers) {
            const encoded: string[] = data._child_msg_custom._b64_buffers
            buffers = encoded.map((b64: string) => {
              const binary = atob(b64)
              const bytes = new Uint8Array(binary.length)
              for (let i = 0; i < binary.length; i++) {
                bytes[i] = binary.charCodeAt(i)
              }
              return new DataView(bytes.buffer)
            })
          }
          child._emit_custom_msg(content, buffers)
        }
        return
      }
    })
  }

  override remove(): void {
    // Clean up child models from the registry before removing the view
    for (const id of this._child_model_ids) {
      MODEL_REGISTRY.delete(id)
    }
    this._child_model_ids = []
    super.remove()
    if (this.destroyer) {
      this.destroyer.then((d: any) => d({model: this.adapter, el: this.container}))
    }
  }

  override after_rendered(): void {
    this.render_children()
    this._rendered = true
  }
}

export namespace AnyWidgetComponent {
  export type Attrs = p.AttrsOf<Props>

  export type Props = ReactiveESM.Props
}

export interface AnyWidgetComponent extends AnyWidgetComponent.Attrs {}

export class AnyWidgetComponent extends ReactiveESM {
  declare properties: AnyWidgetComponent.Props
  override sucrase_transforms: Transform[] = ["typescript", "jsx"]
  // Pending msg:custom handlers registered before view exists
  _pending_msg_handlers: ((data: any) => void)[] | null = null
  // Reference to the view, set during view initialization so that
  // model-level adapters (e.g. from _run_initializer) can connect events
  _anywidget_view: AnyWidgetComponentView | null = null

  constructor(attrs?: Partial<AnyWidgetComponent.Attrs>) {
    super(attrs)
  }

  override compile(): string | null {
    if (this.bundle != null) {
      return this.esm
    }
    // Try sucrase transpilation first.  If it fails with a SyntaxError the
    // ESM is likely a pre-bundled JS module (e.g. **tldraw**, **quak**)
    // that does not need TypeScript/JSX compilation — use it as-is.
    try {
      const result = super.compile()
      if (result !== null) {
        // Sucrase 3.35.0 has two known bugs that produce invalid JavaScript
        // when the input ESM uses optional chaining (?.) or nullish coalescing
        // (??) together with class private fields or return-await in a switch:
        //
        //   1. class X { #f; constructor() { super(), this.#f = ... } }
        //      → becomes: super(); __init.call(this);,this.#f = ...  (illegal ;,)
        //      → browser throws: "SyntaxError: Unexpected token ','"
        //
        //   2. case "x": return (await expr)?.prop;
        //      → becomes: case "x": returnawait _asyncOptionalChain(...)  (no space)
        //      → browser throws: "SyntaxError: Unexpected identifier '_asyncOptionalChain'"
        //
        // Sucrase adds '_optionalChain' / '_asyncOptionalChain' helper functions
        // at the TOP of its output ONLY when it down-levels ?. or ??.
        // Modern browsers (Chrome 80+, Firefox 74+, Safari 13.1+) support
        // optional chaining natively, so such down-leveling is never necessary
        // for anywidget ESMs.
        //
        // However, we can only fall back to the raw ESM when it is valid
        // JavaScript.  ESMs containing JSX (e.g. **ipyreactplayer**) NEED
        // the Sucrase transpilation — falling back would give the browser
        // raw JSX which it cannot parse.  So we check for the actual
        // Sucrase bug patterns rather than just the helper presence.
        if (
          (result.includes("function _optionalChain(") ||
           result.includes("function _asyncOptionalChain(")) &&
          !this.esm.includes("function _optionalChain(") &&
          !this.esm.includes("function _asyncOptionalChain(")
        ) {
          // Check for actual Sucrase bug patterns in the output:
          //   Bug 1: ";," (semicolon-comma from mangled super() + private fields)
          //   Bug 2: "returnawait" (missing space from return + await in switch)
          const has_comma_bug = result.includes(";,")
          const has_returnawait_bug = /\breturnawait\s+_/.test(result)
          if (has_comma_bug || has_returnawait_bug) {
            return this.esm
          }
          // No actual bugs — keep the Sucrase output.  This preserves
          // JSX transpilation for widgets like ipyreactplayer while still
          // using native optional chaining at runtime.
        }
        return result
      }
      // super.compile() returns null in dev mode on SyntaxError.
      // Clear the error and fall through to use the raw ESM.
      this.compile_error = null
      return this.esm
    } catch (e) {
      if (e instanceof SyntaxError) {
        return this.esm
      }
      throw e
    }
  }

  // ---- Render cache key --------------------------------------------------
  // ReactiveESM caches its render module in a global MODULE_CACHE keyed by
  // _render_cache_key.  The base class returns "reactive_esm" for all
  // subclasses.  Without this override, AnyWidgetComponent would reuse
  // ReactiveESM's cached render module, which passes `view.model_proxy`
  // to the ESM instead of `view.adapter`.
  //
  // The model_proxy's on() registers raw callbacks (no value wrapping) and
  // lacks send(), so the cache collision breaks:
  //   - **Altair JupyterChart**: change:_params callback gets undefined
  //   - **Mosaic**: view.model.send() is not a function
  //
  // Using a distinct key ensures AnyWidgetComponent always gets its own
  // render module that correctly passes the AnyWidgetAdapter.
  protected override get _render_cache_key() {
    return "anywidget_component"
  }

  // ---- Render module -----------------------------------------------------
  // This render module is loaded as a JS blob and cached under the key
  // above.  It is the glue between Bokeh's view lifecycle and the
  // anywidget ESM's render() function.
  //
  // Key difference from ReactiveESM._render_code():
  //   - Passes `view.adapter` (AnyWidgetAdapter) as the `model` argument,
  //     NOT `view.model_proxy`.  The adapter implements the full anywidget
  //     protocol (get/set/on/off/save_changes/send) with proper callback
  //     wrapping and trait name translation.
  protected override _render_code(): string {
    return `
// ---------------------------------------------------------------------------
// Shadow DOM query patching
// ---------------------------------------------------------------------------
// Many anywidget ESM bundles (e.g. widget-periodictable, which bundles jQuery)
// use document.querySelectorAll / document.getElementsByClassName to find
// elements they just rendered.  In Panel, ESM content is rendered inside a
// Bokeh shadow DOM, so these global queries return nothing.
//
// We install a ONE-TIME monkey-patch on Document.prototype that falls back to
// searching open shadow roots when the normal document query finds no results.
// This is safe because:
//   - It only activates when the original query returns zero results
//   - It searches ALL open shadow roots (not just ours)
//   - It preserves the original return type (NodeList / HTMLCollection)
// ---------------------------------------------------------------------------
if (!document.__pnl_shadow_patched) {
  document.__pnl_shadow_patched = true

  // Search all open shadow roots for elements matching a CSS selector.
  // ShadowRoot only supports querySelectorAll (not getElementsByClassName
  // or getElementById), so all fallback searches use querySelectorAll.
  function _searchShadowRoots(root, selector) {
    const all = root.querySelectorAll('*')
    for (const el of all) {
      if (el.shadowRoot) {
        const results = el.shadowRoot.querySelectorAll(selector)
        if (results.length > 0) return results
        const nested = _searchShadowRoots(el.shadowRoot, selector)
        if (nested && nested.length > 0) return nested
      }
    }
    return null
  }

  const _origQSA = Document.prototype.querySelectorAll
  Document.prototype.querySelectorAll = function(...args) {
    const results = _origQSA.apply(this, args)
    if (results.length > 0) return results
    return _searchShadowRoots(this, args[0]) || results
  }

  const _origGEBCN = Document.prototype.getElementsByClassName
  Document.prototype.getElementsByClassName = function(className) {
    const results = _origGEBCN.call(this, className)
    if (results.length > 0) return results
    // Convert class name to CSS selector for shadow root search
    const selector = '.' + className.trim().split(/\\s+/).join('.')
    return _searchShadowRoots(this, selector) || results
  }

  const _origGEBI = Document.prototype.getElementById
  Document.prototype.getElementById = function(id) {
    const result = _origGEBI.call(this, id)
    if (result) return result
    // Search shadow roots for element with matching ID
    const found = _searchShadowRoots(this, '#' + CSS.escape(id))
    return found && found.length > 0 ? found[0] : null
  }
}

function render(id) {
  const view = Bokeh.index.find_one_by_id(id)
  if (!view) { return }

  // Save the original Bokeh model — Bokeh layout internals (update_bbox,
  // render_children, etc.) access view.model.children and other Bokeh-
  // specific properties, so view.model must be the Bokeh model for those.
  const original_model = view.model

  // Temporarily set view.model to the adapter during the ESM render call.
  // Some widgets (e.g. **Mosaic**) access view.model inside their render
  // function and expect the anywidget model interface.
  view.model = view.adapter

  const experimental = { invoke: view.adapter.invoke.bind(view.adapter) }
  let result
  try {
    // Headless widgets (e.g. ipymidi's MIDIInterface with _view_name=None)
    // only export initialize() and have no render() function.  Skip the
    // render call gracefully — the widget still syncs traits via initialize().
    if (view.render_fn) {
      result = view.render_fn({
        view, model: view.adapter, data: original_model.data, el: view.container,
        experimental
      })
    }
  } finally {
    // Restore the Bokeh model synchronously after calling the ESM render
    // function.  This MUST happen before returning so that other views'
    // find_one_by_id() traversal (which calls view.children() which reads
    // view.model.children) sees the real Bokeh model — not the adapter.
    // Without this, rendering multiple AnyWidgetComponents in a layout
    // causes "Cannot read properties of undefined" during traversal.
    view.model = original_model
  }

  const out = Promise.resolve(result || null)
  view.destroyer = out
  out.then(() => {
    view.after_rendered()
  })
}

export default {render}`
  }

  // Pass an AnyWidgetModelAdapter (not model_proxy) to the ESM's optional
  // initialize() function, matching the anywidget protocol.
  protected override _run_initializer(initialize: (props: any) => void): void {
    const adapter = new AnyWidgetModelAdapter(this)
    const props = {
      model: adapter,
      experimental: {invoke: adapter.invoke.bind(adapter)},
    }
    initialize(props)
  }

  static override __module__ = "panel.models.esm"

  static {
    this.prototype.default_view = AnyWidgetComponentView
  }
}
