import type { TooltipView } from "@bokehjs/models/ui/tooltip";
import { Tooltip } from "@bokehjs/models/ui/tooltip";
import type { IterViews } from "@bokehjs/core/build_views";
import type * as p from "@bokehjs/core/properties";
import { Button as BkButton, ButtonView as BkButtonView } from "@bokehjs/models/widgets/button";
export declare class ButtonView extends BkButtonView {
    model: Button;
    protected tooltip: TooltipView | null;
    children(): IterViews;
    connect_signals(): void;
    update_tooltip(): Promise<void>;
    lazy_initialize(): Promise<void>;
    remove(): void;
    render(): void;
}
export declare namespace Button {
    type Attrs = p.AttrsOf<Props>;
    type Props = BkButton.Props & {
        tooltip: p.Property<Tooltip | null>;
        tooltip_delay: p.Property<number>;
    };
}
export interface Button extends Button.Attrs {
}
export declare class Button extends BkButton {
    properties: Button.Props;
    __view_type__: ButtonView;
    static __module__: string;
    constructor(attrs?: Partial<Button.Attrs>);
}
//# sourceMappingURL=button.d.ts.map