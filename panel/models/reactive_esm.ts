import {transform} from "sucrase"
import type {Transform} from "sucrase"

import {div} from "@bokehjs/core/dom"
import type {StyleSheetLike} from "@bokehjs/core/dom"
import type * as p from "@bokehjs/core/properties"
import type {LayoutDOM} from "@bokehjs/models/layouts/layout_dom"
import {isArray} from "@bokehjs/core/util/types"
import type {UIElement, UIElementView} from "@bokehjs/models/ui/ui_element"

import {serializeEvent} from "./event-to-object"
import {DOMEvent} from "./html"
import {HTMLBox, HTMLBoxView, set_size} from "./layout"
import {convertUndefined, find_attributes, formatError, hash} from "./util"

import error_css from "styles/models/esm.css"

function model_getter(target: ReactiveESMView, name: string) {
  const model = target.model
  if (Reflect.has(model.data, name)) {
    if (name in model.data.attributes && !target.accessed_properties.includes(name)) {
      target.accessed_properties.push(name)
    }
    return Reflect.get(model.data, name)
  } else if (Reflect.has(model, name)) {
    return Reflect.get(model, name)
  }
  return undefined
}

function model_setter(target: ReactiveESMView, name: string, value: any): boolean {
  const model = target.model
  if (Reflect.has(model.data, name)) {
    return Reflect.set(model.data, name, value)
  } else if (Reflect.has(model, name)) {
    return Reflect.set(model, name, value)
  }
  return false
}

export class ReactiveESMView extends HTMLBoxView {
  declare model: ReactiveESM
  sucrase_transforms: Transform[] = ["typescript"]
  container: HTMLDivElement
  accessed_properties: string[] = []
  model_proxy: any
  compiled: string | null = null
  compiled_module: any = null
  compile_error: Error | null = null
  _changing: boolean = false
  _watchers: any = {}
  _child_callbacks: Map<string, (new_views: UIElementView[]) => void>

  override initialize(): void {
    super.initialize()
    this.model.data.watch = (callback: any, prop: string | string[]) => {
      const props = isArray(prop) ? prop : [prop]
      for (const p of props) {
        const cb = () => {
          callback(prop, null, this.model.data[p])
        }
        this.model.data.properties[p].change.connect(cb)
        if (p in this._watchers) {
          this._watchers[p].push(cb)
        } else {
          this._watchers[p] = [cb]
        }
      }
    }
    this.model.data.send_event = (name: string, event: Event) => {
      const serialized = convertUndefined(serializeEvent(event))
      this.model.trigger_event(new DOMEvent(name, serialized))
    }
    this.model_proxy = new Proxy(this, {
      get: model_getter,
      set: model_setter
    })
  }

  override async lazy_initialize(): Promise<void> {
    await super.lazy_initialize()
    await this.recompile()
  }

  async recompile(): Promise<void> {
    this.compile_error = null
    const compiled = this.compile()
    if (compiled === null) {
      this.compiled_module = null
      return
    }
    this.compiled = compiled
    this._declare_importmap()
    const url = URL.createObjectURL(
      new Blob([this.compiled], {type: "text/javascript"}),
    )
    try {
      // @ts-ignore
      const mod = this.compiled_module = await importShim(url)
      let initialize
      if (mod.initialize) {
        initialize = this.compiled_module.initialize
      } else if (mod.default && mod.default.initialize) {
        initialize = mod.default.initialize
      }
      if (initialize) {
        this._run_initializer(initialize)
      }
    } catch (e: any) {
      this.compiled_module = null
      if (this.model.dev) {
        this.compile_error = e
      } else {
        throw e
      }
    }
  }

  protected _run_initializer(initialize: (props: any) => void): void {
    const props = {model: this.model, data: this.model.data}
    initialize(props)
  }

  override stylesheets(): StyleSheetLike[] {
    const stylesheets = super.stylesheets()
    if (this.model.dev) {
      stylesheets.push(error_css)
    }
    return stylesheets
  }

  override connect_signals(): void {
    super.connect_signals()
    const {esm, importmap} = this.model.properties
    this.on_change([esm, importmap], async () => {
      await this.recompile()
      this.invalidate_render()
    })
    const child_props = this.model.children.map((child: string) => this.model.data.properties[child])
    this.on_change(child_props, () => {
      this.update_children()
    })
  }

