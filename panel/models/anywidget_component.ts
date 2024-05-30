import type * as p from "@bokehjs/core/properties"

import {ReactComponent, ReactComponentView} from "./react_component"

const panel_adapter = `
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
`

export class AnyWidgetComponentView extends ReactComponentView {

  protected override _render_affixes(): [string, string] {
    const prefix = `
const _view = Bokeh.index.find_one_by_id('${this.model.id}')

${panel_adapter}

const _model = new PanelModel(_view.model)

let props = {view: _view, model: _model, data: _view.model.data, el: _view.container}`
    return [prefix, ""]
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
