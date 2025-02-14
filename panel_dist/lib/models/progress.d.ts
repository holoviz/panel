import type { StyleSheetLike } from "@bokehjs/core/dom";
import type * as p from "@bokehjs/core/properties";
import { HTMLBox, HTMLBoxView } from "./layout";
export declare class ProgressView extends HTMLBoxView {
    model: Progress;
    protected progressEl: HTMLProgressElement;
    connect_signals(): void;
    render(): void;
    stylesheets(): StyleSheetLike[];
    setCSS(): void;
    setValue(): void;
    setMax(): void;
}
export declare namespace Progress {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        active: p.Property<boolean>;
        bar_color: p.Property<string>;
        css: p.Property<string[]>;
        max: p.Property<number | null>;
        value: p.Property<number | null>;
    };
}
export interface Progress extends Progress.Attrs {
}
export declare class Progress extends HTMLBox {
    properties: Progress.Props;
    constructor(attrs?: Partial<Progress.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=progress.d.ts.map