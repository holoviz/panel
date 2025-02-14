import { ModelEvent } from "@bokehjs/core/bokeh_events";
import type { StyleSheetLike } from "@bokehjs/core/dom";
import type * as p from "@bokehjs/core/properties";
import type { Attrs, Dict } from "@bokehjs/core/types";
import { Markup } from "@bokehjs/models/widgets/markup";
import { PanelMarkupView } from "./layout";
export declare class HTMLStreamEvent extends ModelEvent {
    readonly model: HTML;
    readonly patch: string;
    readonly start: number;
    constructor(model: HTML, patch: string, start: number);
    protected get event_values(): Attrs;
    static from_values(values: object): HTMLStreamEvent;
}
export declare class DOMEvent extends ModelEvent {
    readonly node: string;
    readonly data: unknown;
    constructor(node: string, data: unknown);
    protected get event_values(): Attrs;
}
export declare function html_decode(input: string): string | null;
export declare function run_scripts(node: Element): void;
export declare class HTMLView extends PanelMarkupView {
    model: HTML;
    _buffer: string | null;
    protected readonly _event_listeners: Map<string, Map<string, (event: Event) => void>>;
    connect_signals(): void;
    stylesheets(): StyleSheetLike[];
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
        events: p.Property<Dict<string[]>>;
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