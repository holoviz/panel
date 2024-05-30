import type * as p from "@bokehjs/core/properties"

import {ReactiveESMView} from "./reactive_esm"
import {ReactComponent, ReactComponentView} from "./react_component"

export class AnyWidgetComponentView extends ReactComponentView {

  override compile(): string | null {
    return ReactiveESMView.prototype.compile.call(this)
  }

  protected override _render_code(): string {
    return `
const view = Bokeh.index.find_one_by_id('${this.model.id}')

class PanelModel {

  constructor(model) {
    this.model = model;
  }

  get(name) {
    let value
    if (name in this.model.data.attributes) {
      value = this.model.data[name]
    } else {
      value = this.model[name]
    }
    if (value instanceof ArrayBuffer) {
      value = new Uint8Array(value)
    }
    return value
  }

  set(name, value) {
    return this.data[name] = value;
  }

  save_changes() {
    // no-op, not a thing in panel
  }

  on(event, cb) {
    if (event.startsWith("change:")) {
      this.model.data.watch(() => cb(), event.slice("change:".length))
    } else {
      console.error("Only change events supported")
    }
  }

  off(event, cb) {
    // Implement unwatch
  }
}

const model = new PanelModel(view.model)
let props = {view, model, data: view.model.data, el: view.container}

let render;
if (view.rendered_module.default) {
  render = view.rendered_module.default.render
} else {
  render = view.rendered_module.render
}

render(props)`
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
