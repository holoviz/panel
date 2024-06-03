import type * as p from "@bokehjs/core/properties"

import {ReactiveESMView} from "./reactive_esm"
import {ReactComponent, ReactComponentView} from "./react_component"

class AnyWidgetAdapter {
  declare view: AnyWidgetComponentView
  declare model: AnyWidgetComponent
  declare model_changes: any
  declare data_changes: any

  constructor(view: AnyWidgetComponentView) {
    this.view = view
    this.model = view.model
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
      value = new Uint8Array(value)
    }
    return value
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
      this.model.data.watch(() => cb(), event.slice("change:".length))
    } else {
      console.error("Only change events supported")
    }
  }

  // @ts-ignore
  off(event: string, cb: () => void) {
    // Implement unwatch
  }
}

export class AnyWidgetComponentView extends ReactComponentView {
  adapter: AnyWidgetAdapter

  override initialize(): void {
    super.initialize()
    this.adapter = new AnyWidgetAdapter(this)
  }

  override compile(): string | null {
    return ReactiveESMView.prototype.compile.call(this)
  }

  protected override _run_initializer(initialize: (props: any) => void): void {
    const props = {model: this.model, data: this.adapter}
    initialize(props)
  }

  protected override _render_code(): string {
    return `
const view = Bokeh.index.find_one_by_id('${this.model.id}')

let props = {view, model: view.adapter, data: view.model.data, el: view.container}

view.render_fn(props)
view.render_children()`
  }
}

export namespace AnyWidgetComponent {
  export type Attrs = p.AttrsOf<Props>

  export type Props = ReactComponent.Props
}

export interface AnyWidgetComponent extends AnyWidgetComponent.Attrs {}

export class AnyWidgetComponent extends ReactComponent {
  declare properties: AnyWidgetComponent.Props

  constructor(attrs?: Partial<AnyWidgetComponent.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.esm"

  static {
    this.prototype.default_view = AnyWidgetComponentView
  }
}
