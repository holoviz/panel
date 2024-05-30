import type * as p from "@bokehjs/core/properties"

import {ReactComponent, ReactComponentView} from "./react_component"

const panel_adapter = `
class PanelModel {

  constructor(model) {
    this.model = model;
  }

  get(name) {
    let value
    if (name in this.model.attributes) {
      value = this.model[name]
    } else {
      value = this.model.data[name]
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
}
`

export class AnyWidgetComponentView extends ReactComponentView {

  protected override _render_code(): string {
    const [prefix, suffix] = this._render_affixes()
    return `
${prefix}

${panel_adapter}

const _model = new PanelModel(view.model)
props = {...props, model: _model}

${this.rendered}

const rendered = render(props)

${suffix}`
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
