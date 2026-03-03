import type * as p from "@bokehjs/core/properties";
import type { Transform } from "sucrase";
import { ReactiveESM, ReactiveESMView } from "./reactive_esm";
declare class AnyWidgetModelAdapter {
    model: AnyWidgetComponent;
    model_changes: any;
    data_changes: any;
    view: AnyWidgetComponentView | null;
    constructor(model: AnyWidgetComponent);
    get(name: any): any;
    set(name: string, value: any): void;
    save_changes(): void;
    on(event: string, cb: () => void): void;
    off(event: string, cb: () => void): void;
}
declare class AnyWidgetAdapter extends AnyWidgetModelAdapter {
    view: AnyWidgetComponentView;
    constructor(view: AnyWidgetComponentView);
    get_child(name: any): HTMLElement | HTMLElement[] | undefined;
}
export declare class AnyWidgetComponentView extends ReactiveESMView {
    model: AnyWidgetComponent;
    adapter: AnyWidgetAdapter;
    destroyer: Promise<((props: any) => void) | null>;
    initialize(): void;
    remove(): void;
    after_rendered(): void;
}
export declare namespace AnyWidgetComponent {
    type Attrs = p.AttrsOf<Props>;
    type Props = ReactiveESM.Props;
}
export interface AnyWidgetComponent extends AnyWidgetComponent.Attrs {
}
export declare class AnyWidgetComponent extends ReactiveESM {
    properties: AnyWidgetComponent.Props;
    sucrase_transforms: Transform[];
    constructor(attrs?: Partial<AnyWidgetComponent.Attrs>);
    protected _render_code(): string;
    protected _run_initializer(initialize: (props: any) => void): void;
    static __module__: string;
}
export {};
//# sourceMappingURL=anywidget_component.d.ts.map