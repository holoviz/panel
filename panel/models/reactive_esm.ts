import {transform} from "sucrase"
import type {Transform} from "sucrase"

import {ModelEvent, server_event} from "@bokehjs/core/bokeh_events"
import {div} from "@bokehjs/core/dom"
import type {StyleSheetLike} from "@bokehjs/core/dom"
import {ImportedStyleSheet} from "@bokehjs/core/dom"
import type * as p from "@bokehjs/core/properties"
import type {Attrs} from "@bokehjs/core/types"
import type {LayoutDOM} from "@bokehjs/models/layouts/layout_dom"
import {LayoutDOMView} from "@bokehjs/models/layouts/layout_dom"
import {isArray} from "@bokehjs/core/util/types"
import type {UIElement, UIElementView} from "@bokehjs/models/ui/ui_element"

import {serializeEvent} from "./event-to-object"
import {DOMEvent} from "./html"
import {HTMLBox, HTMLBoxView, set_size} from "./layout"
import {convertUndefined, formatError} from "./util"

import esm_css from "styles/models/esm.css"

const MODULE_CACHE = new Map()

export class DataEvent extends ModelEvent {

  constructor(readonly data: unknown) {
    super()
  }

  protected override get event_values(): Attrs {
    return {model: this.origin, data: this.data}
  }

  static {
    this.prototype.event_name = "data_event"
  }
}

@server_event("esm_event")
export class ESMEvent extends DataEvent {

  static override from_values(values: object) {
    const {model, data} = values as {model: ReactiveESM, data: any}
    const event = new ESMEvent(data)
    event.origin = model
    return event
  }
}

export function model_getter(target: ReactiveESMView, name: string) {
  const model = target.model
  if (name === "get_child") {
    return (child: string) => {
      if (!target.accessed_children.includes(child)) {
        target.accessed_children.push(child)
      }
      const child_model: UIElement | UIElement[] = model.data[child]
      if (isArray(child_model)) {
        const children = []
        for (const subchild of child_model) {
          children.push(target.get_child_view(subchild)?.el)
        }
        return children
      } else if (model != null) {
        return target.get_child_view(child_model)?.el
      }
      return null
    }
  } else if (name === "send_msg") {
    return (data: any) => {
      model.trigger_event(new DataEvent(data))
    }
  } else if (name === "send_event") {
    return (name: string, event: Event) => {
      const serialized = convertUndefined(serializeEvent(event))
      model.trigger_event(new DOMEvent(name, serialized))
    }
  } else if (name === "off") {
    return (prop: string | string[], callback: any) => {
      const props = isArray(prop) ? prop : [prop]
      for (let p of props) {
        if (p.startsWith("change:")) {
          p = p.slice("change:".length)
        }
        if (p in model.attributes || p.split(".")[0] in model.data.attributes) {
          model.unwatch(target, p, callback)
          continue
        } else if (p === "msg:custom") {
          target.remove_on_event(callback)
          continue
        }
        if (p.startsWith("lifecycle:")) {
          p = p.slice("lifecycle:".length)
        }
        if (target._lifecycle_handlers.has(p)) {
          const handlers = target._lifecycle_handlers.get(p)
          if (handlers && handlers.includes(callback)) {
            target._lifecycle_handlers.set(p, handlers.filter(v => v !== callback))
          }
          continue
        }
        console.warn(`Could not unregister callback for event type '${p}'`)
      }
    }
  } else if (name === "on") {
    return (prop: string | string[], callback: any, force: boolean = false) => {
      const props = isArray(prop) ? prop : [prop]
      for (let p of props) {
        if (p.startsWith("change:")) {
          p = p.slice("change:".length)
        }
        if (p in model.attributes || p.split(".")[0] in model.data.attributes) {
          model.watch(target, p, callback, force)
          continue
        } else if (p === "msg:custom") {
          target.on_event(callback)
          continue
        }
        if (p.startsWith("lifecycle:")) {
          p = p.slice("lifecycle:".length)
        }
        if (target._lifecycle_handlers.has(p)) {
          (target._lifecycle_handlers.get(p) || []).push(callback)
          continue
        }
        console.warn(`Could not register callback for event type '${p}'`)
      }
    }
  } else if (Reflect.has(model.data, name)) {
    if (name in model.data.attributes && !target.accessed_properties.includes(name)) {
      target.accessed_properties.push(name)
    }
    return Reflect.get(model.data, name)
  } else if (Reflect.has(model, name)) {
    return Reflect.get(model, name)
  }
  return undefined
}

