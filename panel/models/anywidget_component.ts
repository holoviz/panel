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
  // Cached name maps (built lazily from esm_constants._trait_name_map)
  _cached_trait_name_map: Record<string, string> | null
  _cached_param_name_map: Record<string, string> | null

  constructor(model: AnyWidgetComponent) {
    this.view = null
    this.model = model
    this.model_changes = {}
    this.data_changes = {}
    this._cb_map = new Map()
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

    return value
  }

  set(name: string, value: any) {
    const param_name = this._to_param_name(name)
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
  send(data: any, _options?: any) {
    this.model.trigger_event(new DataEvent(data))
  }

  on(event: string, cb: (...args: any[]) => void) {
    if (event.startsWith("change:")) {
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
    } else if (event === "msg:custom" && this.view) {
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
      this.view.on_event(wrapped)
    } else {
      console.error(`Event of type '${event}' not recognized.`)
    }
  }

  off(event: string, cb: (...args: any[]) => void) {
    if (event.startsWith("change:")) {
      const trait_name = event.slice("change:".length)
      const prop = this._to_param_name(trait_name)
      // Retrieve the wrapped callback that on() registered with Bokeh,
      // falling back to the original in case on() was never called.
      const wrapped = this._cb_map.get(cb) || cb
      this._cb_map.delete(cb)
      this.model.unwatch(this.view, prop, wrapped)
    } else if (event === "msg:custom" && this.view) {
      const wrapped = this._cb_map.get(cb) || cb
      this._cb_map.delete(cb)
      this.view.remove_on_event(wrapped)
    } else {
      console.error(`Event of type '${event}' not recognized.`)
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

  const out = Promise.resolve(view.render_fn({
    view, model: view.adapter, data: original_model.data, el: view.container
  }) || null)
  view.destroyer = out
  out.then(() => {
    // Restore the Bokeh model BEFORE after_rendered() — it calls
    // render_children() which iterates this.model.children.
    view.model = original_model
    view.after_rendered()
  })
}

export default {render}`
  }

  // Pass an AnyWidgetModelAdapter (not model_proxy) to the ESM's optional
  // initialize() function, matching the anywidget protocol.
  protected override _run_initializer(initialize: (props: any) => void): void {
    const props = {model: new AnyWidgetModelAdapter(this)}
    initialize(props)
  }

  static override __module__ = "panel.models.esm"

  static {
    this.prototype.default_view = AnyWidgetComponentView
  }
}
