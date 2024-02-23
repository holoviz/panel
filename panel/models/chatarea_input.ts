import { TextAreaInput as PnTextAreaInput, TextAreaInputView as PnTextAreaInputView } from "./textarea_input";
import * as p from "@bokehjs/core/properties";
import { ModelEvent } from "@bokehjs/core/bokeh_events"


export class ShiftEnterKeyDown extends ModelEvent {
  static {
    this.prototype.event_name = "shift_enter_key_down"
  }
}

export class ChatAreaInputView extends PnTextAreaInputView {
  model: ChatAreaInput;

  render(): void {
    super.render()

    this.el.addEventListener("keydown", (event) => {
      if (event.key === 'Enter' && event.shiftKey) {
        this.model.trigger_event(new ShiftEnterKeyDown())
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
