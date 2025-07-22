import { Select, SelectView } from "@bokehjs/models/widgets/select";
import type * as p from "@bokehjs/core/properties";
export declare class CustomSelectView extends SelectView {
    model: CustomSelect;
    connect_signals(): void;
    protected options_el(): HTMLOptionElement[] | HTMLOptGroupElement[];
    protected _update_disabled_options(): void;
}
export declare namespace CustomSelect {
    type Attrs = p.AttrsOf<Props>;
    type Props = Select.Props & {
        disabled_options: p.Property<string[]>;
    };
}
export interface CustomSelect extends CustomSelect.Attrs {
}
export declare class CustomSelect extends Select {
    properties: CustomSelect.Props;
    __view_type__: CustomSelectView;
    constructor(attrs?: Partial<CustomSelect.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=customselect.d.ts.map