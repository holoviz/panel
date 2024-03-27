import {TextInput as BkTextInput, TextInputView as BkTextInputView} from "@bokehjs/models/widgets/text_input"
import type * as p from "@bokehjs/core/properties"

export class TextInputView extends BkTextInputView {
  declare model: TextInput

  override _keyup(event: KeyboardEvent): void {
    super._keyup(event)
    if (event.key == "Enter") {
      this.model.enter_pressed += 1
    }
  }
}

export namespace TextInput {
  export type Attrs = p.AttrsOf<Props>
  export type Props = BkTextInput.Props & {
    enter_pressed: p.Property<number>
  }
}

export interface TextInput extends TextInput.Attrs { }

export class TextInput extends BkTextInput {
  declare properties: TextInput.Props

  constructor(attrs?: Partial<TextInput.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.widgets"

  static {
    this.prototype.default_view = TextInputView

    this.define<TextInput.Props>(({Int}) => ({
      enter_pressed: [ Int,       0 ],
    }))
  }
}
