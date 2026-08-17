import { Tooltip } from "@bokehjs/models/ui/tooltip";
import { build_view } from "@bokehjs/core/build_views";
import { Button as BkButton, ButtonView as BkButtonView } from "@bokehjs/models/widgets/button";
export class ButtonView extends BkButtonView {
    static __name__ = "ButtonView";
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
export class Button extends BkButton {
    static __name__ = "Button";
    static __module__ = "panel.models.widgets";
    constructor(attrs) {
        super(attrs);
    }
    static {
        this.prototype.default_view = ButtonView;
        this.define(({ Nullable, Ref, Float }) => ({
            tooltip: [Nullable(Ref(Tooltip)), null],
            tooltip_delay: [Float, 500],
        }));
    }
}
//# sourceMappingURL=button.js.map