import type * as p from "@bokehjs/core/properties";
import { ModelEvent } from "@bokehjs/core/bokeh_events";
import type { Attrs } from "@bokehjs/core/types";
import { HTMLBox, HTMLBoxView } from "./layout";
export declare class KeystrokeEvent extends ModelEvent {
    readonly key: string;
    constructor(key: string);
    protected get event_values(): Attrs;
}
export declare class TerminalView extends HTMLBoxView {
    model: Terminal;
    term: any;
    webLinksAddon: any;
    container: HTMLDivElement;
    _rendered: boolean;
    connect_signals(): void;
    render(): void;
    getNewTerminal(): any;
    getNewWebLinksAddon(): any;
    handleOnData(value: string): void;
    write(): void;
    clear(): void;
    fit(): void;
    after_layout(): void;
}
export declare namespace Terminal {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        options: p.Property<any>;
        output: p.Property<string>;
        ncols: p.Property<number>;
        nrows: p.Property<number>;
        _clears: p.Property<number>;
    };
}
export interface Terminal extends Terminal.Attrs {
}
export declare class Terminal extends HTMLBox {
    properties: Terminal.Props;
    constructor(attrs?: Partial<Terminal.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=terminal.d.ts.map