export function model_setter(target: ReactiveESMView, name: string, value: any): boolean {
  const model = target.model
  if (Reflect.has(model.data, name)) {
    return Reflect.set(model.data, name, value)
  } else if (Reflect.has(model, name)) {
    return Reflect.set(model, name, value)
  }
  return false
}

function init_model_getter(target: ReactiveESM, name: string) {
  if (Reflect.has(target.data, name)) {
    return Reflect.get(target.data, name)
  } else if (Reflect.has(target, name)) {
    return Reflect.get(target, name)
  }
}

function init_model_setter(target: ReactiveESM, name: string, value: any): boolean {
  if (Reflect.has(target.data, name)) {
    return Reflect.set(target.data, name, value)
  } else if (Reflect.has(target, name)) {
    return Reflect.set(target, name, value)
  }
  return false
}

export class ReactiveESMView extends HTMLBoxView {
  declare model: ReactiveESM
  container: HTMLDivElement
  accessed_properties: string[] = []
  accessed_children: string[] = []
  compiled_module: any = null
  model_proxy: any
  _changing: boolean = false
  _child_callbacks: Map<string, ((new_views: UIElementView[]) => void)[]>
  _child_rendered: Map<UIElementView, boolean> = new Map()
  _event_handlers: ((data: unknown) => void)[] = []
  _lifecycle_handlers: Map<string, ((...args: any[]) => void)[]> =  new Map([
    ["update_layout", []],
    ["after_layout", []],
    ["after_render", []],
    ["resize", []],
    ["remove", []],
    ["mounted", []],
  ])
  _module_cache: Map<string, any>
  _rendered: boolean = false
  _stale_children: boolean = false
  _mounted: Map<string, Set<string>> = new Map()

  override initialize(): void {
    super.initialize()
    this._module_cache = MODULE_CACHE
    this._child_callbacks = new Map()
    this.model_proxy = new Proxy(this, {
      get: model_getter,
      set: model_setter,
    })
  }

  override async lazy_initialize(): Promise<void> {
    await super.lazy_initialize()
    this.compiled_module = await this.model.compiled_module
  }

  override stylesheets(): StyleSheetLike[] {
    const stylesheets = super.stylesheets()
    stylesheets.push(esm_css)
    if (this.model.css_bundle) {
      if (this.model.bundle === "url") {
        stylesheets.push(new ImportedStyleSheet(this.model.css_bundle))
      } else {
        stylesheets.push(this.model.css_bundle)
      }
    }
    return stylesheets
  }

  override connect_signals(): void {
    super.connect_signals()
    const {esm, importmap, class_name} = this.model.properties
    this.on_change([esm, importmap], async () => {
      this.compiled_module = await this.model.compiled_module
      this.invalidate_render()
    })
    this.on_change(class_name, () => {
      this.container.className = this.model.class_name.replace(/([a-z])([A-Z])/g, "$1-$2").toLowerCase()
    })
    const child_props = this.model.children.map((child: string) => this.model.data.properties[child])
    this.on_change(child_props, () => {
      this.update_children()
    })
    this.model.on_event(ESMEvent, (event: ESMEvent) => {
      for (const cb of this._event_handlers) {
        cb(event.data)
      }
    })
  }

  override disconnect_signals(): void {
    super.disconnect_signals()
    this._child_callbacks = new Map()
    this.model.disconnect_watchers(this)
  }

  _on_mounted(): void {}

  notify_mount(child: string, id: string, remove: boolean): void {
    if (!this._mounted.has(child)) {
      this._mounted.set(child, new Set())
    }
    if (remove) {
      this._mounted.get(child)?.delete(id)
    } else {
      this._mounted.get(child)?.add(id)
    }
    let children = this.model.data[child]
    if (!isArray(children)) {
      children = [children]
    }
    if (children.every((model: UIElement) => this._mounted.get(child)?.has(model.id))) {
      this._on_mounted()
      for (const cb of this._lifecycle_handlers.get("mounted") || []) {
        cb(child)
      }
    }
  }

