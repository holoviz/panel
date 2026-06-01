import { TextAreaInput as BkTextAreaInput, TextAreaInputView as BkTextAreaInputView } from "@bokehjs/models/widgets/textarea_input";
export class TextAreaInputView extends BkTextAreaInputView {
    static __name__ = "TextAreaInputView";
    connect_signals() {
        super.connect_signals();
        const { value, max_rows } = this.model.properties;
        this.on_change([max_rows, value], () => this.update_rows());
    }
    update_rows() {
        if (!this.model.auto_grow) {
            return;
        }
        // Use this.el directly to access the textarea element
        const textarea = this.input_el;
        const textLines = textarea.value.split("\n");
        const numRows = Math.max(textLines.length, this.model.rows, 1);
        textarea.rows = Math.min(numRows, this.model.max_rows || Infinity);
    }
    render() {
        super.render();
        this.update_rows();
        this.el.addEventListener("input", () => {
            this.update_rows();
        });
    }
}
export class TextAreaInput extends BkTextAreaInput {
    static __name__ = "TextAreaInput";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.widgets";
    static {
        this.prototype.default_view = TextAreaInputView;
        this.define(({ Bool, Int, Nullable }) => ({
            auto_grow: [Bool, false],
            max_rows: [Nullable(Int), null],
        }));
    }
}
//# sourceMappingURL=textarea_input.js.map