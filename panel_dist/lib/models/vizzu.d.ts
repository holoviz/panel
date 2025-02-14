import type * as p from "@bokehjs/core/properties";
import { ColumnDataSource } from "@bokehjs/models/sources/column_data_source";
import { ModelEvent } from "@bokehjs/core/bokeh_events";
import type { Attrs } from "@bokehjs/core/types";
import { HTMLBox, HTMLBoxView } from "./layout";
export declare class VizzuEvent extends ModelEvent {
    readonly data: any;
    event_name: string;
    publish: boolean;
    constructor(data: any);
    protected get event_values(): Attrs;
}
export declare class VizzuChartView extends HTMLBoxView {
    model: VizzuChart;
    container: HTMLDivElement;
    update: string[];
    vizzu_view: any;
    _animating: boolean;
    connect_signals(): void;
    get valid_config(): boolean;
    private config;
    private data;
    render(): void;
    remove(): void;
}
export declare namespace VizzuChart {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        animation: p.Property<any>;
        config: p.Property<any>;
        columns: p.Property<any>;
        source: p.Property<ColumnDataSource>;
        duration: p.Property<number>;
        style: p.Property<any>;
        tooltip: p.Property<boolean>;
    };
}
export interface VizzuChart extends VizzuChart.Attrs {
}
export declare class VizzuChart extends HTMLBox {
    properties: VizzuChart.Props;
    constructor(attrs?: Partial<VizzuChart.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=vizzu.d.ts.map