  protected _disconnect_watchers(): void {
    for (const p in this._watchers) {
      const prop = this.model.data.properties[p]
      for (const cb of this._watchers[p]) {
        prop.change.disconnect(cb)
      }
    }
    this._watchers = {}
  }

  override disconnect_signals(): void {
    super.disconnect_signals()
    this._child_callbacks = new Map()
    this._watchers = {}
  }

  get_child(model: UIElement): UIElementView | undefined {
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

  override render(): void {
    this.empty()
    this._update_stylesheets()
    this._update_css_classes()
    this._apply_styles()
    this._apply_visible()

    this._child_callbacks = new Map()
    this._watchers = {}

    set_size(this.el, this.model)
    this.container = div({style: "display: contents;"})
    this.shadow_el.append(this.container)
    if (this.compile_error) {
      const error = div({class: "error"})
      error.innerHTML = formatError(this.compile_error, this.model.esm)
      this.container.appendChild(error)
    } else {
      this.render_esm()
    }
  }

  compile(): string | null {
    let compiled
    try {
      compiled = transform(
        this.model.esm, {
          transforms: this.sucrase_transforms,
          filePath: "render.tsx",
        },
      ).code
    } catch (e) {
      if (e instanceof SyntaxError && this.model.dev) {
        this.compile_error = e
        return null
      } else {
        throw e
      }
    }
    return compiled
  }

  protected _declare_importmap(): void {
    if (this.model.importmap) {
      const importMap = {...this.model.importmap}
      // @ts-ignore
      importShim.addImportMap(importMap)
    }
  }

  protected _render_code(): string {
    const rerender_vars = find_attributes(
      this.compiled || "", "children", [],
    )
    return `
const view = Bokeh.index.find_one_by_id('${this.model.id}')

const children = {}
for (const child of view.model.children) {
  const child_model = view.model.data[child]
  if (Array.isArray(child_model)) {
    const subchildren = children[child] = []
    for (const subchild of child_model) {
      subchildren.push(view._child_views.get(subchild).el)
    }
  } else {
    children[child] = view._child_views.get(child_model).el
  }
}

const output = view.render_fn({
  view: view, model: view.model_proxy, data: view.model.data, el: view.container, children: children
})

if (output instanceof Element) {
  view.container.replaceChildren(output)
}

view.render_children()
view.model.data.watch(() => view.render_esm(), ${JSON.stringify(rerender_vars)})`
  }

  render_esm(): void {
    if (this.compiled === null) {
      return
    }
    this.accessed_properties = []
    this._disconnect_watchers()
    const code = this._render_code()
    const render_url = URL.createObjectURL(
      new Blob([code], {type: "text/javascript"}),
    )
    // @ts-ignore
    importShim(render_url)
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
        if (parent) {
          view.render()
          view.after_render()
        }
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

    for (const child_view of this.child_views) {
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
      } else if (new_views.has(child)) {
        new_views.get(child).push(child_view)
      } else {
        new_views.set(child, [child_view])
      }
    }

    for (const child of this.model.children) {
      const callback = this._child_callbacks.get(child)
      if (callback) {
        const new_children = new_views.get(child) || []
        callback(new_children)
      }
    }

    this._update_children()
    this.invalidate_layout()
  }

  on_child_render(child: string, callback: (new_views: UIElementView[]) => void): void {
    this._child_callbacks.set(child, callback)
  }

  remove_on_child_render(child: string): void {
    this._child_callbacks.delete(child)
  }
}

export namespace ReactiveESM {
  export type Attrs = p.AttrsOf<Props>

  export type Props = HTMLBox.Props & {
    children: p.Property<any>
    data: p.Property<any>
    dev: p.Property<boolean>
    esm: p.Property<string>
    importmap: p.Property<any>
  }
}

export interface ReactiveESM extends ReactiveESM.Attrs {}

export class ReactiveESM extends HTMLBox {
  declare properties: ReactiveESM.Props

  constructor(attrs?: Partial<ReactiveESM.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.esm"

  static {
    this.prototype.default_view = ReactiveESMView
    this.define<ReactiveESM.Props>(({Any, Array, Bool, String}) => ({
      children:  [ Array(String),       [] ],
      data:      [ Any                     ],
      dev:       [ Bool,             false ],
      esm:       [ String,              "" ],
      importmap: [ Any,                 {} ],
    }))
  }
}
