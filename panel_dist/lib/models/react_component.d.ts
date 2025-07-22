import type { StyleSheetLike } from "@bokehjs/core/dom";
import { InlineStyleSheet } from "@bokehjs/core/dom";
import type { CSSStyles, CSSStyleSheetDecl } from "@bokehjs/core/css";
import type * as p from "@bokehjs/core/properties";
import type { Transform } from "sucrase";
import { ReactiveESM, ReactiveESMView, model_getter, model_setter } from "./reactive_esm";
export declare class HostedStyleSheet extends InlineStyleSheet {
    readonly persistent: boolean;
    host_id: string;
    constructor(css?: string | CSSStyleSheetDecl, id?: string, persistent?: boolean, host_id?: string);
    replace(css: string, styles?: CSSStyles): void;
    prepend(css: string, styles?: CSSStyles): void;
    append(css: string, styles?: CSSStyles): void;
}
export declare class ReactComponentView extends ReactiveESMView {
    model: ReactComponent;
    style_cache: HTMLHeadElement;
    model_getter: typeof model_getter;
    model_setter: typeof model_setter;
    react_root: any;
    _force_update_callbacks: (() => void)[];
    initialize(): void;
    get use_shadow_dom(): boolean;
    render_esm(): void;
    on_force_update(cb: () => void): void;
    force_update(): void;
    remove(): void;
    get root_view(): ReactComponentView;
    protected _apply_stylesheets(stylesheets: StyleSheetLike[]): void;
    render(): void;
    r_after_render(): void;
    _update_layout(): void;
    update_children(): Promise<void>;
    _on_mounted(): void;
    patch_container(container: HTMLDivElement): void;
    after_rendered(): void;
}
export declare namespace ReactComponent {
    type Attrs = p.AttrsOf<Props>;
    type Props = ReactiveESM.Props & {
        root_node: p.Property<string | null>;
        use_shadow_dom: p.Property<boolean>;
    };
}
export interface ReactComponent extends ReactComponent.Attrs {
}
export declare class ReactComponent extends ReactiveESM {
    properties: ReactComponent.Props;
    sucrase_transforms: Transform[];
    constructor(attrs?: Partial<ReactComponent.Attrs>);
    get usesMui(): boolean;
    protected _render_code(): string;
    compile(): string | null;
    protected get _render_cache_key(): string;
    static __module__: string;
}
//# sourceMappingURL=react_component.d.ts.map