import {TextAreaInput as PnTextAreaInput, TextAreaInputView as PnTextAreaInputView} from "./textarea_input"
import type * as p from "@bokehjs/core/properties"
import {ModelEvent} from "@bokehjs/core/bokeh_events"
import type {Attrs} from "@bokehjs/core/types"

export class ChatMessageEvent extends ModelEvent {
  constructor(readonly value: string) {
    super()
  }

  override get event_values(): Attrs {
    return {model: this.origin, value: this.value}
  }

  static {
    this.prototype.event_name = "chat_message_event"
  }
}

export class ChatAreaInputView extends PnTextAreaInputView {
  declare model: ChatAreaInput

  override connect_signals(): void {
    super.connect_signals()

    const {value_input} = this.model.properties
    this.on_change(value_input, () => this.update_rows())
  }

  override render(): void {
    super.render()

    this.el.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        if (!event.shiftKey && (event.ctrlKey != this.model.enter_sends)) {
          if (!this.model.disabled_enter) {
            this.model.trigger_event(new ChatMessageEvent(this.model.value_input))
            this.model.value_input = ""
          }
          event.preventDefault()
        } else if (event.ctrlKey && this.model.enter_sends) {
          this.model.value_input += "\n"
          event.preventDefault()
        }
      }
    })
  }
}

export namespace ChatAreaInput {
  export type Attrs = p.AttrsOf<Props>
  export type Props = PnTextAreaInput.Props & {
    disabled_enter: p.Property<boolean>
    enter_sends: p.Property<boolean>
  }
}

export interface ChatAreaInput extends ChatAreaInput.Attrs { }

export class ChatAreaInput extends PnTextAreaInput {
  declare: ChatAreaInput.Props

  constructor(attrs?: Partial<ChatAreaInput.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.chatarea_input"

  static {
    this.prototype.default_view = ChatAreaInputView
    this.define<ChatAreaInput.Props>(({Bool}) => {
      return {
        disabled_enter: [ Bool, false ],
        enter_sends: [ Bool, true ],
      }
    })
  }
}
