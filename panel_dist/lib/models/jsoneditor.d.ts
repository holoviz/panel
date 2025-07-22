import type * as p from "@bokehjs/core/properties";
import type { StyleSheetLike } from "@bokehjs/core/dom";
import { ModelEvent } from "@bokehjs/core/bokeh_events";
import { HTMLBox, HTMLBoxView } from "./layout";
import type { Attrs } from "@bokehjs/core/types";
export declare class JSONEditEvent extends ModelEvent {
    readonly data: any;
    constructor(data: any);
    protected get event_values(): Attrs;
}
export declare class JSONEditorView extends HTMLBoxView {
    model: JSONEditor;
    editor: any;
    _menu_context: any;
    connect_signals(): void;
    stylesheets(): StyleSheetLike[];
    remove(): void;
    render(): void;
}
export declare namespace JSONEditor {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        css: p.Property<string[]>;
        data: p.Property<any>;
        menu: p.Property<boolean>;
        mode: p.Property<string>;
        search: p.Property<boolean>;
        selection: p.Property<any[]>;
        schema: p.Property<any>;
        templates: p.Property<any[]>;
    };
}
export interface JSONEditor extends JSONEditor.Attrs {
}
export declare class JSONEditor extends HTMLBox {
    properties: JSONEditor.Props;
    constructor(attrs?: Partial<JSONEditor.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=jsoneditor.d.ts.map