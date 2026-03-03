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

class AnyWidgetModelAdapter {
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
  // Cached name maps (built lazily from esm_constants._trait_name_map)
  _cached_trait_name_map: Record<string, string> | null
  _cached_param_name_map: Record<string, string> | null

  constructor(model: AnyWidgetComponent) {
    this.view = null
    this.model = model
    this.model_changes = {}
    this.data_changes = {}
    this._cb_map = new Map()
    this._generic_change_cbs = new Set()
    this._cached_trait_name_map = null
    this._cached_param_name_map = null
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
    if (Array.isArray(value)) {
      return value.map((v: any) => this._decode_binary(v))
    }
    const result: Record<string, any> = {}
    for (const [k, v] of Object.entries(value)) {
      result[k] = this._decode_binary(v)
    }
    return result
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
      this._generic_change_cbs.add(cb)
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
        // Also fire generic "change" listeners
        for (const gcb of this._generic_change_cbs) {
          try { gcb() } catch (e) { console.error("Error in generic change callback:", e) }
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

  // ---- widget_manager stub ------------------------------------------------
  // The native anywidget protocol exposes model.widget_manager for compound
  // widgets that need to look up other widget models.  Panel doesn't have
  // a Jupyter widget manager, so we provide a stub that warns on use.
  get widget_manager(): any {
    return {
      get_model: (model_id: string) => {
        console.warn(
          `[Panel AnyWidget] widget_manager.get_model('${model_id}') ` +
          `is not supported. Compound widgets using IPY_MODEL_ references ` +
          `require Jupyter's widget manager.`,
        )
        return Promise.reject(
          new Error("widget_manager not available in Panel"),
        )
      },
    }
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
      this._cb_map.clear()
      return
    }
    if (event === "change") {
      if (cb) {
        this._generic_change_cbs.delete(cb)
      } else {
        this._generic_change_cbs.clear()
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
class AnyWidgetAdapter extends AnyWidgetModelAdapter {
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
  }

  override remove(): void {
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
