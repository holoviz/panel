import type * as p from "@bokehjs/core/properties"

import {ReactiveESMView} from "./reactive_esm"
import {ReactComponent, ReactComponentView} from "./react_component"

class PanelModel {
  declare model: AnyWidgetComponent

  constructor(model: AnyWidgetComponent) {
    this.model = model
  }

  get(name: any) {
    let value
    console.log(this.model)
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

  set(name: string, value: any) {
    if (name in this.model.data.attributes) {
      this.model.data.setv({[name]: value})
    } else if (name in this.model.attributes) {
      this.model.setv({[name]: value})
    }
  }

  save_changes() {
    // no-op, not a thing in panel
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
  adapter: PanelModel

  override initialize(): void {
    super.initialize()
    this.adapter = new PanelModel(this.model)
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

view.render_fn(props)`
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
