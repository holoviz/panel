import type * as p from "@bokehjs/core/properties";
import { InputWidget, InputWidgetView } from "@bokehjs/models/widgets/input_widget";
export declare class SingleSelectView extends InputWidgetView {
    model: SingleSelect;
    input_el: HTMLSelectElement;
    connect_signals(): void;
    render(): void;
    _render_input(): HTMLElement;
    render_selection(): void;
    change_input(): void;
}
export declare namespace SingleSelect {
    type Attrs = p.AttrsOf<Props>;
    type Props = InputWidget.Props & {
        disabled_options: p.Property<string[]>;
        options: p.Property<(string | [string, string])[]>;
        size: p.Property<number>;
        value: p.Property<string | null>;
    };
}
export interface SingleSelect extends SingleSelect.Attrs {
}
export declare class SingleSelect extends InputWidget {
    properties: SingleSelect.Props;
    __view_type__: SingleSelectView;
    constructor(attrs?: Partial<SingleSelect.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=singleselect.d.ts.map