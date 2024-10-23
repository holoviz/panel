import { Select, SelectView } from "@bokehjs/models/widgets/select";
export class CustomSelectView extends SelectView {
    static __name__ = "CustomSelectView";
    connect_signals() {
        super.connect_signals();
        const { disabled_options } = this.model.properties;
        this.on_change(disabled_options, () => this._update_disabled_options());
    }
    options_el() {
        const opts = super.options_el();
        const { disabled_options } = this.model;
        opts.forEach((element) => {
            // XXX: what about HTMLOptGroupElement?
            if (element instanceof HTMLOptionElement && disabled_options.includes(element.value)) {
                element.setAttribute("disabled", "true");
            }
        });
        return opts;
    }
    _update_disabled_options() {
        for (const element of this.input_el.options) {
            if (this.model.disabled_options.includes(element.value)) {
                element.setAttribute("disabled", "true");
            }
            else {
                element.removeAttribute("disabled");
            }
        }
    }
}
export class CustomSelect extends Select {
    static __name__ = "CustomSelect";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.widgets";
    static {
        this.prototype.default_view = CustomSelectView;
        this.define(({ List, Str }) => {
            return {
                disabled_options: [List(Str), []],
            };
        });
    }
}
//# sourceMappingURL=customselect.js.map