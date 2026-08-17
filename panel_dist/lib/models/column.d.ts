import { ModelEvent } from "@bokehjs/core/bokeh_events";
import type * as p from "@bokehjs/core/properties";
import type { Attrs } from "@bokehjs/core/types";
import type { EventCallback } from "@bokehjs/model";
import { Column as BkColumn, ColumnView as BkColumnView } from "@bokehjs/models/layouts/column";
export declare class ScrollButtonClick extends ModelEvent {
}
export declare class ScrollToEvent extends ModelEvent {
    readonly model: Column;
    readonly index: any;
    constructor(model: Column, index: any);
    protected get event_values(): Attrs;
    static from_values(values: object): ScrollToEvent;
}
export declare class ColumnView extends BkColumnView {
    model: Column;
    _updating: boolean;
    scroll_down_button_el: HTMLElement;
    connect_signals(): void;
    get distance_from_latest(): number;
    scroll_to_index(index: number): void;
    scroll_to_position(): void;
    scroll_to_latest(scroll_limit?: number | null): void;
    trigger_auto_scroll(): void;
    record_scroll_position(): void;
    toggle_scroll_button(): void;
    _update_layout(): void;
    render(): void;
    update_children(): Promise<void>;
    after_render(): void;
}
export declare namespace Column {
    type Attrs = p.AttrsOf<Props>;
    type Props = BkColumn.Props & {
        scroll_position: p.Property<number>;
        scroll_index: p.Property<number | null>;
        auto_scroll_limit: p.Property<number>;
        scroll_button_threshold: p.Property<number>;
        view_latest: p.Property<boolean>;
    };
}
export interface Column extends Column.Attrs {
}
export declare class Column extends BkColumn {
    properties: Column.Props;
    constructor(attrs?: Partial<Column.Attrs>);
    static __module__: string;
    on_click(callback: EventCallback<ScrollButtonClick>): void;
}
//# sourceMappingURL=column.d.ts.map