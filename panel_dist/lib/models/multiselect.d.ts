import { MultiSelect, MultiSelectView } from "@bokehjs/models/widgets/multiselect";
import { ModelEvent } from "@bokehjs/core/bokeh_events";
import type * as p from "@bokehjs/core/properties";
import type { Attrs } from "@bokehjs/core/types";
export declare class DoubleClickEvent extends ModelEvent {
    readonly option: any;
    constructor(option: any);
    protected get event_values(): Attrs;
}
export declare class CustomMultiSelectView extends MultiSelectView {
    model: CustomMultiSelect;
    render(): void;
}
export declare namespace CustomMultiSelect {
    type Attrs = p.AttrsOf<Props>;
    type Props = MultiSelect.Props;
}
export interface CustomMultiSelect extends CustomMultiSelect.Attrs {
}
export declare class CustomMultiSelect extends MultiSelect {
    properties: CustomMultiSelect.Props;
    __view_type__: CustomMultiSelectView;
    constructor(attrs?: Partial<CustomMultiSelect.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=multiselect.d.ts.map