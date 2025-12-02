import type * as p from "@bokehjs/core/properties";
import { Markup } from "@bokehjs/models/widgets/markup";
import { PanelMarkupView } from "./layout";
export declare class JSONView extends PanelMarkupView {
    model: JSON;
    connect_signals(): void;
    render(): void;
}
export declare const JSONTheme: import("@bokehjs/core/kinds").Kinds.Enum<"light" | "dark">;
export declare namespace JSON {
    type Attrs = p.AttrsOf<Props>;
    type Props = Markup.Props & {
        css: p.Property<string[]>;
        depth: p.Property<number | null>;
        hover_preview: p.Property<boolean>;
        theme: p.Property<typeof JSONTheme["__type__"]>;
    };
}
export interface JSON extends JSON.Attrs {
}
export declare class JSON extends Markup {
    properties: JSON.Props;
    constructor(attrs?: Partial<JSON.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=json.d.ts.map