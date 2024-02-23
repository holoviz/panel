import { TextAreaInput as PnTextAreaInput, TextAreaInputView as PnTextAreaInputView } from "./textarea_input";
import * as p from "@bokehjs/core/properties";
import { ModelEvent } from "@bokehjs/core/bokeh_events"
import type {Attrs} from "@bokehjs/core/types"


export class ChatMessageEvent extends ModelEvent {
  constructor(readonly value: string) {
    super()
  }

  protected get event_values(): Attrs {
    return {model: this.origin, value: this.value}
  }

  static {
    this.prototype.event_name = "chat_message_event"
  }
}

export class ChatAreaInputView extends PnTextAreaInputView {
  model: ChatAreaInput;

  render(): void {
    super.render()

    this.el.addEventListener("keydown", (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        this.model.trigger_event(new ChatMessageEvent(this.model.value_input))
        this.model.value_input = ""
        event.preventDefault();
      }
    });
  }
}

export namespace ChatAreaInput {
  export type Attrs = p.AttrsOf<Props>;
  export type Props = PnTextAreaInput.Props & {
  };
}

export interface ChatAreaInput extends ChatAreaInput.Attrs { }

export class ChatAreaInput extends PnTextAreaInput {
  properties: ChatAreaInput.Props;

  constructor(attrs?: Partial<ChatAreaInput.Attrs>) {
    super(attrs);
  }

  static __module__ = "panel.models.chatarea_input";

  static {
    this.prototype.default_view = ChatAreaInputView;

    this.define<ChatAreaInput.Props>(({ }) => ({
    }));
  }
}
