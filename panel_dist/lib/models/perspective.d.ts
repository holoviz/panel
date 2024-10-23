import { ModelEvent } from "@bokehjs/core/bokeh_events";
import type { StyleSheetLike } from "@bokehjs/core/dom";
import type * as p from "@bokehjs/core/properties";
import { ColumnDataSource } from "@bokehjs/models/sources/column_data_source";
import { HTMLBox, HTMLBoxView } from "./layout";
import type { Attrs } from "@bokehjs/core/types";
export declare class PerspectiveClickEvent extends ModelEvent {
    readonly config: any;
    readonly column_names: string[];
    readonly row: any[];
    constructor(config: any, column_names: string[], row: any[]);
    protected get event_values(): Attrs;
}
export declare class PerspectiveView extends HTMLBoxView {
    model: Perspective;
    perspective_element: any;
    table: any;
    worker: any;
    _updating: boolean;
    _config_listener: any;
    _current_config: any;
    _current_plugin: string | null;
    _loaded: boolean;
    _plugin_configs: any;
    connect_signals(): void;
    disconnect_signals(): void;
    remove(): void;
    stylesheets(): StyleSheetLike[];
    render(): void;
    sync_config(): boolean;
    get data(): any;
    setData(): void;
    stream(): void;
    patch(): void;
}
export declare namespace Perspective {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        aggregates: p.Property<any>;
        split_by: p.Property<any[] | null>;
        columns: p.Property<any[]>;
        columns_config: p.Property<any>;
        expressions: p.Property<any>;
        editable: p.Property<boolean | null>;
        filters: p.Property<any[] | null>;
        group_by: p.Property<any[] | null>;
        plugin: p.Property<any>;
        plugin_config: p.Property<any>;
        selectable: p.Property<boolean | null>;
        schema: p.Property<any>;
        settings: p.Property<boolean>;
        sort: p.Property<any[] | null>;
        source: p.Property<ColumnDataSource>;
        theme: p.Property<any>;
        title: p.Property<string | null>;
    };
}
export interface Perspective extends Perspective.Attrs {
}
export declare class Perspective extends HTMLBox {
    properties: Perspective.Props;
    constructor(attrs?: Partial<Perspective.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=perspective.d.ts.map