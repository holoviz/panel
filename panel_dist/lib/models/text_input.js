import { TextInput as BkTextInput, TextInputView as BkTextInputView } from "@bokehjs/models/widgets/text_input";
import { ModelEvent } from "@bokehjs/core/bokeh_events";
export class EnterEvent extends ModelEvent {
    value_input;
    static __name__ = "EnterEvent";
    constructor(value_input) {
        super();
        this.value_input = value_input;
    }
    get event_values() {
        return { model: this.origin, value_input: this.value_input };
    }
    static {
        this.prototype.event_name = "enter-pressed";
    }
}
export class TextInputView extends BkTextInputView {
    static __name__ = "TextInputView";
    _keyup(event) {
        super._keyup(event);
        if (event.key == "Enter") {
            const { value_input } = this.model;
            this.model.trigger_event(new EnterEvent(value_input));
        }
    }
}
export class TextInput extends BkTextInput {
    static __name__ = "TextInput";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.widgets";
    static {
        this.prototype.default_view = TextInputView;
        this.define(({}) => ({}));
    }
}
//# sourceMappingURL=text_input.js.map