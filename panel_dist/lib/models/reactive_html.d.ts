import type * as p from "@bokehjs/core/properties";
import type { LayoutDOM } from "@bokehjs/models/layouts/layout_dom";
import { HTMLBox, HTMLBoxView } from "./layout";
export declare class ReactiveHTMLView extends HTMLBoxView {
    model: ReactiveHTML;
    html: string;
    container: HTMLDivElement;
    _parent: any;
    _changing: boolean;
    _event_listeners: any;
    _mutation_observers: MutationObserver[];
    _script_fns: any;
    _state: any;
    initialize(): void;
    _recursive_connect(model: any, update_children: boolean, path: string): void;
    connect_signals(): void;
    connect_scripts(): void;
    run_script(property: string, silent?: boolean): void;
    get_records(property: string, index?: boolean): any[];
    disconnect_signals(): void;
    remove(): void;
    get child_models(): LayoutDOM[];
    _after_layout(): void;
    render(): void;
    private _send_event;
    private _render_child;
    _render_node(node: any, children: any[]): void;
    private _render_children;
    private _render_html;
    private _render_script;
    private _remove_mutation_observers;
    private _setup_mutation_observers;
    private _remove_event_listeners;
    private _setup_event_listeners;
    private _update;
    private _update_model;
}
export declare namespace ReactiveHTML {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        attrs: p.Property<any>;
        callbacks: p.Property<any>;
        children: p.Property<any>;
        data: p.Property<any>;
        event_params: p.Property<string[]>;
        events: p.Property<any>;
        html: p.Property<string>;
        looped: p.Property<string[]>;
        nodes: p.Property<string[]>;
        scripts: p.Property<any>;
    };
}
export interface ReactiveHTML extends ReactiveHTML.Attrs {
}
export declare class ReactiveHTML extends HTMLBox {
    properties: ReactiveHTML.Props;
    constructor(attrs?: Partial<ReactiveHTML.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=reactive_html.d.ts.map