import type * as p from "@bokehjs/core/properties"

import {ReactiveESM, ReactiveESMView} from "./reactive_esm"

class AnyWidgetModelAdapter {
  declare model: AnyWidgetComponent
  declare model_changes: any
  declare data_changes: any
  declare view: AnyWidgetComponentView | null

  constructor(model: AnyWidgetComponent) {
    this.view = null
    this.model = model
    this.model_changes = {}
    this.data_changes = {}
  }

  get(name: any) {
    let value
    if (name in this.model.data.attributes) {
      value = this.model.data.attributes[name]
    } else {
      value = this.model.attributes[name]
    }
    if (value instanceof ArrayBuffer) {
      value = new DataView(value)
    }
    return value
  }

  set(name: string, value: any) {
    if (name in this.model.data.attributes) {
      this.data_changes = {...this.data_changes, [name]: value}
    } else if (name in this.model.attributes) {
      this.model_changes = {...this.model_changes, [name]: value}
    }
  }

  save_changes() {
    this.model.setv(this.model_changes)
    this.model_changes = {}
    this.model.data.setv(this.data_changes)
    this.data_changes = {}
  }

  on(event: string, cb: () => void) {
    if (event.startsWith("change:")) {
      this.model.watch(this.view, event.slice("change:".length), cb)
    } else if (event === "msg:custom" && this.view) {
      this.view.on_event(cb)
    } else {
      console.error(`Event of type '${event}' not recognized.`)
    }
  }

  off(event: string, cb: () => void) {
    if (event.startsWith("change:")) {
      this.model.unwatch(this.view, event.slice("change:".length), cb)
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

  protected override _render_code(): string {
    return `
const view = Bokeh.index.find_one_by_id('${this.model.id}')

function render() {
  const out = Promise.resolve(view.render_fn({
    view, model: view.adapter, data: view.model.data, el: view.container
  }) || null)
  view.destroyer = out
  out.then(() => view.after_rendered())
}

export default {render}`
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

  constructor(attrs?: Partial<AnyWidgetComponent.Attrs>) {
    super(attrs)
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
