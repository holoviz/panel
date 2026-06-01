import { HTMLBox, HTMLBoxView } from "./layout";
import { Plot } from "@bokehjs/models/plots";
import type * as p from "@bokehjs/core/properties";
import { TickFormatter } from "@bokehjs/models/formatters";
export declare class TrendIndicatorView extends HTMLBoxView {
    model: TrendIndicator;
    containerDiv: HTMLDivElement;
    textDiv: HTMLDivElement;
    titleDiv: HTMLDivElement;
    valueDiv: HTMLDivElement;
    value2Div: HTMLDivElement;
    changeDiv: HTMLElement;
    plotDiv: HTMLDivElement;
    plot: Plot;
    _value_format: string;
    _value_change_format: string;
    initialize(): void;
    connect_signals(): void;
    render(): Promise<void>;
    private setPlot;
    after_layout(): void;
    updateTextFontSize(): void;
    updateTextFontSizeColumn(): void;
    updateTitle(update_fontsize?: boolean): void;
    updateValue(update_fontsize?: boolean): void;
    updateValue2(update_fontsize?: boolean): void;
    updateValueChange(): void;
    updateLayout(): void;
}
export declare namespace TrendIndicator {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        change_formatter: p.Property<TickFormatter>;
        description: p.Property<string>;
        formatter: p.Property<TickFormatter>;
        layout: p.Property<string>;
        source: p.Property<any>;
        plot_x: p.Property<string>;
        plot_y: p.Property<string>;
        plot_color: p.Property<string>;
        plot_type: p.Property<string>;
        pos_color: p.Property<string>;
        neg_color: p.Property<string>;
        title: p.Property<string>;
        value: p.Property<number>;
        value_change: p.Property<number>;
    };
}
export interface TrendIndicator extends TrendIndicator.Attrs {
}
export declare class TrendIndicator extends HTMLBox {
    properties: TrendIndicator.Props;
    constructor(attrs?: Partial<TrendIndicator.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=trend.d.ts.map