import type * as p from "@bokehjs/core/properties";
import { LayoutDOM, LayoutDOMView } from "@bokehjs/models/layouts/layout_dom";
import { ColumnDataSource } from "@bokehjs/models/sources/column_data_source";
export declare class DeckGLPlotView extends LayoutDOMView {
    model: DeckGLPlot;
    jsonConverter: any;
    deckGL: any;
    _connected: any[];
    _map: any;
    _layer_map: any;
    _view_cb: any;
    _initialized: boolean;
    connect_signals(): void;
    remove(): void;
    _update_layers(): void;
    _connect_sources(render?: boolean): void;
    initialize(): void;
    _update_data(render?: boolean): void;
    _on_click_event(event: any): void;
    _on_hover_event(event: any): void;
    _on_viewState_event(event: any): void;
    get child_models(): LayoutDOM[];
    getData(): any;
    _sync_viewstate(event: any): void;
    rerender_(): void;
    updateDeck(): void;
    createDeck({ mapboxApiKey, container, jsonInput, tooltip }: any): void;
    render(): void;
    resize(): void;
    after_layout(): void;
    after_resize(): void;
}
export declare namespace DeckGLPlot {
    type Attrs = p.AttrsOf<Props>;
    type Props = LayoutDOM.Props & {
        data: p.Property<any>;
        data_sources: p.Property<ColumnDataSource[]>;
        initialViewState: p.Property<any>;
        layers: p.Property<any[]>;
        mapbox_api_key: p.Property<string>;
        tooltip: p.Property<any>;
        configuration: p.Property<string>;
        clickState: p.Property<any>;
        hoverState: p.Property<any>;
        throttle: p.Property<any>;
        viewState: p.Property<any>;
    };
}
export interface DeckGLPlot extends DeckGLPlot.Attrs {
}
export declare class DeckGLPlot extends LayoutDOM {
    properties: DeckGLPlot.Props;
    constructor(attrs?: Partial<DeckGLPlot.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=deckgl.d.ts.map