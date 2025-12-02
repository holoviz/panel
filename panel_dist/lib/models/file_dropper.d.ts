import { ModelEvent } from "@bokehjs/core/bokeh_events";
import type { StyleSheetLike } from "@bokehjs/core/dom";
import type * as p from "@bokehjs/core/properties";
import type { Attrs } from "@bokehjs/core/types";
import { InputWidget, InputWidgetView } from "@bokehjs/models/widgets/input_widget";
export declare class UploadEvent extends ModelEvent {
    readonly data: any;
    constructor(data: any);
    protected get event_values(): Attrs;
}
export declare class DeleteEvent extends ModelEvent {
    readonly data: any;
    constructor(data: any);
    protected get event_values(): Attrs;
}
export declare class FileDropperView extends InputWidgetView {
    model: FileDropper;
    input_el: HTMLInputElement;
    _file_pond: any | null;
    _transfer_in_process: string | null;
    initialize(): void;
    connect_signals(): void;
    remove(): void;
    stylesheets(): StyleSheetLike[];
    protected _render_input(): HTMLInputElement;
    render(): void;
    private _process_upload;
}
export declare const DropperLayout: import("@bokehjs/core/kinds").Kinds.Enum<"circle" | "integrated" | "compact">;
export declare namespace FileDropper {
    type Attrs = p.AttrsOf<Props>;
    type Props = InputWidget.Props & {
        accepted_filetypes: p.Property<string[]>;
        chunk_size: p.Property<number>;
        layout: p.Property<typeof DropperLayout["__type__"] | null>;
        max_file_size: p.Property<string | null>;
        max_files: p.Property<number | null>;
        max_total_file_size: p.Property<string | null>;
        mime_type: p.Property<any>;
        multiple: p.Property<boolean>;
        previews: p.Property<string[]>;
    };
}
export interface FileDropper extends FileDropper.Attrs {
}
export declare class FileDropper extends InputWidget {
    properties: FileDropper.Props;
    static __module__: string;
    constructor(attrs?: Partial<FileDropper.Attrs>);
}
//# sourceMappingURL=file_dropper.d.ts.map