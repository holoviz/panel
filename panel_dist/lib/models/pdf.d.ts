import type * as p from "@bokehjs/core/properties";
import { Markup } from "@bokehjs/models/widgets/markup";
import { PanelMarkupView } from "./layout";
export declare class PDFView extends PanelMarkupView {
    model: PDF;
    connect_signals(): void;
    render(): void;
    update(): void;
    protected convert_base64_to_blob(): Blob;
}
export declare namespace PDF {
    type Attrs = p.AttrsOf<Props>;
    type Props = Markup.Props & {
        embed: p.Property<boolean>;
        start_page: p.Property<number>;
    };
}
export interface PDF extends PDF.Attrs {
}
export declare class PDF extends Markup {
    properties: PDF.Props;
    constructor(attrs?: Partial<PDF.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=pdf.d.ts.map