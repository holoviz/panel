import {TextAreaInput as BkTextAreaInput, TextAreaInputView as BkTextAreaInputView} from "@bokehjs/models/widgets/textarea_input"
import type * as p from "@bokehjs/core/properties"

export class TextAreaInputView extends BkTextAreaInputView {
  declare model: TextAreaInput

  override connect_signals(): void {
    super.connect_signals()

    const {value, max_rows} = this.model.properties

    this.on_change([max_rows, value], () => this.update_rows())
  }

  update_rows(): void {
    if (!this.model.auto_grow) {
      return
    }

    // Use this.el directly to access the textarea element
    const textarea = this.input_el
    const textLines = textarea.value.split("\n")
    const numRows = Math.max(textLines.length, this.model.rows, 1)
    textarea.rows = Math.min(numRows, this.model.max_rows || Infinity)
  }

  override render(): void {
    super.render()
    this.update_rows()
    this.el.addEventListener("input", () => {
      this.update_rows()
    })
  }
}

export namespace TextAreaInput {
  export type Attrs = p.AttrsOf<Props>
  export type Props = BkTextAreaInput.Props & {
    auto_grow: p.Property<boolean>
    max_rows: p.Property<number | null>
  }
}

export interface TextAreaInput extends TextAreaInput.Attrs { }

export class TextAreaInput extends BkTextAreaInput {
  declare properties: TextAreaInput.Props

  constructor(attrs?: Partial<TextAreaInput.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.widgets"

  static {
    this.prototype.default_view = TextAreaInputView

    this.define<TextAreaInput.Props>(({Bool, Int, Nullable}) => ({
      auto_grow: [ Bool,       false ],
      max_rows:  [ Nullable(Int),  null ],
    }))
  }
}
