import { ModelEvent } from "@bokehjs/core/bokeh_events";
import type { StyleSheetLike } from "@bokehjs/core/dom";
import type * as p from "@bokehjs/core/properties";
import type { LayoutDOM } from "@bokehjs/models/layouts/layout_dom";
import { ColumnDataSource } from "@bokehjs/models/sources/column_data_source";
import { TableColumn } from "@bokehjs/models/widgets/tables";
import type { Attrs } from "@bokehjs/core/types";
import { HTMLBox, HTMLBoxView } from "./layout";
export declare class TableEditEvent extends ModelEvent {
    readonly column: string;
    readonly row: number;
    readonly pre: boolean;
    constructor(column: string, row: number, pre: boolean);
    protected get event_values(): Attrs;
}
export declare class CellClickEvent extends ModelEvent {
    readonly column: string;
    readonly row: number;
    constructor(column: string, row: number);
    protected get event_values(): Attrs;
}
export declare class SelectionEvent extends ModelEvent {
    readonly indices: number[];
    readonly selected: boolean;
    readonly flush: boolean;
    constructor(indices: number[], selected: boolean, flush?: boolean);
    protected get event_values(): Attrs;
}
export declare class DataTabulatorView extends HTMLBoxView {
    model: DataTabulator;
    tabulator: any;
    columns: Map<string, any>;
    container: HTMLDivElement | null;
    _tabulator_cell_updating: boolean;
    _updating_page: boolean;
    _updating_expanded: boolean;
    _updating_sort: boolean;
    _updating_page_size: boolean;
    _selection_updating: boolean;
    _last_selected_row: any;
    _initializing: boolean;
    _lastVerticalScrollbarTopPosition: number;
    _lastHorizontalScrollbarLeftPosition: number;
    _applied_styles: boolean;
    _building: boolean;
    _redrawing: boolean;
    _debounced_redraw: any;
    _restore_scroll: boolean | "horizontal" | "vertical";
    _updating_scroll: boolean;
    _is_scrolling: boolean;
    _automatic_page_size: boolean;
    connect_signals(): void;
    get groupBy(): boolean | ((data: any) => string);
    get sorters(): any[];
    invalidate_render(): void;
    redraw(columns?: boolean, rows?: boolean): void;
    get is_drawing(): boolean;
    after_layout(): void;
    after_resize(): void;
    _resize_redraw(): void;
    stylesheets(): StyleSheetLike[];
    setCSSClasses(el: HTMLDivElement): void;
    render(): void;
    style_redraw(): void;
    tableInit(): void;
    init_callbacks(): void;
    tableBuilt(): void;
    recompute_page_size(): void;
    requestPage(page: number, sorters: any[]): Promise<void>;
    getLayout(): string;
    getConfiguration(): any;
    get_child(idx: number): LayoutDOM | null;
    get child_models(): LayoutDOM[];
    get row_index(): Map<number, any>;
    renderChildren(): void;
    _render_row(row: any, resize?: boolean): void;
    resize_table(): void;
    _expand_render(cell: any): string;
    _update_expand(cell: any): void;
    getData(): any[];
    getColumns(): any;
    renderEditor(column: any, cell: any, onRendered: any, success: any, cancel: any): any;
    setData(): Promise<void>;
    addData(): void;
    postUpdate(): void;
    updateOrAddData(): void;
    setFrozen(): void;
    setVisibility(): void;
    updatePage(pageno: number): void;
    setGroupBy(): void;
    setSorters(): void;
    setStyles(): void;
    setHidden(): void;
    setMaxPage(): void;
    setPage(): void;
    setPageSize(): void;
    setSelection(): void;
    restore_scroll(horizontal?: boolean, vertical?: boolean): void;
    record_scroll(): void;
    rowClicked(e: any, row: any): void;
    _filter_selected(indices: number[]): number[];
    rowSelectionChanged(data: any, _row: any, selected: any, deselected: any): void;
    cellEdited(cell: any): void;
}
export declare const TableLayout: import("@bokehjs/core/kinds").Kinds.Enum<"fit_data" | "fit_data_fill" | "fit_data_stretch" | "fit_data_table" | "fit_columns">;
export declare namespace DataTabulator {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        aggregators: p.Property<any>;
        buttons: p.Property<any>;
        children: p.Property<Map<number, LayoutDOM>>;
        columns: p.Property<TableColumn[]>;
        configuration: p.Property<any>;
        download: p.Property<boolean>;
        editable: p.Property<boolean>;
        embed_content: p.Property<boolean>;
        expanded: p.Property<number[]>;
        filename: p.Property<string>;
        filters: p.Property<any[]>;
        follow: p.Property<boolean>;
        frozen_rows: p.Property<number[]>;
        groupby: p.Property<string[]>;
        hidden_columns: p.Property<string[]>;
        indexes: p.Property<string[]>;
        layout: p.Property<typeof TableLayout["__type__"]>;
        max_page: p.Property<number>;
        page: p.Property<number>;
        page_size: p.Property<number | null>;
        pagination: p.Property<string | null>;
        select_mode: p.Property<any>;
        selectable_rows: p.Property<number[] | null>;
        source: p.Property<ColumnDataSource>;
        sorters: p.Property<any[]>;
        cell_styles: p.Property<any>;
        theme_classes: p.Property<string[]>;
        container_popup: p.Property<boolean>;
    };
}
export interface DataTabulator extends DataTabulator.Attrs {
}
export declare class DataTabulator extends HTMLBox {
    properties: DataTabulator.Props;
    constructor(attrs?: Partial<DataTabulator.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=tabulator.d.ts.map