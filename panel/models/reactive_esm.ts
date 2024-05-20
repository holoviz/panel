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
import {HTMLBox, HTMLBoxView} from "./layout"
import {convertUndefined, formatError} from "./util"

import error_css from "styles/models/esm.css"

export class ReactiveESMView extends HTMLBoxView {
  declare model: ReactiveESM
  sucrase_transforms: Transform[] = ["typescript"]
  container: HTMLDivElement
  modelState: typeof Proxy
  rendered: string | null = null
  _changing: boolean = false
  _watchers: any = {}
  _child_callbacks: Map<string, (new_views: UIElementView[]) => void>
  _rerender_vars: string[] = []

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
  }

  override stylesheets(): StyleSheetLike[] {
    const stylesheets = super.stylesheets()
    if (this.model.dev) {
      stylesheets.push(error_css)
    }
    return stylesheets
  }

  disconnect_watchers(): void {
    for (const p in this._watchers) {
      const prop = this.model.data.properties[p]
      for (const cb of this._watchers[p]) {
        prop.change.disconnect(cb)
      }
    }
    this._watchers = {}
  }

  override connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.esm.change, () => {
      this.invalidate_render()
    })
    const child_props = this.model.children.map((child: string) => this.model.data.properties[child])
    this.on_change(child_props, () => {
      this.update_children()
    })
  }

  override disconnect_signals(): void {
    super.disconnect_signals()
    this._child_callbacks = new Map()
    this._watchers = {}
  }

  get_child(model: UIElement): UIElementView | undefined {
    return this._child_views.get(model)
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

    this.container = div({style: "display: contents;"})
    this.shadow_el.append(this.container)
    if (this.model.compiled) {
      this.rendered = this.model.compiled
    } else {
      try {
        this.rendered = transform(
          this.model.esm, {
            transforms: this.sucrase_transforms,
            filePath: "render.tsx",
          },
        ).code
      } catch (e) {
        if (e instanceof SyntaxError && this.model.dev) {
          const error = div({class: "error"})
          error.innerHTML = formatError(e, this.model.esm)
          this.container.appendChild(error)
          return
        } else {
          throw e
        }
      }
    }
    this._render_esm()
  }

  protected _render_esm(): void {
    this.disconnect_watchers()
    if (this.model.importmap) {
      const importMap = {...this.model.importmap}
      // @ts-ignore
      importShim.addImportMap(importMap)
    }

    const code = `
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
${this.rendered}

const output = render({view: view, model: view.model, data: view.model.data, el: view.container, children, html: view._htm})

if (output instanceof Element) {
  view.container.appendChild(output)
}

view.render_children();`

    const url = URL.createObjectURL(
      new Blob([code], {type: "text/javascript"}),
    )
    // @ts-ignore
    importShim(url)
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
      for (const child of this.model.children) {
        let models = this.model.data[child]
        models = isArray(models) ? models : [models]
        for (const model of models) {
          if (model === child_view.model) {
            if (new_views.has(child)) {
              new_views.get(child).push(child_view)
            } else {
              new_views.set(child, [child_view])
            }
          }
        }
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
    compiled: p.Property<string | null>
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
    this.define<ReactiveESM.Props>(({Any, Array, Bool, Nullable, String}) => ({
      children:  [ Array(String),       [] ],
      compiled:  [ Nullable(String),  null ],
      data:      [ Any                     ],
      dev:       [ Bool,             false ],
      esm:       [ String,              "" ],
      importmap: [ Any,                 {} ],
    }))
  }
}