  on_event(callback: (data: unknown) => void): void {
    this._event_handlers.push(callback)
  }

  remove_on_event(callback: (data: unknown) => void): boolean {
    if (this._event_handlers.includes(callback)) {
      this._event_handlers = this._event_handlers.filter((item) => item !== callback)
      return true
    }
    return false
  }

  get_child_view(model: UIElement): UIElementView | undefined {
    return this._child_views.get(model)
  }

  get render_fn(): ((props: any) => any) | null {
    if (this.compiled_module === null) {
      return null
    } else if (this.compiled_module.default) {
      return this.compiled_module.default.render
    } else {
      return this.compiled_module.render
    }
  }

  override get child_models(): LayoutDOM[] {
    const children = []
    for (const child of this.model.children) {
      const model = this.model.data[child]
      if (isArray(model)) {
        for (const subchild of model) {
          children.push(subchild)
        }
      } else if (model != null) {
        children.push(model)
      }
    }
    return children
  }

  render_error(error: SyntaxError): void {
    const error_div = div({class: "error"})
    error_div.innerHTML = formatError(error, this.model.esm)
    this.container.appendChild(error_div)
  }

  override render(): void {
    this.empty()
    this._update_stylesheets()
    this._update_css_classes()
    this._apply_styles()
    this._update_css_variables()
    this._apply_visible()

    this._child_callbacks = new Map()
    this._child_rendered.clear()

    this._rendered = false
    set_size(this.el, this.model)
    this.container = div()
    this.container.className = this.model.class_name.replace(/([a-z])([A-Z])/g, "$1-$2").toLowerCase()
    set_size(this.container, this.model, false)
    this.shadow_el.append(this.container)
    if (this.model.compile_error) {
      this.render_error(this.model.compile_error)
    } else {
      this.render_esm()
    }
    for (const element_view of this.element_views) {
      // this.shadow_el is needed for Bokeh < 3.7.0 as this.self_target is not defined
      // can be removed when our minimum version is Bokeh 3.7.0
      // https://github.com/holoviz/panel/pull/7948
      const target = element_view.rendering_target() ?? this.self_target ?? this.shadow_el
      element_view.render_to(target)
    }
  }

  override get is_managed(): boolean {
    return this.parent instanceof LayoutDOMView && !(this.parent instanceof ReactiveESMView)
  }

  override compute_layout(): void {
    if (this.is_managed) {
      super.compute_layout()
      return
    }
    this.measure_layout()
    this.update_bbox()
    this._compute_layout()
    this.after_layout();
    // Override private property
    (this as any)._layout_computed = true
  }

  protected override _update_bbox(): boolean {
    const displayed = (() => {
      // Consider using Element.checkVisibility() in the future.
      // https://w3c.github.io/csswg-drafts/cssom-view-1/#dom-element-checkvisibility
      if (!this.el.isConnected) {
        return false
      } else if (this.el.offsetParent != null) {
        return true
      } else {
        const {position, display} = getComputedStyle(this.el)
        return position == "fixed" && display != "none"
      }
    })();

    // Override private property
    (this as any)._is_displayed = displayed
    return true
  }

  after_rendered(): void {
    const handlers = (this._lifecycle_handlers.get("after_render") || [])
    for (const cb of handlers) {
      cb()
    }
    this.render_children()
    this.model_proxy.on(this.accessed_children, () => { this._stale_children = true })
    if (!this._rendered) {
      for (const cb of (this._lifecycle_handlers.get("after_layout") || [])) {
        cb()
      }
    }
    this._rendered = true
  }

  render_esm(): void {
    if (this.model.compiled === null || this.model.render_module === null) {
      return
    }
    this.accessed_properties = []
    for (const lf of this._lifecycle_handlers.keys()) {
      (this._lifecycle_handlers.get(lf) || []).splice(0)
    }
    this.model.disconnect_watchers(this)
    this.model.render_module.then((mod: any) => mod.default.render(this.model.id))
  }

