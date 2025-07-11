import type { StyleSheetLike } from "@bokehjs/core/dom";
import type * as p from "@bokehjs/core/properties";
import { HTMLBox, HTMLBoxView } from "./layout";
export declare class IPyWidgetView extends HTMLBoxView {
    model: IPyWidget;
    private ipyview;
    private ipychildren;
    private manager;
    initialize(): void;
    remove(): void;
    protected _ipy_stylesheets(): StyleSheetLike[];
    stylesheets(): StyleSheetLike[];
    render(): void;
}
export declare namespace IPyWidget {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        bundle: p.Property<any>;
    };
}
export interface IPyWidget extends IPyWidget.Attrs {
}
export declare class IPyWidget extends HTMLBox {
    properties: IPyWidget.Props;
    constructor(attrs?: Partial<IPyWidget.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=ipywidget.d.ts.map