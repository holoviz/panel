import type { Dict } from "@bokehjs/core/types";
import type * as p from "@bokehjs/core/properties";
import { Model } from "@bokehjs/model";
import { UIElement } from "@bokehjs/models/ui/ui_element";
import { HTMLBox, HTMLBoxView } from "./layout";
export declare class ReactiveHTMLView extends HTMLBoxView {
    model: ReactiveHTML;
    html: string;
    container: HTMLDivElement;
    protected _changing: boolean;
    protected readonly _event_listeners: Map<string, Map<string, (event: Event) => void>>;
    protected _mutation_observers: MutationObserver[];
    protected _script_fns: Map<string, Function>;
    protected _state: any;
    initialize(): void;
    _recursive_connect(model: Model, update_children: boolean, path: string): void;
    connect_signals(): void;
    connect_scripts(): void;
    run_script(property: string, silent?: boolean): void;
    get_records(property_name: string, index?: boolean): unknown[];
    disconnect_signals(): void;
    remove(): void;
    get child_models(): UIElement[];
    _after_layout(): void;
    render(): void;
    private _send_event;
    private _render_child;
    _render_node(node: string, children: (string | UIElement)[]): void;
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
        attrs: p.Property<Dict<[string, string[], string][]>>;
        callbacks: p.Property<Dict<[string, string][]>>;
        children: p.Property<Dict<(UIElement | string)[] | string>>;
        data: p.Property<Model>;
        event_params: p.Property<string[]>;
        events: p.Property<Dict<Dict<boolean>>>;
        html: p.Property<string>;
        looped: p.Property<string[]>;
        nodes: p.Property<string[]>;
        scripts: p.Property<Dict<string[]>>;
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