  render_children() {
    for (const child of this.model.children) {
      const child_model = this.model.data[child]
      const children = isArray(child_model) ? child_model : [child_model]
      for (const subchild of children) {
        const view = this._child_views.get(subchild)
        if (!view) {
          continue
        }
        const parent = view.el.parentNode
        if (parent && !this._child_rendered.has(view)) {
          this.rerender_(view)
          this._child_rendered.set(view, true)
        }
      }
    }
    this.after_render()
  }

  override invalidate_layout(): void {
    if (this.is_managed) {
      super.invalidate_layout()
      return
    }
    this.update_layout()
    this.compute_layout()
  }

  override remove(): void {
    super.remove()
    for (const cb of (this._lifecycle_handlers.get("remove") || [])) {
      cb()
    }
    this._child_callbacks.clear()
    this._child_rendered.clear()
    this._mounted.clear()
  }

  override after_resize(): void {
    if (this._rendered && !this._changing) {
      super.after_resize()
      for (const cb of (this._lifecycle_handlers.get("resize") || [])) {
        cb()
      }
    }
  }

  override after_layout(): void {
    super.after_layout()
    if (this._rendered && !this._changing) {
      for (const cb of (this._lifecycle_handlers.get("after_layout") || [])) {
        cb()
      }
    }
  }

  protected _lookup_child(child_view: UIElementView): string | null {
    for (const child of this.model.children) {
      let models = this.model.data[child]
      models = isArray(models) ? models : [models]
      for (const model of models) {
        if (model === child_view.model) {
          return child
        }
      }
    }
    return null
  }

  override async update_children(): Promise<void> {
    const created_children = new Set(await this.build_child_views())

    const all_views = this.child_views
    for (const child_view of all_views) {
      child_view.el.remove()
    }

    const new_views = new Map()
    for (const child_view of this.child_views) {
      if (!created_children.has(child_view)) {
        continue
      }
      const child = this._lookup_child(child_view)
      if (!child) {
        continue
      }

      if (new_views.has(child)) {
        new_views.get(child).push(child_view)
      } else {
        new_views.set(child, [child_view])
      }
    }

    for (const view of this._child_rendered.keys()) {
      if (!all_views.includes(view)) {
        this._child_rendered.delete(view)
      }
    }

    for (const child of this.model.children) {
      const callbacks = this._child_callbacks.get(child) || []
      const new_children = new_views.get(child) || []
      for (const callback of callbacks) {
        callback(new_children)
      }
    }
    if (this._stale_children) {
      this.render_esm()
      this._stale_children = false
    }
    this._update_children()
    this.invalidate_layout()
  }

  on_child_render(child: string, callback: (new_views: UIElementView[]) => void): void {
    if (!this._child_callbacks.has(child)) {
      this._child_callbacks.set(child, [])
    }
    const callbacks = this._child_callbacks.get(child) || []
    callbacks.push(callback)
  }

  remove_on_child_render(child: string, callback?: (new_views: UIElementView[]) => void): void {
    if (!this._child_callbacks.has(child)) {
      return
    }
    if (callback === undefined) {
      this._child_callbacks.delete(child)
    } else {
      let callbacks = this._child_callbacks.get(child) || []
      callbacks = callbacks.filter((cb) => cb !== callback)
      this._child_callbacks.set(child, callbacks)
    }
  }
}

export namespace ReactiveESM {
  export type Attrs = p.AttrsOf<Props>

  export type Props = HTMLBox.Props & {
    css_bundle: p.Property<string | null>
    bundle: p.Property<string | null>
    children: p.Property<any>
    class_name: p.Property<string>
    data: p.Property<any>
    dev: p.Property<boolean>
    esm: p.Property<string>
    events: p.Property<string[]>
    importmap: p.Property<any>
  }
}

export interface ReactiveESM extends ReactiveESM.Attrs {}

export class ReactiveESM extends HTMLBox {
  declare properties: ReactiveESM.Props
  compiled: string | null = null
  compiled_module: Promise<any> | null = null
  compile_error: Error | null = null
  model_proxy: any
  render_module: Promise<any> | null = null
  sucrase_transforms: Transform[] = ["typescript"]
  _destroyer: any | null = null
  _esm_watchers: any = {}
  _event_callbacks: Map<(data: unknown) => void, (data: unknown) => void> = new Map()

