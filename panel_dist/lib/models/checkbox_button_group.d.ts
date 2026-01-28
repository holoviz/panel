import type { TooltipView } from "@bokehjs/models/ui/tooltip";
import { Tooltip } from "@bokehjs/models/ui/tooltip";
import type { IterViews } from "@bokehjs/core/build_views";
import type * as p from "@bokehjs/core/properties";
import { CheckboxButtonGroup as bkCheckboxButtonGroup, CheckboxButtonGroupView as bkCheckboxButtonGroupView } from "@bokehjs/models/widgets/checkbox_button_group";
export declare class CheckboxButtonGroupView extends bkCheckboxButtonGroupView {
    model: CheckboxButtonGroup;
    protected tooltip: TooltipView | null;
    children(): IterViews;
    connect_signals(): void;
    update_tooltip(): Promise<void>;
    lazy_initialize(): Promise<void>;
    remove(): void;
    render(): void;
}
export declare namespace CheckboxButtonGroup {
    type Attrs = p.AttrsOf<Props>;
    type Props = bkCheckboxButtonGroup.Props & {
        tooltip: p.Property<Tooltip | null>;
        tooltip_delay: p.Property<number>;
    };
}
export interface CheckboxButtonGroup extends CheckboxButtonGroup.Attrs {
}
export declare class CheckboxButtonGroup extends bkCheckboxButtonGroup {
    properties: CheckboxButtonGroup.Props;
    __view_type__: CheckboxButtonGroupView;
    static __module__: string;
    constructor(attrs?: Partial<CheckboxButtonGroup.Attrs>);
}
//# sourceMappingURL=checkbox_button_group.d.ts.map