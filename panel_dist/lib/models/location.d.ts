import type * as p from "@bokehjs/core/properties";
import { View } from "@bokehjs/core/view";
import { Model } from "@bokehjs/model";
export declare class LocationView extends View {
    model: Location;
    _hash_listener: any;
    initialize(): void;
    connect_signals(): void;
    remove(): void;
    update(change: string): void;
}
export declare namespace Location {
    type Attrs = p.AttrsOf<Props>;
    type Props = Model.Props & {
        href: p.Property<string>;
        hostname: p.Property<string>;
        pathname: p.Property<string>;
        protocol: p.Property<string>;
        port: p.Property<string>;
        search: p.Property<string>;
        hash: p.Property<string>;
        reload: p.Property<boolean>;
    };
}
export interface Location extends Location.Attrs {
}
export declare class Location extends Model {
    properties: Location.Props;
    static __module__: string;
    constructor(attrs?: Partial<Location.Attrs>);
}
//# sourceMappingURL=location.d.ts.map