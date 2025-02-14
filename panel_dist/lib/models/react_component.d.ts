import type * as p from "@bokehjs/core/properties";
import type { Transform } from "sucrase";
import { ReactiveESM, ReactiveESMView, model_getter, model_setter } from "./reactive_esm";
export declare class ReactComponentView extends ReactiveESMView {
    model: ReactComponent;
    style_cache: HTMLHeadElement;
    model_getter: typeof model_getter;
    model_setter: typeof model_setter;
    render_esm(): void;
    after_rendered(): void;
    protected _render_code(): string;
}
export declare namespace ReactComponent {
    type Attrs = p.AttrsOf<Props>;
    type Props = ReactiveESM.Props;
}
export interface ReactComponent extends ReactComponent.Attrs {
}
export declare class ReactComponent extends ReactiveESM {
    properties: ReactComponent.Props;
    sucrase_transforms: Transform[];
    constructor(attrs?: Partial<ReactComponent.Attrs>);
    get usesMui(): boolean;
    compile(): string | null;
    static __module__: string;
}
//# sourceMappingURL=react_component.d.ts.map