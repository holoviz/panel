import type * as p from "@bokehjs/core/properties";
import type { StyleSheetLike } from "@bokehjs/core/dom";
import { HTMLBox, HTMLBoxView } from "./layout";
export declare class VideoView extends HTMLBoxView {
    model: Video;
    protected video_el: HTMLVideoElement;
    private _time;
    private _blocked;
    private _setting;
    initialize(): void;
    connect_signals(): void;
    stylesheets(): StyleSheetLike[];
    render(): void;
    update_time(): void;
    update_volume(): void;
    set_loop(): void;
    set_muted(): void;
    set_autoplay(): void;
    set_paused(): void;
    set_volume(): void;
    set_time(): void;
    set_value(): void;
}
export declare namespace Video {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        loop: p.Property<boolean>;
        paused: p.Property<boolean>;
        muted: p.Property<boolean>;
        autoplay: p.Property<boolean>;
        time: p.Property<number>;
        throttle: p.Property<number>;
        value: p.Property<string>;
        volume: p.Property<number | null>;
    };
}
export interface Video extends Video.Attrs {
}
export declare class Video extends HTMLBox {
    properties: Video.Props;
    constructor(attrs?: Partial<Video.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=video.d.ts.map