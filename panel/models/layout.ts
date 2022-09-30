import {classes} from "@bokehjs/core/dom"
import {MarkupView} from "@bokehjs/models/widgets/markup"
import {LayoutDOM, LayoutDOMView} from "@bokehjs/models/layouts/layout_dom"
import * as p from "@bokehjs/core/properties"

export class PanelMarkupView extends MarkupView {}

export abstract class HTMLBoxView extends LayoutDOMView {
  override model: HTMLBox

  _prev_css_classes: string[]

  get child_models(): LayoutDOM[] {
    return []
  }

  connect_signals(): void {
    super.connect_signals()

    // Note due to on_change hack properties must be defined in this order.
    const {css_classes} = this.model.properties
    this._prev_css_classes = this.model.css_classes
    this.on_change([css_classes], () => {
      // Note: This ensures that changes in the background and changes
      // to the loading parameter in Panel do NOT trigger a full re-render
      const css = []
      let skip = false
      for (const cls of this.model.css_classes) {
        if (cls === 'pn-loading')
          skip = true
        else if (skip)
          skip = false
        else
          css.push(cls)
      }
      const prev = this._prev_css_classes
      if (JSON.stringify(css) === JSON.stringify(prev)) {
        classes(this.el).clear().add(...this.css_classes())
      } else {
        this.invalidate_render()
      }
      this._prev_css_classes = css
    })
  }

  on_change(properties: any, fn: () => void): void {
    // HACKALERT: LayoutDOMView triggers re-renders whenever css_classes change
    // which is very expensive so we do not connect this signal and handle it
    // ourself
    const p = this.model.properties
    if (properties.length === 2 && properties[0] === p.background && properties[1] === p.css_classes) {
      return
    }
    super.on_change(properties, fn)
  }
}

export namespace HTMLBox {
  export type Attrs = p.AttrsOf<Props>
  export type Props = LayoutDOM.Props
}

export interface HTMLBox extends HTMLBox.Attrs {}

export abstract class HTMLBox extends LayoutDOM {
  override properties: HTMLBox.Props

  constructor(attrs?: Partial<HTMLBox.Attrs>) {
    super(attrs)
  }
}
