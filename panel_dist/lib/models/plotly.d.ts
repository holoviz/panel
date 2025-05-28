import { ModelEvent } from "@bokehjs/core/bokeh_events";
import type { StyleSheetLike } from "@bokehjs/core/dom";
import type * as p from "@bokehjs/core/properties";
import type { Attrs } from "@bokehjs/core/types";
import { HTMLBox, HTMLBoxView } from "./layout";
export declare class PlotlyEvent extends ModelEvent {
    readonly data: any;
    constructor(data: any);
    protected get event_values(): Attrs;
}
interface PlotlyHTMLElement extends HTMLDivElement {
    _fullLayout: any;
    _hoverdata: any;
    layout: any;
    on(event: "plotly_relayout", callback: (eventData: any) => void): void;
    on(event: "plotly_relayouting", callback: (eventData: any) => void): void;
    on(event: "plotly_restyle", callback: (eventData: any) => void): void;
    on(event: "plotly_click", callback: (eventData: any) => void): void;
    on(event: "plotly_doubleclick", callback: (eventData: any) => void): void;
    on(event: "plotly_hover", callback: (eventData: any) => void): void;
    on(event: "plotly_clickannotation", callback: (eventData: any) => void): void;
    on(event: "plotly_selected", callback: (eventData: any) => void): void;
    on(event: "plotly_deselect", callback: () => void): void;
    on(event: "plotly_unhover", callback: () => void): void;
}
export declare class PlotlyPlotView extends HTMLBoxView {
    model: PlotlyPlot;
    _setViewport: Function;
    _settingViewport: boolean;
    _plotInitialized: boolean;
    _rendered: boolean;
    _reacting: boolean;
    _relayouting: boolean;
    _hoverdata: any;
    container: PlotlyHTMLElement;
    _watched_sources: string[];
    _end_relayouting: (() => void) & {
        clear(): void;
    } & {
        flush(): void;
    };
    _throttled_resize: any;
    initialize(): void;
    connect_signals(): void;
    stylesheets(): StyleSheetLike[];
    remove(): void;
    render(): void;
    style_redraw(): void;
    resize_layout(): void;
    after_layout(): void;
    _trace_data(): any;
    _layout_data(): any;
    _install_callbacks(): void;
    plot(new_plot?: boolean): Promise<void>;
    _get_trace(index: number, update: boolean): any;
    _updateViewportFromProperty(): void;
    _updateViewportProperty(): void;
    _updateSetViewportFunction(): void;
}
export declare namespace PlotlyPlot {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        data: p.Property<any[]>;
        frames: p.Property<any[] | null>;
        layout: p.Property<any>;
        config: p.Property<any>;
        data_sources: p.Property<any[]>;
        relayout: p.Property<any>;
        restyle: p.Property<any>;
        relayout_data: p.Property<any>;
        restyle_data: p.Property<any>;
        viewport: p.Property<any>;
        viewport_update_policy: p.Property<string>;
        viewport_update_throttle: p.Property<number>;
        _render_count: p.Property<number>;
    };
}
export interface PlotlyPlot extends PlotlyPlot.Attrs {
}
export declare class PlotlyPlot extends HTMLBox {
    properties: PlotlyPlot.Props;
    constructor(attrs?: Partial<PlotlyPlot.Attrs>);
    static __module__: string;
}
export {};
//# sourceMappingURL=plotly.d.ts.map