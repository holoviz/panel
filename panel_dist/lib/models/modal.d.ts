import type * as p from "@bokehjs/core/properties";
import { Column as BkColumn, ColumnView as BkColumnView } from "@bokehjs/models/layouts/column";
import { ModelEvent } from "@bokehjs/core/bokeh_events";
import type { StyleSheetLike } from "@bokehjs/core/dom";
import type { Attrs } from "@bokehjs/core/types";
declare type A11yDialogView = {
    on(event: string, listener: () => void): void;
    show(): void;
    hide(): void;
};
export declare class ModalDialogEvent extends ModelEvent {
    readonly model: Modal;
    readonly open: boolean;
    constructor(model: Modal, open: boolean);
    protected get event_values(): Attrs;
    static from_values(values: object): ModalDialogEvent;
}
export declare class ModalView extends BkColumnView {
    model: Modal;
    modal: A11yDialogView;
    close_button: HTMLButtonElement;
    connect_signals(): void;
    render(): void;
    stylesheets(): StyleSheetLike[];
    update_children(): Promise<void>;
    create_modal(): void;
    update_close_button(): void;
}
export declare namespace Modal {
    type Attrs = p.AttrsOf<Props>;
    type Props = BkColumn.Props & {
        open: p.Property<boolean>;
        show_close_button: p.Property<boolean>;
        background_close: p.Property<boolean>;
    };
}
export interface Modal extends Modal.Attrs {
}
export declare class Modal extends BkColumn {
    properties: Modal.Props;
    constructor(attrs?: Partial<Modal.Attrs>);
    static __module__: string;
}
export {};
//# sourceMappingURL=modal.d.ts.map