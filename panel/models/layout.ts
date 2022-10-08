import {MarkupView} from "@bokehjs/models/widgets/markup"
import {LayoutDOM, LayoutDOMView} from "@bokehjs/models/layouts/layout_dom"
import * as p from "@bokehjs/core/properties"

export class PanelMarkupView extends MarkupView {}

export abstract class HTMLBoxView extends LayoutDOMView {
  override model: HTMLBox

  get child_models(): LayoutDOM[] {
    return []
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
