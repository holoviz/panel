import { ModelEvent } from "@bokehjs/core/bokeh_events";
import type * as p from "@bokehjs/core/properties";
import type { Attrs } from "@bokehjs/core/types";
import { Markup } from "@bokehjs/models/widgets/markup";
import { PanelMarkupView } from "./layout";
export declare class DOMEvent extends ModelEvent {
    readonly node: string;
    readonly data: any;
    constructor(node: string, data: any);
    protected get event_values(): Attrs;
}
export declare function htmlDecode(input: string): string | null;
export declare function runScripts(node: any): void;
export declare class HTMLView extends PanelMarkupView {
    model: HTML;
    _event_listeners: any;
    connect_signals(): void;
    protected rerender(): void;
    set_html(html: string | null): void;
    render(): void;
    style_redraw(): void;
    process_tex(): string;
    private contains_tex;
    private _remove_event_listeners;
    private _setup_event_listeners;
}
export declare namespace HTML {
    type Attrs = p.AttrsOf<Props>;
    type Props = Markup.Props & {
        events: p.Property<any>;
        run_scripts: p.Property<boolean>;
    };
}
export interface HTML extends HTML.Attrs {
}
export declare class HTML extends Markup {
    properties: HTML.Props;
    constructor(attrs?: Partial<HTML.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=html.d.ts.map