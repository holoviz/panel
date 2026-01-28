import type { TooltipView } from "@bokehjs/models/ui/tooltip";
import { Tooltip } from "@bokehjs/models/ui/tooltip";
import type { IterViews } from "@bokehjs/core/build_views";
import type * as p from "@bokehjs/core/properties";
import { RadioButtonGroup as bkRadioButtonGroup, RadioButtonGroupView as bkRadioButtonGroupView } from "@bokehjs/models/widgets/radio_button_group";
export declare class RadioButtonGroupView extends bkRadioButtonGroupView {
    model: RadioButtonGroup;
    protected tooltip: TooltipView | null;
    children(): IterViews;
    connect_signals(): void;
    update_tooltip(): Promise<void>;
    lazy_initialize(): Promise<void>;
    remove(): void;
    render(): void;
}
export declare namespace RadioButtonGroup {
    type Attrs = p.AttrsOf<Props>;
    type Props = bkRadioButtonGroup.Props & {
        tooltip: p.Property<Tooltip | null>;
        tooltip_delay: p.Property<number>;
    };
}
export interface RadioButtonGroup extends RadioButtonGroup.Attrs {
}
export declare class RadioButtonGroup extends bkRadioButtonGroup {
    properties: RadioButtonGroup.Props;
    __view_type__: RadioButtonGroupView;
    static __module__: string;
    constructor(attrs?: Partial<RadioButtonGroup.Attrs>);
}
//# sourceMappingURL=radio_button_group.d.ts.map