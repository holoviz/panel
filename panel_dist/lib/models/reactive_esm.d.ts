import type { Transform } from "sucrase";
import { ModelEvent } from "@bokehjs/core/bokeh_events";
import type { StyleSheetLike } from "@bokehjs/core/dom";
import type * as p from "@bokehjs/core/properties";
import type { Attrs } from "@bokehjs/core/types";
import type { LayoutDOM } from "@bokehjs/models/layouts/layout_dom";
import type { UIElement, UIElementView } from "@bokehjs/models/ui/ui_element";
import { HTMLBox, HTMLBoxView } from "./layout";
export declare class DataEvent extends ModelEvent {
    readonly data: unknown;
    constructor(data: unknown);
    protected get event_values(): Attrs;
}
export declare class ESMEvent extends DataEvent {
    static from_values(values: object): ESMEvent;
}
export declare function model_getter(target: ReactiveESMView, name: string): any;
export declare function model_setter(target: ReactiveESMView, name: string, value: any): boolean;
export declare class ReactiveESMView extends HTMLBoxView {
    model: ReactiveESM;
    container: HTMLDivElement;
    accessed_properties: string[];
    accessed_children: string[];
    compiled_module: any;
    model_proxy: any;
    render_module: Promise<any> | null;
    _changing: boolean;
    _child_callbacks: Map<string, ((new_views: UIElementView[]) => void)[]>;
    _child_rendered: Map<UIElementView, boolean>;
    _event_handlers: ((data: unknown) => void)[];
    _lifecycle_handlers: Map<string, (() => void)[]>;
    _module_cache: Map<string, any>;
    _rendered: boolean;
    _stale_children: boolean;
    initialize(): void;
    lazy_initialize(): Promise<void>;
    stylesheets(): StyleSheetLike[];
    connect_signals(): void;
    disconnect_signals(): void;
    on_event(callback: (data: unknown) => void): void;
    remove_on_event(callback: (data: unknown) => void): boolean;
    get_child_view(model: UIElement): UIElementView | undefined;
    get render_fn(): ((props: any) => any) | null;
    get child_models(): LayoutDOM[];
    render_error(error: SyntaxError): void;
    render(): void;
    protected _render_code(): string;
    after_rendered(): void;
    render_esm(): void;
    render_children(): void;
    remove(): void;
    after_resize(): void;
    after_layout(): void;
    protected _lookup_child(child_view: UIElementView): string | null;
    update_children(): Promise<void>;
    on_child_render(child: string, callback: (new_views: UIElementView[]) => void): void;
    remove_on_child_render(child: string): void;
}
export declare namespace ReactiveESM {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        bundle: p.Property<string | null>;
        children: p.Property<any>;
        class_name: p.Property<string>;
        data: p.Property<any>;
        dev: p.Property<boolean>;
        esm: p.Property<string>;
        importmap: p.Property<any>;
    };
}
export interface ReactiveESM extends ReactiveESM.Attrs {
}
export declare class ReactiveESM extends HTMLBox {
    properties: ReactiveESM.Props;
    compiled: string | null;
    compiled_module: Promise<any> | null;
    compile_error: Error | null;
    model_proxy: any;
    sucrase_transforms: Transform[];
    _destroyer: any | null;
    _esm_watchers: any;
    constructor(attrs?: Partial<ReactiveESM.Attrs>);
    initialize(): void;
    connect_signals(): void;
    watch(view: ReactiveESMView | null, prop: string, cb: any): void;
    unwatch(view: ReactiveESMView | null, prop: string, cb: any): boolean;
    disconnect_watchers(view: ReactiveESMView): void;
    protected _declare_importmap(): void;
    protected _run_initializer(initialize: (props: any) => any): void;
    destroy(): void;
    compile(): string | null;
    recompile(): Promise<void>;
    static __module__: string;
}
//# sourceMappingURL=reactive_esm.d.ts.map