  constructor(attrs?: Partial<ReactiveESM.Attrs>) {
    super(attrs)
  }

  override initialize(): void {
    super.initialize()
    this.model_proxy = new Proxy(this, {
      get: init_model_getter,
      set: init_model_setter,
    })
    this.recompile()
  }

  override connect_signals(): void {
    super.connect_signals()
    this.connect(this.properties.esm.change, () => this.recompile())
    this.connect(this.properties.importmap.change, () => this.recompile())
  }

  watch(view: ReactiveESMView | null, prop: string, cb: any, force: boolean = false): void {
    if (prop in this._esm_watchers) {
      this._esm_watchers[prop].push([view, cb])
    } else {
      this._esm_watchers[prop] = [[view, cb]]
    }

    const propPath = prop.split(".")
    let target: any = this.data
    let resolvedProp: string | null = null
    for (let i = 0; i < propPath.length - 1; i++) {
      if (target && target.properties && propPath[i] in target.properties) {
        target = target[propPath[i]]
      } else {
        // Break if any level of the path is invalid
        target = null
        break
      }
    }

    if (target && target.properties && propPath[propPath.length - 1] in target.properties) {
      resolvedProp = propPath[propPath.length - 1]
    }

    // Handle reset of param.Event properties
    if (!force && target === this.data && resolvedProp && this.events.includes(resolvedProp)) {
      const orig_cb = cb
      cb = () => {
        if (resolvedProp && this.data[resolvedProp]) {
          orig_cb()
          this.data.setv({[resolvedProp]: false})
        }
      }
      this._event_callbacks.set(orig_cb, cb)
    }

    // Attach watcher if property is found
    if (resolvedProp && target) {
      target.property(resolvedProp).change.connect(cb)
    } else if (prop in this.properties) {
      this.property(prop).change.connect(cb)
    }
  }

  unwatch(view: ReactiveESMView | null, prop: string, cb: any): boolean {
    if (!(prop in this._esm_watchers)) {
      return false
    }

    // Filter out the specific callback for this view
    const remaining = []
    for (const [wview, wcb] of this._esm_watchers[prop]) {
      if (wview !== view || wcb !== cb) {
        remaining.push([wview, wcb])
      }
    }

    // Update or delete watcher list
    if (remaining.length > 0) {
      this._esm_watchers[prop] = remaining
    } else {
      delete this._esm_watchers[prop]
    }

    // Resolve nested properties
    const propPath = prop.split(".")
    let target: any = this.data
    let resolvedProp: string | null = null

    for (let i = 0; i < propPath.length - 1; i++) {
      if (target && target.properties && propPath[i] in target.properties) {
        target = target[propPath[i]]
      } else {
        // Stop if the path does not exist
        target = null
        break
      }
    }

    if (target && target.properties && propPath[propPath.length - 1] in target.properties) {
      resolvedProp = propPath[propPath.length - 1]
    }

    if (this._event_callbacks.has(cb)) {
      cb = this._event_callbacks.get(cb)
      this._event_callbacks.delete(cb)
    }

    // Detach watcher if property is found
    if (resolvedProp && target) {
      return target.property(resolvedProp).change.disconnect(cb)
    } else if (prop in this.properties) {
      return this.property(prop).change.disconnect(cb)
    }

    return false
  }

  disconnect_watchers(view: ReactiveESMView): void {
    for (const p in this._esm_watchers) {
      const prop = this.data.properties[p]
      const remaining = []
      for (const [wview, cb] of this._esm_watchers[p]) {
        if (wview === view) {
          prop?.change.disconnect(cb)
        } else {
          remaining.push([wview, cb])
        }
      }
      if (remaining.length > 0) {
        this._esm_watchers[p] = remaining
      } else {
        delete this._esm_watchers[p]
      }
    }
  }

  protected _declare_importmap(): void {
    if (this.importmap) {
      const importMap = {...this.importmap}
      try {
        // @ts-ignore
        importShim.addImportMap(importMap)
      } catch (e) {
        console.warn(`Failed to add import map: ${e}`)
      }
    }
  }

  protected _run_initializer(initialize: (props: any) => any): void {
    const props = {model: this.model_proxy}
    this._destroyer = initialize(props)
  }

