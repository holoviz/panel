import { ClickableIcon, ClickableIconView } from "./icon";
export class ButtonIconView extends ClickableIconView {
    static __name__ = "ButtonIconView";
    _click_listener;
    *controls() { }
    update_cursor() {
        this.icon_view.el.style.cursor = this.model.disabled ? "default" : "pointer";
    }
    click() {
        if (this.model.disabled) {
            return;
        }
        super.click();
        const updateState = (value, disabled) => {
            this.model.value = value;
            this.model.disabled = disabled;
        };
        updateState(true, true);
        new Promise(resolve => setTimeout(resolve, this.model.toggle_duration))
            .then(() => {
            updateState(false, false);
        });
    }
}
export class ButtonIcon extends ClickableIcon {
    static __name__ = "ButtonIcon";
    static __module__ = "panel.models.icon";
    constructor(attrs) {
        super(attrs);
    }
    static {
        this.prototype.default_view = ButtonIconView;
        this.define(({ Int }) => ({
            toggle_duration: [Int, 75],
        }));
    }
}
//# sourceMappingURL=button_icon.js.map