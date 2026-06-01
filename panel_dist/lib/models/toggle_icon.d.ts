import { ClickableIcon, ClickableIconView } from "./icon";
import type * as p from "@bokehjs/core/properties";
export declare class ToggleIconView extends ClickableIconView {
    model: ToggleIcon;
    controls(): Generator<never, void, unknown>;
    click(): void;
}
export declare namespace ToggleIcon {
    type Attrs = p.AttrsOf<Props>;
    type Props = ClickableIcon.Props & {};
}
export interface ToggleIcon extends ToggleIcon.Attrs {
}
export declare class ToggleIcon extends ClickableIcon {
    properties: ToggleIcon.Props;
    __view_type__: ToggleIconView;
    static __module__: string;
    constructor(attrs?: Partial<ToggleIcon.Attrs>);
}
//# sourceMappingURL=toggle_icon.d.ts.map