  override destroy(): void {
    super.destroy()
    if (this._destroyer) {
      this._destroyer(this.model_proxy)
    }
  }

  init_module(): void {
    if (this.compile_error) {
      return
    } else if (MODULE_CACHE.has(this._render_cache_key)) {
      this.render_module = MODULE_CACHE.get(this._render_cache_key)
    } else {
      const code = this._render_code()
      const render_url = URL.createObjectURL(
        new Blob([code], {type: "text/javascript"}),
      )
      // @ts-ignore
      this.render_module = importShim(render_url)
      MODULE_CACHE.set(this._render_cache_key, this.render_module)
    }
  }

  protected _render_code(): string {
    return `
function render(id) {
  const view = Bokeh.index.find_one_by_id(id)
  if (view == null) {
    return null
  }

  const output = view.render_fn({
    view: view, model: view.model_proxy, data: view.model.data, el: view.container
  })

  Promise.resolve(output).then((out) => {
    if (out instanceof Element) {
      view.container.replaceChildren(out)
    }
    view.after_rendered()
  })
}

export default {render}`
  }

  protected get _render_cache_key() {
    return "reactive_esm"
  }

  compile(): string | null {
    if (this.bundle != null) {
      return this.esm
    }
    let compiled
    try {
      compiled = transform(
        this.esm, {
          transforms: this.sucrase_transforms,
          filePath: "render.tsx",
        },
      ).code
    } catch (e) {
      if (e instanceof SyntaxError) {
        if (this.dev) {
          this.compile_error = e
          return null
        } else {
          e.message = `${e.message}. See more information with '--dev' flag.`
          throw e
        }
      } else {
        throw e
      }
    }
    return compiled
  }

  async recompile(): Promise<void> {
    this.compile_error = null
    const compiled = this.compile()
    if (compiled === null) {
      this.compiled_module = Promise.resolve(null)
      return
    }
    this.compiled = compiled
    this._declare_importmap()
    let esm_module
    const use_cache = (!this.dev || this.bundle)
    const cache_key = (this.bundle === "url") ? this.esm : (this.bundle || `${this.class_name}-${this.esm.length}`)
    let resolve: (value: any) => void
    if (use_cache && MODULE_CACHE.has(cache_key)) {
      esm_module = Promise.resolve(MODULE_CACHE.get(cache_key))
    } else {
      if (use_cache) {
        MODULE_CACHE.set(cache_key, new Promise((res) => { resolve = res }))
      }
      let url
      if (this.bundle === "url") {
        url = this.esm
      } else {
        url = URL.createObjectURL(new Blob([this.compiled], {type: "text/javascript"}))
      }
      esm_module = (window as any).importShim(url)
    }
    this.compiled_module = (esm_module as Promise<any>).then((mod: any) => {
      if (resolve) {
        resolve(mod)
      }
      try {
        let initialize
        if (this.bundle != null && (mod.default || {}).hasOwnProperty(this.class_name)) {
          mod = mod.default[(this.class_name as any)]
        }
        if (mod.initialize) {
          initialize = mod.initialize
        } else if (mod.default && mod.default.initialize) {
          initialize = mod.default.initialize
        } else if (typeof mod.default === "function") {
          const initialized = mod.default()
          mod = {default: initialized}
          initialize = initialized.initialize
        }
        if (initialize) {
          this._run_initializer(initialize)
        }
        this.init_module()
        return mod
      } catch (e: any) {
        if (this.dev) {
          this.compile_error = e
        }
        console.error(`Could not initialize module due to error: ${e}`)
        return null
      }
    })
  }

  static override __module__ = "panel.models.esm"

  static {
    this.prototype.default_view = ReactiveESMView
    this.define<ReactiveESM.Props>(({Any, Array, Bool, Nullable, Str}) => ({
      css_bundle:  [ Nullable(Str),     null ],
      bundle:      [ Nullable(Str),     null ],
      children:    [ Array(Str),          [] ],
      class_name:  [ Str,                 "" ],
      data:        [ Any                     ],
      dev:         [ Bool,             false ],
      esm:         [ Str,                 "" ],
      events:      [ Array(Str),          [] ],
      importmap:   [ Any,                 {} ],
    }))
  }
}
