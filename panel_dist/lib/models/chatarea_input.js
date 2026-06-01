import { TextAreaInput as PnTextAreaInput, TextAreaInputView as PnTextAreaInputView } from "./textarea_input";
import { ModelEvent } from "@bokehjs/core/bokeh_events";
export class ChatMessageEvent extends ModelEvent {
    value;
    static __name__ = "ChatMessageEvent";
    constructor(value) {
        super();
        this.value = value;
    }
    get event_values() {
        return { model: this.origin, value: this.value };
    }
    static {
        this.prototype.event_name = "chat_message_event";
    }
}
export class ChatAreaInputView extends PnTextAreaInputView {
    static __name__ = "ChatAreaInputView";
    connect_signals() {
        super.connect_signals();
        const { value_input } = this.model.properties;
        this.on_change(value_input, () => this.update_rows());
    }
    render() {
        super.render();
        this.el.addEventListener("keydown", (event) => {
            if (event.key === "Enter") {
                if (!event.shiftKey && (event.ctrlKey != this.model.enter_sends)) {
                    if (!this.model.disabled_enter) {
                        this.model.trigger_event(new ChatMessageEvent(this.model.value_input));
                        this.model.value_input = "";
                    }
                    event.preventDefault();
                }
                else if (event.ctrlKey && this.model.enter_sends) {
                    this.model.value_input += "\n";
                    event.preventDefault();
                }
            }
        });
    }
}
export class ChatAreaInput extends PnTextAreaInput {
    static __name__ = "ChatAreaInput";
    declare;
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.chatarea_input";
    static {
        this.prototype.default_view = ChatAreaInputView;
        this.define(({ Bool }) => {
            return {
                disabled_enter: [Bool, false],
                enter_sends: [Bool, true],
            };
        });
    }
}
//# sourceMappingURL=chatarea_input.js.map