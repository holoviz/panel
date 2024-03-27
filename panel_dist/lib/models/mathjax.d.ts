import type * as p from "@bokehjs/core/properties";
import { Markup } from "@bokehjs/models/widgets/markup";
import { PanelMarkupView } from "./layout";
export declare class MathJaxView extends PanelMarkupView {
    model: MathJax;
    connect_signals(): void;
    render(): void;
}
export declare namespace MathJax {
    type Attrs = p.AttrsOf<Props>;
    type Props = Markup.Props & {
        text: p.Property<string>;
    };
}
export interface MathJax extends MathJax.Attrs {
}
export declare class MathJax extends Markup {
    properties: MathJax.Props;
    constructor(attrs?: Partial<MathJax.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=mathjax.d.ts.map