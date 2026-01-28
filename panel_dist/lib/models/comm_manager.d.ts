import type * as p from "@bokehjs/core/properties";
import { View } from "@bokehjs/core/view";
import { Model } from "@bokehjs/model";
import { Receiver } from "@bokehjs/protocol/receiver";
import type { DocumentChangedEvent } from "@bokehjs/document";
export declare const comm_settings: any;
export declare class CommManagerView extends View {
    model: CommManager;
}
export declare namespace CommManager {
    type Attrs = p.AttrsOf<Props>;
    type Props = Model.Props & {
        plot_id: p.Property<string | null>;
        comm_id: p.Property<string | null>;
        client_comm_id: p.Property<string | null>;
        timeout: p.Property<number>;
        debounce: p.Property<number>;
    };
}
export interface CommManager extends CommManager.Attrs {
}
export declare class CommManager extends Model {
    properties: CommManager.Props;
    __view_type__: CommManagerView;
    ns: any;
    _receiver: Receiver;
    _client_comm: any;
    _event_buffer: DocumentChangedEvent[];
    _timeout: number;
    _blocked: boolean;
    _reconnect: boolean;
    constructor(attrs?: Partial<CommManager.Attrs>);
    initialize(): void;
    protected _document_listener: (event: DocumentChangedEvent) => void;
    protected _doc_attached(): void;
    protected _document_changed(event: DocumentChangedEvent): void;
    protected _extract_buffers(value: unknown, buffers: ArrayBuffer[]): any;
    process_events(): void;
    disconnect_signals(): void;
    on_ack(msg: any): void;
    msg_handler(msg: any): void;
    static __module__: string;
}
//# sourceMappingURL=comm_manager.d.ts.map