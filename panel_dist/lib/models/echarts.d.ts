import { ModelEvent } from "@bokehjs/core/bokeh_events";
import type * as p from "@bokehjs/core/properties";
import type { Attrs } from "@bokehjs/core/types";
import { HTMLBox, HTMLBoxView } from "./layout";
export declare class EChartsEvent extends ModelEvent {
    readonly type: string;
    readonly data: any;
    readonly query: string;
    constructor(type: string, data: any, query: string);
    protected get event_values(): Attrs;
}
export declare class EChartsView extends HTMLBoxView {
    model: ECharts;
    container: Element;
    _chart: any;
    _callbacks: Array<any>[];
    connect_signals(): void;
    render(): void;
    remove(): void;
    after_layout(): void;
    _plot(): void;
    _resize(): void;
    _subscribe(): void;
}
export declare namespace ECharts {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        data: p.Property<any>;
        options: p.Property<any>;
        event_config: p.Property<any>;
        js_events: p.Property<any>;
        renderer: p.Property<string>;
        theme: p.Property<string>;
    };
}
export interface ECharts extends ECharts.Attrs {
}
export declare class ECharts extends HTMLBox {
    properties: ECharts.Props;
    constructor(attrs?: Partial<ECharts.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=echarts.d.ts.map