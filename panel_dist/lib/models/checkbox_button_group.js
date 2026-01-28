import { Tooltip } from "@bokehjs/models/ui/tooltip";
import { build_view } from "@bokehjs/core/build_views";
import { CheckboxButtonGroup as bkCheckboxButtonGroup, CheckboxButtonGroupView as bkCheckboxButtonGroupView, } from "@bokehjs/models/widgets/checkbox_button_group";
export class CheckboxButtonGroupView extends bkCheckboxButtonGroupView {
    static __name__ = "CheckboxButtonGroupView";
    tooltip;
    *children() {
        yield* super.children();
        if (this.tooltip != null) {
            yield this.tooltip;
        }
    }
    connect_signals() {
        super.connect_signals();
        const { tooltip } = this.model.properties;
        this.on_change(tooltip, () => this.update_tooltip());
    }
    async update_tooltip() {
        if (this.tooltip != null) {
            this.tooltip.remove();
        }
        const { tooltip } = this.model;
        if (tooltip != null) {
            this.tooltip = await build_view(tooltip, { parent: this });
        }
    }
    async lazy_initialize() {
        await super.lazy_initialize();
        const { tooltip } = this.model;
        if (tooltip != null) {
            this.tooltip = await build_view(tooltip, { parent: this });
        }
    }
    remove() {
        this.tooltip?.remove();
        super.remove();
    }
    render() {
        super.render();
        const toggle = (visible) => {
            this.tooltip?.model.setv({
                visible,
            });
        };
        let timer;
        this.el.addEventListener("mouseenter", () => {
            timer = setTimeout(() => toggle(true), this.model.tooltip_delay);
        });
        this.el.addEventListener("mouseleave", () => {
            clearTimeout(timer);
            toggle(false);
        });
    }
}
export class CheckboxButtonGroup extends bkCheckboxButtonGroup {
    static __name__ = "CheckboxButtonGroup";
    static __module__ = "panel.models.widgets";
    constructor(attrs) {
        super(attrs);
    }
    static {
        this.prototype.default_view = CheckboxButtonGroupView;
        this.define(({ Nullable, Ref, Float }) => ({
            tooltip: [Nullable(Ref(Tooltip)), null],
            tooltip_delay: [Float, 500],
        }));
    }
}
//# sourceMappingURL=checkbox_button_group.js.map