import type { IterViews } from "@bokehjs/core/build_views";
import { ButtonType } from "@bokehjs/core/enums";
import type * as p from "@bokehjs/core/properties";
import { InputWidget, InputWidgetView } from "@bokehjs/models/widgets/input_widget";
import type { IconView } from "@bokehjs/models/ui/icons/icon";
import { Icon } from "@bokehjs/models/ui/icons/icon";
import type { StyleSheetLike } from "@bokehjs/core/dom";
export declare class FileDownloadView extends InputWidgetView {
    model: FileDownload;
    protected icon_view?: IconView;
    anchor_el: HTMLAnchorElement;
    button_el: HTMLButtonElement;
    label_el: Text;
    input_el: HTMLInputElement;
    _downloadable: boolean;
    _click_listener: any;
    _prev_href: string | null;
    _prev_download: string | null;
    children(): IterViews;
    controls(): Generator<any, void, unknown>;
    connect_signals(): void;
    remove(): void;
    lazy_initialize(): Promise<void>;
    _render_input(): HTMLElement;
    render(): void;
    stylesheets(): StyleSheetLike[];
    _increment_clicks(): void;
    _handle_click(): void;
    _make_link_downloadable(): void;
    _update_href(): void;
    _update_download(): void;
    _update_label(): void;
    _update_button_style(): void;
}
export declare namespace FileDownload {
    type Attrs = p.AttrsOf<Props>;
    type Props = InputWidget.Props & {
        auto: p.Property<boolean>;
        button_type: p.Property<ButtonType>;
        clicks: p.Property<number>;
        data: p.Property<string | null>;
        embed: p.Property<boolean>;
        icon: p.Property<Icon | null>;
        label: p.Property<string>;
        filename: p.Property<string | null>;
        _transfers: p.Property<number>;
    };
}
export interface FileDownload extends FileDownload.Attrs {
}
export declare class FileDownload extends InputWidget {
    properties: FileDownload.Props;
    constructor(attrs?: Partial<FileDownload.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=file_download.d.ts.map