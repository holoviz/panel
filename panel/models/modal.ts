import type * as p from "@bokehjs/core/properties"
import {Column as BkColumn, ColumnView as BkColumnView} from "@bokehjs/models/layouts/column"

export class ModalView extends BkColumnView {
  declare model: Modal

  override connect_signals(): void {
    super.connect_signals()
    const {} = this.model.properties
    this.on_change([], () => { this.update() })
  }

  override render(): void {
    super.render()
  }

  update(): void {
    console.log("update")
  }
}

export namespace Modal {
  export type Attrs = p.AttrsOf<Props>

  export type Props = BkColumn.Props & {
    is_open: p.Property<boolean>
    show_close_button: p.Property<boolean>
  }
}

export interface Modal extends Modal.Attrs {}

export class Modal extends BkColumn {
  declare properties: Modal.Props

  constructor(attrs?: Partial<Modal.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.layout"
  static {
    this.prototype.default_view = ModalView
    this.define<Modal.Props>(({Bool}) => ({
      is_open: [Bool, false],
      show_close_button: [Bool, true],
    }))
  }
}
