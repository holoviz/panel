import { ClickableIcon, ClickableIconView } from "./icon";
export class ToggleIconView extends ClickableIconView {
    static __name__ = "ToggleIconView";
    *controls() { }
    click() {
        if (this.model.disabled) {
            return;
        }
        super.click();
        this.model.value = !this.model.value;
    }
}
export class ToggleIcon extends ClickableIcon {
    static __name__ = "ToggleIcon";
    static __module__ = "panel.models.icon";
    constructor(attrs) {
        super(attrs);
    }
    static {
        this.prototype.default_view = ToggleIconView;
        this.define(({}) => ({}));
    }
}
//# sourceMappingURL=toggle_icon.js.map