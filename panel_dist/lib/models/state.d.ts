import type * as p from "@bokehjs/core/properties";
import { View } from "@bokehjs/core/view";
import { Model } from "@bokehjs/model";
import { Receiver } from "@bokehjs/protocol/receiver";
export declare class StateView extends View {
    model: State;
}
export declare namespace State {
    type Attrs = p.AttrsOf<Props>;
    type Props = Model.Props & {
        json: p.Property<boolean>;
        state: p.Property<object>;
        values: p.Property<any[]>;
        widgets: p.Property<{
            [key: string]: number;
        }>;
    };
}
export interface State extends State.Attrs {
}
export declare class State extends Model {
    properties: State.Props;
    _receiver: Receiver;
    _cache: {
        [key: string]: string;
    };
    constructor(attrs?: Partial<State.Attrs>);
    apply_state(state: any): void;
    _receive_json(result: string, path: string): void;
    set_state(widget: any, value: any): void;
    static __module__: string;
}
//# sourceMappingURL=state.d.ts.map