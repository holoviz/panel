import type * as p from "@bokehjs/core/properties";
import { ModelEvent } from "@bokehjs/core/bokeh_events";
import { LayoutDOM, LayoutDOMView } from "@bokehjs/models/layouts/layout_dom";
import type { Attrs } from "@bokehjs/core/types";
export declare class VegaEvent extends ModelEvent {
    readonly data: any;
    constructor(data: any);
    protected get event_values(): Attrs;
}
export declare class VegaPlotView extends LayoutDOMView {
    model: VegaPlot;
    vega_view: any;
    container: HTMLDivElement;
    _callbacks: string[];
    _connected: string[];
    _replot: any;
    _resize: any;
    _rendered: boolean;
    connect_signals(): void;
    _connect_sources(): void;
    remove(): void;
    _dispatch_event(name: string, value: any): void;
    _fetch_datasets(): any;
    get child_models(): LayoutDOM[];
    render(): void;
    _plot(): void;
    after_layout(): void;
    resize_view(view: any): void;
}
export declare namespace VegaPlot {
    type Attrs = p.AttrsOf<Props>;
    type Props = LayoutDOM.Props & {
        data: p.Property<any>;
        data_sources: p.Property<any>;
        events: p.Property<string[]>;
        show_actions: p.Property<boolean>;
        theme: p.Property<string | null>;
        throttle: p.Property<any>;
    };
}
export interface VegaPlot extends VegaPlot.Attrs {
}
export declare class VegaPlot extends LayoutDOM {
    properties: VegaPlot.Props;
    constructor(attrs?: Partial<VegaPlot.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=vega.d.ts.map