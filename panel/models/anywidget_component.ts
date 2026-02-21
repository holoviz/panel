import type * as p from "@bokehjs/core/properties"
import type {Transform} from "sucrase"

import {DataEvent, ReactiveESM, ReactiveESMView} from "./reactive_esm"

class AnyWidgetModelAdapter {
  declare model: AnyWidgetComponent
  declare model_changes: any
  declare data_changes: any
  declare view: AnyWidgetComponentView | null
  // Maps original callbacks to their wrapped versions for change: events.
  // Needed because we wrap callbacks in on() to pass the new value (see
  // comment there), and off() must unregister the wrapped version, not
  // the original that the caller passes back.
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

  // Maps traitlet name (what ESM code uses) → param name (what Bokeh model uses).
  // e.g. { "height": "w_height", "width": "w_width" }
  get _trait_name_map(): Record<string, string> {
    if (this._cached_trait_name_map === null) {
      const constants = this.model.data?.attributes?.esm_constants
      this._cached_trait_name_map = (constants && constants._trait_name_map) ? constants._trait_name_map : {}
    }
    return this._cached_trait_name_map
  }

  // Reverse map: param name → traitlet name.
  // e.g. { "w_height": "height", "w_width": "width" }
  get _param_name_map(): Record<string, string> {
    if (this._cached_param_name_map === null) {
      const m: Record<string, string> = {}
      for (const [trait, param] of Object.entries(this._trait_name_map)) {
        m[param] = trait
      }
      this._cached_param_name_map = m
    }
    return this._cached_param_name_map
  }

  // Translate a traitlet name (used by ESM) to the param name (used by Bokeh model)
  _to_param_name(trait_name: string): string {
    return this._trait_name_map[trait_name] || trait_name
  }

  // Translate a param name (used by Bokeh model) to the traitlet name (used by ESM)
  _to_trait_name(param_name: string): string {
    return this._param_name_map[param_name] || param_name
  }

  get(name: any) {
    // Translate traitlet name to param name for data model lookup
    const param_name = this._to_param_name(name)
    let value
    const propPath = param_name.split(".")
    let targetModel: any = this.model.data

    for (let i = 0; i < propPath.length - 1; i++) {
      if (targetModel && targetModel.attributes && propPath[i] in targetModel.attributes) {
        targetModel = targetModel.attributes[propPath[i]]
      } else {
        // Stop if any part of the path is missing
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
    // Translate traitlet name to param name
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

  send(data: any, _options?: any) {
    this.model.trigger_event(new DataEvent(data))
  }

  on(event: string, cb: (value?: any) => void) {
    if (event.startsWith("change:")) {
      // Translate traitlet name to param name for Bokeh model watching
      const trait_name = event.slice("change:".length)
      const prop = this._to_param_name(trait_name)
      // The anywidget protocol specifies that change: callbacks receive the
      // new value as the first argument, e.g.:
      //   model.on("change:_params", (new_params) => { ... })
      // Bokeh's Signal0.connect() calls callbacks with no arguments, so we
      // wrap the callback to fetch and pass the current value. Without this,
      // libraries like Altair that destructure the argument (Object.entries(new_params))
      // receive undefined and throw a TypeError, which prevents Vega signal
      // listeners from being registered and breaks selection sync.
      const wrapped = () => {
        const value = this.get(trait_name)
        if (value !== undefined) {
          cb(value)
        }
      }
      this._cb_map.set(cb, wrapped)
      this.model.watch(this.view, prop, wrapped)
    } else if (event === "msg:custom" && this.view) {
      this.view.on_event(cb)
    } else {
      console.error(`Event of type '${event}' not recognized.`)
    }
  }

  off(event: string, cb: (value?: any) => void) {
    if (event.startsWith("change:")) {
      // Translate traitlet name to param name
      const trait_name = event.slice("change:".length)
      const prop = this._to_param_name(trait_name)
      // Look up the wrapped callback that on() registered with Bokeh.
      // Fall back to the original cb in case on() was never called for it.
      const wrapped = this._cb_map.get(cb) || cb
      this._cb_map.delete(cb)
      this.model.unwatch(this.view, prop, wrapped)
    } else if (event === "msg:custom" && this.view) {
      this.view.remove_on_event(cb)
    } else {
      console.error(`Event of type '${event}' not recognized.`)
    }
  }
}

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
    // Try the standard sucrase transpilation first.  If it fails with a
    // SyntaxError the ESM is likely a pre-bundled JS module (e.g. tldraw,
    // quak) that does not need TypeScript/JSX compilation — use it as-is.
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

  protected override _render_code(): string {
    return `
function render(id) {
  const view = Bokeh.index.find_one_by_id(id)
  if (!view) { return }

  const out = Promise.resolve(view.render_fn({
    view, model: view.adapter, data: view.model.data, el: view.container
  }) || null)
  view.destroyer = out
  out.then(() => view.after_rendered())
}

export default {render}`
  }

  protected override _run_initializer(initialize: (props: any) => void): void {
    const props = {model: new AnyWidgetModelAdapter(this)}
    initialize(props)
  }

  static override __module__ = "panel.models.esm"

  static {
    this.prototype.default_view = AnyWidgetComponentView
  }
}
