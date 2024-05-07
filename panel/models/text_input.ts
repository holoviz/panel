import {TextInput as BkTextInput, TextInputView as BkTextInputView} from "@bokehjs/models/widgets/text_input"
import type * as p from "@bokehjs/core/properties"
import {ModelEvent} from "@bokehjs/core/bokeh_events"
import type {Attrs} from "@bokehjs/core/types"

export class EnterEvent extends ModelEvent {
  constructor(readonly value_input: string) {
    super()
  }

  protected override get event_values(): Attrs {
    return {model: this.origin, value_input: this.value_input}
  }

  static {
    this.prototype.event_name = "enter-pressed"
  }
}

export class TextInputView extends BkTextInputView {
  declare model: TextInput

  override _keyup(event: KeyboardEvent): void {
    super._keyup(event)
    if (event.key == "Enter") {
      const {value_input} = this.model
      this.model.trigger_event(new EnterEvent(value_input))
    }
  }
}

export namespace TextInput {
  export type Attrs = p.AttrsOf<Props>
  export type Props = BkTextInput.Props
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

    this.define<TextInput.Props>(({}) => ({ }))
  }
}
