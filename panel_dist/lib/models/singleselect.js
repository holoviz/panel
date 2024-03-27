import { select, option } from "@bokehjs/core/dom";
import { isString } from "@bokehjs/core/util/types";
import { InputWidget, InputWidgetView } from "@bokehjs/models/widgets/input_widget";
import * as inputs from "@bokehjs/styles/widgets/inputs.css";
export class SingleSelectView extends InputWidgetView {
    static __name__ = "SingleSelectView";
    connect_signals() {
        super.connect_signals();
        const { value, options, disabled_options, size, disabled } = this.model.properties;
        this.on_change(value, () => this.render_selection());
        this.on_change(options, () => this.render());
        this.on_change(disabled_options, () => this.render());
        this.on_change(size, () => this.render());
        this.on_change(disabled, () => this.render());
    }
    render() {
        super.render();
        this.render_selection();
    }
    _render_input() {
        const options = this.model.options.map((opt) => {
            let value, _label;
            if (isString(opt)) {
                value = _label = opt;
            }
            else {
                [value, _label] = opt;
            }
            const disabled = this.model.disabled_options.includes(value);
            return option({ value, disabled }, _label);
        });
        this.input_el = select({
            multiple: false,
            class: inputs.input,
            name: this.model.name,
            disabled: this.model.disabled,
        }, options);
        this.input_el.style.backgroundImage = "none";
        this.input_el.addEventListener("change", () => this.change_input());
        return this.input_el;
    }
    render_selection() {
        const selected = this.model.value;
        for (const el of this.input_el.querySelectorAll("option")) {
            if (el.value === selected) {
                el.selected = true;
            }
        }
        // Note that some browser implementations might not reduce
        // the number of visible options for size <= 3.
        this.input_el.size = this.model.size;
    }
    change_input() {
        const is_focused = this.el.querySelector("select:focus") != null;
        let value = null;
        for (const el of this.shadow_el.querySelectorAll("option")) {
            if (el.selected) {
                value = el.value;
                break;
            }
        }
        this.model.value = value;
        super.change_input();
        // Restore focus back to the <select> afterwards,
        // so that even if python on_change callback is invoked,
        // focus remains on <select> and one can seamlessly scroll
        // up/down.
        if (is_focused) {
            this.input_el.focus();
        }
    }
}
export class SingleSelect extends InputWidget {
    static __name__ = "SingleSelect";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.widgets";
    static {
        this.prototype.default_view = SingleSelectView;
        this.define(({ Any, List, Int, Nullable, Str }) => ({
            disabled_options: [List(Str), []],
            options: [List(Any), []],
            size: [Int, 4], // 4 is the HTML default
            value: [Nullable(Str), null],
        }));
    }
}
//# sourceMappingURL=singleselect.js.map