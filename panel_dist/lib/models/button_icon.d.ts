import { ClickableIcon, ClickableIconView } from "./icon";
import type * as p from "@bokehjs/core/properties";
export declare class ButtonIconView extends ClickableIconView {
    model: ButtonIcon;
    _click_listener: any;
    controls(): Generator<never, void, unknown>;
    update_cursor(): void;
    click(): void;
}
export declare namespace ButtonIcon {
    type Attrs = p.AttrsOf<Props>;
    type Props = ClickableIcon.Props & {
        toggle_duration: p.Property<number>;
    };
}
export interface ButtonIcon extends ButtonIcon.Attrs {
}
export declare class ButtonIcon extends ClickableIcon {
    properties: ButtonIcon.Props;
    __view_type__: ButtonIconView;
    static __module__: string;
    constructor(attrs?: Partial<ButtonIcon.Attrs>);
}
//# sourceMappingURL=button_icon.d.ts.map