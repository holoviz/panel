import type * as p from "@bokehjs/core/properties";
import { HTMLBox, HTMLBoxView } from "./layout";
import type { Ace } from "ace-code";
declare type ModeList = {
    getModeForPath(path: string): {
        mode: string;
    };
};
export declare class AcePlotView extends HTMLBoxView {
    model: AcePlot;
    protected _editor: Ace.Editor;
    protected _langTools: unknown;
    protected _modelist: ModeList;
    protected _container: HTMLDivElement;
    connect_signals(): void;
    render(): void;
    _update_code_from_model(): void;
    _update_print_margin(): void;
    _update_code_from_editor(): void;
    _update_code_input_from_editor(): void;
    _update_theme(): void;
    _update_filename(): void;
    _update_language(): void;
    _add_annotations(): void;
    after_layout(): void;
}
export declare namespace AcePlot {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        code: p.Property<string>;
        code_input: p.Property<string>;
        on_keyup: p.Property<boolean>;
        language: p.Property<string>;
        filename: p.Property<string | null>;
        indent: p.Property<number>;
        theme: p.Property<string>;
        annotations: p.Property<any[]>;
        print_margin: p.Property<boolean>;
        readonly: p.Property<boolean>;
        soft_tabs: p.Property<boolean>;
    };
}
export interface AcePlot extends AcePlot.Attrs {
}
export declare class AcePlot extends HTMLBox {
    properties: AcePlot.Props;
    constructor(attrs?: Partial<AcePlot.Attrs>);
    static __module__: string;
}
export {};
//# sourceMappingURL=ace.d.ts.map